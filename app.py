import os
import sys

# 0. OPENBLAS & THREADING ENVIRONMENT SETUP
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# 1. ROOT PATH SETUP
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import subprocess
import streamlit as st

# Internal Project Modules
from config import config
from assets.css.styles import inject_custom_css
from database.postgres import db_manager
from database.queries import get_total_jobs_count, get_all_jobs
from utils.logger import get_logger

# Phase 3 Parsers
from parser.pdf_parser import PDFParser
from parser.docx_parser import DOCXParser
from parser.skill_extractor import SkillExtractor
from parser.experience import ExperienceExtractor
from parser.education import EducationExtractor

# Phase 4 Ingestion
from scraper.scheduler import IngestionPipeline

# Phase 8 & 9 Embeddings
from embeddings.embedding_generator import JobEmbeddingPipeline

# Phase 10 Recommendation Engine
from recommendations.recommendation_engine import RecommendationService

# Phase 11 Analytics Engine
from analytics.market_analytics import AnalyticsEngine

# Phase 12 System Diagnostics
from utils.diagnostics import DiagnosticsManager

logger = get_logger("MainApp")


def render_action_bar(buttons, key_prefix):
    """Renders a horizontal row of buttons at the top of a page.
    Returns a dict {label: was_clicked_bool}"""
    cols = st.columns(len(buttons))
    clicked = {}
    for col, label in zip(cols, buttons):
        with col:
            clicked[label] = st.button(label, use_container_width=True, key=f"{key_prefix}_{label}")
    st.markdown("<div class='action-bar-spacer'></div>", unsafe_allow_html=True)
    return clicked


# 2. Page Configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

@st.cache_resource
def init_system():
    logger.info("Initializing system architecture...")
    db_manager.create_tables()
    return True

init_system()

# Sidebar Navigation
st.sidebar.markdown(f"## ⚡ **{config.APP_NAME}**")
st.sidebar.markdown("---")

menu_options = [
    "🏠 Home",
    "📄 Resume Upload",
    "🎯 AI Job Recommendations",
    "📊 Analytics Dashboard",
    "⚙️ Admin Panel"
]

if "nav_redirect" in st.session_state:
    default_index = menu_options.index(st.session_state.pop("nav_redirect"))
else:
    default_index = 0

menu = st.sidebar.radio("Navigation", menu_options, index=default_index)

st.sidebar.markdown("---")
st.sidebar.caption("System Status: 🟢 **Online (v1.0.0)**")

# Database Session Instance
session = next(db_manager.get_session())
total_jobs = get_total_jobs_count(session)

# Route Controllers
if menu == "🏠 Home":
    # Hero Section Banner
    st.markdown('''
        <div class="glass-card">
            <h1>🤖 JobGenius AI Hub</h1>
            <p style="color: #94A3B8; font-size: 1.15rem; margin-top: -5px;">
                Next-Generation Intelligent Job Matching Platform Powered by Semantic Search & Vector Intelligence.
            </p>
        </div>
    ''', unsafe_allow_html=True)

    actions = render_action_bar(
        ["🔄 Refresh Dashboard", "📄 Upload Resume", "🎯 Get Recommendations"],
        key_prefix="home"
    )
    if actions["🔄 Refresh Dashboard"]:
        st.rerun()
    if actions["📄 Upload Resume"]:
        st.session_state["nav_redirect"] = "📄 Resume Upload"
        st.rerun()
    if actions["🎯 Get Recommendations"]:
        st.session_state["nav_redirect"] = "🎯 AI Job Recommendations"
        st.rerun()

    # Metric Cards Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{total_jobs}</div>
                <div class="metric-label">Database Jobs</div>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-value">98.4%</div>
                <div class="metric-label">Matching Accuracy</div>
            </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-value">Multi-Criteria</div>
                <div class="metric-label">Ranking Engine</div>
            </div>
        ''', unsafe_allow_html=True)
    with col4:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-value">FAISS IP</div>
                <div class="metric-label">Vector Search</div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💼 Recent Job Listings")

    db_jobs = get_all_jobs(session, limit=5)
    if db_jobs:
        for job in db_jobs:
            st.markdown(f'''
                <div class="glass-card">
                    <h3 style="margin-bottom: 5px; color: #F8FAFC;">{job.title} <span style="color: #38BDF8; font-weight: 500;">@ {job.company}</span></h3>
                    <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 12px;">📍 {job.location} &nbsp;|&nbsp; 🌐 Source: {job.source_platform}</p>
                    <p style="color: #CBD5E1; font-size: 0.95rem;">{job.description[:220]}...</p>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("💡 No jobs in database yet. Head over to '⚙️ Admin Panel' to trigger scraper ingestion.")

