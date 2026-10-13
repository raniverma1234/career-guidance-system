"""
Step 3: Career dataset + ML training data.

Run from the backend folder (with venv on):
    python seed_data.py            -> fills the database, creates data/training_data.csv
    python seed_data.py --reset    -> clears old career data first, then fills again

NOTE: This is an EDUCATIONAL / recommendation dataset. It is NOT real hiring data.
"""
import os
import sys
import numpy as np
import pandas as pd

from database import SessionLocal
from models import Skill, Career, CareerSkill, Roadmap, Project

# ---------------------------------------------------------------- SKILLS
SKILLS = {
    "Python": "Programming", "SQL": "Data", "Excel": "Data",
    "Statistics": "Data", "Data Visualization": "Data", "Power BI": "Data",
    "Machine Learning": "AI/ML", "Deep Learning": "AI/ML",
    "DSA": "Programming", "JavaScript": "Web", "HTML/CSS": "Web",
    "React": "Web", "Backend/APIs": "Web", "Git/GitHub": "Tools",
    "Linux": "Systems", "Networking": "Systems", "Cloud Computing": "Systems",
    "Docker": "DevOps", "CI/CD": "DevOps", "Cyber Security": "Security",
    "UI/UX Design": "Design", "Communication": "Soft Skills",
    "Business Analysis": "Management",
}

INTERESTS = ["data", "programming", "ai_ml", "management", "design"]

