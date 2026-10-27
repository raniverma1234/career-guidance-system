from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, UserSkill, Career, Assessment, Recommendation, Progress
from auth_utils import require_admin
import question_bank as qb
import admin_stats as stats

router = APIRouter(prefix="/admin", tags=["Admin"])


def _d(value):
    """DateTime -> date (or None)."""
    return value.date() if value is not None else None


@router.get("/dashboard")
def dashboard(
    days: int = Query(14, ge=7, le=60, description="How many days of usage to show"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    today = date.today()

    users = db.query(User.user_id, User.role, User.created_at, User.career_goal).all()
    student_created = {u.user_id: _d(u.created_at) for u in users if u.role == "student"}
    students = set(student_created)

    skill_ids = {r[0] for r in db.query(Assessment.user_id).filter(Assessment.assessment_type == "skill").distinct().all()}
    interest_ids = {r[0] for r in db.query(Assessment.user_id).filter(Assessment.assessment_type == "interest").distinct().all()}

    recs = (
        db.query(Recommendation.user_id, Career.career_name, Recommendation.match_score, Recommendation.generated_at)
        .join(Career, Career.career_id == Recommendation.career_id)
        .all()
    )
    rec_rows = [(r.user_id, r.career_name, r.match_score) for r in recs]
    rec_users = {r.user_id for r in recs}

    user_skills = [
        (r.user_id, r.skill_name, r.category, r.level)
        for r in db.query(UserSkill.user_id, Skill.skill_name, Skill.category, UserSkill.level)
        .join(Skill, Skill.skill_id == UserSkill.skill_id).all()
    ]

    area_of = {qid: q["area"] for qid, q in qb.INTEREST_BY_ID.items()}
    interest_rows = [
        (r.user_id, (r.question or "").split(" | ")[0], r.answer)
        for r in db.query(Assessment.user_id, Assessment.question, Assessment.answer)
        .filter(Assessment.assessment_type == "interest").all()
    ]

    progress = db.query(Progress.user_id, Progress.completed, Progress.updated_at).all()

    return {
        "overview": stats.build_overview(
            student_created, skill_ids, interest_ids, rec_users,
            [(p.user_id, p.completed) for p in progress], today),
        "popular_careers": stats.popular_careers(rec_rows, students),
        "popular_career_goals": stats.popular_goals([u.career_goal for u in users if u.role == "student"]),
        "popular_skills": stats.popular_skills(user_skills, students),
        "assessment_results": {
            "interest_areas": stats.interest_results(interest_rows, area_of, students),
            "skill_categories": stats.skill_category_results(user_skills, students),
        },
        "usage": stats.usage_series(
            list(student_created.values()),
            [_d(r.generated_at) for r in recs if r.user_id in students],
            [_d(p.updated_at) for p in progress if p.user_id in students],
            days, today),
        "note": "All numbers are calculated from this system's own data. Match scores are indicators, not predictions.",
    }


@router.get("/students")
def list_students(
    q: Optional[str] = Query(None, description="Search by name or email"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(User).filter(User.role == "student")
    if q and q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like)))
    total = query.count()
    rows = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    ids = [u.user_id for u in rows]

    skill_ids, interest_ids, best = set(), set(), {}
    if ids:
        for uid, a_type in db.query(Assessment.user_id, Assessment.assessment_type).filter(
                Assessment.user_id.in_(ids)).distinct().all():
            (skill_ids if a_type == "skill" else interest_ids).add(uid)
        for uid, name, score in (
            db.query(Recommendation.user_id, Career.career_name, Recommendation.match_score)
            .join(Career, Career.career_id == Recommendation.career_id)
            .filter(Recommendation.user_id.in_(ids)).all()
        ):
            if uid not in best or (score or 0) > best[uid][1]:
                best[uid] = (name, score or 0)

    return {
        "total": total, "limit": limit, "offset": offset,
        "students": [{
            "user_id": u.user_id, "name": u.name, "email": u.email,
            "branch": u.branch, "semester": u.semester, "career_goal": u.career_goal,
            "joined": u.created_at,
            "skill_assessment_done": u.user_id in skill_ids,
            "interest_assessment_done": u.user_id in interest_ids,
            "top_match": ({"career_name": best[u.user_id][0], "match_percent": best[u.user_id][1]}
                          if u.user_id in best else None),
        } for u in rows],
    }