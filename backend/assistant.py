"""
Step 12: AI Career Assistant logic (pure Python, no database, no internet).

Two ways to answer, same data:
  1. rule_based_reply()  - works without any API key. Understands the question (English / Hinglish)
                           and builds the answer from the student's own data.
  2. build_system_prompt() - used when an AI key is configured: the same student data is given
                           to the AI model so it can answer in natural language.

The assistant is profile-aware: skills, interests, recommendations, skill gaps, roadmap progress.
"""
import re

# ------------------------------------------------------------------ CAREERS
CAREER_PATTERNS = {
    "Data Analyst": [r"data analy(st|tics)"],
    "Data Scientist": [r"data scien(tist|ce)"],
    "ML Engineer": [r"\bml engineer", r"machine learning engineer"],
    "Software Developer": [r"software (developer|engineer|dev)\b", r"\bsde\b"],
    "Web Developer": [r"web dev(eloper)?\b", r"frontend developer", r"full ?stack"],
    "UI/UX Designer": [r"ui ?/? ?ux", r"\bux designer"],
    "Cyber Security Analyst": [r"cyber ?security", r"security analyst"],
    "Cloud Engineer": [r"cloud engineer"],
    "DevOps Engineer": [r"devops"],
    "Business Analyst": [r"business analy(st|sis)"],
}


def find_careers(message, names):
    """career names mentioned in the message, in the order they appear."""
    text = message.lower()
    hits = []
    for name in names:
        for p in CAREER_PATTERNS.get(name, [re.escape(name.lower())]):
            m = re.search(p, text)
            if m:
                hits.append((m.start(), name))
                break
    return [n for _, n in sorted(hits)]


# ------------------------------------------------------------------ INTENTS
INTENTS = [
    ("guarantee", [r"guarantee", r"placement", r"salary", r"job (milegi|mil jayegi|lag)", r"naukri (milegi|lagegi|mil)"]),
    ("compare", [r"compare", r"\bvs\b", r"versus", r"difference", r"\bfark\b"]),
    ("resume", [r"resume", r"\bcv\b"]),
    ("projects", [r"project"]),
    ("interview", [r"interview"]),
    ("progress", [r"progress", r"complete", r"kitna (hua|ho gaya)", r"\bdone\b"]),
    ("skill_gap", [r"\bgaps?\b", r"missing", r"\bkami\b", r"kamzor", r"weak", r"improve", r"nahi aata", r"\black"]),
    ("learn_next", [r"learn", r"seekh", r"sikh", r"\bnext\b", r"roadmap", r"\bplan\b", r"shuru", r"\bstart", r"\baage\b", r"padh", r"study", r"prepare"]),
    ("career_suggestion", [r"(which|kaun si|kaunsi|konsi|best|suitable) (career|job)"]),
    ("my_skills", [r"my skills", r"meri skills", r"strength", r"kya aata", r"\bstrong"]),
    ("career_suggestion", [r"career", r"job role", r"\bsuit", r"recommend", r"suggest", r"best fit", r"kya ban", r"kaun si"]),
]
_GREETING = re.compile(r"^\s*(hi+|hello|hey|namaste|hola|help)\b", re.I)


def detect_intent(message):
    text = message.lower()
    if _GREETING.match(text) and len(text.split()) <= 4:
        return "greeting"
    for intent, patterns in INTENTS:
        if any(re.search(p, text) for p in patterns):
            return intent
    return "fallback"


# ------------------------------------------------------------------ CONTEXT
def _split(text):
    return [t.strip() for t in (text or "").split(",") if t.strip()]


def summarize_target(analysis, projects, career):
    """analysis: skill_gap.analyze() result, projects: ranked projects, career: dict"""
    todo = [s for s in analysis["skills"] if s["status"] != "Available"]
    done = sorted([s for s in analysis["skills"] if s["status"] == "Available"], key=lambda s: -s["your_level"])
    return {
        "career_id": career.get("career_id"),
        "career_name": analysis["career_name"],
        "readiness_percent": analysis["readiness_percent"],
        "available": analysis["available"], "to_improve": analysis["to_improve"], "to_learn": analysis["to_learn"],
        "estimated_weeks": analysis["estimated_weeks"], "estimated_months": analysis["estimated_months"],
        "next_step": analysis["next_step"],
        "gaps": [{"skill": s["skill"], "your_level": s["your_level"], "target_level": s["required_level"],
                  "priority": s["priority"], "status": s["status"]} for s in todo[:5]],
        "strengths": [{"skill": s["skill"], "your_level": s["your_level"]} for s in done[:4]],
        "projects": [{"title": p["title"], "difficulty": p["difficulty"], "estimated_time": p["estimated_time"],
                      "ready_percent": p["ready_percent"]} for p in projects[:3]],
        "tools": _split(career.get("tools")),
        "interview_topics": _split(career.get("interview_topics")),
    }