# ---------------------------------------------------------------- CAREERS
# skills: importance 1-5 | interests: typical interest score 0-10
CAREERS = [
    {
        "name": "Data Analyst",
        "description": "Collects, cleans and analyses data to find insights and support business decisions through reports and dashboards.",
        "tools": "Excel, SQL, Power BI, Tableau, Python (Pandas)",
        "interview": "SQL joins, aggregations, Excel formulas, statistics basics, dashboard design, case studies",
        "skills": {"Excel": 5, "SQL": 5, "Data Visualization": 5, "Statistics": 4, "Python": 4, "Power BI": 4, "Communication": 3},
        "interests": [9, 5, 4, 4, 3],
        "roadmap": [
            "Excel Foundations|Advanced Excel, formulas, pivot tables, data cleaning",
            "SQL|SQL basics, joins, group by, subqueries, window functions",
            "Statistics|Descriptive stats, probability, hypothesis testing",
            "Python for Data|Python basics, Pandas, NumPy, Matplotlib",
            "Dashboards|Power BI or Tableau, data visualization principles",
            "Portfolio & Interview|2-3 projects, resume, GitHub, interview practice",
        ],
        "projects": [
            "Sales Dashboard|Beginner|Excel, Power BI|Superstore Sales dataset|Interactive sales dashboard with KPIs|2 weeks",
            "Employee Analytics|Intermediate|SQL, Python, Data Visualization|HR Analytics dataset|Attrition analysis report with charts|3 weeks",
            "Customer Churn Analysis|Intermediate|Python, Statistics, Pandas|Telco Churn dataset|Churn drivers report and charts|3 weeks",
        ],
    },
    {
        "name": "Data Scientist",
        "description": "Builds statistical and machine learning models to solve business problems and communicates the findings.",
        "tools": "Python, Scikit-learn, Pandas, Jupyter, SQL, Matplotlib",
        "interview": "Statistics, probability, ML algorithms, model evaluation, feature engineering, SQL, case studies",
        "skills": {"Python": 5, "Statistics": 5, "Machine Learning": 5, "SQL": 4, "Data Visualization": 4, "Deep Learning": 3, "Git/GitHub": 3},
        "interests": [9, 7, 8, 3, 2],
        "roadmap": [
            "Python & Math|Python, NumPy, Pandas, linear algebra and probability basics",
            "Statistics|Hypothesis testing, distributions, regression",
            "Machine Learning|Regression, classification, clustering, model evaluation",
            "Advanced ML|Feature engineering, tuning, ensembles, intro to deep learning",
            "Real Projects|End-to-end projects, Kaggle practice, storytelling with data",
            "Portfolio & Interview|GitHub, resume, ML interview questions",
        ],
        "projects": [
            "House Price Prediction|Beginner|Python, Machine Learning|Housing prices dataset|Regression model with evaluation report|2 weeks",
            "Customer Segmentation|Intermediate|Python, Machine Learning, Statistics|Mall Customers dataset|Clusters with business interpretation|3 weeks",
            "Loan Default Prediction|Advanced|Python, ML, SQL|Loan dataset|Classification model with feature analysis|4 weeks",
        ],
    },
    {
        "name": "ML Engineer",
        "description": "Designs, trains and deploys machine learning models into real applications and keeps them running.",
        "tools": "Python, Scikit-learn, TensorFlow/PyTorch, Docker, FastAPI, Cloud",
        "interview": "ML algorithms, DSA, model deployment, APIs, system design basics, Python coding",
        "skills": {"Python": 5, "Machine Learning": 5, "Deep Learning": 4, "Git/GitHub": 4, "DSA": 3, "Docker": 3, "Cloud Computing": 3, "Backend/APIs": 3},
        "interests": [6, 8, 10, 2, 1],
        "roadmap": [
            "Python & DSA|Advanced Python, data structures, algorithms",
            "ML Fundamentals|Scikit-learn, supervised and unsupervised learning",
            "Deep Learning|Neural networks, CNN, RNN, TensorFlow or PyTorch",
            "Deployment|FastAPI, Docker, saving and serving models",
            "MLOps & Cloud|Model monitoring, cloud deployment, CI/CD basics",
            "Portfolio & Interview|Deployed projects, resume, interview practice",
        ],
        "projects": [
            "Image Classifier App|Intermediate|Python, Deep Learning|CIFAR-10 dataset|Web app that classifies uploaded images|3 weeks",
            "Spam Detection API|Intermediate|Python, ML, Backend/APIs|SMS Spam dataset|FastAPI service that returns spam or not|2 weeks",
            "Deployed Recommendation Engine|Advanced|Python, ML, Docker, Cloud|MovieLens dataset|Dockerized recommender hosted online|4 weeks",
        ],
    },
    {
        "name": "Software Developer",
        "description": "Designs, builds, tests and maintains software applications and backend systems.",
        "tools": "Python/Java, Git, SQL, REST APIs, VS Code, Linux",
        "interview": "DSA, OOP, system design basics, databases, APIs, problem solving",
        "skills": {"DSA": 5, "Backend/APIs": 5, "Python": 4, "Git/GitHub": 4, "SQL": 3, "JavaScript": 3, "Linux": 2},
        "interests": [3, 10, 4, 3, 3],
        "roadmap": [
            "Programming Core|One language in depth, OOP, problem solving",
            "DSA|Arrays, strings, trees, graphs, sorting, searching",
            "Databases|SQL, schema design, an ORM",
            "Backend|REST APIs, authentication, FastAPI or Spring Boot",
            "Projects|Full application with database and tests",
            "Portfolio & Interview|GitHub, resume, mock interviews, system design basics",
        ],
        "projects": [
            "Library Management System|Beginner|Python, SQL|Self-created data|CRUD application with a database|2 weeks",
            "Task Manager API|Intermediate|Backend/APIs, SQL, Git/GitHub|Self-created data|REST API with login and tests|3 weeks",
            "E-commerce Backend|Advanced|Backend/APIs, DSA, SQL|Self-created data|Products, cart and orders API|5 weeks",
        ],
    },
    {
        "name": "Web Developer",
        "description": "Builds websites and web applications, from the user interface to the server side.",
        "tools": "HTML, CSS, JavaScript, React, Node.js/FastAPI, Git",
        "interview": "HTML/CSS, JavaScript, React, responsive design, REST APIs, Git",
        "skills": {"HTML/CSS": 5, "JavaScript": 5, "React": 4, "Backend/APIs": 3, "Git/GitHub": 4, "UI/UX Design": 2, "SQL": 2},
        "interests": [3, 9, 3, 3, 7],
        "roadmap": [
            "HTML & CSS|Semantic HTML, Flexbox, Grid, responsive design",
            "JavaScript|ES6, DOM, async JavaScript, fetch API",
            "React|Components, hooks, routing, state management",
            "Backend Basics|REST APIs, authentication, databases",
            "Projects|Full-stack projects, deployment",
            "Portfolio & Interview|Portfolio website, GitHub, interview practice",
        ],
        "projects": [
            "Personal Portfolio Website|Beginner|HTML/CSS, JavaScript|Self-created content|Responsive portfolio site|1 week",
            "Weather App|Intermediate|JavaScript, React, APIs|Open weather API|Live weather app with search|2 weeks",
            "Full-stack Blog Platform|Advanced|React, Backend/APIs, SQL|Self-created data|Blog with login, posts and comments|5 weeks",
        ],
    },
    {
        "name": "UI/UX Designer",
        "description": "Designs how digital products look and feel, based on user research, wireframes and prototypes.",
        "tools": "Figma, Adobe XD, Miro, basic HTML/CSS",
        "interview": "Design process, user research, wireframing, usability, portfolio case studies",
        "skills": {"UI/UX Design": 5, "Communication": 4, "HTML/CSS": 3, "Business Analysis": 2, "Data Visualization": 2, "JavaScript": 1},
        "interests": [3, 3, 2, 4, 10],
        "roadmap": [
            "Design Basics|Colour, typography, layout, design principles",
            "Figma|Frames, components, auto layout, prototyping",
            "UX Research|User interviews, personas, user journeys",
            "Wireframes & Prototypes|Low and high fidelity designs, usability testing",
            "Case Studies|2-3 complete design case studies",
            "Portfolio & Interview|Portfolio site, resume, design challenge practice",
        ],
        "projects": [
            "Mobile App Redesign|Beginner|UI/UX Design|Existing public app|Redesigned screens in Figma|2 weeks",
            "Food Delivery App Prototype|Intermediate|UI/UX Design, Communication|Self-created research|Clickable prototype with user flow|3 weeks",
            "E-learning Platform Case Study|Advanced|UI/UX Design, HTML/CSS|User interviews|Full case study from research to prototype|5 weeks",
        ],
    },
    {
        "name": "Cyber Security Analyst",
        "description": "Protects systems and networks by monitoring for threats, finding vulnerabilities and responding to incidents.",
        "tools": "Wireshark, Nmap, Kali Linux, Burp Suite, SIEM tools",
        "interview": "Networking, OWASP Top 10, cryptography basics, Linux, incident response",
        "skills": {"Cyber Security": 5, "Networking": 5, "Linux": 4, "Python": 3, "Cloud Computing": 2, "Communication": 2},
        "interests": [4, 6, 3, 3, 1],
        "roadmap": [
            "Networking|TCP/IP, DNS, HTTP, firewalls, packet analysis",
            "Linux|Linux commands, permissions, shell scripting",
            "Security Fundamentals|CIA triad, cryptography, common attacks, OWASP Top 10",
            "Tools|Wireshark, Nmap, Burp Suite, vulnerability scanning",
            "Practice Labs|TryHackMe or HackTheBox labs, a small capture-the-flag",
            "Portfolio & Interview|Lab write-ups, resume, interview practice",
        ],
        "projects": [
            "Network Traffic Analysis|Beginner|Networking, Cyber Security|Sample packet captures|Report of suspicious traffic found|2 weeks",
            "Web Vulnerability Assessment|Intermediate|Cyber Security, Linux|Intentionally vulnerable app (DVWA)|Vulnerability report with fixes|3 weeks",
            "Log Monitoring Dashboard|Advanced|Python, Linux, Cyber Security|Sample server logs|Script that flags suspicious activity|4 weeks",
        ],
    },
    {
        "name": "Cloud Engineer",
        "description": "Designs, deploys and manages applications and infrastructure on cloud platforms.",
        "tools": "AWS/Azure/GCP, Linux, Docker, Terraform, Python",
        "interview": "Cloud services, networking, Linux, IAM, storage, scaling, cost basics",
        "skills": {"Cloud Computing": 5, "Linux": 4, "Networking": 4, "Docker": 3, "CI/CD": 3, "Python": 3, "Cyber Security": 2},
        "interests": [3, 7, 3, 3, 1],
        "roadmap": [
            "Linux & Networking|Linux administration, IP, DNS, load balancers",
            "Cloud Basics|Compute, storage, databases, IAM on one cloud (AWS or Azure)",
            "Containers|Docker basics, container networking",
            "Infrastructure|Infrastructure as code, monitoring, scaling",
            "Projects|Deploy a real app on the cloud",
            "Portfolio & Interview|Cloud certification prep, resume, interview practice",
        ],
        "projects": [
            "Static Website on Cloud|Beginner|Cloud Computing|Own website files|Website hosted with a public URL|1 week",
            "Web App Deployment|Intermediate|Cloud Computing, Docker, Linux|Own web app|Containerised app running on a cloud VM|3 weeks",
            "Auto-scaling Architecture|Advanced|Cloud Computing, Networking, CI/CD|Own web app|Load-balanced, auto-scaling deployment|4 weeks",
        ],
    },
    {
        "name": "DevOps Engineer",
        "description": "Connects development and operations by automating building, testing, deployment and monitoring of software.",
        "tools": "Git, Jenkins/GitHub Actions, Docker, Kubernetes, Linux, Terraform",
        "interview": "CI/CD, Docker, Kubernetes basics, Linux, scripting, monitoring, Git workflows",
        "skills": {"CI/CD": 5, "Docker": 5, "Linux": 5, "Cloud Computing": 4, "Git/GitHub": 4, "Python": 3, "Networking": 3},
        "interests": [3, 8, 3, 3, 1],
        "roadmap": [
            "Linux & Scripting|Linux, Bash, Python scripting",
            "Version Control|Git branching, pull requests, workflows",
            "Containers|Docker, Docker Compose, basics of Kubernetes",
            "CI/CD|GitHub Actions or Jenkins pipelines, automated testing",
            "Cloud & Monitoring|Cloud deployment, logs, monitoring, alerts",
            "Portfolio & Interview|Pipeline projects, resume, interview practice",
        ],
        "projects": [
            "Dockerize a Web App|Beginner|Docker, Linux|Own web app|Docker image and compose file|1 week",
            "CI Pipeline with GitHub Actions|Intermediate|CI/CD, Git/GitHub|Own repository|Pipeline that tests and builds on every push|2 weeks",
            "Automated Deployment Pipeline|Advanced|CI/CD, Docker, Cloud Computing|Own web app|Push-to-deploy pipeline on the cloud|4 weeks",
        ],
    },
    {
        "name": "Business Analyst",
        "description": "Understands business needs, analyses processes and data, and turns requirements into solutions for teams.",
        "tools": "Excel, SQL, Power BI, Jira, Visio/draw.io, documentation tools",
        "interview": "Requirement gathering, user stories, process modelling, SQL, Excel, case studies",
        "skills": {"Business Analysis": 5, "Communication": 5, "Excel": 4, "SQL": 4, "Power BI": 3, "Data Visualization": 3, "Statistics": 2},
        "interests": [7, 3, 3, 9, 3],
        "roadmap": [
            "Business Basics|Business processes, stakeholders, SDLC, Agile and Scrum",
            "Requirements|User stories, BRD and FRD documents, use cases",
            "Excel & SQL|Advanced Excel, SQL for data retrieval",
            "Dashboards|Power BI or Tableau reports for business metrics",
            "Case Studies|2-3 case studies with process flow diagrams",
            "Portfolio & Interview|Documentation samples, resume, case interview practice",
        ],
        "projects": [
            "Requirement Document for an App|Beginner|Business Analysis, Communication|Self-created scenario|BRD with user stories|2 weeks",
            "Process Improvement Case Study|Intermediate|Business Analysis, Excel|Sample process data|As-is and to-be process flow with analysis|3 weeks",
            "KPI Dashboard for a Retail Business|Intermediate|SQL, Power BI, Data Visualization|Superstore dataset|Dashboard with business KPIs|3 weeks",
        ],
    },
]

