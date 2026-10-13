from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, UserSkill
from schemas import UserOut, ProfileUpdate, SkillOut, SkillLevelIn, SkillLevelOut
from auth_utils import get_current_user

router = APIRouter(tags=["Profile"])


@router.get("/profile/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile/me", response_model=UserOut)
def update_me(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/skills", response_model=List[SkillOut])
def all_skills(db: Session = Depends(get_db)):
    return db.query(Skill).order_by(Skill.category, Skill.skill_name).all()


@router.get("/profile/skills", response_model=List[SkillLevelOut])
def my_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(UserSkill, Skill)
        .join(Skill, Skill.skill_id == UserSkill.skill_id)
        .filter(UserSkill.user_id == current_user.user_id)
        .all()
    )
    return [
        {"skill_name": s.skill_name, "category": s.category, "level": us.level}
        for us, s in rows
    ]


@router.put("/profile/skills", response_model=List[SkillLevelOut])
def set_my_skills(
    items: List[SkillLevelIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    names = [i.skill_name for i in items]
    skills = {
        s.skill_name: s
        for s in db.query(Skill).filter(Skill.skill_name.in_(names)).all()
    }
    unknown = [n for n in names if n not in skills]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown skills: {unknown}")

    for item in items:
        skill = skills[item.skill_name]
        row = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == current_user.user_id,
                    UserSkill.skill_id == skill.skill_id)
            .first()
        )
        if row:
            row.level = item.level
        else:
            db.add(UserSkill(user_id=current_user.user_id,
                             skill_id=skill.skill_id, level=item.level))
    db.commit()
    return my_skills(db=db, current_user=current_user)