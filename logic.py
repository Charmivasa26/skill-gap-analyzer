"""
logic.py - Gap Analysis, Roadmap Generation and Reasoning Engine
Computes skill gap and builds dependency-ordered learning roadmap.
"""

from skills import SKILL_DEPENDENCIES, extract_skills

LEARNING_RESOURCES = {
    "Python":           "docs.python.org/3/tutorial | freeCodeCamp Python",
    "JavaScript":       "javascript.info | MDN Web Docs",
    "TypeScript":       "typescriptlang.org/docs",
    "SQL":              "sqlzoo.net | Mode SQL Tutorial",
    "HTML":             "developer.mozilla.org/docs/Learn/HTML",
    "CSS":              "developer.mozilla.org/docs/Learn/CSS",
    "React":            "react.dev/learn | Full Stack Open",
    "Angular":          "angular.io/tutorial",
    "Django":           "docs.djangoproject.com/intro/tutorial",
    "FastAPI":          "fastapi.tiangolo.com/tutorial",
    "Flask":            "flask.palletsprojects.com/tutorial",
    "Node.js":          "nodejs.dev/learn",
    "Docker":           "docs.docker.com/get-started",
    "Kubernetes":       "kubernetes.io/docs/tutorials",
    "CI/CD":            "docs.github.com/actions | CircleCI Docs",
    "Linux":            "linuxjourney.com | The Linux Command Line",
    "AWS":              "aws.amazon.com/training | AWS Skill Builder",
    "Azure":            "learn.microsoft.com/training/azure",
    "GCP":              "cloud.google.com/training",
    "Git":              "git-scm.com/book | GitHub Skills",
    "Machine Learning": "coursera.org/learn/machine-learning | fast.ai",
    "Deep Learning":    "deeplearning.ai/courses | fast.ai Part 2",
    "NLP":              "huggingface.co/learn/nlp-course",
    "LLM Integration":  "python.langchain.com/docs | LlamaIndex Docs",
    "Vector Databases": "docs.pinecone.io | Chroma Docs",
    "MLOps":            "mlflow.org/docs | Made With ML",
    "Data Analysis":    "pandas.pydata.org/docs | Kaggle Learn",
    "Data Visualization": "matplotlib.org/tutorials | Plotly Docs",
    "Statistics":       "khanacademy.org/math/statistics-probability",
    "ETL":              "airflow.apache.org/docs | dbt Docs",
    "Spark":            "spark.apache.org/docs/latest/quick-start.html",
    "REST APIs":        "restfulapi.net | Postman Learning Center",
    "System Design":    "github.com/donnemartin/system-design-primer",
    "MongoDB":          "learn.mongodb.com",
    "PostgreSQL":       "postgresqltutorial.com",
    "Redis":            "redis.io/docs/getting-started",
    "Testing":          "docs.pytest.org | TestingJavaScript.com",
    "Agile":            "atlassian.com/agile",
    "Project Management": "pmi.org/learning/library",
    "Leadership":       "coursera.org/learn/inspiring-leadership",
    "Communication":    "coursera.org/learn/wharton-communication-skills",
    "HR Management":    "shrm.org/resources | Coursera HR courses",
    "Recruitment":      "linkedin.com/learning/recruitment-foundations",
    "Financial Analysis": "coursera.org/learn/financial-analysis",
    "Excel":            "support.microsoft.com/excel | ExcelJet.net",
    "Digital Marketing": "google.com/skillshop | HubSpot Academy",
    "SEO/SEM":          "moz.com/learn/seo | Google Search Central",
    "UI/UX Design":     "figma.com/resources/learn-design | Nielsen Norman Group",
}

ESTIMATED_HOURS = {
    "Python": 40, "JavaScript": 40, "TypeScript": 20, "SQL": 20,
    "HTML": 15, "CSS": 20, "React": 30, "Angular": 30,
    "Django": 25, "FastAPI": 15, "Flask": 15, "Node.js": 25,
    "Docker": 20, "Kubernetes": 30, "CI/CD": 15, "Linux": 20,
    "AWS": 40, "Azure": 35, "GCP": 35, "Git": 10,
    "Machine Learning": 60, "Deep Learning": 50, "NLP": 40,
    "LLM Integration": 25, "Vector Databases": 15, "MLOps": 30,
    "Data Analysis": 30, "Data Visualization": 20, "Statistics": 35,
    "ETL": 20, "Spark": 30, "REST APIs": 20, "System Design": 35,
    "MongoDB": 15, "PostgreSQL": 20, "Redis": 10, "Testing": 20,
    "Project Management": 20, "Agile": 10, "Leadership": 15,
    "Communication": 15, "Strategic Planning": 15, "Business Analysis": 20,
    "Product Management": 25, "Financial Analysis": 30, "Excel": 15,
    "Budgeting": 15, "Risk Management": 15, "Accounting": 25,
    "HR Management": 20, "Recruitment": 15, "Performance Management": 15,
    "Training & Development": 15, "Labour Law": 20, "Payroll": 15,
    "Digital Marketing": 25, "SEO/SEM": 20, "Content Marketing": 15,
    "Email Marketing": 10, "Marketing Analytics": 20, "Brand Management": 15,
    "UI/UX Design": 30, "Graphic Design": 25,
}

