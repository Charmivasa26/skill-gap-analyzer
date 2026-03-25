"""
app.py - AI Skill Gap Analyzer
Run with: streamlit run app.py
"""

import io
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import streamlit as st
from pypdf import PdfReader
from skills import extract_skills, extract_skills_with_confidence, detect_experience_level
from logic import compute_skill_gap, generate_roadmap, summarize_gap, ESTIMATED_HOURS

st.set_page_config(
    page_title="AI Skill Gap Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# SAMPLE DATA — TECH PERSONA
# ---------------------------------------------------------------------------
SAMPLE_RESUME_TECH = """John Doe | john.doe@email.com | linkedin.com/in/johndoe

SUMMARY
Data analyst with 3 years of experience in Python, SQL, and data visualization.

SKILLS
Python, SQL, R, Pandas, NumPy, Matplotlib, Seaborn, Git, Tableau, Statistics, Data Analysis, ETL

EXPERIENCE
Data Analyst - Acme Corp (2021-Present)
Built automated ETL pipelines using Python and SQL
Created dashboards using Tableau and Matplotlib
Managed version control using Git and GitHub

EDUCATION
B.Sc. Computer Science - State University (2021)
"""

SAMPLE_JD_TECH = """Machine Learning Engineer - TechStartup Inc.

REQUIRED SKILLS
Python, Machine Learning, Deep Learning, NLP, LLM Integration,
Vector Databases, Docker, Kubernetes, MLOps, REST APIs,
SQL, System Design, FastAPI, CI/CD, AWS
"""

# ---------------------------------------------------------------------------
# SAMPLE DATA — HR PERSONA (proves cross-domain scalability)
# ---------------------------------------------------------------------------
SAMPLE_RESUME_HR = """Sarah Johnson | sarah.j@email.com

SUMMARY
HR Manager with 5 years of experience in recruitment, onboarding, and payroll.

SKILLS
HR Management, Recruitment, Payroll, Training & Development,
Performance Management, Communication, Leadership, Labour Law,
Agile, Project Management, Excel

EXPERIENCE
HR Manager - GlobalCorp (2019-Present)
Led recruitment for 200+ roles, managed payroll for 500 employees
Designed training programs, handled performance management cycles
Ensured labour law and statutory compliance

EDUCATION
MBA Human Resources - Delhi University (2019)
"""

SAMPLE_JD_HR = """HR Director - Enterprise Solutions Inc.

REQUIRED SKILLS
Strategic Planning, HR Management, Recruitment, Leadership,
Performance Management, Training & Development, Labour Law,
Budgeting, Business Analysis, Communication, Project Management,
Financial Analysis, Product Management
"""

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
_defaults = {
    "dark_mode":         True,
    "show_settings":     False,
    "resume_ta":         "",
    "jd_ta":             "",
    "_load_resume_flag": False,
    "_load_jd_flag":     False,
    "_last_resume_file": "",
    "_last_jd_file":     "",
    "sample_persona":    "tech",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Apply sample flags BEFORE widgets render — writes directly to widget keys
if st.session_state.pop("_load_resume_flag", False):
    p = st.session_state.get("sample_persona", "tech")
    st.session_state["resume_ta"] = SAMPLE_RESUME_TECH if p == "tech" else SAMPLE_RESUME_HR

if st.session_state.pop("_load_jd_flag", False):
    p = st.session_state.get("sample_persona", "tech")
    st.session_state["jd_ta"] = SAMPLE_JD_TECH if p == "tech" else SAMPLE_JD_HR

# ---------------------------------------------------------------------------
# THEME
# ---------------------------------------------------------------------------
dark = st.session_state["dark_mode"]
BG       = "#0f1117" if dark else "#f8fafc"
CARD     = "#1a1f2e" if dark else "#ffffff"
BORDER   = "#2a3040" if dark else "#d1d5db"
TEXT     = "#e2e8f0" if dark else "#111827"
SUBTEXT  = "#8892a4" if dark else "#374151"
ACCENT   = "#63b3ed" if dark else "#1d4ed8"
DIVIDER  = "#232b3a" if dark else "#e5e7eb"
INPUT_BG = "#1a1f2e" if dark else "#ffffff"
TAB_SEL  = "#2d3748" if dark else "#bfdbfe"
HERO_BG  = (
    "linear-gradient(135deg,#1a1f2e 0%,#0d1117 60%,#0f2027 100%)"
    if dark else
    "linear-gradient(135deg,#eff6ff 0%,#f0fdf4 50%,#f8fafc 100%)"
)
PANEL_BG   = "#1e1b4b" if dark else "#eef2ff"
PANEL_TEXT = "#c7d2fe" if dark else "#3730a3"
PANEL_H    = "#a5b4fc" if dark else "#4338ca"
HERO_TITLE = "#ffffff" if dark else "#111827"
STEP_NUM_C = "#4a5568" if dark else "#6b7280"

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="collapsedControl"] {{ display: none !important; }}
.stApp {{ background: {BG} !important; }}
.stApp, .stApp p, .stApp span, .stApp div,
.stApp label, .stApp li, .stApp h1, .stApp h2,
.stApp h3, .stApp h4, .stApp h5 {{ color: {TEXT} !important; }}
.hero {{ background: {HERO_BG}; border: 1px solid {BORDER}; border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; }}
.hero-badge {{ display: inline-block; background: rgba(99,179,237,0.15); border: 1px solid rgba(99,179,237,0.35); color: {ACCENT} !important; padding: 0.22rem 0.7rem; border-radius: 999px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.6rem; font-family: 'Space Mono', monospace; }}
.hero-title {{ font-size: 2.2rem; font-weight: 700; color: {HERO_TITLE} !important; margin: 0; line-height: 1.2; }}
.hero-subtitle {{ font-size: 1rem; color: {SUBTEXT} !important; margin-top: 0.4rem; }}
.section-header {{ font-size: 1.15rem; font-weight: 700; color: {TEXT} !important; border-left: 3px solid {ACCENT}; padding-left: 0.75rem; margin: 1.5rem 0 1rem 0; }}
.metric-row {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }}
.metric-card {{ flex: 1; min-width: 110px; background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 1rem 1.1rem; text-align: center; }}
.metric-value {{ font-size: 1.9rem; font-weight: 700; color: {ACCENT} !important; font-family: 'Space Mono', monospace; line-height: 1.1; }}
.metric-label {{ font-size: 0.72rem; color: {SUBTEXT} !important; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.05em; }}
.metric-card-green {{ flex: 1; min-width: 110px; background: {CARD}; border: 1px solid rgba(16,185,129,0.4); border-radius: 12px; padding: 1rem 1.1rem; text-align: center; }}
.metric-value-green {{ font-size: 1.9rem; font-weight: 700; color: #10b981 !important; font-family: 'Space Mono', monospace; line-height: 1.1; }}
.metric-label-green {{ font-size: 0.72rem; color: {SUBTEXT} !important; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.05em; }}
.pill-container {{ display: flex; flex-wrap: wrap; gap: 0.45rem; margin-bottom: 0.5rem; }}
.pill {{ display: inline-block; padding: 0.28rem 0.7rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; font-family: 'Space Mono', monospace; }}
.pill-green {{ background: rgba(21,128,61,0.12); border: 1px solid rgba(21,128,61,0.35); color: {"#68d391" if dark else "#15803d"} !important; }}
.pill-red   {{ background: rgba(185,28,28,0.1);  border: 1px solid rgba(185,28,28,0.3);  color: {"#fc814a" if dark else "#b91c1c"} !important; }}
.pill-blue  {{ background: rgba(29,78,216,0.1);  border: 1px solid rgba(29,78,216,0.3);  color: {"#63b3ed" if dark else "#1d4ed8"} !important; }}
.pill-gray  {{ background: rgba(75,85,99,0.12);  border: 1px solid rgba(75,85,99,0.3);   color: {"#94a3b8" if dark else "#374151"} !important; }}
.conf-bar-bg  {{ background: {BORDER}; border-radius: 999px; height: 6px; overflow: hidden; margin-top: 4px; }}
.conf-bar-fill {{ height: 100%; background: linear-gradient(90deg,#3182ce,{ACCENT}); border-radius: 999px; }}
.progress-bg  {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 999px; height: 10px; overflow: hidden; margin-top: 0.4rem; margin-bottom: 1rem; }}
.progress-fill {{ height: 100%; background: linear-gradient(90deg,#3182ce,{ACCENT}); border-radius: 999px; }}
.stTextArea textarea {{ background: {INPUT_BG} !important; border: 1px solid {BORDER} !important; color: {TEXT} !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; }}
.stTextArea textarea:focus {{ border-color: {ACCENT} !important; box-shadow: 0 0 0 2px rgba(99,179,237,0.2) !important; }}
.stTextArea textarea::placeholder {{ color: {SUBTEXT} !important; opacity: 1 !important; }}
.stButton > button {{ background: linear-gradient(135deg,#2b6cb0,#3182ce) !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.92rem !important; padding: 0.6rem 1.6rem !important; transition: all 0.2s !important; }}
.stButton > button:hover {{ opacity: 0.88 !important; transform: translateY(-1px) !important; }}
.stButton > button p, .stButton > button span {{ color: #ffffff !important; }}
[data-testid="stFileUploader"] section {{ background: {INPUT_BG} !important; border: 1px dashed {BORDER} !important; border-radius: 10px !important; padding: 0.6rem 1rem !important; }}
[data-testid="stFileUploader"] *, [data-testid="stFileUploader"] p, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] div {{ color: {TEXT} !important; }}
[data-testid="stFileUploader"] button {{ background: linear-gradient(135deg,#2b6cb0,#3182ce) !important; color: #ffffff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }}
[data-testid="stFileUploader"] button span, [data-testid="stFileUploader"] button p {{ color: #ffffff !important; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; background: {CARD}; border-radius: 10px; padding: 4px; border: 1px solid {BORDER}; }}
.stTabs [data-baseweb="tab"] {{ color: {SUBTEXT} !important; font-weight: 500; border-radius: 8px; }}
.stTabs [aria-selected="true"] {{ background: {TAB_SEL} !important; color: {TEXT} !important; }}
.stCaption, [data-testid="stCaptionContainer"] p {{ color: {SUBTEXT} !important; }}
[data-testid="stDownloadButton"] button {{ background: linear-gradient(135deg,#2b6cb0,#3182ce) !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }}
[data-testid="stDownloadButton"] button p, [data-testid="stDownloadButton"] button span {{ color: #ffffff !important; }}
[data-testid="stAlert"] {{ border-radius: 10px !important; }}
hr {{ border-color: {DIVIDER} !important; margin: 1.5rem 0 !important; }}
.settings-panel {{ background: {PANEL_BG}; border: 2px solid #6366f1; border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 4px 20px rgba(99,102,241,0.2); }}
.settings-panel p, .settings-panel span, .settings-panel div, .settings-panel li {{ color: {PANEL_TEXT} !important; }}
.settings-panel h3 {{ color: {PANEL_H} !important; margin-bottom: 0.8rem; }}
.exp-badge {{ display: inline-block; padding: 0.25rem 0.8rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; font-family: 'Space Mono', monospace; margin-left: 0.5rem; }}
.exp-junior {{ background: rgba(72,187,120,0.15); border:1px solid rgba(72,187,120,0.4); color:#68d391; }}
.exp-mid    {{ background: rgba(99,179,237,0.15); border:1px solid rgba(99,179,237,0.4); color:#63b3ed; }}
.exp-senior {{ background: rgba(246,173,85,0.15); border:1px solid rgba(246,173,85,0.4); color:#f6ad55; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def render_pills(skill_list, style="blue"):
    if not skill_list:
        st.markdown(f"<span style='color:{SUBTEXT};font-size:0.85rem;'>None found</span>", unsafe_allow_html=True)
        return
    pills = "".join(f'<span class="pill pill-{style}">{s}</span>' for s in skill_list)
    st.markdown(f'<div class="pill-container">{pills}</div>', unsafe_allow_html=True)


def read_uploaded_file(f):
    raw = f.read()
    if f.type == "application/pdf":
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
    for enc in ("utf-8", "latin-1", "cp1252"):
        try: return raw.decode(enc)
        except: continue
    return raw.decode("utf-8", errors="replace")


def exp_badge(level):
    cls = {"Junior": "exp-junior", "Mid-Level": "exp-mid", "Senior": "exp-senior"}.get(level, "exp-mid")
    return f'<span class="exp-badge {cls}">{level}</span>'


def draw_radar(matched, missing):
    all_skills = matched + missing
    if not all_skills:
        return None
    display = (matched[:6] + missing[:6]) if len(all_skills) > 12 else all_skills
    n = max(len(display), 3)
    while len(display) < 3:
        display.append("")

    angles = [2 * math.pi * i / n for i in range(n)] + [0]
    matched_set = set(matched)
    values = [1.0 if s in matched_set else 0.0 for s in display] + [1.0 if display[0] in matched_set else 0.0]
    full   = [1.0] * (n + 1)

    CHART_BG   = "#1a1f2e" if dark else "#ffffff"
    CHART_GRID = "#2a3040" if dark else "#e2e8f0"
    CHART_TEXT = "#e2e8f0" if dark else "#111827"

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["", "", "", ""], color=CHART_TEXT)
    ax.yaxis.grid(True, color=CHART_GRID, linewidth=0.6, linestyle="--")
    ax.xaxis.grid(True, color=CHART_GRID, linewidth=0.6)
    ax.fill(angles, full, color="#2a3040" if dark else "#e2e8f0", alpha=0.3)
    ax.fill(angles, values, color="#3182ce", alpha=0.35)
    ax.plot(angles, values, color="#63b3ed", linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([])
    for i, s in enumerate(display):
        angle = angles[i]
        color = "#68d391" if s in matched_set else "#fc814a"
        label = s[:12] + "…" if len(s) > 13 else s
        ha = "center"
        x = math.cos(angle - math.pi / 2)
        if x > 0.1: ha = "left"
        if x < -0.1: ha = "right"
        ax.text(angle, 1.3, label, ha=ha, va="center", fontsize=7, color=color,
                fontweight="bold", transform=ax.transData)
    legend_handles = [
        mpatches.Patch(color="#3182ce", alpha=0.7, label="You have"),
        mpatches.Patch(color="#2a3040" if dark else "#e2e8f0", alpha=0.7, label="To learn"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", bbox_to_anchor=(1.4, 1.15),
              fontsize=8, framealpha=0.0, labelcolor=CHART_TEXT)
    ax.spines["polar"].set_color(CHART_GRID)
    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# NAV — Settings button
# ---------------------------------------------------------------------------
nav_l, nav_r = st.columns([10, 1])
with nav_r:
    if st.button("⚙️", key="settings_btn", help="Settings"):
        st.session_state["show_settings"] = not st.session_state["show_settings"]
        st.rerun()

# ---------------------------------------------------------------------------
# SETTINGS PANEL
# ---------------------------------------------------------------------------
if st.session_state["show_settings"]:
    st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
    sc1, sc2 = st.columns([2, 3])
    with sc1:
        st.markdown("### ⚙️ Settings")
        lbl = "☀️ Switch to Light Mode" if dark else "🌙 Switch to Dark Mode"
        if st.button(lbl, key="theme_toggle", use_container_width=True):
            st.session_state["dark_mode"] = not dark
            st.session_state["show_settings"] = False
            st.rerun()
    with sc2:
        st.markdown("### 📘 How to use")
        st.markdown("1. Choose a sample persona OR upload your own files\n"
                    "2. Click **Analyze Skill Gap**\n"
                    "3. Review Dashboard, Radar Chart, Skill Breakdown & Roadmap\n"
                    "4. Download your personalized report")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">🎯 ARTPARK CodeForge Hackathon</div>
    <div class="hero-title">AI Skill Gap Analyzer</div>
    <div class="hero-subtitle">
        Upload or paste your resume &amp; job description — get an instant skill gap report,
        radar chart, and a personalized dependency-ordered learning roadmap.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PERSONA SELECTOR
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">👤 Choose a Sample Persona</div>', unsafe_allow_html=True)
st.caption("Pick a domain to instantly load sample data — or skip and upload your own below.")

pc1, pc2, pc3 = st.columns([2, 2, 6])
with pc1:
    if st.button("💻 Tech: Data Analyst → ML Engineer", use_container_width=True, key="persona_tech"):
        st.session_state["sample_persona"] = "tech"
        st.session_state["resume_ta"]      = SAMPLE_RESUME_TECH
        st.session_state["jd_ta"]          = SAMPLE_JD_TECH
        st.rerun()
with pc2:
    if st.button("👥 HR: HR Manager → HR Director", use_container_width=True, key="persona_hr"):
        st.session_state["sample_persona"] = "hr"
        st.session_state["resume_ta"]      = SAMPLE_RESUME_HR
        st.session_state["jd_ta"]          = SAMPLE_JD_HR
        st.rerun()

# ---------------------------------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">📄 Input Documents</div>', unsafe_allow_html=True)

cl, cr = st.columns(2, gap="large")

with cl:
    st.markdown(f"<p style='font-weight:600;color:{TEXT};margin-bottom:0.4rem;'>📄 Your Resume</p>", unsafe_allow_html=True)
    uploaded_resume = st.file_uploader("Upload resume", type=["pdf", "txt"],
                                        key="resume_uploader", label_visibility="collapsed")
    if uploaded_resume is not None:
        fname = uploaded_resume.name
        if fname != st.session_state["_last_resume_file"]:
            try:
                st.session_state["resume_ta"]         = read_uploaded_file(uploaded_resume)
                st.session_state["_last_resume_file"] = fname
                st.success(f"✅ Loaded: **{fname}**")
            except Exception as e:
                st.error(f"Could not read file: {e}")
    st.text_area("Resume", placeholder="Or paste / type your resume here…",
                 height=260, label_visibility="collapsed", key="resume_ta")
    if st.button("📋 Load Sample Resume", key="load_resume_btn", use_container_width=True):
        st.session_state["_load_resume_flag"] = True
        st.rerun()

with cr:
    st.markdown(f"<p style='font-weight:600;color:{TEXT};margin-bottom:0.4rem;'>📋 Target Job Description</p>", unsafe_allow_html=True)
    uploaded_jd = st.file_uploader("Upload JD", type=["pdf", "txt"],
                                    key="jd_uploader", label_visibility="collapsed")
    if uploaded_jd is not None:
        fname = uploaded_jd.name
        if fname != st.session_state["_last_jd_file"]:
            try:
                st.session_state["jd_ta"]          = read_uploaded_file(uploaded_jd)
                st.session_state["_last_jd_file"]  = fname
                st.success(f"✅ Loaded: **{fname}**")
            except Exception as e:
                st.error(f"Could not read file: {e}")
    st.text_area("JD", placeholder="Or paste / type the job description here…",
                 height=260, label_visibility="collapsed", key="jd_ta")
    if st.button("📋 Load Sample JD", key="load_jd_btn", use_container_width=True):
        st.session_state["_load_jd_flag"] = True
        st.rerun()

st.markdown("")
go = st.button("🚀 Analyze Skill Gap", use_container_width=True, key="analyze_btn")

# ---------------------------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------------------------
if go:
    resume_val = st.session_state.get("resume_ta", "").strip()
    jd_val     = st.session_state.get("jd_ta", "").strip()

    if not resume_val or not jd_val:
        st.warning("⚠️ Please provide both a resume and a job description.")
        st.stop()

    with st.spinner("Analyzing your skills…"):
        r_skills   = extract_skills(resume_val)
        j_skills   = extract_skills(jd_val)
        r_conf     = extract_skills_with_confidence(resume_val)
        exp_level  = detect_experience_level(resume_val)
        gap        = compute_skill_gap(r_skills, j_skills)
        roadmap    = generate_roadmap(gap["missing"], r_skills)
        summary    = summarize_gap(gap, roadmap)
        time_saved = sum(ESTIMATED_HOURS.get(s, 20) for s in gap["matched"])

    st.markdown("---")
    match_pct = summary["match_percentage"]

    # ── DASHBOARD ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{SUBTEXT};font-size:0.9rem;margin-bottom:0.8rem;'>"
        f"Detected experience level: {exp_badge(exp_level)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="metric-value">{match_pct}%</div><div class="metric-label">Profile Match</div></div>
        <div class="metric-card"><div class="metric-value">{summary['skills_matched']}</div><div class="metric-label">Skills Matched</div></div>
        <div class="metric-card"><div class="metric-value">{summary['skills_missing']}</div><div class="metric-label">Skills to Learn</div></div>
        <div class="metric-card"><div class="metric-value">{summary['total_learn_hours']}h</div><div class="metric-label">Est. Study Hours</div></div>
        <div class="metric-card"><div class="metric-value">{summary['weeks_20h_per_week']}w</div><div class="metric-label">Weeks @ 20h/wk</div></div>
        <div class="metric-card-green"><div class="metric-value-green">{time_saved}h</div><div class="metric-label-green">⚡ Training Saved</div></div>
    </div>
    <p style="font-size:0.82rem;color:{SUBTEXT};margin-bottom:0.5rem;">
        ⚡ <strong style="color:#10b981;">{time_saved} hours</strong> of redundant training eliminated —
        this candidate already knows {len(gap['matched'])} required skills so onboarding skips those modules.
    </p>
    <div style="margin-bottom:1.5rem;">
        <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:{SUBTEXT};margin-bottom:4px;">
            <span>Profile fit for this role</span><span>{match_pct}%</span>
        </div>
        <div class="progress-bg"><div class="progress-fill" style="width:{match_pct}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── RADAR + SKILL TABS ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">🕸️ Skill Radar & Breakdown</div>', unsafe_allow_html=True)
    radar_col, tab_col = st.columns([2, 3], gap="large")

    with radar_col:
        st.caption("🟢 Green = you have it   🟠 Orange = to learn")
        fig = draw_radar(gap["matched"], gap["missing"])
        if fig:
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    with tab_col:
        t1, t2, t3, t4 = st.tabs([
            f"✅ Matched ({len(gap['matched'])})",
            f"❌ Missing ({len(gap['missing'])})",
            f"⭐ Bonus ({len(gap['extra'])})",
            "📋 All Extracted",
        ])
        with t1:
            st.caption("Skills on your resume that the role requires")
            render_pills(gap["matched"], "green")
        with t2:
            st.caption("Skills the role needs that are missing from your resume")
            render_pills(gap["missing"], "red")
        with t3:
            st.caption("Extra skills you have beyond what is required")
            render_pills(gap["extra"], "gray")
        with t4:
            ca, cb = st.columns(2)
            with ca:
                st.markdown(f"<p style='font-weight:600;color:{TEXT};'>From Resume</p>", unsafe_allow_html=True)
                render_pills(r_skills, "blue")
                if r_conf:
                    st.markdown(f"<p style='font-size:0.78rem;color:{SUBTEXT};margin-top:0.5rem;'>Confidence scores:</p>", unsafe_allow_html=True)
                    for sk, conf in sorted(r_conf.items(), key=lambda x: -x[1]):
                        pct = int(conf * 100)
                        st.markdown(
                            f"<div style='display:flex;align-items:center;gap:0.5rem;margin-bottom:4px;font-size:0.8rem;color:{TEXT};'>"
                            f"<span style='min-width:140px;'>{sk}</span>"
                            f"<div class='conf-bar-bg' style='flex:1;'><div class='conf-bar-fill' style='width:{pct}%;'></div></div>"
                            f"<span style='min-width:32px;text-align:right;color:{SUBTEXT};'>{pct}%</span></div>",
                            unsafe_allow_html=True,
                        )
            with cb:
                st.markdown(f"<p style='font-weight:600;color:{TEXT};'>From Job Description</p>", unsafe_allow_html=True)
                render_pills(j_skills, "blue")

    # ── ROADMAP ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🗺️ Personalized Learning Roadmap</div>', unsafe_allow_html=True)
    if not roadmap:
        st.success("🎉 Your profile already covers all the required skills!")
    else:
        st.markdown(
            f"<p style='color:{SUBTEXT};font-size:0.9rem;margin-bottom:1rem;'>"
            f"Your <strong style='color:{ACCENT};'>{len(roadmap)}-step</strong> roadmap ordered by prerequisites. "
            f"Estimated total: <strong style='color:{ACCENT};'>{summary['total_learn_hours']} hours</strong>.</p>",
            unsafe_allow_html=True,
        )
        for step in roadmap:
            st.markdown(
                f"<div style='background:{CARD};border:1px solid {BORDER};border-left:4px solid {ACCENT};"
                f"border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:0.75rem;'>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:0.7rem;color:{STEP_NUM_C};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem;'>STEP {step['step']} OF {len(roadmap)}</div>"
                f"<div style='font-size:1.15rem;font-weight:700;color:{TEXT};margin-bottom:0.3rem;'>{step['skill']}</div>"
                f"<div style='font-size:0.82rem;color:{SUBTEXT};'>{step['priority']} &nbsp;·&nbsp; ⏱ ~{step['hours']} hours</div>",
                unsafe_allow_html=True,
            )
            if step["prereqs_ok"]:
                st.success(f"✓ You already know: {', '.join(step['prereqs_ok'])}")
            if step["prereqs_needed"]:
                st.warning(f"⚠ Complete these first: {', '.join(step['prereqs_needed'])}")
            st.markdown(f"<hr style='border:none;border-top:1px solid {DIVIDER};margin:0.6rem 0;'>", unsafe_allow_html=True)
            st.markdown(f"💡 **Reasoning:** {step['reasoning']}")
            st.markdown(
                f"<p style='font-size:0.82rem;color:{ACCENT};margin-top:0.3rem;margin-bottom:0;'>"
                f"📚 <strong style='color:{ACCENT};'>Free Resources:</strong> {step['resources']}</p>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    # ── EXPORT ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📥 Export Your Roadmap</div>', unsafe_allow_html=True)
    if roadmap:
        lines = [
            "=" * 60, "AI SKILL GAP ANALYZER — PERSONALIZED ROADMAP REPORT", "=" * 60, "",
            f"Experience Level:        {exp_level}",
            f"Profile Match:           {match_pct}%",
            f"Skills Matched:          {summary['skills_matched']}",
            f"Skills to Learn:         {summary['skills_missing']}",
            f"Training Hours Saved:    {time_saved}h (redundant modules eliminated)",
            f"Est. Study Hours Needed: {summary['total_learn_hours']}h",
            f"Weeks @ 20h/wk:         {summary['weeks_20h_per_week']}", "",
            "MATCHED SKILLS:", ", ".join(gap["matched"]) or "None", "",
            "MISSING SKILLS:", ", ".join(gap["missing"]) or "None", "",
            "=" * 60, "LEARNING ROADMAP", "=" * 60,
        ]
        for s in roadmap:
            lines += [
                "", f"Step {s['step']}: {s['skill']}",
                f"  Priority : {s['priority']}", f"  Hours    : ~{s['hours']}",
                f"  Reasoning: {s['reasoning']}",
                f"  Resources: {s['resources']}",
            ]
        st.download_button(
            label="⬇️ Download Roadmap (.txt)",
            data="\n".join(lines),
            file_name="skill_gap_roadmap.txt",
            mime="text/plain",
        )

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:{SUBTEXT};font-size:0.78rem;'>"
    "AI Skill Gap Analyzer · ARTPARK CodeForge Hackathon · Built with Streamlit</p>",
    unsafe_allow_html=True,
)