# --------------------------------------------------- TRAINING DATA (for ML)
def build_training_data(rows_per_career=60, seed=42):
    rng = np.random.default_rng(seed)
    skill_names = list(SKILLS.keys())
    records = []
    for c in CAREERS:
        for _ in range(rows_per_career):
            row = {}
            for s in skill_names:
                if s in c["skills"]:
                    mean = 3.0 + 1.2 * c["skills"][s]   # importance 5 -> about 9
                    sd = 1.5
                else:
                    mean, sd = 2.5, 2.0
                row[s] = int(np.clip(round(rng.normal(mean, sd)), 0, 10))
            for name, m in zip(INTERESTS, c["interests"]):
                row["interest_" + name] = int(np.clip(round(rng.normal(m, 1.3)), 0, 10))
            row["career"] = c["name"]
            records.append(row)
    df = pd.DataFrame(records).sample(frac=1, random_state=seed).reset_index(drop=True)
    return df

# ------------------------------------------------------------- DB SEEDING
def seed_database(reset=False):
    db = SessionLocal()
    try:
        if reset:
            for model in (Project, Roadmap, CareerSkill, Career, Skill):
                db.query(model).delete()
            db.commit()
            print("Old career data cleared.")

        if db.query(Career).count() > 0:
            print("Careers already exist. Nothing added. (Use --reset to reload.)")
            return

        skill_ids = {}
        for name, cat in SKILLS.items():
            s = Skill(skill_name=name, category=cat)
            db.add(s)
            db.flush()
            skill_ids[name] = s.skill_id

        for c in CAREERS:
            career = Career(career_name=c["name"], description=c["description"],
                            tools=c["tools"], interview_topics=c["interview"])
            db.add(career)
            db.flush()

            for skill_name, importance in c["skills"].items():
                db.add(CareerSkill(career_id=career.career_id,
                                   skill_id=skill_ids[skill_name], importance=importance))

            for i, item in enumerate(c["roadmap"], start=1):
                title, topics = item.split("|")
                db.add(Roadmap(career_id=career.career_id, month_no=i, title=title, topics=topics))

            for item in c["projects"]:
                t, diff, req, ds, out, time = item.split("|")
                db.add(Project(career_id=career.career_id, title=t, difficulty=diff,
                               required_skills=req, dataset=ds, expected_output=out,
                               estimated_time=time))
        db.commit()
        print("Database filled successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(reset="--reset" in sys.argv)

    os.makedirs("data", exist_ok=True)
    df = build_training_data()
    df.to_csv("data/training_data.csv", index=False)
    print(f"Training data saved: data/training_data.csv ({len(df)} rows, {df.shape[1]-1} features)")
    print(f"Skills: {len(SKILLS)} | Careers: {len(CAREERS)} | Projects: {sum(len(c['projects']) for c in CAREERS)}")
