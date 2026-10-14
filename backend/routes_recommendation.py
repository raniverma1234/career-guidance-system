from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, UserSkill, Career, CareerSkill, Assessment, Recommendation
from auth_utils import get_current_user
import question_bank as qb
import recommender

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _student_data(db: Session, user: User):
    skill_rows = (
        db.query(UserSkill, Skill)
        .join(Skill, Skill.skill_id == UserSkill.skill_id)
        .filter(UserSkill.user_id == user.user_id)
        .all()
    )
    if not skill_rows:
        raise HTTPException(status_code=400, detail="Please take the skill assessment first")
    skill_levels = {s.skill_name: us.level for us, s in skill_rows}

    interest_rows = db.query(Assessment).filter(
        Assessment.user_id == user.user_id,
        Assessment.assessment_type == "interest",
    ).all()
    if not interest_rows:
        raise HTTPException(status_code=400, detail="Please take the interest assessment first")
    answers = {r.question.split(" | ")[0]: r.answer for r in interest_rows}
    results, _ = qb.score_interest_answers(answers)
    interests = {recommender.INTEREST_COL[r["area"]]: r["score_10"] for r in results}
    return skill_levels, interests


def _career_data(db: Session):
    rows = (
        db.query(Career.career_id, Career.career_name, Skill.skill_name, CareerSkill.importance)
        .join(CareerSkill, CareerSkill.career_id == Career.career_id)
        .join(Skill, Skill.skill_id == CareerSkill.skill_id)
        .all()
    )
    weights, ids = {}, {}
    for cid, cname, sname, imp in rows:
        weights.setdefault(cname, {})[sname] = imp
        ids[cname] = cid
    return weights, ids


@router.post("/generate")
def generate(
    top_n: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill_levels, interests = _student_data(db, current_user)
    weights, ids = _career_data(db)
    if not weights:
        raise HTTPException(status_code=500, detail="No career data found. Run seed_data.py first")

    recs = recommender.recommend(skill_levels, interests, weights, top_n=top_n)

    db.query(Recommendation).filter(Recommendation.user_id == current_user.user_id).delete()
    for r in recs:
        db.add(Recommendation(
            user_id=current_user.user_id,
            career_id=ids[r["career_name"]],
            match_score=r["match_percent"],
            explanation=r["explanation"],
        ))
    db.commit()
    return {"recommendations": recs}


@router.get("/me")
def my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Recommendation, Career)
        .join(Career, Career.career_id == Recommendation.career_id)
        .filter(Recommendation.user_id == current_user.user_id)
        .order_by(Recommendation.match_score.desc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No recommendations yet. Call POST /recommendations/generate")
    return {"recommendations": [
        {
            "career_id": c.career_id,
            "career_name": c.career_name,
            "match_percent": r.match_score,
            "explanation": r.explanation,
            "generated_at": r.generated_at,
        } for r, c in rows
    ]}