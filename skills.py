"""
skills.py - Skill Extraction Engine
Defines skill catalog, extracts skills, confidence scores, experience level.
"""

import re
from collections import defaultdict

SKILL_CATALOG = {
    "Python":           ["python"],
    "JavaScript":       ["javascript", "js", "es6"],
    "TypeScript":       ["typescript"],
    "Java":             ["java"],
    "SQL":              ["sql", "mysql", "postgresql", "sqlite"],
    "HTML":             ["html", "html5"],
    "CSS":              ["css", "scss", "sass"],
    "React":            ["react", "reactjs"],
    "Angular":          ["angular"],
    "Django":           ["django"],
    "FastAPI":          ["fastapi"],
    "Flask":            ["flask"],
    "Node.js":          ["nodejs"],
    "Docker":           ["docker", "dockerfile", "containerization"],
    "Kubernetes":       ["kubernetes", "k8s"],
    "CI/CD":            ["ci/cd", "cicd", "github actions", "jenkins"],
    "Linux":            ["linux", "unix", "bash", "shell scripting"],
    "AWS":              ["aws", "amazon web services", "ec2", "lambda"],
    "Azure":            ["azure", "microsoft azure"],
    "GCP":              ["gcp", "google cloud", "bigquery"],
    "Git":              ["git", "github", "gitlab", "version control"],
    "Machine Learning": ["machine learning", "scikit-learn", "sklearn"],
    "Deep Learning":    ["deep learning", "neural network", "pytorch", "tensorflow", "keras"],
    "NLP":              ["nlp", "natural language processing", "bert", "transformers", "spacy"],
    "Data Analysis":    ["data analysis", "pandas", "numpy", "data wrangling", "eda"],
    "Data Visualization": ["data visualization", "matplotlib", "seaborn", "plotly", "tableau", "power bi"],
    "Statistics":       ["statistics", "hypothesis testing", "regression", "probability"],
    "Spark":            ["apache spark", "pyspark"],
    "ETL":              ["etl", "data pipeline", "airflow"],
    "LLM Integration":  ["langchain", "prompt engineering", "rag", "retrieval augmented", "openai api"],
    "Vector Databases": ["pinecone", "faiss", "chroma", "weaviate", "vector database"],
    "MLOps":            ["mlops", "mlflow", "model deployment", "model serving"],
    "REST APIs":        ["rest api", "restful", "api design"],
    "System Design":    ["system design", "microservices", "distributed systems", "scalability"],
    "MongoDB":          ["mongodb", "mongo"],
    "PostgreSQL":       ["postgresql", "postgres"],
    "Redis":            ["redis"],
    "Testing":          ["unit testing", "pytest", "jest", "tdd", "selenium"],
    "Project Management": ["project management", "pmp", "jira", "asana"],
    "Agile":            ["agile", "scrum", "sprint", "kanban"],
    "Leadership":       ["leadership", "team lead", "people management", "mentoring"],
    "Communication":    ["communication", "presentation", "stakeholder management"],
    "Strategic Planning": ["strategic planning", "okr", "kpi"],
    "Business Analysis": ["business analysis", "requirements gathering"],
    "Product Management": ["product management", "product roadmap", "user stories"],
    "Financial Analysis": ["financial analysis", "financial modeling", "dcf"],
    "Excel":            ["excel", "spreadsheet", "pivot table", "vlookup"],
    "Budgeting":        ["budgeting", "forecasting", "variance analysis"],
    "Risk Management":  ["risk management", "compliance"],
    "Accounting":       ["accounting", "bookkeeping", "gaap", "ifrs"],
    "HR Management":    ["hr management", "human resources", "hris", "workday"],
    "Recruitment":      ["recruitment", "talent acquisition", "headhunting", "sourcing"],
    "Performance Management": ["performance management", "appraisal", "360 feedback"],
    "Training & Development": ["learning and development", "l&d", "onboarding training"],
    "Labour Law":       ["labour law", "employment law", "statutory compliance"],
    "Payroll":          ["payroll", "salary processing", "compensation"],
    "Digital Marketing": ["digital marketing", "online marketing", "performance marketing"],
    "SEO/SEM":          ["seo", "sem", "google ads", "ppc"],
    "Content Marketing": ["content marketing", "copywriting", "content strategy"],
    "Email Marketing":  ["email marketing", "mailchimp", "hubspot"],
    "Marketing Analytics": ["google analytics", "mixpanel", "marketing analytics"],
    "Brand Management": ["brand management", "branding", "brand strategy"],
    "UI/UX Design":     ["ui/ux", "user experience", "figma", "sketch", "adobe xd"],
    "Graphic Design":   ["graphic design", "photoshop", "illustrator", "canva"],
}

