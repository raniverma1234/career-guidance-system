"""
Step 5: Question bank + scoring for the skill and interest assessments.
Pure Python (no database) so it is easy to test and change.
"""

LEVEL_OPTIONS = ["None", "Beginner", "Intermediate", "Advanced"]
LEVEL_SCORE = {"None": 0, "Beginner": 3, "Intermediate": 6, "Advanced": 9}
YESNO_OPTIONS = ["Yes", "No"]
YESNO_SCORE = {"Yes": 8, "No": 1}
RATING_OPTIONS = ["1", "2", "3", "4", "5"]   # 1 = not comfortable, 5 = very comfortable

# ------------------------------------------------------------ SKILL QUESTIONS
# type: level (None/Beginner/Intermediate/Advanced) | yesno | rating (1-5)
# The "skill" value must match a skill_name in the skills table.
SKILL_QUESTIONS = [
    {"id": "S01", "skill": "Python", "type": "level", "text": "How would you rate your Python programming?"},
    {"id": "S02", "skill": "Python", "type": "yesno", "text": "Can you write a Python function that uses loops and conditions without looking up the syntax?"},
    {"id": "S03", "skill": "SQL", "type": "level", "text": "How would you rate your SQL knowledge?"},
    {"id": "S04", "skill": "SQL", "type": "yesno", "text": "Can you write a SQL JOIN query that combines two tables?"},
    {"id": "S05", "skill": "Excel", "type": "rating", "text": "How comfortable are you with Excel (formulas, charts, data cleaning)?"},
    {"id": "S06", "skill": "Excel", "type": "yesno", "text": "Have you built pivot tables in Excel?"},
    {"id": "S07", "skill": "Statistics", "type": "rating", "text": "How comfortable are you with statistics (probability, distributions, hypothesis testing)?"},
    {"id": "S08", "skill": "Statistics", "type": "yesno", "text": "Can you explain mean, median and standard deviation, and when to use each?"},
    {"id": "S09", "skill": "Data Visualization", "type": "rating", "text": "How comfortable are you creating charts and visual reports from data?"},
    {"id": "S10", "skill": "Power BI", "type": "level", "text": "How would you rate your Power BI (or Tableau) skills?"},
    {"id": "S11", "skill": "Machine Learning", "type": "level", "text": "How would you rate your machine learning knowledge?"},
    {"id": "S12", "skill": "Machine Learning", "type": "yesno", "text": "Have you trained a model using Scikit-learn (or a similar library)?"},
    {"id": "S13", "skill": "Deep Learning", "type": "level", "text": "How would you rate your deep learning knowledge (neural networks, TensorFlow, PyTorch)?"},
    {"id": "S14", "skill": "DSA", "type": "rating", "text": "How comfortable are you with data structures and algorithms (arrays, trees, sorting, searching)?"},
    {"id": "S15", "skill": "JavaScript", "type": "level", "text": "How would you rate your JavaScript skills?"},
    {"id": "S16", "skill": "HTML/CSS", "type": "rating", "text": "How comfortable are you building web pages with HTML and CSS?"},
    {"id": "S17", "skill": "React", "type": "level", "text": "How would you rate your React skills?"},
    {"id": "S18", "skill": "Backend/APIs", "type": "rating", "text": "How comfortable are you building backend services and REST APIs?"},
    {"id": "S19", "skill": "Git/GitHub", "type": "yesno", "text": "Can you use Git to commit, create branches and push code to GitHub?"},
    {"id": "S20", "skill": "Linux", "type": "rating", "text": "How comfortable are you using the Linux command line?"},
    {"id": "S21", "skill": "Networking", "type": "rating", "text": "How comfortable are you with computer networking (TCP/IP, DNS, HTTP)?"},
    {"id": "S22", "skill": "Cloud Computing", "type": "level", "text": "How would you rate your cloud computing knowledge (AWS, Azure or GCP)?"},
    {"id": "S23", "skill": "Docker", "type": "level", "text": "How would you rate your Docker and container knowledge?"},
    {"id": "S24", "skill": "CI/CD", "type": "level", "text": "How would you rate your CI/CD pipeline knowledge?"},
    {"id": "S25", "skill": "Cyber Security", "type": "level", "text": "How would you rate your cyber security knowledge?"},
    {"id": "S26", "skill": "UI/UX Design", "type": "level", "text": "How would you rate your UI/UX design skills (Figma, wireframes, prototypes)?"},
    {"id": "S27", "skill": "Communication", "type": "rating", "text": "How confident are you explaining ideas in writing and in presentations?"},
    {"id": "S28", "skill": "Business Analysis", "type": "rating", "text": "How comfortable are you gathering requirements and analysing business problems?"},
]

# --------------------------------------------------------- INTEREST QUESTIONS
# Answer on a 1-5 scale: 1 = strongly disagree ... 5 = strongly agree
INTEREST_AREAS = ["Data", "Programming", "AI/ML", "Management", "Design"]