PRACTICAL_TIPS = {
    "Python":           "Start with small scripts — Python's readability makes it beginner-friendly.",
    "Machine Learning": "Work through a Kaggle competition once you finish theory.",
    "Docker":           "Containerize one of your existing projects to make it concrete.",
    "React":            "Build a small to-do app first — hooks click faster with practice.",
    "SQL":              "Practice daily queries on a sample database like Northwind.",
    "AWS":              "The free tier is enough to deploy a real project — aim for that early.",
    "System Design":    "Study the Primer repo and try designing systems you already use.",
    "NLP":              "The Hugging Face course is free and uses real transformer models from day one.",
    "LLM Integration":  "Build a simple RAG chatbot with LangChain — covers 80% of real use-cases.",
    "Git":              "Commit every day, even tiny changes — muscle memory is the goal.",
    "Statistics":       "Pair theory with Python (scipy, statsmodels) to stay grounded.",
    "Deep Learning":    "fast.ai teaches top-down — you run models on real data on day one.",
    "Kubernetes":       "Learn Docker thoroughly first — K8s complexity drops significantly after that.",
    "HR Management":    "Get SHRM-CP certified — widely recognized and boosts credibility.",
    "Recruitment":      "Practice with mock interviews and LinkedIn Recruiter free trial.",
    "Financial Analysis": "Build a real DCF model on a company you know — theory clicks faster.",
    "Digital Marketing": "Run a small Google Ads campaign with a $10 budget to learn hands-on.",
}


def compute_skill_gap(resume_skills, jd_skills):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    return {
        "matched": sorted(resume_set & jd_set),
        "missing": sorted(jd_set - resume_set),
        "extra":   sorted(resume_set - jd_set),
    }


def _topological_sort(skills_to_learn):
    target_set = set(skills_to_learn)
    in_degree  = {s: 0 for s in target_set}
    dependents = {s: [] for s in target_set}

    for skill in target_set:
        for prereq in SKILL_DEPENDENCIES.get(skill, []):
            if prereq in target_set:
                in_degree[skill] += 1
                dependents[prereq].append(skill)

    queue   = sorted(s for s in target_set if in_degree[s] == 0)
    ordered = []

    while queue:
        node = queue.pop(0)
        ordered.append(node)
        for dep in sorted(dependents[node]):
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    remaining = [s for s in skills_to_learn if s not in ordered]
    return ordered + sorted(remaining)


def _dependency_depth(skill, target_skills):
    target_set = set(target_skills)
    depth      = 0
    visited    = set()

    def dfs(s, d):
        nonlocal depth
        if s in visited:
            return
        visited.add(s)
        for prereq in SKILL_DEPENDENCIES.get(s, []):
            if prereq in target_set:
                depth = max(depth, d + 1)
                dfs(prereq, d + 1)

    dfs(skill, 0)
    return depth


def _generate_reasoning(skill, prereqs_ok, prereqs_needed):
    lines = [f"{skill} is required by the target role but not found on your resume."]
    if prereqs_ok:
        lines.append(f"You already know {', '.join(prereqs_ok)}, which gives you a solid foundation.")
    else:
        lines.append(f"Start from the basics of {skill}.")
    if prereqs_needed:
        lines.append(f"Complete {', '.join(prereqs_needed)} first before tackling {skill}.")
    tip = PRACTICAL_TIPS.get(skill, "")
    if tip:
        lines.append(tip)
    return " ".join(lines)


def generate_roadmap(missing_skills, resume_skills):
    if not missing_skills:
        return []

    ordered    = _topological_sort(missing_skills)
    resume_set = set(resume_skills)
    roadmap    = []

    for idx, skill in enumerate(ordered, start=1):
        all_prereqs    = SKILL_DEPENDENCIES.get(skill, [])
        prereqs_needed = [p for p in all_prereqs if p not in resume_set and p in set(missing_skills)]
        prereqs_ok     = [p for p in all_prereqs if p in resume_set]
        depth          = _dependency_depth(skill, missing_skills)

        if depth == 0:
            priority = "🟢 Foundation"
        elif depth <= 2:
            priority = "🟡 Core"
        else:
            priority = "🔴 Advanced"

        roadmap.append({
            "step":           idx,
            "skill":          skill,
            "priority":       priority,
            "prereqs_needed": prereqs_needed,
            "prereqs_ok":     prereqs_ok,
            "hours":          ESTIMATED_HOURS.get(skill, 20),
            "resources":      LEARNING_RESOURCES.get(skill, "Search official documentation"),
            "reasoning":      _generate_reasoning(skill, prereqs_ok, prereqs_needed),
        })

    return roadmap


def summarize_gap(gap, roadmap):
    total_hours  = sum(r["hours"] for r in roadmap)
    match_pct    = (
        round(len(gap["matched"]) / (len(gap["matched"]) + len(gap["missing"])) * 100)
        if (gap["matched"] or gap["missing"]) else 0
    )
    return {
        "match_percentage":   match_pct,
        "skills_matched":     len(gap["matched"]),
        "skills_missing":     len(gap["missing"]),
        "total_learn_hours":  total_hours,
        "weeks_10h_per_week": round(total_hours / 10, 1),
        "weeks_20h_per_week": round(total_hours / 20, 1),
    }