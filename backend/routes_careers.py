from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, UserSkill, Career, CareerSkill, Project
from auth_utils import get_current_user
import skill_gap

router = APIRouter(prefix="/careers", tags=["Careers"])


def _my_levels(db: Session, user: User):
    rows = (
        db.query(UserSkill, Skill)
        .join(Skill, Skill.skill_id == UserSkill.skill_id)
        .filter(UserSkill.user_id == user.user_id)
        .all()
    )
    if not rows:
        raise HTTPException(status_code=400, detail="Please take the skill assessment first")
    return {s.skill_name: us.level for us, s in rows}


def _career_weights(db: Session, career_id: int):
    career = db.query(Career).filter(Career.career_id == career_id).first()
    if career is None:
        raise HTTPException(status_code=404, detail=f"Career {career_id} not found")
    rows = (
        db.query(Skill.skill_name, Skill.category, CareerSkill.importance)
        .join(CareerSkill, CareerSkill.skill_id == Skill.skill_id)
        .filter(CareerSkill.career_id == career_id)
        .all()
    )
    weights = {name: imp for name, _, imp in rows}
    categories = {name: cat for name, cat, _ in rows}
    return career, weights, categories


def _projects(db: Session, career_id: int, levels: dict):
    rows = db.query(Project).filter(Project.career_id == career_id).all()
    plist = [{
        "title": p.title, "difficulty": p.difficulty, "required_skills": p.required_skills,
        "dataset": p.dataset, "expected_output": p.expected_output,
        "estimated_time": p.estimated_time,
    } for p in rows]
    all_names = {name for (name,) in db.query(Skill.skill_name).all()}
    return skill_gap.rank_projects(plist, levels, all_names)


@router.get("")
def list_careers(db: Session = Depends(get_db)):
    careers = db.query(Career).order_by(Career.career_name).all()
    return [{"career_id": c.career_id, "career_name": c.career_name,
             "description": c.description} for c in careers]


@router.get("/compare")
def compare_careers(
    career_ids: str = Query(..., description="2 or 3 career ids separated by commas, e.g. 1,4"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ids = list(dict.fromkeys(int(x) for x in career_ids.split(",") if x.strip()))
    except ValueError:
        raise HTTPException(status_code=400, detail="career_ids must be numbers like 1,4")
    if not 2 <= len(ids) <= 3:
        raise HTTPException(status_code=400, detail="Please choose 2 or 3 different careers")

    levels = _my_levels(db, current_user)
    analyses, projects = [], {}
    for cid in ids:
        career, weights, cats = _career_weights(db, cid)
        a = skill_gap.analyze(career.career_name, weights, levels, cats)
        analyses.append(a)
        projects[career.career_name] = _projects(db, cid, levels)

    result = skill_gap.compare(analyses)
    result["recommended_projects"] = projects
    return result


@router.get("/{career_id}/skill-gap")
def skill_gap_for_career(
    career_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    levels = _my_levels(db, current_user)
    career, weights, cats = _career_weights(db, career_id)
    result = skill_gap.analyze(career.career_name, weights, levels, cats)
    result["career_id"] = career_id
    result["recommended_projects"] = _projects(db, career_id, levels)
    return result