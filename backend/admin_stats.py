"""
Step 13: Admin dashboard statistics (pure Python, no database).
The routes fetch simple rows from the database; these functions turn them into dashboard numbers.
Only students are counted (admins are left out of every statistic).
"""
from collections import Counter, defaultdict
from datetime import timedelta


def _pct(a, b):
    return round(a / b * 100, 1) if b else 0.0


def build_overview(student_created, skill_ids, interest_ids, rec_user_ids, progress_rows, today):
    """
    student_created : {user_id: date joined}   (students only)
    skill_ids / interest_ids / rec_user_ids : sets of user ids
    progress_rows   : [(user_id, completed_bool)]
    """
    students = set(student_created)
    skill, interest = skill_ids & students, interest_ids & students
    both = skill & interest
    week_start = today - timedelta(days=6)
    done = [(u, c) for u, c in progress_rows if u in students and c]
    return {
        "total_students": len(students),
        "new_students_last_7_days": sum(1 for d in student_created.values() if d and d >= week_start),
        "skill_assessments_taken": len(skill),
        "interest_assessments_taken": len(interest),
        "both_assessments_taken": len(both),
        "assessment_completion_percent": _pct(len(both), len(students)),
        "students_with_recommendations": len(rec_user_ids & students),
        "students_with_progress": len({u for u, _ in done}),
        "completed_roadmap_and_project_items": len(done),
    }


def popular_careers(rec_rows, students, limit=5):
    """rec_rows: [(user_id, career_name, match_score)] - the saved recommendations."""
    rows = [r for r in rec_rows if r[0] in students]
    best = {}
    for uid, career, score in rows:
        if uid not in best or (score or 0) > best[uid][1]:
            best[uid] = (career, score or 0)
    top_counts = Counter(c for c, _ in best.values())
    times = Counter(r[1] for r in rows)
    scores = defaultdict(list)
    for _, career, score in rows:
        scores[career].append(score or 0)
    out = [{
        "career_name": c,
        "students_with_this_as_top_match": top_counts.get(c, 0),
        "times_recommended": times[c],
        "average_match_percent": round(sum(scores[c]) / len(scores[c]), 1),
    } for c in times]
    out.sort(key=lambda x: (-x["students_with_this_as_top_match"], -x["times_recommended"], x["career_name"]))
    return out[:limit]


def popular_goals(goals, limit=5):
    cleaned = [g.strip().lower() for g in goals if g and g.strip()]
    return [{"career_goal": g.title(), "students": n} for g, n in Counter(cleaned).most_common(limit)]


def popular_skills(user_skill_rows, students, strong_level=6, limit=5):
    """user_skill_rows: [(user_id, skill_name, category, level)]"""
    levels = defaultdict(list)
    for uid, skill, _cat, level in user_skill_rows:
        if uid in students:
            levels[skill].append(level)
    rows = [{
        "skill": s, "students_rated": len(v),
        "students_strong": sum(1 for x in v if x >= strong_level),
        "average_level": round(sum(v) / len(v), 1),
    } for s, v in levels.items()]
    return {
        "strong_level_used": strong_level,
        "most_known": sorted(rows, key=lambda r: (-r["students_strong"], -r["average_level"], r["skill"]))[:limit],
        "needs_attention": sorted(rows, key=lambda r: (r["average_level"], r["skill"]))[:limit],
    }


def skill_category_results(user_skill_rows, students):
    cats = defaultdict(list)
    for uid, _skill, category, level in user_skill_rows:
        if uid in students:
            cats[category or "Other"].append(level)
    out = [{"category": c, "average_level": round(sum(v) / len(v), 1), "ratings": len(v)} for c, v in cats.items()]
    return sorted(out, key=lambda r: -r["average_level"])


def interest_results(interest_rows, area_of, students):
    """interest_rows: [(user_id, question_id, answer)]; area_of: {question_id: area}"""
    totals, counts, who = defaultdict(float), defaultdict(int), defaultdict(set)
    for uid, qid, answer in interest_rows:
        area = area_of.get(qid)
        if uid not in students or area is None:
            continue
        try:
            value = float(answer)
        except (TypeError, ValueError):
            continue
        totals[area] += value / 5 * 100
        counts[area] += 1
        who[area].add(uid)
    out = [{"area": a, "average_percent": round(totals[a] / counts[a]), "students": len(who[a])} for a in totals]
    return sorted(out, key=lambda r: -r["average_percent"])


def usage_series(joined_dates, recommendation_dates, progress_dates, days, today):
    """One row per day for the last `days` days (oldest first), zero-filled."""
    def count(dates):
        c = Counter(d for d in dates if d)
        return c
    j, r, p = count(joined_dates), count(recommendation_dates), count(progress_dates)
    out = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        out.append({"date": d.isoformat(), "registrations": j[d],
                    "recommendations_generated": r[d], "progress_updates": p[d]})
    return out