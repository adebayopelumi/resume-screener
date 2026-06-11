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
    page_title="ResumeInt — NLP Screener",
    page_icon="▸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');

*, *::before, *::after {
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
}

/* Base */
html, body, .stApp {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* Grid overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* Main block container */
.block-container {
    padding: 48px 60px !important;
    max-width: 1400px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #00ff41; border-radius: 0; }

/* Headings */
h1, h2, h3 { color: #ffffff !important; letter-spacing: -0.5px; }

/* Divider */
hr { border: none; border-top: 1px solid #111111 !important; margin: 32px 0; }

/* ── Inputs ── */
.stTextArea textarea {
    background-color: #050505 !important;
    color: #00ff41 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 2px !important;
    resize: vertical !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
    caret-color: #00ff41;
}
.stTextArea textarea:focus {
    border-color: #00ff41 !important;
    box-shadow: 0 0 0 1px #00ff4122 !important;
}
.stTextArea textarea::placeholder { color: #2a2a2a !important; }
.stTextArea > label, .stTextInput > label, .stFileUploader > label {
    color: #555555 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    background-color: #050505 !important;
    border: 1px dashed #1e1e1e !important;
    border-radius: 2px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover { border-color: #00ff41 !important; }
[data-testid="stFileUploadDropzone"] * { color: #555555 !important; }
[data-testid="stFileUploadDropzone"] small { color: #333333 !important; }

/* Buttons */
.stButton > button {
    background-color: transparent !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
    border-radius: 2px !important;
    font-size: 12px !important;
    padding: 8px 20px !important;
    transition: all 0.15s;
}
.stButton > button:hover {
    background-color: #00ff41 !important;
    color: #000000 !important;
}

/* Radio */
.stRadio > label { color: #555555 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1.5px; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #888888 !important; font-size: 13px !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    border-bottom: 1px solid #111111;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    color: #333333 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 10px 20px !important;
    background: transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #00ff41 !important;
    border-bottom: 1px solid #00ff41 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent; padding-top: 20px; }

/* Metrics */
[data-testid="metric-container"] {
    background-color: #050505;
    border: 1px solid #111111;
    border-left: 2px solid #00ff41;
    padding: 20px 24px !important;
    border-radius: 2px;
}
[data-testid="metric-container"] label {
    color: #444444 !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00ff41 !important;
    font-size: 32px !important;
    font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #444444 !important; }

/* Dataframe */
[data-testid="stDataFrame"] iframe { border: 1px solid #111111 !important; }

/* Expander */
details { border: 1px solid #111111 !important; border-radius: 2px !important; }
details > summary {
    color: #444444 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 12px 16px !important;
    background: #050505 !important;
}
details[open] > summary { color: #888888 !important; border-bottom: 1px solid #111111; }
.streamlit-expanderContent { background: #050505 !important; padding: 16px !important; }

/* Spinner */
[data-testid="stSpinner"] > div { border-top-color: #00ff41 !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #030303 !important;
    border-right: 1px solid #111111 !important;
}
[data-testid="stSidebar"] * { color: #555555 !important; }
[data-testid="stSidebar"] hr { border-color: #111111 !important; }

/* Alert boxes */
[data-baseweb="notification"] {
    background-color: #050505 !important;
    border: 1px solid #111111 !important;
    border-left: 2px solid #00ff41 !important;
    border-radius: 2px !important;
    color: #555555 !important;
}

/* Animations */
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

/* Custom components */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 1px solid #1a1a1a;
    padding: 5px 14px;
    border-radius: 2px;
    font-size: 10px;
    color: #555555;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.badge .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #00ff41;
    box-shadow: 0 0 6px #00ff41;
    flex-shrink: 0;
}
.cursor {
    color: #00ff41;
    animation: blink 1s infinite;
    font-weight: 700;
}
.hero-title {
    font-size: 52px;
    font-weight: 700;
    line-height: 1.1;
    margin: 0 0 12px 0;
    letter-spacing: -1px;
}
.hero-sub {
    font-size: 14px;
    color: #444444;
    line-height: 1.7;
    margin-bottom: 32px;
    max-width: 520px;
}
.stat-row {
    display: flex;
    gap: 40px;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #111111;
}
.stat-block { text-align: left; }
.stat-num { font-size: 28px; font-weight: 700; color: #ffffff; }
.stat-lbl { font-size: 10px; color: #333333; text-transform: uppercase; letter-spacing: 2px; margin-top: 2px; }
.section-label {
    font-size: 10px;
    color: #333333;
    text-transform: uppercase;
    letter-spacing: 3px;
    padding-left: 12px;
    border-left: 2px solid #00ff41;
    margin-bottom: 16px;
    margin-top: 32px;
}
.skill-green {
    display: inline-block;
    background: #001a0a;
    color: #00ff41;
    border: 1px solid #00ff4144;
    padding: 3px 12px;
    border-radius: 2px;
    margin: 3px;
    font-size: 12px;
}
.skill-red {
    display: inline-block;
    background: #1a0000;
    color: #ff4141;
    border: 1px solid #ff414144;
    padding: 3px 12px;
    border-radius: 2px;
    margin: 3px;
    font-size: 12px;
}
.skill-gray {
    display: inline-block;
    background: #0a0a0a;
    color: #555555;
    border: 1px solid #1a1a1a;
    padding: 3px 12px;
    border-radius: 2px;
    margin: 3px;
    font-size: 12px;
}
.verdict-green {
    border: 1px solid #00ff4144;
    background: #001a0a;
    color: #00ff41;
    padding: 16px 20px;
    border-radius: 2px;
    font-size: 14px;
    font-weight: 600;
}
.verdict-yellow {
    border: 1px solid #ffaa0044;
    background: #1a1000;
    color: #ffaa00;
    padding: 16px 20px;
    border-radius: 2px;
    font-size: 14px;
    font-weight: 600;
}
.verdict-red {
    border: 1px solid #ff414144;
    background: #1a0000;
    color: #ff4141;
    padding: 16px 20px;
    border-radius: 2px;
    font-size: 14px;
    font-weight: 600;
}
.rank-badge {
    display: inline-block;
    width: 24px; height: 24px;
    line-height: 24px;
    text-align: center;
    border: 1px solid #00ff41;
    color: #00ff41;
    font-size: 11px;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

PLOTLY_BASE = dict(
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(family="JetBrains Mono, Courier New, monospace", color="#888888", size=11),
    margin=dict(t=40, b=20, l=20, r=20),
)

# ── Sidebar mode selector ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label" style="margin-top:0">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("", ["Single Resume", "Batch Ranking"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="section-label" style="margin-top:0">Stack</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px; color:#333; line-height:2.2">
    ▸ all-MiniLM-L6-v2<br>
    ▸ Cosine similarity<br>
    ▸ Regex skill extract<br>
    ▸ 100+ skill index<br>
    ▸ PDF / DOCX / TXT
    </div>
    """, unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="badge"><span class="dot"></span>NLP RESUME INTELLIGENCE</div>
<div class="hero-title">Screen Resumes<br>with AI<span class="cursor">|</span></div>
<div class="hero-sub">
Upload a resume and compare it to any job description using sentence embeddings,
cosine similarity, and automated skill extraction — ranked and scored instantly.
</div>
""", unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown('<div class="stat-block"><div class="stat-num">100+</div><div class="stat-lbl">Skills Indexed</div></div>', unsafe_allow_html=True)
with col_s2:
    st.markdown('<div class="stat-block"><div class="stat-num">5</div><div class="stat-lbl">Skill Categories</div></div>', unsafe_allow_html=True)
with col_s3:
    st.markdown('<div class="stat-block"><div class="stat-num">∞</div><div class="stat-lbl">Resumes / Session</div></div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Input section ──────────────────────────────────────────────────────────────
col_jd, col_up = st.columns([1, 1], gap="large")

with col_jd:
    st.markdown('<div class="section-label">01 — Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "job_description",
        height=220,
        placeholder="Paste job description here...\n\nWe are looking for a Machine Learning Engineer\nwith experience in Python, PyTorch, NLP...",
        label_visibility="collapsed",
    )

with col_up:
    if mode == "Single Resume":
        st.markdown('<div class="section-label">02 — Resume</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("upload", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    else:
        st.markdown('<div class="section-label">02 — Resumes (Batch)</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("upload", type=["pdf", "docx", "txt"], accept_multiple_files=True, label_visibility="collapsed")

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SINGLE RESUME MODE
# ══════════════════════════════════════════════════════════════════════════════
if mode == "Single Resume":
    if not jd_text.strip() or not uploaded:
        st.markdown("""
        <div style="text-align:center; padding: 60px 0; color: #222222; font-size: 13px;">
            ▸ Paste a job description and upload a resume to begin analysis
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("Analysing..."):
            resume_text = extract_text(uploaded, uploaded.name)
            similarity = compute_similarity(resume_text, jd_text)
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(jd_text)
            overlap = get_skill_overlap(resume_skills, jd_skills)

        pct = round(similarity * 100, 1)
        skill_pct = round(overlap["match_rate"] * 100, 1)

        if pct >= 70:
            verdict_html = f'<div class="verdict-green">▸ STRONG MATCH — {pct}% semantic similarity. Candidate aligns well with the role.</div>'
            bar_color = "#00ff41"
        elif pct >= 45:
            verdict_html = f'<div class="verdict-yellow">▸ POTENTIAL MATCH — {pct}% semantic similarity. Some alignment, gaps present.</div>'
            bar_color = "#ffaa00"
        else:
            verdict_html = f'<div class="verdict-red">▸ WEAK MATCH — {pct}% semantic similarity. Significant skill/context gap.</div>'
            bar_color = "#ff4141"

        st.markdown('<div class="section-label">Analysis Results</div>', unsafe_allow_html=True)
        st.markdown(verdict_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Metrics row ────────────────────────────────────────────────────────
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.metric("Similarity Score", f"{pct}%")
        with mc2:
            st.metric("Skill Match", f"{skill_pct}%")
        with mc3:
            st.metric("Matched Skills", len(overlap["matched"]))
        with mc4:
            st.metric("Missing Skills", len(overlap["missing"]))

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Score bar ──────────────────────────────────────────────────────────
        fig_bar = go.Figure(go.Bar(
            x=[pct],
            y=["Match"],
            orientation="h",
            marker_color=bar_color,
            marker_line_width=0,
            width=0.3,
        ))
        fig_bar.add_shape(type="line", x0=70, x1=70, y0=-0.5, y1=0.5,
                          line=dict(color="#ffffff", width=1, dash="dot"))
        fig_bar.add_annotation(x=70, y=0.5, text="70% threshold", showarrow=False,
                               font=dict(size=9, color="#333333"), yshift=10)
        fig_bar.update_xaxes(range=[0, 100], showgrid=False, showticklabels=True,
                              tickfont=dict(size=10, color="#333333"), ticksuffix="%")
        fig_bar.update_yaxes(showticklabels=False, showgrid=False)
        fig_bar.update_layout(
            **PLOTLY_BASE,
            height=90,
            margin=dict(t=10, b=10, l=0, r=0),
            xaxis=dict(color="#111111"),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        # ── Skill tabs ─────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Skill Breakdown</div>', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["Matched", "Missing", "All Resume Skills"])

        with tab1:
            if overlap["matched"]:
                html = "".join(f'<span class="skill-green">{s}</span>' for s in overlap["matched"])
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#222;font-size:13px">No skill overlap detected.</span>', unsafe_allow_html=True)

        with tab2:
            if overlap["missing"]:
                html = "".join(f'<span class="skill-red">{s}</span>' for s in overlap["missing"])
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#00ff41;font-size:13px">▸ Resume covers all JD skills.</span>', unsafe_allow_html=True)

        with tab3:
            for cat, skills in resume_skills.items():
                if skills:
                    st.markdown(f'<div style="color:#333;font-size:10px;text-transform:uppercase;letter-spacing:2px;margin:12px 0 6px">{cat.replace("_"," ")}</div>', unsafe_allow_html=True)
                    html = "".join(f'<span class="skill-gray">{s}</span>' for s in skills)
                    st.markdown(html, unsafe_allow_html=True)

        # ── Radar chart ────────────────────────────────────────────────────────
        from data.skills_db import SKILLS as SKILL_CATS
        cats = list(SKILL_CATS.keys())
        labels = [c.replace("_", " ").upper() for c in cats]
        jd_vals = [min(len(jd_skills.get(c, [])), 10) for c in cats]
        res_vals = [min(len(resume_skills.get(c, [])), 10) for c in cats]

        if any(jd_vals) or any(res_vals):
            st.markdown('<div class="section-label">Category Coverage</div>', unsafe_allow_html=True)
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=jd_vals + [jd_vals[0]], theta=labels + [labels[0]],
                fill="toself", name="Job Description",
                line=dict(color="#333333", width=1),
                fillcolor="rgba(51,51,51,0.3)",
            ))
            fig_r.add_trace(go.Scatterpolar(
                r=res_vals + [res_vals[0]], theta=labels + [labels[0]],
                fill="toself", name="Resume",
                line=dict(color="#00ff41", width=1.5),
                fillcolor="rgba(0,255,65,0.08)",
            ))
            fig_r.update_layout(
                **PLOTLY_BASE,
                height=360,
                polar=dict(
                    bgcolor="#000000",
                    radialaxis=dict(visible=True, range=[0, 10], color="#1a1a1a",
                                   gridcolor="#111111", tickfont=dict(size=9, color="#333333")),
                    angularaxis=dict(color="#333333", gridcolor="#111111",
                                     tickfont=dict(size=9, color="#555555")),
                ),
                legend=dict(font=dict(size=10, color="#555555"), bgcolor="transparent"),
            )
            st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})

        # ── Raw text ───────────────────────────────────────────────────────────
        with st.expander("▸ view extracted text"):
            st.markdown(f'<pre style="color:#333;font-size:11px;line-height:1.7;white-space:pre-wrap">{resume_text[:3000]}{"…" if len(resume_text)>3000 else ""}</pre>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BATCH RANKING MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    if not jd_text.strip() or not uploaded_files:
        st.markdown("""
        <div style="text-align:center; padding: 60px 0; color: #222222; font-size: 13px;">
            ▸ Paste a job description and upload resumes to begin ranking
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner(f"Ranking {len(uploaded_files)} resumes..."):
            resumes = []
            for f in uploaded_files:
                text = extract_text(f, f.name)
                skills = extract_skills(text)
                resumes.append({"name": f.name, "text": text, "skills": skills})
            ranked = rank_resumes(resumes, jd_text)
            jd_skills = extract_skills(jd_text)

        st.markdown('<div class="section-label">Ranking Results</div>', unsafe_allow_html=True)

        # ── Stats ──────────────────────────────────────────────────────────────
        avg_sim = round(sum(r["similarity"] for r in ranked) / len(ranked), 1)
        strong = sum(1 for r in ranked if r["similarity"] >= 70)

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.metric("Resumes Screened", len(ranked))
        with rc2:
            st.metric("Avg Similarity", f"{avg_sim}%")
        with rc3:
            st.metric("Strong Matches", strong)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Bar chart ──────────────────────────────────────────────────────────
        names = [r["name"].replace(".pdf","").replace(".docx","").replace(".txt","") for r in ranked]
        scores = [r["similarity"] for r in ranked]
        colors = ["#00ff41" if s >= 70 else "#ffaa00" if s >= 45 else "#ff4141" for s in scores]

        fig_b = go.Figure(go.Bar(
            x=names,
            y=scores,
            marker_color=colors,
            marker_line_width=0,
            text=[f"{s}%" for s in scores],
            textposition="outside",
            textfont=dict(size=10, color="#888888"),
        ))
        fig_b.add_shape(type="line", x0=-0.5, x1=len(names)-0.5, y0=70, y1=70,
                        line=dict(color="#ffffff", width=1, dash="dot"))
        fig_b.update_xaxes(showgrid=False, tickfont=dict(size=10, color="#555555"))
        fig_b.update_yaxes(range=[0, 110], showgrid=True, gridcolor="#0a0a0a",
                           ticksuffix="%", tickfont=dict(size=10, color="#333333"))
        fig_b.update_layout(**PLOTLY_BASE, height=300, margin=dict(t=20, b=10, l=0, r=0))
        st.plotly_chart(fig_b, use_container_width=True, config={"displayModeBar": False})

        # ── Ranked list ────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Leaderboard</div>', unsafe_allow_html=True)
        for i, r in enumerate(ranked, 1):
            ov = get_skill_overlap(r["skills"], jd_skills)
            score = r["similarity"]
            color = "#00ff41" if score >= 70 else "#ffaa00" if score >= 45 else "#ff4141"
            bar_w = int(score)
            st.markdown(f"""
            <div style="border:1px solid #111;padding:16px 20px;margin-bottom:8px;border-radius:2px;border-left:2px solid {color}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                    <div style="display:flex;align-items:center;gap:12px">
                        <span style="color:{color};font-size:11px;border:1px solid {color};padding:2px 8px">#{i}</span>
                        <span style="color:#ffffff;font-size:13px">{r["name"]}</span>
                    </div>
                    <span style="color:{color};font-size:20px;font-weight:700">{score}%</span>
                </div>
                <div style="background:#0a0a0a;height:2px;border-radius:0;overflow:hidden">
                    <div style="background:{color};height:100%;width:{bar_w}%;transition:width 0.5s"></div>
                </div>
                <div style="margin-top:10px;font-size:11px;color:#333;display:flex;gap:20px">
                    <span>▸ {len(ov["matched"])} skills matched</span>
                    <span>▸ {len(ov["missing"])} skills missing</span>
                    <span>▸ skill match: {round(ov["match_rate"]*100)}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Top candidate deep-dive ────────────────────────────────────────────
        if ranked:
            top = ranked[0]
            top_ov = get_skill_overlap(top["skills"], jd_skills)
            st.markdown(f'<div class="section-label">Top Candidate — {top["name"]}</div>', unsafe_allow_html=True)
            tc1, tc2 = st.columns(2)
            with tc1:
                st.markdown('<div style="color:#333;font-size:10px;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px">Matched</div>', unsafe_allow_html=True)
                if top_ov["matched"]:
                    st.markdown("".join(f'<span class="skill-green">{s}</span>' for s in top_ov["matched"]), unsafe_allow_html=True)
            with tc2:
                st.markdown('<div style="color:#333;font-size:10px;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px">Missing</div>', unsafe_allow_html=True)
                if top_ov["missing"]:
                    st.markdown("".join(f'<span class="skill-red">{s}</span>' for s in top_ov["missing"]), unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color:#00ff41;font-size:12px">▸ All JD skills covered</span>', unsafe_allow_html=True)
