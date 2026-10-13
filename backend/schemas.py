from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)
    age: Optional[int] = Field(default=None, ge=10, le=100)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    role: str
    age: Optional[int] = None
    education: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    career_goal: Optional[str] = None
    interests: Optional[str] = None
    projects: Optional[str] = None
    certifications: Optional[str] = None
    experience: Optional[str] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    age: Optional[int] = Field(default=None, ge=10, le=100)
    education: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = Field(default=None, ge=1, le=12)
    cgpa: Optional[float] = Field(default=None, ge=0, le=10)
    career_goal: Optional[str] = None
    interests: Optional[str] = None
    projects: Optional[str] = None
    certifications: Optional[str] = None
    experience: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    skill_name: str
    category: Optional[str] = None


class SkillLevelIn(BaseModel):
    skill_name: str
    level: int = Field(ge=0, le=10)


class SkillLevelOut(BaseModel):
    skill_name: str
    category: Optional[str] = None
    level: int