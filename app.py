import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.pdf_parser import extract_text
from src.skill_extractor import extract_skills, get_skill_overlap
from src.embeddings import compute_similarity, rank_resumes

st.set_page_config(
    page_title="Resume Screener",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Resume Screening NLP System")
st.markdown("Compare resumes to a job description using embeddings, similarity scoring, and skill extraction.")

# ── Sidebar: mode ──────────────────────────────────────────────────────────────
mode = st.sidebar.radio("Mode", ["Single Resume", "Batch Ranking"])
st.sidebar.markdown("---")
st.sidebar.markdown("**How it works**")
st.sidebar.markdown(
    "- Embeddings via `all-MiniLM-L6-v2`\n"
    "- Cosine similarity scoring\n"
    "- Rule-based skill extraction\n"
    "- Category-level skill gap analysis"
)

# ── Job Description ─────────────────────────────────────────────────────────────
st.subheader("1. Job Description")
jd_text = st.text_area(
    "Paste the job description here",
    height=200,
    placeholder="We are looking for a Machine Learning Engineer with experience in Python, PyTorch, NLP...",
)

st.subheader("2. Resume(s)")

# ── Single mode ────────────────────────────────────────────────────────────────
if mode == "Single Resume":
    uploaded = st.file_uploader("Upload resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    if uploaded and jd_text.strip():
        with st.spinner("Analysing resume…"):
            resume_text = extract_text(uploaded, uploaded.name)
            similarity = compute_similarity(resume_text, jd_text)
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(jd_text)
            overlap = get_skill_overlap(resume_skills, jd_skills)

        st.markdown("---")
        st.subheader("Results")

        # ── Score gauge ────────────────────────────────────────────────────────
        pct = round(similarity * 100, 1)
        color = "#2ecc71" if pct >= 70 else "#f39c12" if pct >= 45 else "#e74c3c"

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct,
                number={"suffix": "%", "font": {"size": 36}},
                title={"text": "Match Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": color},
                    "steps": [
                        {"range": [0, 45], "color": "#fdecea"},
                        {"range": [45, 70], "color": "#fef9e7"},
                        {"range": [70, 100], "color": "#eafaf1"},
                    ],
                    "threshold": {"line": {"color": "black", "width": 2}, "value": 70},
                },
            ))
            fig.update_layout(height=280, margin=dict(t=40, b=0, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            skill_pct = round(overlap["match_rate"] * 100, 1)
            st.metric("Skill Match Rate", f"{skill_pct}%")
            st.metric("Matched Skills", len(overlap["matched"]))
            st.metric("Missing Skills", len(overlap["missing"]))

        with col3:
            verdict = (
                "Strong Match ✅" if pct >= 70
                else "Potential Match ⚠️" if pct >= 45
                else "Weak Match ❌"
            )
            st.markdown(f"### Verdict: {verdict}")
            st.markdown(f"Semantic similarity between this resume and the job description is **{pct}%**.")

        # ── Skill breakdown ────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("Skill Analysis")

        tab1, tab2, tab3 = st.tabs(["Matched Skills", "Missing Skills", "Resume Skills"])

        with tab1:
            if overlap["matched"]:
                skills_html = " ".join(
                    f'<span style="background:#d5f5e3;padding:4px 10px;border-radius:20px;margin:3px;display:inline-block;font-size:13px">{s}</span>'
                    for s in overlap["matched"]
                )
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.info("No skill overlap detected.")

        with tab2:
            if overlap["missing"]:
                skills_html = " ".join(
                    f'<span style="background:#fdecea;padding:4px 10px;border-radius:20px;margin:3px;display:inline-block;font-size:13px">{s}</span>'
                    for s in overlap["missing"]
                )
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.success("Resume covers all skills mentioned in the job description!")

        with tab3:
            for category, skills in resume_skills.items():
                if skills:
                    st.markdown(f"**{category.replace('_', ' ').title()}**")
                    skills_html = " ".join(
                        f'<span style="background:#eaf2ff;padding:4px 10px;border-radius:20px;margin:3px;display:inline-block;font-size:13px">{s}</span>'
                        for s in skills
                    )
                    st.markdown(skills_html, unsafe_allow_html=True)

        # ── Category radar chart ───────────────────────────────────────────────
        from data.skills_db import SKILLS as SKILL_CATS

        jd_cat_counts = {cat: len(jd_skills.get(cat, [])) for cat in SKILL_CATS}
        resume_cat_counts = {cat: len(resume_skills.get(cat, [])) for cat in SKILL_CATS}
        cats = list(SKILL_CATS.keys())
        jd_vals = [min(jd_cat_counts[c], 10) for c in cats]
        resume_vals = [min(resume_cat_counts[c], 10) for c in cats]
        labels = [c.replace("_", " ").title() for c in cats]

        if any(jd_vals) or any(resume_vals):
            st.markdown("---")
            st.subheader("Skill Category Coverage")
            fig2 = go.Figure()
            fig2.add_trace(go.Scatterpolar(r=jd_vals + [jd_vals[0]], theta=labels + [labels[0]], fill="toself", name="Job Description", opacity=0.5))
            fig2.add_trace(go.Scatterpolar(r=resume_vals + [resume_vals[0]], theta=labels + [labels[0]], fill="toself", name="Resume", opacity=0.5))
            fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=400)
            st.plotly_chart(fig2, use_container_width=True)

        # ── Extracted text preview ─────────────────────────────────────────────
        with st.expander("View extracted resume text"):
            st.text(resume_text[:3000] + ("…" if len(resume_text) > 3000 else ""))

    elif uploaded and not jd_text.strip():
        st.warning("Please paste a job description above.")
    elif jd_text.strip() and not uploaded:
        st.info("Upload a resume to get started.")

# ── Batch mode ──────────────────────────────────────────────────────────────────
else:
    uploaded_files = st.file_uploader(
        "Upload multiple resumes (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files and jd_text.strip():
        with st.spinner(f"Analysing {len(uploaded_files)} resumes…"):
            resumes = []
            for f in uploaded_files:
                text = extract_text(f, f.name)
                skills = extract_skills(text)
                resumes.append({"name": f.name, "text": text, "skills": skills})

            ranked = rank_resumes(resumes, jd_text)
            jd_skills = extract_skills(jd_text)

        st.markdown("---")
        st.subheader(f"Ranking — {len(ranked)} Resumes")

        # ── Leaderboard table ──────────────────────────────────────────────────
        rows = []
        for i, r in enumerate(ranked, 1):
            overlap = get_skill_overlap(r["skills"], jd_skills)
            rows.append({
                "Rank": i,
                "Resume": r["name"],
                "Similarity %": r["similarity"],
                "Skill Match %": round(overlap["match_rate"] * 100, 1),
                "Matched Skills": len(overlap["matched"]),
                "Missing Skills": len(overlap["missing"]),
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Bar chart ──────────────────────────────────────────────────────────
        fig = px.bar(
            df,
            x="Resume",
            y="Similarity %",
            color="Similarity %",
            color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
            range_color=[0, 100],
            title="Resume Similarity Scores",
            text="Similarity %",
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        # ── Top candidate deep-dive ────────────────────────────────────────────
        st.markdown("---")
        st.subheader(f"Top Candidate: {ranked[0]['name']}")
        top_overlap = get_skill_overlap(ranked[0]["skills"], jd_skills)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Matched Skills**")
            if top_overlap["matched"]:
                skills_html = " ".join(
                    f'<span style="background:#d5f5e3;padding:4px 10px;border-radius:20px;margin:3px;display:inline-block;font-size:13px">{s}</span>'
                    for s in top_overlap["matched"]
                )
                st.markdown(skills_html, unsafe_allow_html=True)
        with col2:
            st.markdown("**Missing Skills**")
            if top_overlap["missing"]:
                skills_html = " ".join(
                    f'<span style="background:#fdecea;padding:4px 10px;border-radius:20px;margin:3px;display:inline-block;font-size:13px">{s}</span>'
                    for s in top_overlap["missing"]
                )
                st.markdown(skills_html, unsafe_allow_html=True)

    elif uploaded_files and not jd_text.strip():
        st.warning("Please paste a job description above.")
    elif jd_text.strip() and not uploaded_files:
        st.info("Upload one or more resumes to get started.")
