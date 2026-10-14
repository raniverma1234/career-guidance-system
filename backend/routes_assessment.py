from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, UserSkill, Assessment
from auth_utils import get_current_user
import question_bank as qb

router = APIRouter(prefix="/assessment", tags=["Assessment"])


class AnswerIn(BaseModel):
    question_id: str
    answer: Union[str, int]


def _to_dict(items: List[AnswerIn]):
    return {i.question_id: i.answer for i in items}


def _replace_rows(db: Session, user_id: int, a_type: str, details):
    """Delete the old attempt of this type and store the new one."""
    db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.assessment_type == a_type,
    ).delete()
    for qid, text, answer, score in details:
        db.add(Assessment(
            user_id=user_id, assessment_type=a_type,
            question=f"{qid} | {text}", answer=answer, score=score,
        ))


@router.get("/questions")
def get_questions():
    return {
        "skill_questions": qb.public_skill_questions(),
        "interest_questions": qb.public_interest_questions(),
    }


@router.post("/skills")
def submit_skill_assessment(
    items: List[AnswerIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not items:
        raise HTTPException(status_code=400, detail="No answers submitted")
    try:
        levels, details = qb.score_skill_answers(_to_dict(items))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    skills = {s.skill_name: s for s in
              db.query(Skill).filter(Skill.skill_name.in_(list(levels))).all()}
    existing = {us.skill_id: us for us in
                db.query(UserSkill).filter(UserSkill.user_id == current_user.user_id).all()}

    for name, level in levels.items():
        skill = skills.get(name)
        if skill is None:
            continue
        row = existing.get(skill.skill_id)
        if row:
            row.level = level
        else:
            db.add(UserSkill(user_id=current_user.user_id,
                             skill_id=skill.skill_id, level=level))

    _replace_rows(db, current_user.user_id, "skill", details)
    db.commit()

    return {
        "message": "Skill assessment saved",
        "skills": [{"skill_name": n, "level": l}
                   for n, l in sorted(levels.items(), key=lambda x: -x[1])],
    }


@router.post("/interests")
def submit_interest_assessment(
    items: List[AnswerIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        results, details = qb.score_interest_answers(_to_dict(items))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    _replace_rows(db, current_user.user_id, "interest", details)
    db.commit()
    return {"message": "Interest assessment saved", "interests": results}


@router.get("/interests/result")
def interest_result(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.query(Assessment).filter(
        Assessment.user_id == current_user.user_id,
        Assessment.assessment_type == "interest",
    ).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Interest assessment not taken yet")

    answers = {r.question.split(" | ")[0]: r.answer for r in rows}
    results, _ = qb.score_interest_answers(answers)
    return {"interests": results}