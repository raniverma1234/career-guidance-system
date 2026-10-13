from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    education = Column(String(100))
    branch = Column(String(100))
    semester = Column(Integer)
    cgpa = Column(Float)
    career_goal = Column(String(150))
    created_at = Column(DateTime, server_default=func.now())


class Skill(Base):
    __tablename__ = "skills"
    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100))


class UserSkill(Base):
    __tablename__ = "user_skills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"), nullable=False)
    level = Column(Integer, default=0)  # 0-10


class Career(Base):
    __tablename__ = "careers"
    career_id = Column(Integer, primary_key=True, index=True)
    career_name = Column(String(150), unique=True, nullable=False)
    description = Column(Text)
    tools = Column(Text)
    interview_topics = Column(Text)


class CareerSkill(Base):
    __tablename__ = "career_skills"
    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.career_id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"), nullable=False)
    importance = Column(Integer, default=3)  # 1-5


class Assessment(Base):
    __tablename__ = "assessments"
    assessment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    assessment_type = Column(String(20))  # skill / interest
    question = Column(Text)
    answer = Column(String(255))
    score = Column(Float)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.career_id"), nullable=False)
    match_score = Column(Float)
    explanation = Column(Text)
    generated_at = Column(DateTime, server_default=func.now())


class Roadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.career_id"), nullable=False)
    month_no = Column(Integer)
    title = Column(String(150))
    topics = Column(Text)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.career_id"), nullable=False)
    title = Column(String(150))
    difficulty = Column(String(30))
    required_skills = Column(Text)
    dataset = Column(String(200))
    expected_output = Column(Text)
    estimated_time = Column(String(50))


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    item_type = Column(String(20))  # roadmap / project
    item_id = Column(Integer)
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime, server_default=func.now())
    