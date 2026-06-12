import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');

* { font-family: 'JetBrains Mono', 'Courier New', monospace !important; }

/* Hide ALL Streamlit chrome */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stAppHeader { display: none !important; }
[data-testid="stAppHeader"] { display: none !important; }

/* Base */
html, body, .stApp { background-color: #000000 !important; color: #ffffff !important; }

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

.block-container { padding: 48px 60px !important; max-width: 1400px !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #00ff41; }

hr { border: none; border-top: 1px solid #111111 !important; margin: 32px 0; }

/* Inputs */
.stTextArea textarea {
    background-color: #050505 !important;
    color: #00ff41 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 2px !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
    caret-color: #00ff41;
}
.stTextArea textarea:focus { border-color: #00ff41 !important; box-shadow: 0 0 0 1px #00ff4122 !important; }
.stTextArea textarea::placeholder { color: #2a2a2a !important; }
.stTextArea > label, .stFileUploader > label {
    color: #555555 !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: 1.5px;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploadDropzone"] {
    background-color: #050505 !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 2px !important;
    min-height: 220px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploadDropzone"]:hover { border-color: #00ff41 !important; }

/* Hide only the SVG cloud icon */
[data-testid="stFileUploaderDropzone"] svg,
[data-testid="stFileUploadDropzone"] svg { display: none !important; }

/* Uploader label — show it cleanly above the zone */
[data-testid="stFileUploader"] > label {
    color: #555555 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    margin-bottom: 8px !important;
}

/* Hide the default "Drag and drop" paragraph inside zone */
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploadDropzone"] p {
    display: none !important;
}

/* Hide the limit small text */
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploadDropzone"] small {
    display: none !important;
}

/* Browse files button */
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploadDropzone"] button {
    background: transparent !important;
    color: #888888 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 2px !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    padding: 10px 32px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploadDropzone"] button:hover {
    border-color: #00ff41 !important;
    color: #00ff41 !important;
}
[data-testid="stFileUploaderDropzone"] button span,
[data-testid="stFileUploadDropzone"] button span {
    color: inherit !important;
    font-size: inherit !important;
}

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
    color: #444444 !important; font-size: 10px !important;
    text-transform: uppercase; letter-spacing: 2px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00ff41 !important; font-size: 32px !important; font-weight: 700 !important;
}

/* Expander */
details { border: 1px solid #111111 !important; border-radius: 2px !important; }
details > summary {
    color: #444444 !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: 1.5px;
    padding: 12px 16px !important; background: #050505 !important;
}
details[open] > summary { color: #888888 !important; border-bottom: 1px solid #111111; }
.streamlit-expanderContent { background: #050505 !important; padding: 16px !important; }

/* Spinner */
[data-testid="stSpinner"] > div { border-top-color: #00ff41 !important; }

/* Alerts */
[data-baseweb="notification"] {
    background-color: #050505 !important;
    border: 1px solid #111111 !important;
    border-left: 2px solid #00ff41 !important;
    border-radius: 2px !important;
    color: #555555 !important;
}

/* Mode toggle buttons */
.mode-toggle {
    display: flex;
    gap: 0;
    margin: 24px 0 32px 0;
    border: 1px solid #1a1a1a;
    border-radius: 2px;
    width: fit-content;
}
.mode-btn {
    padding: 10px 28px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    cursor: pointer;
    border: none;
    background: transparent;
    color: #333333;
    transition: all 0.15s;
}
.mode-btn.active {
    background: #00ff41;
    color: #000000;
    font-weight: 700;
}
.mode-btn:not(.active):hover { color: #00ff41; }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

.badge {
    display: inline-flex; align-items: center; gap: 8px;
    border: 1px solid #1a1a1a; padding: 5px 14px; border-radius: 2px;
    font-size: 10px; color: #555555; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 20px;
}
.badge .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00ff41; box-shadow: 0 0 6px #00ff41; flex-shrink: 0;
}
.cursor { color: #00ff41; animation: blink 1s infinite; font-weight: 700; }
.hero-title { font-size: 52px; font-weight: 700; line-height: 1.1; margin: 0 0 12px 0; letter-spacing: -1px; }
.hero-sub { font-size: 14px; color: #444444; line-height: 1.7; margin-bottom: 0; max-width: 600px; }

.section-label {
    font-size: 10px; color: #666666; text-transform: uppercase;
    letter-spacing: 3px; padding-left: 12px; border-left: 2px solid #00ff41;
    margin-bottom: 16px; margin-top: 32px;
}
.skill-green {
    display: inline-block; background: #001a0a; color: #00ff41;
    border: 1px solid #00ff4144; padding: 3px 12px; border-radius: 2px; margin: 3px; font-size: 12px;
}
.skill-red {
    display: inline-block; background: #1a0000; color: #ff4141;
    border: 1px solid #ff414144; padding: 3px 12px; border-radius: 2px; margin: 3px; font-size: 12px;
}
.skill-gray {
    display: inline-block; background: #0a0a0a; color: #555555;
    border: 1px solid #1a1a1a; padding: 3px 12px; border-radius: 2px; margin: 3px; font-size: 12px;
}
.verdict-green { border: 1px solid #00ff4144; background: #001a0a; color: #00ff41; padding: 16px 20px; border-radius: 2px; font-size: 14px; font-weight: 600; }
.verdict-yellow { border: 1px solid #ffaa0044; background: #1a1000; color: #ffaa00; padding: 16px 20px; border-radius: 2px; font-size: 14px; font-weight: 600; }
.verdict-red { border: 1px solid #ff414144; background: #1a0000; color: #ff4141; padding: 16px 20px; border-radius: 2px; font-size: 14px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

PLOTLY_BASE = dict(
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(family="JetBrains Mono, Courier New, monospace", color="#888888", size=11),
    margin=dict(t=40, b=20, l=20, r=20),
)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="badge"><span class="dot"></span>NLP RESUME INTELLIGENCE</div>
<div class="hero-title">Screen Resumes<br>with AI<span class="cursor">|</span></div>
<div class="hero-sub">
Compare resumes to any job description using sentence embeddings, cosine similarity,
and automated skill extraction — scored and ranked instantly.
</div>
""", unsafe_allow_html=True)

# ── Mode toggle (replaces sidebar) ─────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = "Single Resume"

col_m1, col_m2, _ = st.columns([1, 1, 4])
with col_m1:
    if st.button("▸ Single Resume", use_container_width=True,
                 type="primary" if st.session_state.mode == "Single Resume" else "secondary"):
        st.session_state.mode = "Single Resume"
        st.rerun()
with col_m2:
    if st.button("▸ Batch Ranking", use_container_width=True,
                 type="primary" if st.session_state.mode == "Batch Ranking" else "secondary"):
        st.session_state.mode = "Batch Ranking"
        st.rerun()

mode = st.session_state.mode

# ── Stats row ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
sc1, sc2, sc3, sc4 = st.columns(4)
stats = [("100+", "Skills Indexed"), ("5", "Skill Categories"), ("3", "File Formats"), ("∞", "Resumes / Session")]
for col, (num, lbl) in zip([sc1, sc2, sc3, sc4], stats):
    with col:
        st.markdown(f'''
        <div style="border:1px solid #111;padding:16px 20px;border-radius:2px">
            <div style="font-size:26px;font-weight:700;color:#fff">{num}</div>
            <div style="font-size:10px;color:#333;text-transform:uppercase;letter-spacing:2px;margin-top:4px">{lbl}</div>
        </div>''', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Inputs ─────────────────────────────────────────────────────────────────────
col_jd, col_up = st.columns([1, 1], gap="large")

with col_jd:
    st.markdown('<div class="section-label">01 — Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "jd", height=220,
        placeholder="Paste job description here...\n\nWe are looking for a Machine Learning Engineer\nwith experience in Python, PyTorch, NLP...",
        label_visibility="collapsed",
    )

with col_up:
    if mode == "Single Resume":
        st.markdown('<div class="section-label">02 — Resume</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Drop resume here — PDF, DOCX or TXT", type=["pdf", "docx", "txt"])
    else:
        st.markdown('<div class="section-label">02 — Resumes (Batch)</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Drop resumes here — PDF, DOCX or TXT", type=["pdf", "docx", "txt"], accept_multiple_files=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SINGLE RESUME
# ══════════════════════════════════════════════════════════════════════════════
if mode == "Single Resume":
    if not jd_text.strip() or not uploaded:
        st.markdown('<div style="text-align:center;padding:60px 0;color:#1e1e1e;font-size:13px">▸ Paste a job description and upload a resume to begin analysis</div>', unsafe_allow_html=True)
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

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: st.metric("Similarity Score", f"{pct}%")
        with mc2: st.metric("Skill Match", f"{skill_pct}%")
        with mc3: st.metric("Matched Skills", len(overlap["matched"]))
        with mc4: st.metric("Missing Skills", len(overlap["missing"]))

        st.markdown("<br>", unsafe_allow_html=True)

        fig_bar = go.Figure(go.Bar(
            x=[pct], y=[""], orientation="h",
            marker_color=bar_color, marker_line_width=0, width=0.4,
        ))
        fig_bar.add_shape(type="line", x0=70, x1=70, y0=-0.5, y1=0.5,
                          line=dict(color="#ffffff", width=1, dash="dot"))
        fig_bar.add_annotation(x=70, y=0.5, text="threshold 70%", showarrow=False,
                               font=dict(size=9, color="#333333"), yshift=12)
        fig_bar.update_xaxes(range=[0, 100], showgrid=False, ticksuffix="%",
                             tickfont=dict(size=10, color="#333333"))
        fig_bar.update_yaxes(showticklabels=False, showgrid=False)
        fig_bar.update_layout(**PLOTLY_BASE, height=80, margin=dict(t=20, b=10, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-label">Skill Breakdown</div>', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["Matched", "Missing", "All Resume Skills"])

        with tab1:
            if overlap["matched"]:
                st.markdown("".join(f'<span class="skill-green">{s}</span>' for s in overlap["matched"]), unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#222;font-size:13px">No skill overlap detected.</span>', unsafe_allow_html=True)

        with tab2:
            if overlap["missing"]:
                st.markdown("".join(f'<span class="skill-red">{s}</span>' for s in overlap["missing"]), unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#00ff41;font-size:12px">▸ Resume covers all JD skills.</span>', unsafe_allow_html=True)

        with tab3:
            for cat, skills in resume_skills.items():
                if skills:
                    st.markdown(f'<div style="color:#444;font-size:10px;text-transform:uppercase;letter-spacing:2px;margin:12px 0 6px">{cat.replace("_"," ")}</div>', unsafe_allow_html=True)
                    st.markdown("".join(f'<span class="skill-gray">{s}</span>' for s in skills), unsafe_allow_html=True)

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
                line=dict(color="#333333", width=1), fillcolor="rgba(51,51,51,0.3)",
            ))
            fig_r.add_trace(go.Scatterpolar(
                r=res_vals + [res_vals[0]], theta=labels + [labels[0]],
                fill="toself", name="Resume",
                line=dict(color="#00ff41", width=1.5), fillcolor="rgba(0,255,65,0.08)",
            ))
            fig_r.update_layout(
                **PLOTLY_BASE, height=360,
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

        with st.expander("▸ view extracted text"):
            st.markdown(f'<pre style="color:#333;font-size:11px;line-height:1.7;white-space:pre-wrap">{resume_text[:3000]}{"…" if len(resume_text)>3000 else ""}</pre>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BATCH RANKING
# ══════════════════════════════════════════════════════════════════════════════
else:
    if not jd_text.strip() or not uploaded_files:
        st.markdown('<div style="text-align:center;padding:60px 0;color:#1e1e1e;font-size:13px">▸ Paste a job description and upload resumes to begin ranking</div>', unsafe_allow_html=True)
    else:
        with st.spinner(f"Ranking {len(uploaded_files)} resumes..."):
            resumes = []
            for f in uploaded_files:
                text = extract_text(f, f.name)
                skills = extract_skills(text)
                resumes.append({"name": f.name, "text": text, "skills": skills})
            ranked = rank_resumes(resumes, jd_text)
            jd_skills = extract_skills(jd_text)

        avg_sim = round(sum(r["similarity"] for r in ranked) / len(ranked), 1)
        strong = sum(1 for r in ranked if r["similarity"] >= 70)

        st.markdown('<div class="section-label">Ranking Results</div>', unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns(3)
        with rc1: st.metric("Resumes Screened", len(ranked))
        with rc2: st.metric("Avg Similarity", f"{avg_sim}%")
        with rc3: st.metric("Strong Matches", strong)

        st.markdown("<br>", unsafe_allow_html=True)

        names = [r["name"].rsplit(".", 1)[0] for r in ranked]
        scores = [r["similarity"] for r in ranked]
        colors = ["#00ff41" if s >= 70 else "#ffaa00" if s >= 45 else "#ff4141" for s in scores]

        fig_b = go.Figure(go.Bar(
            x=names, y=scores, marker_color=colors, marker_line_width=0,
            text=[f"{s}%" for s in scores], textposition="outside",
            textfont=dict(size=10, color="#888888"),
        ))
        fig_b.add_shape(type="line", x0=-0.5, x1=len(names)-0.5, y0=70, y1=70,
                        line=dict(color="#ffffff", width=1, dash="dot"))
        fig_b.update_xaxes(showgrid=False, tickfont=dict(size=10, color="#555555"))
        fig_b.update_yaxes(range=[0, 115], showgrid=True, gridcolor="#0a0a0a",
                           ticksuffix="%", tickfont=dict(size=10, color="#333333"))
        fig_b.update_layout(**PLOTLY_BASE, height=300, margin=dict(t=20, b=10, l=0, r=0))
        st.plotly_chart(fig_b, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-label">Leaderboard</div>', unsafe_allow_html=True)
        for i, r in enumerate(ranked, 1):
            ov = get_skill_overlap(r["skills"], jd_skills)
            score = r["similarity"]
            color = "#00ff41" if score >= 70 else "#ffaa00" if score >= 45 else "#ff4141"
            st.markdown(f"""
            <div style="border:1px solid #111;padding:16px 20px;margin-bottom:8px;border-radius:2px;border-left:2px solid {color}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                    <div style="display:flex;align-items:center;gap:12px">
                        <span style="color:{color};font-size:11px;border:1px solid {color};padding:2px 8px">#{i}</span>
                        <span style="color:#fff;font-size:13px">{r["name"]}</span>
                    </div>
                    <span style="color:{color};font-size:22px;font-weight:700">{score}%</span>
                </div>
                <div style="background:#0a0a0a;height:2px;overflow:hidden">
                    <div style="background:{color};height:100%;width:{int(score)}%"></div>
                </div>
                <div style="margin-top:10px;font-size:11px;color:#333;display:flex;gap:24px">
                    <span>▸ {len(ov["matched"])} matched</span>
                    <span>▸ {len(ov["missing"])} missing</span>
                    <span>▸ {round(ov["match_rate"]*100)}% skill match</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if ranked:
            top = ranked[0]
            top_ov = get_skill_overlap(top["skills"], jd_skills)
            st.markdown(f'<div class="section-label">Top Candidate — {top["name"]}</div>', unsafe_allow_html=True)
            tc1, tc2 = st.columns(2)
            with tc1:
                st.markdown('<div style="color:#444;font-size:10px;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px">Matched</div>', unsafe_allow_html=True)
                if top_ov["matched"]:
                    st.markdown("".join(f'<span class="skill-green">{s}</span>' for s in top_ov["matched"]), unsafe_allow_html=True)
            with tc2:
                st.markdown('<div style="color:#444;font-size:10px;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px">Missing</div>', unsafe_allow_html=True)
                if top_ov["missing"]:
                    st.markdown("".join(f'<span class="skill-red">{s}</span>' for s in top_ov["missing"]), unsafe_allow_html=True)
                else:
                    st.markdown('<span style="color:#00ff41;font-size:12px">▸ All JD skills covered</span>', unsafe_allow_html=True)