INTEREST_QUESTIONS = [
    {"id": "I01", "area": "Data", "text": "I enjoy working with numbers and data."},
    {"id": "I02", "area": "Data", "text": "I like finding patterns and insights in data."},
    {"id": "I03", "area": "Data", "text": "I enjoy making charts or reports from data."},
    {"id": "I04", "area": "Programming", "text": "I enjoy building websites or applications."},
    {"id": "I05", "area": "Programming", "text": "I like solving problems by writing code."},
    {"id": "I06", "area": "Programming", "text": "I enjoy learning new programming languages and tools."},
    {"id": "I07", "area": "AI/ML", "text": "I am interested in how AI and machine learning work."},
    {"id": "I08", "area": "AI/ML", "text": "I like the idea of teaching computers to make predictions."},
    {"id": "I09", "area": "AI/ML", "text": "I enjoy exploring new AI tools and technologies."},
    {"id": "I10", "area": "Management", "text": "I enjoy solving business and people problems."},
    {"id": "I11", "area": "Management", "text": "I like planning, organising and leading teams or projects."},
    {"id": "I12", "area": "Management", "text": "I enjoy communicating with clients or stakeholders."},
    {"id": "I13", "area": "Design", "text": "I enjoy designing how things look and feel."},
    {"id": "I14", "area": "Design", "text": "I like thinking about how users experience an app."},
    {"id": "I15", "area": "Design", "text": "I enjoy working with colours, layouts and creative ideas."},
]

SKILL_BY_ID = {q["id"]: q for q in SKILL_QUESTIONS}
INTEREST_BY_ID = {q["id"]: q for q in INTEREST_QUESTIONS}


def public_skill_questions():
    out = []
    for q in SKILL_QUESTIONS:
        options = {"level": LEVEL_OPTIONS, "yesno": YESNO_OPTIONS, "rating": RATING_OPTIONS}[q["type"]]
        out.append({"id": q["id"], "skill": q["skill"], "type": q["type"],
                    "text": q["text"], "options": options})
    return out


def public_interest_questions():
    return [{"id": q["id"], "area": q["area"], "text": q["text"], "options": RATING_OPTIONS}
            for q in INTEREST_QUESTIONS]


# ------------------------------------------------------------------- SCORING
def score_skill_answers(answers):
    """
    answers: {question_id: answer}
    returns (skill_levels, details)
      skill_levels: {skill_name: level 0-10}
      details: list of (question_id, question_text, answer, score)
    Raises ValueError for unknown questions or invalid answers.
    """
    per_skill, details = {}, []
    for qid, raw in answers.items():
        q = SKILL_BY_ID.get(qid)
        if q is None:
            raise ValueError(f"Unknown skill question: {qid}")
        ans = str(raw).strip()
        if q["type"] == "level":
            ans = ans.title()
            if ans not in LEVEL_SCORE:
                raise ValueError(f"{qid}: answer must be one of {LEVEL_OPTIONS}")
            score = LEVEL_SCORE[ans]
        elif q["type"] == "yesno":
            ans = ans.title()
            if ans not in YESNO_SCORE:
                raise ValueError(f"{qid}: answer must be Yes or No")
            score = YESNO_SCORE[ans]
        else:
            if ans not in RATING_OPTIONS:
                raise ValueError(f"{qid}: answer must be a number from 1 to 5")
            score = int(ans) * 2
        per_skill.setdefault(q["skill"], []).append(score)
        details.append((qid, q["text"], ans, score))

    levels = {s: int(sum(v) / len(v) + 0.5) for s, v in per_skill.items()}
    return levels, details


def score_interest_answers(answers):
    """
    answers: {question_id: 1-5}. All 15 questions are required.
    returns (results, details); results sorted high to low:
      [{"area": "Data", "percent": 87, "score_10": 8.7}, ...]
    """
    missing = [qid for qid in INTEREST_BY_ID if qid not in answers]
    if missing:
        raise ValueError(f"Please answer all interest questions. Missing: {missing}")

    totals, details = {a: 0 for a in INTEREST_AREAS}, []
    for qid, raw in answers.items():
        q = INTEREST_BY_ID.get(qid)
        if q is None:
            raise ValueError(f"Unknown interest question: {qid}")
        ans = str(raw).strip()
        if ans not in RATING_OPTIONS:
            raise ValueError(f"{qid}: answer must be a number from 1 to 5")
        totals[q["area"]] += int(ans)
        details.append((qid, q["text"], ans, float(ans)))

    results = []
    for area in INTEREST_AREAS:
        pct = round(totals[area] / 15 * 100)      # 3 questions x max 5 = 15
        results.append({"area": area, "percent": pct, "score_10": round(pct / 10, 1)})
    results.sort(key=lambda r: r["percent"], reverse=True)
    return results, details