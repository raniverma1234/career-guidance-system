from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Skill, Career, CareerSkill, Project, Roadmap
import explorer

router = APIRouter(prefix="/explorer", tags=["Job Role Explorer"])


@router.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    careers = db.query(Career).order_by(Career.career_name).all()

    skill_rows = (
        db.query(CareerSkill.career_id, Skill.skill_name, CareerSkill.importance)
        .join(Skill, Skill.skill_id == CareerSkill.skill_id)
        .all()
    )
    skills_by_career = {}
    for cid, name, imp in skill_rows:
        skills_by_career.setdefault(cid, []).append({"skill": name, "importance": imp})

    project_counts = dict(
        db.query(Project.career_id, func.count(Project.id)).group_by(Project.career_id).all()
    )

    return [
        explorer.build_role_summary(
            {"career_id": c.career_id, "career_name": c.career_name, "description": c.description},
            skills_by_career.get(c.career_id, []),
            project_counts.get(c.career_id, 0),
        )
        for c in careers
    ]


@router.get("/roles/{career_id}")
def role_detail(career_id: int, db: Session = Depends(get_db)):
    career = db.query(Career).filter(Career.career_id == career_id).first()
    if career is None:
        raise HTTPException(status_code=404, detail=f"Career {career_id} not found")

    skill_rows = (
        db.query(Skill.skill_name, Skill.category, CareerSkill.importance)
        .join(CareerSkill, CareerSkill.skill_id == Skill.skill_id)
        .filter(CareerSkill.career_id == career_id)
        .all()
    )
    skills = [{"skill": n, "category": c, "importance": i} for n, c, i in skill_rows]

    projects = [{
        "project_id": p.id, "title": p.title, "difficulty": p.difficulty,
        "required_skills": p.required_skills, "dataset": p.dataset,
        "expected_output": p.expected_output, "estimated_time": p.estimated_time,
    } for p in db.query(Project).filter(Project.career_id == career_id).all()]

    months = [{"month_no": r.month_no, "title": r.title, "topics": r.topics}
              for r in db.query(Roadmap).filter(Roadmap.career_id == career_id)
              .order_by(Roadmap.month_no).all()]

    return explorer.build_role_detail(
        {"career_id": career.career_id, "career_name": career.career_name,
         "description": career.description, "tools": career.tools,
         "interview_topics": career.interview_topics},
        skills, projects, months,
    )