SKILL_DEPENDENCIES = {
    "Machine Learning":  ["Python", "Statistics", "Data Analysis"],
    "Deep Learning":     ["Machine Learning", "Python"],
    "NLP":               ["Deep Learning", "Python"],
    "LLM Integration":   ["NLP", "Python", "REST APIs"],
    "Vector Databases":  ["LLM Integration"],
    "MLOps":             ["Machine Learning", "Docker", "Python"],
    "Data Analysis":     ["Python", "SQL"],
    "Data Visualization": ["Data Analysis"],
    "ETL":               ["SQL", "Python"],
    "Spark":             ["Python", "SQL", "ETL"],
    "FastAPI":           ["Python", "REST APIs"],
    "Flask":             ["Python"],
    "Django":            ["Python"],
    "Kubernetes":        ["Docker", "Linux"],
    "CI/CD":             ["Git", "Docker"],
    "AWS":               ["Linux", "CI/CD"],
    "Azure":             ["Linux"],
    "GCP":               ["Linux"],
    "System Design":     ["Docker", "REST APIs"],
    "Statistics":        ["Python"],
    "PostgreSQL":        ["SQL"],
    "MongoDB":           ["SQL"],
    "Financial Analysis": ["Excel", "Statistics"],
    "Budgeting":         ["Financial Analysis"],
    "Performance Management": ["HR Management", "Communication"],
    "Training & Development": ["HR Management", "Communication"],
    "Business Analysis": ["Communication", "Project Management"],
    "Product Management": ["Agile", "Communication"],
    "SEO/SEM":           ["Marketing Analytics", "Digital Marketing"],
    "Email Marketing":   ["Digital Marketing", "Marketing Analytics"],
    "Content Marketing": ["Communication", "Digital Marketing"],
}

SENIOR_SIGNALS = ["senior", "lead", "principal", "architect", "head of",
                  "director", "10+ years", "8+ years", "7+ years", "expert", "manager"]
MID_SIGNALS    = ["mid", "3 years", "4 years", "5 years", "intermediate", "experienced"]
JUNIOR_SIGNALS = ["junior", "entry", "fresher", "graduate", "intern",
                  "1 year", "2 years", "beginner", "trainee"]


def detect_experience_level(text):
    lower = text.lower()
    s = sum(1 for x in SENIOR_SIGNALS if x in lower)
    m = sum(1 for x in MID_SIGNALS    if x in lower)
    j = sum(1 for x in JUNIOR_SIGNALS if x in lower)
    if s >= m and s >= j and s > 0:
        return "Senior"
    elif m >= j and m > 0:
        return "Mid-Level"
    elif j > 0:
        return "Junior"
    return "Mid-Level"


def extract_skills(text):
    if not text or not text.strip():
        return []
    normalized = re.sub(r"\s+", " ", text.lower())
    found = set()
    for skill_name, aliases in SKILL_CATALOG.items():
        for alias in aliases:
            try:
                if re.search(r"\b" + re.escape(alias) + r"\b", normalized):
                    found.add(skill_name)
                    break
            except re.error:
                if alias in normalized:
                    found.add(skill_name)
                    break
    return sorted(found)


def extract_skills_with_confidence(text):
    if not text or not text.strip():
        return {}
    normalized = re.sub(r"\s+", " ", text.lower())
    counts = defaultdict(int)
    for skill_name, aliases in SKILL_CATALOG.items():
        for alias in aliases:
            try:
                counts[skill_name] += len(re.findall(r"\b" + re.escape(alias) + r"\b", normalized))
            except re.error:
                counts[skill_name] += normalized.count(alias)
    found = {k: v for k, v in counts.items() if v > 0}
    if not found:
        return {}
    mx = max(found.values())
    return dict(sorted({k: round(min(v / mx, 1.0), 2) for k, v in found.items()}.items()))


def get_all_skills():
    return sorted(SKILL_CATALOG.keys())