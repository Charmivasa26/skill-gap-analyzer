# 🎯 AI Skill Gap Analyzer

An AI-driven, adaptive learning engine that parses a candidate's resume and a target job
description, identifies the skill gap, and generates a personalized, dependency-ordered
learning roadmap with reasoning — all running **100% locally** with no paid APIs.

Built for the **ARTPARK CodeForge Hackathon** — *AI-Adaptive Onboarding Engine*.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Intelligent Parsing** | 80+ skills extracted via alias regex from PDF, TXT, or pasted text |
| **Confidence Scoring** | Mention frequency normalized 0.0–1.0 per skill |
| **Experience Detection** | Junior / Mid-Level / Senior from resume signal keywords |
| **Skill Gap Detection** | Set arithmetic — matched, missing, and bonus skills |
| **Dependency Roadmap** | Kahn's topological sort ensures prerequisites before dependents |
| **Reasoning Trace** | Plain-English explanation for every roadmap step |
| **Radar Chart** | Visual spider chart — green = have it, orange = to learn |
| **Training Saved Metric** | Exact hours of redundant onboarding eliminated |
| **Cross-Domain Support** | Tech, Data/AI, DevOps, HR, Finance, Marketing, Design |
| **Two Sample Personas** | Tech (Data Analyst → ML Engineer) and HR (Manager → Director) |
| **PDF + TXT Upload** | Both resume and JD accept file uploads |
| **Light / Dark Mode** | Full theme toggle via settings panel |
| **Downloadable Report** | One-click .txt export of complete roadmap |
| **Zero Hallucinations** | Strictly catalog-bound — never invents skills |
| **Fully Offline** | No paid APIs, no internet required after pip install |

---

## 🗂 Project Structure

```
skill_gap_app/
│
├── app.py            ← Streamlit UI (entry point)
├── skills.py         ← Skill catalog, extraction, confidence scoring, experience detection
├── logic.py          ← Gap analysis, roadmap generation, reasoning engine
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## 🚀 Quick Start

### 1. Clone / download the project

```bash
git clone https://github.com/your-username/ai-skill-gap-analyzer.git
cd ai-skill-gap-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | >= 1.32.0 | Web UI framework |
| `pypdf` | >= 3.0.0 | PDF text extraction |
| `matplotlib` | >= 3.7.0 | Radar chart rendering |
| `numpy` | >= 1.24.0 | Polar coordinate arrays for chart |

> **No LLMs, no embeddings, no databases, no paid APIs** — pure Python logic.

---

## 🐳 Dockerfile — Not Included

A Dockerfile is **not included** in this submission. This is a deliberate decision for
the following reasons:

1. **Zero-dependency setup** — the project requires only `pip install -r requirements.txt`
   and `streamlit run app.py`. There are no system-level dependencies, compiled binaries,
   or environment-specific configurations that would require containerization.

2. **Pure Python stack** — all four dependencies (streamlit, pypdf, matplotlib, numpy)
   are standard Python packages available on PyPI and install identically on Windows,
   macOS, and Linux without any Docker overhead.

3. **Judge reproducibility is fully guaranteed** — any judge can run the project in under
   2 minutes using only Python 3.11 and pip, which are universally available. A Dockerfile
   would add complexity without adding reproducibility.

4. **Hackathon guidelines state optional** — the ARTPARK CodeForge Hackathon brief
   explicitly states: *"Dockerization is optional but encouraged."* Given the simplicity
   of the setup, Docker adds no practical value here.

If Docker is preferred, the equivalent two commands are:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
```bash
docker build -t skill-gap-analyzer .
docker run -p 8501:8501 skill-gap-analyzer
```

---

## 🧠 Logic Overview

### Skill Extraction (`skills.py`)

- **SKILL_CATALOG** maps 80+ skills to their aliases (e.g., `"Machine Learning"` → `["machine learning", "scikit-learn", "sklearn"]`)
- Text is lowercased and whitespace-normalized
- Word-boundary regex (`\b`) prevents false positives
- `extract_skills_with_confidence()` counts alias mentions and normalizes to 0.0–1.0
- `detect_experience_level()` classifies Senior / Mid-Level / Junior from signal keywords

### Skill Gap Detection (`logic.py`)

```
matched = resume_skills ∩ jd_skills   # skills you have that they want
missing = jd_skills − resume_skills   # skills you need to learn
extra   = resume_skills − jd_skills   # bonus skills you bring
```

### Adaptive Pathing Algorithm (`logic.py`)

1. **Dependency Graph** — `SKILL_DEPENDENCIES` encodes prerequisite relationships
2. **Kahn's BFS Topological Sort** — orders missing skills so prerequisites always come first
3. **Priority Tiers** — Foundation / Core / Advanced assigned by dependency depth
4. **Reasoning Engine** — per-step plain-English explanation with practical tips
5. **Training Saved** — `sum(ESTIMATED_HOURS[s] for s in matched_skills)`

---

## 📊 Evaluation Criteria Mapping

| Criterion | Implementation |
|---|---|
| Technical Sophistication (20%) | DAG pathing + confidence scoring + experience detection |
| Grounding & Reliability (15%) | Strictly catalog-bound — zero hallucinations |
| Reasoning Trace (10%) | Per-step plain-English explanations |
| Product Impact (10%) | Training saved metric — exact redundant hours eliminated |
| User Experience (15%) | Radar chart, dark/light mode, PDF upload, progress bar |
| Cross-Domain Scalability (10%) | Tech, HR, Finance, Marketing — two built-in personas |
| Communication & Docs (20%) | This README + technical documentation PDF |

---

## 🗂 Datasets Referenced

| Dataset | Use |
|---|---|
| [Kaggle Resume Dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data) | Skill vocabulary and alias validation |
| [O*NET Database](https://www.onetcenter.org/db_releases.html) | Occupational skill taxonomy |
| [Jobs & Job Descriptions](https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description) | JD vocabulary validation |

---

## 📄 License

MIT License — free for personal and commercial use.
