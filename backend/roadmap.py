"""
Step 8: Personalised month-wise roadmap (pure Python, no database).

The roadmap template (6 months per career) is stored in the database. For each month we find
which of the career's required skills that month teaches (by keywords in its title/topics),
then compare them with the student's skill levels:

  Focus         - at least one skill of that month is below the target level
  Light review  - the student already meets the target for every skill of that month
  Milestone     - no specific skill (projects, portfolio, interview preparation)

Skills that the career needs but no month mentions are listed separately as "other_gaps".
"""
import re
import skill_gap

# regular-expression keywords (lower case). \b means "whole word".
SKILL_KEYWORDS = {
    "Python": [r"python"],
    "SQL": [r"\bsql\b"],
    "Excel": [r"excel"],
    "Statistics": [r"statistics", r"hypothesis"],
    "Data Visualization": [r"visualization", r"dashboard"],
    "Power BI": [r"power bi", r"tableau"],
    "Machine Learning": [r"machine learning", r"\bml\b", r"scikit", r"supervised"],
    "Deep Learning": [r"deep learning", r"neural", r"tensorflow", r"pytorch"],
    "DSA": [r"\bdsa\b", r"data structures", r"algorithms"],
    "JavaScript": [r"javascript", r"\bes6\b"],
    "HTML/CSS": [r"\bhtml\b", r"\bcss\b"],
    "React": [r"\breact\b"],
    "Backend/APIs": [r"\brest\b", r"\bapis\b", r"fastapi", r"spring boot", r"backend"],
    "Git/GitHub": [r"\bgit\b", r"github", r"version control"],
    "Linux": [r"\blinux\b", r"\bbash\b"],
    "Networking": [r"networking", r"tcp/ip", r"\bdns\b"],
    "Cloud Computing": [r"\bcloud\b"],
    "Docker": [r"docker", r"container"],
    "CI/CD": [r"ci/cd", r"pipeline", r"jenkins", r"github actions"],
    "Cyber Security": [r"cyber", r"security", r"owasp", r"cryptography", r"vulnerab", r"burp"],
    "UI/UX Design": [r"figma", r"\bux\b", r"wireframe", r"prototype", r"design principles", r"typography", r"usability"],
    "Communication": [r"communicat"],
    "Business Analysis": [r"business", r"requirement", r"user stories", r"\bsdlc\b", r"process"],
}

# months whose text does not name the skill directly
OVERRIDES = {
    ("Software Developer", 1): ["Python"],
}

MILESTONE_WORDS = ("portfolio", "project", "case stud")


def focus_skills_for_month(career_name, month, weights):
    title = month["title"].lower()
    if any(w in title for w in MILESTONE_WORDS):      # projects / portfolio months teach no new skill
        return []
    text = f"{month['title']} {month['topics']}".lower()
    found = [s for s, patterns in SKILL_KEYWORDS.items()
             if s in weights and any(re.search(p, text) for p in patterns)]
    for s in OVERRIDES.get((career_name, month["month_no"]), []):
        if s in weights and s not in found:
            found.append(s)
    return found


def build_plan(career_name, months, weights, skill_levels):
    """
    months       : [{"month_no": 1, "title": "...", "topics": "..."}, ...]
    weights      : {"SQL": 5, ...}  skills this career needs
    skill_levels : {"SQL": 9, ...}  the student's levels
    """
    analysis = skill_gap.analyze(career_name, weights, skill_levels)
    by_skill = {r["skill"]: r for r in analysis["skills"]}

    covered, plan = set(), []
    for m in sorted(months, key=lambda x: x["month_no"]):
        focus = focus_skills_for_month(career_name, m, weights)
        covered.update(focus)
        items = [{
            "skill": s, "your_level": by_skill[s]["your_level"],
            "target_level": by_skill[s]["required_level"],
            "gap": by_skill[s]["gap"], "status": by_skill[s]["status"],
        } for s in focus]
        items.sort(key=lambda i: -i["gap"])
        todo = [i for i in items if i["gap"] > 0]
        weeks = sum(i["gap"] for i in todo)

        if not items:
            status = "Milestone"
            advice = f"Apply your skills in practice: {m['topics']}."
        elif not todo:
            status = "Light review"
            advice = ("You already meet the target level for " + ", ".join(i["skill"] for i in items)
                      + ". Revise briefly (about 1 week) and use the extra time on later months.")
        else:
            status = "Focus"
            advice = ("Spend this month on: " + ", ".join(
                f"{i['skill']} ({i['your_level']}/10 to {i['target_level']}/10)" for i in todo) + ".")
            if weeks > 4:
                advice += " At your current level this may take more than one month."

        plan.append({
            "month_no": m["month_no"], "title": m["title"], "topics": m["topics"],
            "status": status, "focus_skills": items,
            "estimated_weeks": weeks, "advice": advice,
        })

    other = [{"skill": r["skill"], "your_level": r["your_level"],
              "target_level": r["required_level"], "priority": r["priority"]}
             for r in analysis["skills"] if r["status"] != "Available" and r["skill"] not in covered]

    counts = {k: sum(1 for p in plan if p["status"] == k) for k in ("Focus", "Light review", "Milestone")}
    return {
        "career_name": career_name,
        "readiness_percent": analysis["readiness_percent"],
        "summary": (f"{counts['Focus']} focus month(s), {counts['Light review']} light-review month(s), "
                    f"{counts['Milestone']} milestone month(s)."),
        "months": plan,
        "other_gaps": other,
        "note": "The plan follows a standard 6-month template, adjusted to your skill levels. "
                "Time estimates are rough (about 1 week per missing skill level).",
    }