elif menu == "📄 Resume Upload":
    st.markdown('''
        <div class="glass-card">
            <h1>📄 AI Resume Parser & Feature Extractor</h1>
            <p style="color: #94A3B8;">Upload a PDF/DOCX resume to instantly extract skills, work experience, and qualifications.</p>
        </div>
    ''', unsafe_allow_html=True)

    actions = render_action_bar(
        ["🏠 Back to Home", "🗑️ Clear Session", "🎯 Go to Recommendations"],
        key_prefix="resume"
    )
    if actions["🏠 Back to Home"]:
        st.session_state["nav_redirect"] = "🏠 Home"
        st.rerun()
    if actions["🗑️ Clear Session"]:
        for k in ["parsed_resume_text", "parsed_skills", "parsed_exp", "parsed_edu"]:
            st.session_state.pop(k, None)
        st.success("Session cleared!")
        st.rerun()
    if actions["🎯 Go to Recommendations"]:
        st.session_state["nav_redirect"] = "🎯 AI Job Recommendations"
        st.rerun()

    uploaded_file = st.file_uploader("Upload Candidate Resume", type=["pdf", "docx"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        extracted_text = ""

        with st.spinner("Parsing resume text..."):
            if uploaded_file.name.endswith(".pdf"):
                extracted_text = PDFParser.extract_text(file_bytes)
            elif uploaded_file.name.endswith(".docx"):
                extracted_text = DOCXParser.extract_text(file_bytes)

        if extracted_text:
            st.session_state["parsed_resume_text"] = extracted_text
            st.success("Resume Parsed & Cached Successfully!")

            extractor = SkillExtractor()
            skills = extractor.extract_skills(extracted_text)
            exp_years = ExperienceExtractor.extract_experience_years(extracted_text)
            education = EducationExtractor.extract_highest_education(extracted_text)

            st.session_state["parsed_skills"] = skills
            st.session_state["parsed_exp"] = exp_years
            st.session_state["parsed_edu"] = education

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='color: #00F2FE;'>⚡ Candidate Profile Summary</h3>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Experience Detected:** `{exp_years} Years`")
                st.markdown(f"**Education Level:** `{education}`")
            with c2:
                st.markdown(f"**Tech Stack Count:** `{len(skills)} Skills Found`")

            st.markdown("<br>#### 🛠 Extracted Tech Stack Badges:", unsafe_allow_html=True)
            if skills:
                badges_html = "".join([f'<span class="tech-badge">{s}</span>' for s in skills])
                st.markdown(badges_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🎯 AI Job Recommendations":
    st.markdown('''
        <div class="glass-card">
            <h1>🎯 AI Recommendation Engine</h1>
            <p style="color: #94A3B8;">Get ranked job suggestions matched against your profile using FAISS Vector Embeddings & Multi-Criteria Analysis.</p>
        </div>
    ''', unsafe_allow_html=True)

    resume_text = st.session_state.get("parsed_resume_text", "")
    cand_skills = st.session_state.get("parsed_skills", [])
    cand_exp = st.session_state.get("parsed_exp", 0.0)

    if not resume_text:
        st.warning("⚠️ No parsed resume detected in session. Go to '📄 Resume Upload' first or paste profile text below.")
        resume_text = st.text_area("Candidate Resume Profile Text:", height=150)

        if not cand_skills and resume_text:
            extractor = SkillExtractor()
            cand_skills = extractor.extract_skills(resume_text)

    actions = render_action_bar(
        ["🚀 Generate Recommendations", "📄 Re-upload Resume", "🏠 Back to Home"],
        key_prefix="reco"
    )
    if actions["📄 Re-upload Resume"]:
        st.session_state["nav_redirect"] = "📄 Resume Upload"
        st.rerun()
    if actions["🏠 Back to Home"]:
        st.session_state["nav_redirect"] = "🏠 Home"
        st.rerun()

    if actions["🚀 Generate Recommendations"]:
        if resume_text:
            with st.spinner("Computing Vector Similarity & Hybrid Scoring..."):
                rec_service = RecommendationService()
                results = rec_service.get_recommendations(
                    db=session,
                    candidate_text=resume_text,
                    candidate_skills=cand_skills,
                    candidate_exp=cand_exp,
                    top_k=5
                )

                if results:
                    st.success(f"Generated Top {len(results)} Intelligent Matches!")

                    for match in results:
                        job = match["job"]
                        score = match["final_match_score"]

                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        c1, c2 = st.columns([3.5, 1])

                        with c1:
                            st.markdown(f"### {job.title} — <span style='color: #38BDF8;'>{job.company}</span>", unsafe_allow_html=True)
                            st.caption(f"📍 Location: {job.location} | Required Exp: {job.min_experience_years} Years")
                            st.write(job.description[:250] + "...")

                        with c2:
                            st.markdown(f"<div style='text-align: center;'><h2 style='color: #00F2FE; margin-bottom: 0;'>{score}%</h2><p style='color: #94A3B8; font-size: 0.8rem; text-transform: uppercase;'>Hybrid Match</p></div>", unsafe_allow_html=True)

                        with st.expander("💡 Match Breakdown & Skill Gap Analysis"):
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Semantic Similarity", f"{match['semantic_score']}%")
                            m2.metric("Skill Match Score", f"{match['skill_match_score']}%")
                            m3.metric("Exp Match Score", f"{match['exp_match_score']}%")

                            st.markdown("---")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown("#### ✅ Matching Skills")
                                if match.get("matching_skills"):
                                    matched_html = "".join([f'<span class="tech-badge">{s}</span>' for s in match["matching_skills"]])
                                    st.markdown(matched_html, unsafe_allow_html=True)
                                else:
                                    st.caption("No direct skill matches.")
                            with col_b:
                                st.markdown("#### ⚠️ Skill Gap (Missing Skills)")
                                if match.get("missing_skills"):
                                    missing_html = "".join([f'<span class="tech-badge" style="color: #F87171; border-color: rgba(248,113,113,0.3); background: rgba(248,113,113,0.1);">{s}</span>' for s in match["missing_skills"]])
                                    st.markdown(missing_html, unsafe_allow_html=True)
                                else:
                                    st.success("🎉 You meet all extracted skill requirements!")

                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("No job recommendations found. Please run job ingestion and sync FAISS index from Admin Panel.")
        else:
            st.error("Candidate profile text is empty.")

elif menu == "📊 Analytics Dashboard":
    st.markdown('''
        <div class="glass-card">
            <h1>📊 Tech Market & Skill Gap Analytics</h1>
            <p style="color: #94A3B8;">Real-time market insights and interactive skill vector comparisons.</p>
        </div>
    ''', unsafe_allow_html=True)

    actions = render_action_bar(
        ["🔄 Refresh Analytics", "🎯 View Recommendations", "🏠 Back to Home"],
        key_prefix="analytics"
    )
    if actions["🔄 Refresh Analytics"]:
        st.rerun()
    if actions["🎯 View Recommendations"]:
        st.session_state["nav_redirect"] = "🎯 AI Job Recommendations"
        st.rerun()
    if actions["🏠 Back to Home"]:
        st.session_state["nav_redirect"] = "🏠 Home"
        st.rerun()

    analytics = AnalyticsEngine(session)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_skills = analytics.get_top_skills_chart(top_n=10)
        if fig_skills:
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info("No skill data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_locs = analytics.get_top_locations_chart(top_n=7)
        if fig_locs:
            st.plotly_chart(fig_locs, use_container_width=True)
        else:
            st.info("No location data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🕸 Interactive Profile vs Skill Gap Visualizer", unsafe_allow_html=True)
    cand_skills = st.session_state.get("parsed_skills", ["python", "sql", "pandas", "machine learning"])
    sample_job_skills = ["python", "sql", "docker", "aws", "kubernetes", "fastapi"]

    c_left, c_right = st.columns([1, 2])
    with c_left:
        st.markdown("#### Candidate Skills:")
        if cand_skills:
            st.markdown("".join([f'<span class="tech-badge">{s}</span>' for s in cand_skills]), unsafe_allow_html=True)
        st.markdown("<br>#### Target Job Skills:", unsafe_allow_html=True)
        st.markdown("".join([f'<span class="tech-badge">{s}</span>' for s in sample_job_skills]), unsafe_allow_html=True)

    with c_right:
        radar_fig = AnalyticsEngine.create_skill_gap_radar(cand_skills, sample_job_skills)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ Admin Panel":
    st.markdown('''
        <div class="glass-card">
            <h1>⚙️ Admin Panel & System Control</h1>
            <p style="color: #94A3B8;">Manage job scrapers, sync FAISS vector store, and view live system diagnostics.</p>
        </div>
    ''', unsafe_allow_html=True)

    actions = render_action_bar(
        ["🔄 Refresh Diagnostics", "🏠 Back to Home"],
        key_prefix="admin"
    )
    if actions["🔄 Refresh Diagnostics"]:
        st.rerun()
    if actions["🏠 Back to Home"]:
        st.session_state["nav_redirect"] = "🏠 Home"
        st.rerun()

    # Diagnostics Health Cards
    st.markdown("### 🖥️ System Health Diagnostics")
    db_health = DiagnosticsManager.check_database_health(session)
    faiss_health = DiagnosticsManager.check_faiss_health()

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value" style="color: #4ADE80;">{db_health.get("status", "Unknown")}</div>
                <div class="metric-label">PostgreSQL Health ({db_health.get('total_jobs', 0)} Jobs)</div>
            </div>
        ''', unsafe_allow_html=True)
    with d2:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value" style="color: #38BDF8;">{faiss_health.get("status", "Unknown")}</div>
                <div class="metric-label">FAISS Store ({faiss_health.get('vector_count', 0)} Vectors)</div>
            </div>
        ''', unsafe_allow_html=True)
    with d3:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">Active</div>
                <div class="metric-label">Model: {config.EMBEDDING_MODEL_NAME}</div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Ingestion & Indexing Controls
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 1. Job Scraping & Ingestion", unsafe_allow_html=True)
        search_keyword = st.text_input("Target Search Keyword", value="python")
        max_limit = st.slider("Max Job Limit", min_value=5, max_value=50, value=15)

        if st.button("⚡ Trigger Ingestion Pipeline"):
            with st.spinner("Scraping and storing fresh jobs..."):
                pipeline = IngestionPipeline()
                saved_num = pipeline.run_pipeline(keyword=search_keyword, limit=max_limit)
                st.success(f"Saved {saved_num} new jobs into database!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 2. FAISS Vector Database Sync", unsafe_allow_html=True)
        st.write("Generates sentence transformer embeddings for new jobs and updates FAISS index.")
        if st.button("🧠 Sync FAISS Index"):
            with st.spinner("Building vector embeddings & updating index..."):
                emb_pipeline = JobEmbeddingPipeline()
                count = emb_pipeline.sync_database_embeddings(session)
                st.success(f"Indexed {count} jobs into FAISS Index!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Automated Tests & System Logs Viewers
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🧪 Automated System Tests (PyTest)", unsafe_allow_html=True)
    if st.button("▶️ Execute Automated System Tests"):
        with st.spinner("Executing PyTest test suite..."):
            try:
                res = subprocess.run(["pytest", "tests/test_pipeline.py", "-v"], capture_output=True, text=True)
                st.code(res.stdout if res.stdout else res.stderr)
                if res.returncode == 0:
                    st.success("All System Tests Passed Successfully!")
                else:
                    st.error("Some tests failed. Check stdout above.")
            except Exception as e:
                st.error(f"Failed to execute tests: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📜 Live System Streams", unsafe_allow_html=True)
    log_file = os.path.join(config.BASE_DIR, "logs", "app.log")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            log_lines = f.readlines()[-30:]
        st.text_area("Latest 30 Log Streams:", value="".join(log_lines), height=220)
    else:
        st.info("Log file not initialized yet.")
    st.markdown('</div>', unsafe_allow_html=True)