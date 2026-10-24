"""
Step 11: Progress tracker logic (pure Python, no database).
A student ticks roadmap months and projects as done; this module turns that into percentages.
"""
import difflib


def pct(done, total):
    return round(done / total * 100, 1) if total else 0.0


def summarize(career_id, career_name, months, projects, done_roadmap_ids, done_project_ids):
    """
    months   : [{"roadmap_id", "month_no", "title"}]
    projects : [{"project_id", "title", "difficulty"}]
    done_*   : sets of ids the student has completed
    """
    months = sorted(months, key=lambda m: m["month_no"])
    m_out = [{**m, "completed": m["roadmap_id"] in done_roadmap_ids} for m in months]
    p_out = [{**p, "completed": p["project_id"] in done_project_ids} for p in projects]

    done_m = sum(1 for m in m_out if m["completed"])
    done_p = sum(1 for p in p_out if p["completed"])

    next_up = None
    first_m = next((m for m in m_out if not m["completed"]), None)
    first_p = next((p for p in p_out if not p["completed"]), None)
    if first_m:
        next_up = {"type": "roadmap", "id": first_m["roadmap_id"],
                   "title": f"Month {first_m['month_no']}: {first_m['title']}"}
    elif first_p:
        next_up = {"type": "project", "id": first_p["project_id"], "title": first_p["title"]}

    return {
        "career_id": career_id,
        "career_name": career_name,
        "roadmap": m_out,
        "projects": p_out,
        "completed_months": done_m, "total_months": len(m_out),
        "completed_projects": done_p, "total_projects": len(p_out),
        "roadmap_percent": pct(done_m, len(m_out)),
        "project_percent": pct(done_p, len(p_out)),
        "overall_percent": pct(done_m + done_p, len(m_out) + len(p_out)),
        "next_up": next_up,
        "message": "You have completed everything for this career." if next_up is None and (m_out or p_out) else None,
    }


def match_career_name(goal, names):
    """Match the free-text career goal in the profile to a real career name (or None)."""
    if not goal or not goal.strip():
        return None
    g = goal.strip().lower()
    lower = {n.lower(): n for n in names}
    if g in lower:
        return lower[g]
    for low, original in lower.items():
        if g in low or low in g:
            return original
    close = difflib.get_close_matches(g, list(lower), n=1, cutoff=0.75)
    return lower[close[0]] if close else None