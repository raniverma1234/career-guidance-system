import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import User, Skill, UserSkill, Career, Assessment, Recommendation
from auth_utils import get_current_user
from routes_careers import _career_weights, _projects
from routes_progress import _resolve_career, _career_progress
import question_bank as qb
import skill_gap
import assistant
import assistant_llm

router = APIRouter(prefix="/assistant", tags=["AI Career Assistant"])
log = logging.getLogger("assistant")


class Msg(BaseModel):
    role: str
    content: str


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: List[Msg] = Field(default_factory=list, max_length=12)
    career_id: Optional[int] = None


def _target_summary(db: Session, career: Career, levels: dict):
    career_row, weights, cats = _career_weights(db, career.career_id)
    analysis = skill_gap.analyze(career_row.career_name, weights, levels, cats)
    projects = _projects(db, career.career_id, levels)
    return assistant.summarize_target(analysis, projects, {
        "career_id": career_row.career_id, "tools": career_row.tools,
        "interview_topics": career_row.interview_topics,
    })


def _build_context(db: Session, user: User, message: str, career_id: Optional[int]):
    # skills
    rows = (
        db.query(UserSkill, Skill)
        .join(Skill, Skill.skill_id == UserSkill.skill_id)
        .filter(UserSkill.user_id == user.user_id)
        .all()
    )
    levels = {s.skill_name: us.level for us, s in rows}

    # interests
    interests = []
    int_rows = db.query(Assessment).filter(
        Assessment.user_id == user.user_id, Assessment.assessment_type == "interest").all()
    if int_rows:
        answers = {r.question.split(" | ")[0]: r.answer for r in int_rows}
        try:
            results, _ = qb.score_interest_answers(answers)
            interests = [{"area": r["area"], "percent": r["percent"]} for r in results]
        except ValueError:
            interests = []

    # saved recommendations (top 3)
    rec_rows = (
        db.query(Recommendation, Career)
        .join(Career, Career.career_id == Recommendation.career_id)
        .filter(Recommendation.user_id == user.user_id)
        .order_by(Recommendation.match_score.desc())
        .limit(3)
        .all()
    )
    recs = [{"career_name": c.career_name, "match_percent": r.match_score} for r, c in rec_rows]

    # which career(s) are we talking about?
    all_careers = db.query(Career).all()
    by_name = {c.career_name: c for c in all_careers}
    mentioned = assistant.find_careers(message, list(by_name))[:2]
    chosen = [by_name[n] for n in mentioned]
    if not chosen:
        try:
            chosen = [_resolve_career(db, user, career_id)]
        except HTTPException:
            chosen = []

    targets, progress_data = [], None
    if levels:
        targets = [_target_summary(db, c, levels) for c in chosen]
    if chosen:
        progress_data = _career_progress(db, user, chosen[0])

    profile = {
        "name": user.name, "education": user.education, "branch": user.branch,
        "semester": user.semester, "cgpa": user.cgpa, "career_goal": user.career_goal,
    }
    return assistant.build_context(profile, levels, interests, recs, targets, progress_data)


@router.get("/status")
def status():
    enabled = assistant_llm.is_enabled()
    return {
        "mode": "ai" if enabled else "rule-based",
        "ai_enabled": enabled,
        "provider": assistant_llm.provider(),
        "model": assistant_llm.model_name(),
    }


@router.post("/chat")
def chat(
    body: ChatIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Please type a question")

    ctx = _build_context(db, current_user, message, body.career_id)
    fallback_text, intent = assistant.rule_based_reply(message, ctx)

    reply, mode, note = fallback_text, "rule-based", None
    if assistant_llm.is_enabled():
        try:
            history = assistant.clean_history([m.model_dump() for m in body.history])
            # privacy: send only the first name to the AI service
            first_name = (ctx["user"].get("name") or "").split(" ")[0]
            ai_ctx = {**ctx, "user": {**ctx["user"], "name": first_name}}
            ai_text = assistant_llm.ask(assistant.build_system_prompt(ai_ctx), history, message)
            if ai_text:
                reply, mode = ai_text, "ai"
        except Exception as e:           # network, bad key, no quota, missing package ...
            log.warning("AI call failed: %s", e)
            note = "The AI service is not available right now, so this is the built-in answer."

    return {
        "reply": reply,
        "mode": mode,
        "provider": assistant_llm.provider() if mode == "ai" else None,
        "note": note,
        "suggestions": assistant.suggestions_for(intent, ctx),
    }