def build_context(user, skills, interests, recommendations, targets, progress):
    """
    user            : {"name","education","branch","semester","cgpa","career_goal"}
    skills          : {"Python": 8, ...}
    interests       : [{"area": "Data", "percent": 93}, ...]
    recommendations : [{"career_name","match_percent"}]
    targets         : [summarize_target(...)]  (first one = main career being discussed)
    progress        : progress.summarize() result or None
    """
    return {"user": user, "skills": skills, "interests": interests,
            "recommendations": recommendations, "targets": targets, "progress": progress}


def context_to_text(ctx):
    u, L = ctx["user"], []
    L.append(f"Student: {u.get('name') or 'Student'}; education: {u.get('education') or 'not given'}, "
             f"branch: {u.get('branch') or 'not given'}, semester: {u.get('semester') or 'not given'}, "
             f"CGPA: {u.get('cgpa') or 'not given'}; career goal: {u.get('career_goal') or 'not given'}")
    if ctx["skills"]:
        L.append("Skill levels (0-10): " + ", ".join(
            f"{k} {v}" for k, v in sorted(ctx["skills"].items(), key=lambda x: -x[1])))
    else:
        L.append("Skill assessment: NOT taken yet")
    if ctx["interests"]:
        L.append("Interests: " + ", ".join(f"{i['area']} {i['percent']}%" for i in ctx["interests"]))
    else:
        L.append("Interest assessment: NOT taken yet")
    if ctx["recommendations"]:
        L.append("Top career matches: " + ", ".join(
            f"{r['career_name']} {r['match_percent']}%" for r in ctx["recommendations"]))
    else:
        L.append("Career recommendations: not generated yet")
    for t in ctx["targets"]:
        L.append(f"Career discussed: {t['career_name']} - readiness {t['readiness_percent']}%; "
                 f"{t['available']} skills at target, {t['to_improve']} to improve, {t['to_learn']} to learn; "
                 f"rough time {t['estimated_weeks']} weeks. {t['next_step']}.")
        if t["gaps"]:
            L.append("  Gaps: " + "; ".join(
                f"{g['skill']} {g['your_level']}/10 -> {g['target_level']}/10 ({g['priority']} priority)" for g in t["gaps"]))
        if t["strengths"]:
            L.append("  Strengths: " + ", ".join(f"{s['skill']} {s['your_level']}/10" for s in t["strengths"]))
        if t["projects"]:
            L.append("  Suggested projects: " + "; ".join(
                f"{p['title']} ({p['difficulty']}, {p['ready_percent']}% ready)" for p in t["projects"]))
        if t["tools"]:
            L.append("  Tools: " + ", ".join(t["tools"]))
        if t["interview_topics"]:
            L.append("  Interview topics: " + ", ".join(t["interview_topics"]))
    p = ctx["progress"]
    if p:
        nxt = p["next_up"]["title"] if p.get("next_up") else "all done"
        L.append(f"Progress for {p['career_name']}: overall {p['overall_percent']}% "
                 f"({p['completed_months']}/{p['total_months']} months, "
                 f"{p['completed_projects']}/{p['total_projects']} projects). Next up: {nxt}.")
    return "\n".join(L)


SYSTEM_PROMPT = """You are the AI Career Assistant inside "AI-Powered Personalized Career Guidance and Skill Development System", a student project.

Rules:
- Use ONLY the student data below for facts about the student. Never invent skills, levels, scores or progress.
- Answer career-guidance questions: what to learn next, skill gaps, roadmaps, projects, resume and interview preparation, comparing careers.
- Be practical and short (under 180 words). Prefer a few clear steps or bullets.
- Reply in the same language the student writes in (English, Hindi or Hinglish).
- Match scores and readiness are project-defined indicators, not predictions. Never promise jobs, salary or placements.
- If the needed data is missing (for example no skill assessment), tell the student which assessment to complete first.
- If the question is not about careers or learning, politely bring the student back to career guidance.

STUDENT DATA (private):
"""


