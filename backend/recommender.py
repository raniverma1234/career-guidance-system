"""
Step 6: Career recommendation engine (rule-based + ML hybrid).

Final match score for each career =
    50%  skill match      (student's skill levels vs. career skill importance from the database)
  + 20%  interest match   (student's interest scores vs. typical interest profile of that career)
  + 30%  ML probability   (Random Forest trained on data/training_data.csv)

Run `python recommender.py` to train the model and print its evaluation.
NOTE: the training data is an educational dataset, not real hiring data. Match scores
are indicators of fit, not predictions or guarantees.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "training_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "data", "career_model.joblib")

# weights of the three parts (must add up to 1.0) - you can tune these
W_SKILL, W_INTEREST, W_ML = 0.5, 0.2, 0.3

INTEREST_COL = {
    "Data": "interest_data",
    "Programming": "interest_programming",
    "AI/ML": "interest_ai_ml",
    "Management": "interest_management",
    "Design": "interest_design",
}
COL_TO_AREA = {v: k for k, v in INTEREST_COL.items()}

_bundle = None


# ------------------------------------------------------------------ MODEL
def train_model(verbose=False):
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns="career")
    y = df["career"]

    if verbose:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)
        check = RandomForestClassifier(n_estimators=200, random_state=42).fit(X_tr, y_tr)
        print(f"Rows: {len(df)} | Features: {X.shape[1]} | Careers: {y.nunique()}")
        print(f"Test accuracy: {check.score(X_te, y_te):.3f}")
        cv = cross_val_score(
            RandomForestClassifier(n_estimators=200, random_state=42), X, y, cv=5)
        print(f"5-fold cross-validation accuracy: {cv.mean():.3f}")
        print(classification_report(y_te, check.predict(X_te)))
        print("(Data is synthetic, so accuracy is very high. Do not present it as real-world accuracy.)")

    model = RandomForestClassifier(n_estimators=200, random_state=42).fit(X, y)
    interest_cols = [c for c in X.columns if c.startswith("interest_")]
    profile = df.groupby("career")[interest_cols].mean().to_dict(orient="index")

    bundle = {"model": model, "features": list(X.columns), "interest_profile": profile}
    joblib.dump(bundle, MODEL_PATH)
    return bundle


def get_bundle():
    """Load the saved model, or train it if missing / older than the CSV."""
    global _bundle
    if _bundle is None:
        stale = (not os.path.exists(MODEL_PATH)
                 or os.path.getmtime(MODEL_PATH) < os.path.getmtime(DATA_PATH))
        if not stale:
            try:
                _bundle = joblib.load(MODEL_PATH)
            except Exception:
                stale = True
        if stale:
            _bundle = train_model()
    return _bundle


# ---------------------------------------------------------- RECOMMENDATION
def _explain(career, weights, skill_levels, interests, profile):
    strengths = sorted(
        [(s, imp) for s, imp in weights.items() if imp >= 3 and skill_levels.get(s, 0) >= 7],
        key=lambda x: -(x[1] * skill_levels.get(x[0], 0)))[:3]
    gaps = sorted(
        [(s, imp) for s, imp in weights.items() if imp >= 3 and skill_levels.get(s, 0) < 6],
        key=lambda x: -(x[1] * (10 - skill_levels.get(x[0], 0))))[:3]

    parts = []
    if strengths:
        parts.append("Your strengths for this role: " + ", ".join(
            f"{s} ({skill_levels.get(s, 0)}/10)" for s, _ in strengths) + ".")
    else:
        parts.append("You do not yet have a strong skill in this role's key areas.")
    if gaps:
        parts.append("Skills to improve: " + ", ".join(
            f"{s} ({skill_levels.get(s, 0)}/10, importance {imp}/5)" for s, imp in gaps) + ".")
    if profile:
        top_col = max(profile, key=profile.get)
        area = COL_TO_AREA.get(top_col, top_col)
        parts.append(f"This role is closest to an interest in {area}; "
                     f"your {area} interest score is {interests.get(top_col, 0)}/10.")
    parts.append("This is an indicator of fit based on your profile, not a guarantee.")

    return {
        "strengths": [{"skill": s, "level": skill_levels.get(s, 0)} for s, _ in strengths],
        "gaps": [{"skill": s, "level": skill_levels.get(s, 0), "importance": imp} for s, imp in gaps],
        "explanation": " ".join(parts),
    }


def recommend(skill_levels, interests, career_weights, top_n=5):
    """
    skill_levels   : {"Python": 8, ...}                         (0-10)
    interests      : {"interest_data": 9.3, ...}                (0-10)
    career_weights : {"Data Analyst": {"SQL": 5, ...}, ...}     (importance 1-5, from the database)
    returns a list of dicts, best match first.
    """
    b = get_bundle()
    row = {f: 0 for f in b["features"]}
    for k, v in {**skill_levels, **interests}.items():
        if k in row:
            row[k] = v
    X = pd.DataFrame([row], columns=b["features"])
    proba = dict(zip(b["model"].classes_, b["model"].predict_proba(X)[0]))

    results = []
    for career, weights in career_weights.items():
        total_w = sum(weights.values())
        skill_match = sum(imp * skill_levels.get(s, 0) for s, imp in weights.items()) / (total_w * 10) * 100

        profile = b["interest_profile"].get(career)
        if profile:
            diff = np.mean([abs(interests.get(c, 0) - profile[c]) for c in profile])
            interest_match = (1 - diff / 10) * 100
        else:
            interest_match = 50.0

        ml_prob = proba.get(career, 0.0) * 100
        final = W_SKILL * skill_match + W_INTEREST * interest_match + W_ML * ml_prob

        info = _explain(career, weights, skill_levels, interests, profile)
        results.append({
            "career_name": career,
            "match_percent": round(final, 1),
            "skill_match": round(skill_match, 1),
            "interest_match": round(interest_match, 1),
            "ml_probability": round(ml_prob, 1),
            **info,
        })

    results.sort(key=lambda r: r["match_percent"], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    train_model(verbose=True)
    print("Model saved to", MODEL_PATH)