"""
Step 7: Skill gap analysis and career comparison (pure Python, no database).

For every skill a career needs:
  required level  = from the skill's importance (5 -> 8/10, 4 -> 7, 3 -> 6, 2 -> 5, 1 -> 4)
  status          = Available (level >= required) | Improve (level 4 or more) | Learn (level below 4)
  priority        = High (importance 4-5) | Medium (importance 3) | Low (importance 1-2)

These are project-defined indicators for learning guidance, not real hiring requirements.
"""

REQUIRED_LEVEL = {5: 8, 4: 7, 3: 6, 2: 5, 1: 4}
ALIASES = {"ML": "Machine Learning", "APIs": "Backend/APIs"}
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2, "-": 3}
DIFFICULTY_ORDER = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def _priority(importance):
    if importance >= 4:
        return "High"
    if importance == 3:
        return "Medium"
    return "Low"


def analyze(career_name, weights, skill_levels, categories=None):
    """
    weights      : {"SQL": 5, "Excel": 5, ...}   (importance 1-5)
    skill_levels : {"SQL": 9, ...}               (0-10, missing = 0)
    """
    categories = categories or {}
    rows, earned, possible = [], 0, 0
    for skill, imp in weights.items():
        required = REQUIRED_LEVEL.get(imp, 6)
        level = skill_levels.get(skill, 0)
        gap = max(required - level, 0)
        if gap == 0:
            status, priority = "Available", "-"
        elif level >= 4:
            status, priority = "Improve", _priority(imp)
        else:
            status, priority = "Learn", _priority(imp)
        earned += imp * min(level, required)
        possible += imp * required
        rows.append({
            "skill": skill, "category": categories.get(skill),
            "importance": imp, "required_level": required, "your_level": level,
            "gap": gap, "status": status, "priority": priority,
        })

    rows.sort(key=lambda r: (PRIORITY_ORDER[r["priority"]], -r["gap"], -r["importance"]))
    todo = [r for r in rows if r["status"] != "Available"]
    weeks = sum(r["gap"] for r in todo)          # rough: about 1 week per missing skill level

    return {
        "career_name": career_name,
        "readiness_percent": round(earned / possible * 100, 1) if possible else 0.0,
        "available": sum(1 for r in rows if r["status"] == "Available"),
        "to_improve": sum(1 for r in rows if r["status"] == "Improve"),
        "to_learn": sum(1 for r in rows if r["status"] == "Learn"),
        "estimated_weeks": weeks,
        "estimated_months": round(weeks / 4.3, 1),
        "next_step": (f"Work on {todo[0]['skill']} next" if todo else "You meet all listed skill levels"),
        "skills": rows,
        "note": "Learning time is a rough estimate (about 1 week per missing skill level). "
                "Levels and requirements are project-defined indicators.",
    }


def rank_projects(projects, skill_levels, all_skill_names):
    """
    projects: list of dicts with title, difficulty, required_skills, dataset, expected_output, estimated_time
    Sorted: most-ready first, then easier first.
    """
    out = []
    for p in projects:
        tokens = [ALIASES.get(t.strip(), t.strip())
                  for t in (p["required_skills"] or "").split(",") if t.strip()]
        real = [t for t in tokens if t in all_skill_names]
        ready = [t for t in real if skill_levels.get(t, 0) >= 4]
        pct = round(len(ready) / len(real) * 100) if real else 0
        out.append({**p, "ready_percent": pct,
                    "missing_skills": [t for t in real if t not in ready]})
    out.sort(key=lambda p: (-p["ready_percent"], DIFFICULTY_ORDER.get(p["difficulty"], 9)))
    return out


def compare(analyses):
    """analyses: list of analyze() results -> side-by-side view."""
    names = [a["career_name"] for a in analyses]
    table = {}
    for a in analyses:
        for s in a["skills"]:
            row = table.setdefault(s["skill"], {
                "skill": s["skill"], "category": s["category"],
                "your_level": s["your_level"], "required_level": {}, "importance": {}})
            row["required_level"][a["career_name"]] = s["required_level"]
            row["importance"][a["career_name"]] = s["importance"]
    rows = list(table.values())
    for r in rows:
        for n in names:                       # careers that do not need this skill
            r["required_level"].setdefault(n, None)
            r["importance"].setdefault(n, None)
    rows.sort(key=lambda r: -max(v for v in r["importance"].values() if v))

    return {
        "summary": [{
            "career_name": a["career_name"], "readiness_percent": a["readiness_percent"],
            "available": a["available"], "to_improve": a["to_improve"], "to_learn": a["to_learn"],
            "estimated_weeks": a["estimated_weeks"], "estimated_months": a["estimated_months"],
            "next_step": a["next_step"],
        } for a in analyses],
        "skills": rows,
        "note": "This comparison is informational. It does not say any career is better than another; "
                "it only shows how your current skills line up with each role.",
    }