def build_system_prompt(ctx):
    return SYSTEM_PROMPT + context_to_text(ctx)


def clean_history(history, max_turns=6):
    """Keep the last few turns, start with a user turn, end with an assistant turn, alternate roles."""
    out = []
    for m in history[-max_turns * 2:]:
        role = m.get("role")
        content = (m.get("content") or "").strip()[:1000]
        if role not in ("user", "assistant") or not content:
            continue
        if out and out[-1]["role"] == role:
            out[-1] = {"role": role, "content": content}
        else:
            out.append({"role": role, "content": content})
    while out and out[0]["role"] != "user":
        out.pop(0)
    while out and out[-1]["role"] != "assistant":
        out.pop()
    return out


# ------------------------------------------------------------------ RULE-BASED
DISCLAIMER = "(Scores are project-defined indicators, not guarantees.)"
ALL_SUGGESTIONS = ["What should I learn next?", "Show my skill gaps", "Which projects should I build?",
                   "How is my progress?", "Which careers suit me?", "How can I improve my resume?"]
SUGGESTION_INTENT = {"What should I learn next?": "learn_next", "Show my skill gaps": "skill_gap",
                     "Which projects should I build?": "projects", "How is my progress?": "progress",
                     "Which careers suit me?": "career_suggestion", "How can I improve my resume?": "resume"}

NEED_SKILLS = ("I do not have your skill levels yet. Please complete the skill assessment first, "
               "then I can personalise my advice.")


def _first_name(ctx):
    return (ctx["user"].get("name") or "").split(" ")[0] or "there"


def _need_target(ctx):
    recs = ctx["recommendations"]
    hint = ""
    if recs:
        hint = " Your top matches are " + ", ".join(r["career_name"] for r in recs) + "."
    return ("Which career are you aiming for? Set a career goal in your profile, or ask me like "
            "\"What should I learn for Data Analyst?\"." + hint)


def _gap_lines(t, n=3):
    return "\n".join(f"{i}. {g['skill']}: {g['your_level']}/10, target {g['target_level']}/10 ({g['priority']} priority)"
                     for i, g in enumerate(t["gaps"][:n], start=1))


