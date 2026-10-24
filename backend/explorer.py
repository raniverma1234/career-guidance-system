"""
Step 10: Job Role Explorer (pure Python, no database).
Turns the stored career data into one easy-to-read profile for each role:
what they do, required skills, tools, typical projects, interview topics and a learning roadmap.
"""

# same target levels as the skill gap analysis (Step 7)
TARGET_LEVEL = {5: 8, 4: 7, 3: 6, 2: 5, 1: 4}


def importance_label(imp):
    if imp >= 5:
        return "Essential"
    if imp == 4:
        return "Important"
    if imp == 3:
        return "Useful"
    return "Nice to have"


def split_list(text):
    return [t.strip() for t in (text or "").split(",") if t.strip()]


def build_role_summary(career, skills, project_count):
    """career: dict, skills: [{"skill","importance"}]  -> one short card for the role list."""
    top = sorted(skills, key=lambda s: (-s["importance"], s["skill"]))[:3]
    return {
        "career_id": career["career_id"],
        "career_name": career["career_name"],
        "what_they_do": career["description"],
        "top_skills": [s["skill"] for s in top],
        "skill_count": len(skills),
        "project_count": project_count,
    }


def build_role_detail(career, skills, projects, months):
    """
    career   : {"career_id", "career_name", "description", "tools", "interview_topics"}
    skills   : [{"skill", "category", "importance"}]
    projects : [{"title", "difficulty", "required_skills", "dataset", "expected_output", "estimated_time"}]
    months   : [{"month_no", "title", "topics"}]
    """
    skills = sorted(skills, key=lambda s: (-s["importance"], s["skill"]))
    return {
        "career_id": career["career_id"],
        "career_name": career["career_name"],
        "what_they_do": career["description"],
        "required_skills": [{
            "skill": s["skill"], "category": s["category"], "importance": s["importance"],
            "importance_label": importance_label(s["importance"]),
            "target_level": TARGET_LEVEL.get(s["importance"], 6),
        } for s in skills],
        "tools": split_list(career["tools"]),
        "typical_projects": projects,
        "interview_topics": split_list(career["interview_topics"]),
        "learning_roadmap": sorted(months, key=lambda m: m["month_no"]),
        "note": "Skills, tools and levels come from this project's educational career data. "
                "They are for learning guidance, not official job requirements.",
    }