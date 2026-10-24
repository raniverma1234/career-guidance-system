from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, UserSkill, Project
from auth_utils import get_current_user
from routes_careers import _career_weights
import resume_analyzer

router = APIRouter(prefix="/resume", tags=["Resume"])

MAX_BYTES = 5 * 1024 * 1024   # 5 MB


@router.post("/analyze")
def analyze_resume(
    career_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = file.file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File is too large. Maximum size is 5 MB")

    career, weights, _ = _career_weights(db, career_id)
    try:
        text = resume_analyzer.extract_text(file.filename, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = resume_analyzer.analyze(text, career.career_name, weights)
    result["career_id"] = career_id

    # projects that would add the missing skills to the resume
    all_names = {name for (name,) in db.query(Skill.skill_name).all()}
    missing = {m["skill"] for m in result["missing_skills"]}
    rows = db.query(Project).filter(Project.career_id == career_id).all()
    plist = [{
        "project_id": p.id, "title": p.title, "difficulty": p.difficulty,
        "required_skills": p.required_skills, "dataset": p.dataset,
        "expected_output": p.expected_output, "estimated_time": p.estimated_time,
    } for p in rows]
    result["project_suggestions"] = resume_analyzer.suggest_projects(plist, missing, all_names)

    # compare the resume with the student's own skill assessment (if taken)
    profile_rows = (
        db.query(UserSkill, Skill)
        .join(Skill, Skill.skill_id == UserSkill.skill_id)
        .filter(UserSkill.user_id == current_user.user_id)
        .all()
    )
    if profile_rows:
        found = {s["skill"] for s in result["skills_found"]}
        strong = {s.skill_name for us, s in profile_rows if us.level >= 6}
        result["profile_check"] = {
            "strong_in_assessment_but_not_in_resume": sorted(strong - found),
            "tip": "These are skills you rated yourself 6/10 or more on but the resume does not mention. "
                   "Add them if they are true.",
        }

    # the resume file itself is not stored; only this analysis is returned
    return result