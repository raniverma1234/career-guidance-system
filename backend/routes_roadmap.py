from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, Project, Roadmap
from auth_utils import get_current_user
from routes_careers import _my_levels, _career_weights
import roadmap
import skill_gap

router = APIRouter(prefix="/careers", tags=["Roadmap & Projects"])


@router.get("/{career_id}/roadmap")
def personalised_roadmap(
    career_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    levels = _my_levels(db, current_user)
    career, weights, _ = _career_weights(db, career_id)
    rows = (
        db.query(Roadmap)
        .filter(Roadmap.career_id == career_id)
        .order_by(Roadmap.month_no)
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No roadmap found for this career. Run seed_data.py")

    months = [{"month_no": r.month_no, "title": r.title, "topics": r.topics} for r in rows]
    result = roadmap.build_plan(career.career_name, months, weights, levels)
    result["career_id"] = career_id
    return result


@router.get("/{career_id}/projects")
def recommended_projects(
    career_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    levels = _my_levels(db, current_user)
    career, _, _ = _career_weights(db, career_id)
    rows = db.query(Project).filter(Project.career_id == career_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No projects found for this career. Run seed_data.py")

    plist = [{
        "project_id": p.id, "title": p.title, "difficulty": p.difficulty,
        "required_skills": p.required_skills, "dataset": p.dataset,
        "expected_output": p.expected_output, "estimated_time": p.estimated_time,
    } for p in rows]
    all_names = {name for (name,) in db.query(Skill.skill_name).all()}
    ranked = skill_gap.rank_projects(plist, levels, all_names)
    for i, p in enumerate(ranked, start=1):
        p["recommended_order"] = i

    return {
        "career_id": career_id,
        "career_name": career.career_name,
        "start_with": ranked[0]["title"],
        "projects": ranked,
        "note": "Projects are ordered by how many of their skills you already have, then by difficulty.",
    }