from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from database import get_db
from models import User, Career, Roadmap, Project, Progress, Recommendation
from auth_utils import get_current_user
import progress

router = APIRouter(prefix="/progress", tags=["Progress"])


class ProgressUpdate(BaseModel):
    completed: bool


def _resolve_career(db: Session, user: User, career_id: Optional[int]) -> Career:
    """Which career is the student working towards?
    1) career_id given, 2) career goal in the profile, 3) top saved recommendation."""
    if career_id is not None:
        career = db.query(Career).filter(Career.career_id == career_id).first()
        if career is None:
            raise HTTPException(status_code=404, detail=f"Career {career_id} not found")
        return career

    careers = db.query(Career).all()
    matched = progress.match_career_name(user.career_goal, [c.career_name for c in careers])
    if matched:
        return next(c for c in careers if c.career_name == matched)

    top = (
        db.query(Career)
        .join(Recommendation, Recommendation.career_id == Career.career_id)
        .filter(Recommendation.user_id == user.user_id)
        .order_by(Recommendation.match_score.desc())
        .first()
    )
    if top:
        return top

    raise HTTPException(
        status_code=400,
        detail="Choose a career: pass career_id, set your career goal in the profile, "
               "or generate recommendations first.",
    )


def _career_progress(db: Session, user: User, career: Career):
    months = db.query(Roadmap).filter(Roadmap.career_id == career.career_id).order_by(Roadmap.month_no).all()
    projects = db.query(Project).filter(Project.career_id == career.career_id).all()
    done = db.query(Progress).filter(
        Progress.user_id == user.user_id, Progress.completed.is_(True)).all()
    done_roadmap = {p.item_id for p in done if p.item_type == "roadmap"}
    done_project = {p.item_id for p in done if p.item_type == "project"}

    return progress.summarize(
        career.career_id, career.career_name,
        [{"roadmap_id": r.id, "month_no": r.month_no, "title": r.title} for r in months],
        [{"project_id": p.id, "title": p.title, "difficulty": p.difficulty} for p in projects],
        done_roadmap, done_project,
    )


@router.get("/me")
def my_progress(
    career_id: Optional[int] = Query(None, description="Leave empty to use your career goal or top recommendation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    career = _resolve_career(db, current_user, career_id)
    return _career_progress(db, current_user, career)


@router.put("/{item_type}/{item_id}")
def set_progress(
    item_type: str,
    item_id: int,
    body: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if item_type == "roadmap":
        item = db.query(Roadmap).filter(Roadmap.id == item_id).first()
    elif item_type == "project":
        item = db.query(Project).filter(Project.id == item_id).first()
    else:
        raise HTTPException(status_code=400, detail="item_type must be 'roadmap' or 'project'")
    if item is None:
        raise HTTPException(status_code=404, detail=f"{item_type} {item_id} not found")

    row = db.query(Progress).filter(
        Progress.user_id == current_user.user_id,
        Progress.item_type == item_type,
        Progress.item_id == item_id,
    ).first()
    if row:
        row.completed = body.completed
        row.updated_at = func.now()
    else:
        db.add(Progress(user_id=current_user.user_id, item_type=item_type,
                        item_id=item_id, completed=body.completed))
    db.commit()

    career = db.query(Career).filter(Career.career_id == item.career_id).first()
    return {
        "item_type": item_type,
        "item_id": item_id,
        "completed": body.completed,
        "career_progress": _career_progress(db, current_user, career),
    }