def rule_based_reply(message, ctx):
    intent = detect_intent(message)
    name, t = _first_name(ctx), (ctx["targets"][0] if ctx["targets"] else None)

    if intent == "greeting":
        text = (f"Hi {name}! I am your career assistant. I use your own skills, interests and progress to answer. "
                "You can ask what to learn next, your skill gaps, which projects to build, resume tips or how your "
                "progress is going.")

    elif intent == "guarantee":
        text = ("I cannot predict jobs, salary or placements. Match scores and readiness here are indicators based on "
                "your skills and interests. What I can do is show you what to learn and build to become a stronger "
                "candidate.")

    elif intent == "compare":
        if len(ctx["targets"]) < 2:
            text = "Tell me the two careers you want to compare, for example \"Compare Data Analyst and Web Developer\"."
        else:
            a, b = ctx["targets"][0], ctx["targets"][1]
            text = "\n".join([
                f"{a['career_name']}: {a['readiness_percent']}% ready, {a['to_learn']} to learn, {a['to_improve']} to improve, about {a['estimated_weeks']} weeks. {a['next_step']}.",
                f"{b['career_name']}: {b['readiness_percent']}% ready, {b['to_learn']} to learn, {b['to_improve']} to improve, about {b['estimated_weeks']} weeks. {b['next_step']}.",
                "This is informational: neither career is better in general, it only shows how your current skills line up."])

    elif intent in ("learn_next", "skill_gap", "projects", "interview", "resume", "progress") and not ctx["skills"] \
            and intent != "progress":
        text = NEED_SKILLS

    elif intent == "learn_next":
        if not t:
            text = _need_target(ctx)
        else:
            parts = [f"{name}, for {t['career_name']} you are about {t['readiness_percent']}% ready "
                     f"({t['available']} skills at target, {t['to_improve']} to improve, {t['to_learn']} to learn)."]
            parts.append(f"Next step: {t['next_step']}.")
            if t["gaps"]:
                parts.append("Focus on:\n" + _gap_lines(t))
            if t["estimated_weeks"]:
                parts.append(f"Rough time: about {t['estimated_weeks']} weeks ({t['estimated_months']} months) of regular study.")
            p = ctx["progress"]
            if p and p.get("next_up") and p["career_name"] == t["career_name"]:
                parts.append(f"On your roadmap, next up is {p['next_up']['title']}.")
            parts.append(DISCLAIMER)
            text = "\n".join(parts)

    elif intent == "skill_gap":
        if not t:
            text = _need_target(ctx)
        elif not t["gaps"]:
            text = f"Good news: you meet the target level for every listed skill for {t['career_name']}."
        else:
            text = (f"Skill gaps for {t['career_name']}:\n" + _gap_lines(t, 5))
            if t["strengths"]:
                text += "\nYour strengths: " + ", ".join(f"{s['skill']} ({s['your_level']}/10)" for s in t["strengths"]) + "."

    elif intent == "career_suggestion":
        if ctx["recommendations"]:
            text = ("Your top career matches based on your assessments:\n" + "\n".join(
                f"{i}. {r['career_name']} ({r['match_percent']}%)" for i, r in enumerate(ctx["recommendations"], start=1))
                + "\n" + DISCLAIMER)
        elif ctx["skills"] and ctx["interests"]:
            text = "Your assessments are done. Generate your recommendations to see your top career matches."
        else:
            text = "Complete both the skill and interest assessments, then generate recommendations to see career matches."

    elif intent == "my_skills":
        if not ctx["skills"]:
            text = NEED_SKILLS
        else:
            ranked = sorted(ctx["skills"].items(), key=lambda x: -x[1])
            top = ", ".join(f"{k} ({v}/10)" for k, v in ranked[:4])
            low = ", ".join(f"{k} ({v}/10)" for k, v in ranked[-2:])
            text = f"Your strongest skills: {top}. Lowest right now: {low}."

    elif intent == "projects":
        if not t:
            text = _need_target(ctx)
        elif not t["projects"]:
            text = f"I could not find projects for {t['career_name']} yet."
        else:
            lines = [f"{i}. {p['title']} - {p['difficulty']}, about {p['estimated_time']}, you have {p['ready_percent']}% of the skills"
                     for i, p in enumerate(t["projects"], start=1)]
            text = f"Projects for {t['career_name']} (best match first):\n" + "\n".join(lines) + f"\nStart with: {t['projects'][0]['title']}."

    elif intent == "interview":
        if not t:
            text = _need_target(ctx)
        else:
            text = f"Interview topics for {t['career_name']}: " + ", ".join(t["interview_topics"]) + "."
            if t["gaps"]:
                text += f" Practise {t['gaps'][0]['skill']} extra, because it is your biggest gap right now."

    elif intent == "resume":
        if not t:
            text = _need_target(ctx)
        else:
            text = (f"For a {t['career_name']} resume: use the Resume Analyzer to upload your resume and see missing keywords. ")
            if t["gaps"]:
                text += ("Skills you are still building: " + ", ".join(g["skill"] for g in t["gaps"][:3]) +
                         ". Add them only when you have really used them. ")
            text += "Show skills inside projects and experience, not only in the skills list."

    elif intent == "progress":
        p = ctx["progress"]
        if not p:
            text = _need_target(ctx)
        else:
            text = (f"{p['career_name']}: {p['overall_percent']}% complete "
                    f"({p['completed_months']}/{p['total_months']} roadmap months, "
                    f"{p['completed_projects']}/{p['total_projects']} projects).")
            text += (f" Next up: {p['next_up']['title']}." if p.get("next_up") else " You have completed everything.")

    else:
        text = ("I can help with: what to learn next, your skill gaps, project ideas, interview topics, "
                "resume tips, career matches and your progress. Try one of the suggestions below.")

    return text, intent


def suggestions_for(intent, ctx):
    out = [s for s in ALL_SUGGESTIONS if SUGGESTION_INTENT[s] != intent]
    if not ctx["progress"]:
        out = [s for s in out if SUGGESTION_INTENT[s] != "progress"] or out
    return out[:3]