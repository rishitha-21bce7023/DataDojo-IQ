import json
import base64
import re
from html import escape
from pathlib import Path

import streamlit as st

ASSETS_DIR = Path("assets")

try:
    from foundry_client import ask_foundry_agent
except ModuleNotFoundError as import_error:
    def ask_foundry_agent(user_prompt):
        return (
            "Foundry SDK dependency is not installed in this Python environment. "
            "Install the project requirements and rerun the app to enable Microsoft Foundry responses. "
            f"Missing module detail: {import_error}"
        )


st.set_page_config(
    page_title="DataDojo IQ | Foundry Readiness",
    page_icon=str(ASSETS_DIR / "datadojo_tab_icon.svg"),
    layout="wide",
    initial_sidebar_state="expanded",
)


ROLES = [
    "Junior Data Engineer",
    "Data Engineer",
    "Senior Data Engineer / Manager",
    "Director",
]

DOMAINS = [
    "Sales Analytics",
    "Supply Chain Analytics",
    "Finance Analytics",
    "Customer Insights",
    "Operations Analytics",
]

DATA_PRODUCTS = [
    "Revenue Insights Product",
    "Inventory Quality Product",
    "Customer Activity Product",
    "Forecasting Data Product",
    "Operational Metrics Product",
]

TASK_TYPES = [
    "Configure metadata pipeline",
    "Validate incremental load",
    "Fix schema mismatch",
    "Add data quality checks",
    "Troubleshoot failed pipeline",
    "Document pipeline rules",
]

TARGET_SKILLS = [
    "Metadata Pipeline Configuration",
    "Incremental Load Design",
    "UPSERT Merge Logic",
    "Schema Evolution Handling",
    "Data Quality Rule Design",
    "Pipeline Troubleshooting",
    "Architecture and Governance",
]

SCENARIO_TYPES = [
    "Metadata Pipeline Configuration",
    "Incremental Load Issue",
    "UPSERT Merge Issue",
    "Schema Evolution Issue",
    "Data Quality Rule Design",
    "Pipeline Troubleshooting",
]

SESSION_DEFAULTS = {
    "theme": "Light Mode",
    "generated_roadmap": None,
    "generated_quiz": None,
    "raw_quiz_response": None,
    "quiz_answers": {},
    "quiz_score": None,
    "readiness_status": None,
    "assessment_feedback": None,
    "generated_config_scenario": None,
    "config_answer": "",
    "config_score": None,
    "config_feedback": None,
    "learner_results": {},
    "manager_response": None,
    "director_response": None,
}

ROLE_EXPECTATIONS = {
    "Junior Data Engineer": {
        "description": "Contributes to task-level execution inside a data product.",
        "ownership": "Owns task execution",
        "purpose": "Learns pipeline basics and handles task-level work.",
        "skills": ["metadata basics", "validation", "troubleshooting", "documentation"],
    },
    "Data Engineer": {
        "description": "Owns or operates one data product end-to-end.",
        "ownership": "Owns a data product",
        "purpose": "Designs reliable pipelines, load rules, quality checks, and monitoring.",
        "skills": ["load strategy", "UPSERT", "watermarking", "data quality"],
    },
    "Senior Data Engineer / Manager": {
        "description": "Manages one domain or a data engineering team.",
        "ownership": "Owns domain or team readiness",
        "purpose": "Guides engineers, reviews architecture, and manages readiness risks.",
        "skills": ["architecture review", "coaching", "standards", "risk management"],
    },
    "Director": {
        "description": "Oversees multiple domains and capability maturity.",
        "ownership": "Owns strategic readiness",
        "purpose": "Tracks cross-domain readiness, governance, and capability investment.",
        "skills": ["portfolio readiness", "governance", "investment planning", "risk escalation"],
    },
}

RESOURCE_CATALOG = {
    "metadata": [
        {
            "title": "Azure Data Factory documentation",
            "type": "Documentation",
            "url": "https://learn.microsoft.com/azure/data-factory/",
            "description": "Learn orchestration and pipeline concepts.",
        },
        {
            "title": "Microsoft Fabric Data Engineering documentation",
            "type": "Microsoft Learn",
            "url": "https://learn.microsoft.com/fabric/data-engineering/",
            "description": "Explore lakehouse and data engineering concepts.",
        },
    ],
    "sql": [
        {
            "title": "SQL learning path on Microsoft Learn",
            "type": "Microsoft Learn",
            "url": "https://learn.microsoft.com/training/browse/?terms=sql",
            "description": "Practice SQL concepts for data engineering.",
        }
    ],
    "python": [
        {
            "title": "Python documentation",
            "type": "Documentation",
            "url": "https://docs.python.org/3/",
            "description": "Strengthen Python fundamentals.",
        }
    ],
    "streamlit": [
        {
            "title": "Streamlit documentation",
            "type": "Documentation",
            "url": "https://docs.streamlit.io/",
            "description": "Build interactive Python data apps.",
        }
    ],
    "foundry": [
        {
            "title": "Microsoft Foundry documentation",
            "type": "Microsoft Learn",
            "url": "https://learn.microsoft.com/azure/ai-foundry/",
            "description": "Learn how to build AI apps and agents with Microsoft Foundry.",
        }
    ],
    "quality": [
        {
            "title": "Microsoft Learn data fundamentals",
            "type": "Microsoft Learn",
            "url": "https://learn.microsoft.com/training/browse/?terms=data%20engineering",
            "description": "Build foundational data engineering and quality concepts.",
        }
    ],
}

SECTION_ICONS = {
    "skill gap analysis": "Gap",
    "learning roadmap": "Roadmap",
    "four-week learning roadmap": "Roadmap",
    "strength areas": "Strengths",
    "weak areas": "Gaps",
    "risk in the answer": "Risk",
    "recommended fix": "Fix",
    "best practice answer": "Best Practice",
    "resources": "Resources",
    "recommended revision resources": "Resources",
    "score interpretation": "Score",
    "strategic recommendations": "Strategy",
    "sources used": "Sources",
    "next 30-day action plan": "Plan",
}

KEYWORDS = [
    "UPSERT",
    "INCREMENTAL",
    "FULL LOAD",
    "APPEND",
    "primary key",
    "primary keys",
    "watermark",
    "metadata",
    "schema evolution",
    "data quality",
    "troubleshooting",
    "readiness",
    "risk",
    "recommendation",
    "Microsoft Foundry",
    "Foundry IQ",
    "vector index",
    "synthetic data",
    "Ready",
    "Needs Revision",
    "Not Ready",
]


def init_state():
    for key, val in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val


def apply_theme_from_query_params():
    requested_theme = st.query_params.get("theme")
    if isinstance(requested_theme, list):
        requested_theme = requested_theme[0] if requested_theme else None
    if str(requested_theme).lower() == "dark":
        st.session_state["theme"] = "Dark Mode"
    elif str(requested_theme).lower() == "light":
        st.session_state["theme"] = "Light Mode"


def safe_text(value):
    return escape(str(value or ""))


def asset_data_uri(filename):
    path = ASSETS_DIR / filename
    if not path.exists():
        return ""
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def inject_theme_css(theme):
    if theme == "Dark Mode":
        palette = {
            "bg_page": "#07111F",
            "bg_card": "#0F172A",
            "bg_card_inner": "#172033",
            "text_primary": "#F8FAFC",
            "text_secondary": "#CBD5E1",
            "text_muted": "#94A3B8",
            "border": "#263246",
            "accent_blue": "#38BDF8",
            "accent_teal": "#22D3EE",
            "accent_green": "#A3E635",
            "accent_amber": "#FACC15",
            "accent_red": "#F87171",
            "accent_purple": "#818CF8",
        }
    else:
        palette = {
            "bg_page": "#F7FBFF",
            "bg_card": "#FFFFFF",
            "bg_card_inner": "#EEF6FF",
            "text_primary": "#07111F",
            "text_secondary": "#475569",
            "text_muted": "#64748B",
            "border": "#D9E5F2",
            "accent_blue": "#2563EB",
            "accent_teal": "#06B6D4",
            "accent_green": "#65A30D",
            "accent_amber": "#CA8A04",
            "accent_red": "#DC2626",
            "accent_purple": "#6366F1",
        }
    toggle_track = "linear-gradient(135deg, #07111F 0%, #111827 100%)" if theme == "Dark Mode" else "linear-gradient(135deg, #E0F2FE 0%, #FFFFFF 100%)"
    toggle_knob = "translateX(2.85rem)" if theme == "Dark Mode" else "translateX(0)"
    toggle_icon = "☾" if theme == "Dark Mode" else "☀"
    toggle_icon_color = "#F8FAFC" if theme == "Dark Mode" else "#0F172A"
    toggle_star_opacity = "1" if theme == "Dark Mode" else "0"

    st.markdown(
        f"""
        <style>
        html {{
            scroll-behavior: smooth;
        }}

        *, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            scroll-behavior: smooth;
        }}

        :root {{
            --bg-page: {palette["bg_page"]};
            --bg-card: {palette["bg_card"]};
            --bg-card-inner: {palette["bg_card_inner"]};
            --text-primary: {palette["text_primary"]};
            --text-secondary: {palette["text_secondary"]};
            --text-muted: {palette["text_muted"]};
            --border: {palette["border"]};
            --accent-blue: {palette["accent_blue"]};
            --accent-teal: {palette["accent_teal"]};
            --accent-green: {palette["accent_green"]};
            --accent-amber: {palette["accent_amber"]};
            --accent-red: {palette["accent_red"]};
            --accent-purple: {palette["accent_purple"]};
        }}

        .stApp {{
            background:
                radial-gradient(circle at 10% 8%, color-mix(in srgb, var(--accent-purple) 16%, transparent), transparent 24rem),
                radial-gradient(circle at 92% 4%, color-mix(in srgb, var(--accent-teal) 16%, transparent), transparent 24rem),
                radial-gradient(circle at 55% 0%, color-mix(in srgb, var(--accent-amber) 10%, transparent), transparent 18rem),
                linear-gradient(180deg, color-mix(in srgb, var(--bg-page) 92%, #DBEAFE), var(--bg-page) 20rem),
                var(--bg-page);
            color: var(--text-primary);
        }}

        .block-container {{
            max-width: 1240px;
            padding-top: 4.5rem;
            padding-bottom: 3rem;
        }}

        .page-shell {{
            display: grid;
            gap: 1rem;
        }}

        section[data-testid="stSidebar"] {{
            background:
                radial-gradient(circle at 20% 0%, color-mix(in srgb, var(--accent-blue) 12%, transparent), transparent 12rem),
                radial-gradient(circle at 92% 18%, color-mix(in srgb, var(--accent-amber) 12%, transparent), transparent 13rem),
                linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 94%, transparent), color-mix(in srgb, var(--bg-card-inner) 72%, var(--bg-card)));
            border-right: 1px solid color-mix(in srgb, var(--accent-blue) 16%, var(--border));
            box-shadow: inset -1px 0 0 color-mix(in srgb, var(--accent-teal) 9%, transparent);
        }}

        section[data-testid="stSidebar"]::before {{
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(120deg, transparent 0 36%, color-mix(in srgb, var(--accent-teal) 9%, transparent) 46%, transparent 58%),
                radial-gradient(circle at 20% 72%, color-mix(in srgb, var(--accent-purple) 10%, transparent), transparent 10rem);
            animation: sidebarAura 8s ease-in-out infinite alternate;
        }}

        @keyframes sidebarAura {{
            from {{ opacity: 0.52; transform: translateY(0); }}
            to {{ opacity: 0.88; transform: translateY(1.2rem); }}
        }}

        h1, h2, h3, h4, h5, p, li, label,
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] * {{
            color: var(--text-primary);
            letter-spacing: 0;
        }}

        .section-copy, .brand-subtitle, .flow-step-desc, .muted,
        .ai-section-body, .resource-card-description, .resource-description, .hero-stat-card span,
        .arch-flow-step span, .persona-card span, .role-card span {{
            color: var(--text-secondary);
        }}

        .app-topbar,
        .brand-shell,
        .topbar-brand-card {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            border: 0;
            background: transparent;
            backdrop-filter: none;
            border-radius: 0;
            padding: 0.35rem 0.1rem;
            margin-bottom: 0.35rem;
            min-height: 3.7rem;
            box-shadow: none;
            position: relative;
            overflow: hidden;
        }}

        .topbar-brand-card::after {{
            display: none;
        }}

        .topbar-brand-card {{
            justify-content: flex-start;
        }}

        .topbar-actions,
        .top-toggle-shell {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.55rem;
            min-height: 4.15rem;
            margin-bottom: 0.35rem;
            border: 0;
            border-radius: 30px;
            background: transparent;
            padding: 0.38rem 0;
            box-shadow: none;
            position: relative;
            overflow: hidden;
        }}

        .top-toggle-shell::before {{
            content: "";
            position: absolute;
            inset: 0 auto 0 -40%;
            width: 32%;
            transform: skewX(-18deg);
            background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--accent-blue) 14%, transparent), transparent);
            animation: softSweep 4.8s ease-in-out infinite;
        }}

        @keyframes softSweep {{
            0%, 40% {{ left: -40%; }}
            75%, 100% {{ left: 118%; }}
        }}

        .top-toggle-label {{
            color: var(--text-muted);
            font-weight: 900;
            text-transform: uppercase;
            font-size: 0.72rem;
            margin-right: 0;
        }}

        .brand-logo-mark {{
            width: 3rem;
            height: 3rem;
            flex: 0 0 3rem;
            border-radius: 1rem;
            background:
                radial-gradient(circle at 28% 24%, rgba(255,255,255,0.32), transparent 1.25rem),
                linear-gradient(135deg, #07111F 0%, #133B64 55%, #22D3EE 100%);
            box-shadow: 0 14px 28px color-mix(in srgb, var(--accent-teal) 22%, transparent);
            animation: logoFloat 3.8s ease-in-out infinite alternate;
            position: relative;
            z-index: 1;
        }}

        .brand-logo-mark::before {{
            content: "D";
            position: absolute;
            inset: 0.43rem;
            border: 3px solid #A3E635;
            border-left-width: 5px;
            border-radius: 0.55rem 0.8rem 0.8rem 0.55rem;
            color: #F8FAFC;
            display: grid;
            place-items: center;
            font-size: 1.05rem;
            font-weight: 950;
            font-family: "Arial Rounded MT Bold", "Trebuchet MS", system-ui, sans-serif;
        }}

        .brand-logo-mark::after {{
            content: "";
            position: absolute;
            right: 0.55rem;
            bottom: 0.5rem;
            width: 0.34rem;
            height: 0.34rem;
            border-radius: 999px;
            background: #22D3EE;
            box-shadow: -0.58rem -0.2rem 0 #6366F1, -1.05rem 0.32rem 0 #A3E635;
        }}

        @keyframes logoFloat {{
            from {{ transform: translateY(0) rotate(0deg); }}
            to {{ transform: translateY(-0.22rem) rotate(-1deg); }}
        }}

        .brand-text-block {{
            min-width: 0;
            flex: 1;
        }}

        .brand-wordmark {{
            font-family: "Trebuchet MS", "Arial Rounded MT Bold", ui-rounded, system-ui, sans-serif;
            font-size: clamp(1.28rem, 2vw, 1.75rem);
            font-weight: 950;
            line-height: 1;
            color: var(--text-primary) !important;
            letter-spacing: -0.015em;
            transform: none;
            width: fit-content;
            padding-right: 0.08rem;
        }}

        .brand-wordmark .brand-data {{
            color: var(--text-primary) !important;
            text-shadow: none;
        }}

        .brand-wordmark .brand-dojo {{
            color: var(--accent-teal) !important;
            text-shadow: 0 10px 22px color-mix(in srgb, var(--accent-teal) 18%, transparent);
        }}

        .brand-wordmark .brand-iq {{
            background: linear-gradient(90deg, #A3E635, #22D3EE);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
        }}

        .brand-subtitle {{
            margin-top: 0.2rem;
            font-size: 0.8rem;
            font-weight: 700;
        }}

        .brand-badge, .hero-badge, .ai-source-chip, .resource-chip, .status-badge {{
            display: inline-flex;
            align-items: center;
            width: fit-content;
            border: 1px solid color-mix(in srgb, var(--accent-blue) 38%, var(--border));
            border-radius: 999px;
            background: color-mix(in srgb, var(--accent-blue) 10%, var(--bg-card));
            color: var(--text-primary);
            font-size: 0.78rem;
            font-weight: 850;
            padding: 0.35rem 0.65rem;
            margin: 0.14rem 0.18rem;
        }}

        .hero-shell {{
            position: relative;
            overflow: hidden;
            border-radius: 36px;
            padding: clamp(0.9rem, 2vw, 1.35rem);
            margin: 0.2rem 0 1rem;
            min-height: 25rem;
            width: min(100% + 3.5rem, calc(100vw - 1.2rem));
            margin-left: max(-1.75rem, calc((1240px - 100vw) / 2));
            border: 1px solid rgba(255, 255, 255, 0.20);
            background:
                radial-gradient(circle at 78% 24%, rgba(244, 114, 182, 0.54), transparent 18rem),
                radial-gradient(circle at 55% 62%, rgba(45, 212, 191, 0.38), transparent 17rem),
                radial-gradient(circle at 12% 14%, rgba(59, 130, 246, 0.42), transparent 16rem),
                linear-gradient(135deg, #071226 0%, #1C1648 42%, #073D46 100%);
            box-shadow: 0 34px 78px rgba(15, 23, 42, 0.28);
            isolation: isolate;
        }}

        .hero-shell::before {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(ellipse at 72% 38%, rgba(255,255,255,0.22), transparent 17rem),
                radial-gradient(ellipse at 22% 74%, rgba(45,212,191,0.18), transparent 15rem),
                linear-gradient(115deg, transparent 0 34%, rgba(255,255,255,0.12) 42%, transparent 54%);
            opacity: 0.8;
            animation: heroLightWave 9s ease-in-out infinite alternate;
            pointer-events: none;
            z-index: 0;
        }}

        .hero-shell::after {{
            content: "";
            position: absolute;
            width: 30rem;
            height: 30rem;
            right: -7rem;
            top: -7rem;
            border-radius: 999px;
            border: 1px solid rgba(125, 211, 252, 0.16);
            background:
                radial-gradient(circle, rgba(125,211,252,0.18), transparent 60%),
                conic-gradient(from 110deg, transparent, rgba(45,212,191,0.18), transparent, rgba(168,85,247,0.18), transparent);
            animation: orbitGlow 12s linear infinite;
            pointer-events: none;
            z-index: 0;
        }}

        .hero-grid {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: minmax(300px, 0.8fr) minmax(440px, 1.2fr);
            gap: clamp(0.8rem, 2.2vw, 1.55rem);
            align-items: center;
            min-height: 20.8rem;
            padding-top: 2.35rem;
        }}

        .hero-mini-nav {{
            position: absolute;
            z-index: 2;
            left: clamp(1.3rem, 3vw, 2.2rem);
            right: clamp(1.3rem, 3vw, 2.2rem);
            top: 0.95rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            color: rgba(248,250,252,0.82);
            font-weight: 850;
            font-size: 0.82rem;
        }}

        .hero-mini-nav-links {{
            display: flex;
            align-items: center;
            gap: 1rem;
            color: rgba(203,213,225,0.78);
            font-size: 0.74rem;
            opacity: 0.74;
        }}

        .hero-left, .hero-right {{
            min-width: 0;
        }}

        .hero-shell .hero-mini-nav,
        .hero-shell .hero-mini-nav *,
        .hero-shell .hero-home-mark,
        .hero-shell .hero-home-mark *,
        .hero-shell .hero-tagline,
        .hero-shell .hero-copy,
        .hero-shell .hero-floating-card,
        .hero-shell .hero-floating-card *,
        .hero-shell .hero-terminal,
        .hero-shell .hero-terminal * {{
            color: #F8FAFC !important;
        }}

        @keyframes heroLightWave {{
            from {{ transform: translateX(-1.4rem) scale(1); opacity: 0.62; }}
            to {{ transform: translateX(1.4rem) scale(1.04); opacity: 0.9; }}
        }}

        @keyframes orbitGlow {{
            to {{ transform: rotate(360deg); }}
        }}

        .hero-title {{
            color: #F8FAFC !important;
            font-size: clamp(2.6rem, 5.2vw, 4.45rem);
            line-height: 0.92;
            margin: 0.25rem 0 0.75rem;
            font-weight: 950;
            text-shadow: 0 18px 42px rgba(15,23,42,0.22);
        }}

        .hero-title span {{
            background: linear-gradient(90deg, #7DD3FC, #2DD4BF, #C4B5FD);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
        }}

        .hero-copy {{
            color: #F8FAFC !important;
            max-width: 560px;
            font-size: 1rem;
            line-height: 1.52;
        }}

        .hero-tagline {{
            color: #FDE68A !important;
            font-size: 1.05rem;
            font-weight: 850;
        }}

        .hero-home-mark {{
            display: inline-grid;
            grid-template-columns: 3rem auto;
            align-items: center;
            gap: 0.7rem;
            border: 1px solid rgba(125,211,252,0.34);
            border-radius: 999px;
            padding: 0.45rem 0.85rem 0.45rem 0.45rem;
            background:
                linear-gradient(135deg, rgba(125,211,252,0.16), rgba(255,255,255,0.05)),
                radial-gradient(circle at 1.5rem 1.5rem, rgba(45,212,191,0.30), transparent 2.6rem);
            backdrop-filter: blur(12px);
            color: #FFFFFF;
            font-weight: 950;
            margin-bottom: 1rem;
            box-shadow: 0 16px 34px rgba(15,23,42,0.14);
        }}

        .hero-home-icon {{
            position: relative;
            width: 2.7rem;
            height: 2.7rem;
            border-radius: 999px;
            background: linear-gradient(135deg, #0F172A, #0EA5E9);
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
        }}

        .hero-home-icon span {{
            position: absolute;
            inset: -0.45rem;
            border-radius: 999px;
            border: 1px dashed rgba(255,255,255,0.42);
            animation: homeOrbit 5s linear infinite;
        }}

        .hero-home-icon::before {{
            content: "";
            position: absolute;
            left: 0.52rem;
            right: 0.52rem;
            top: 0.48rem;
            height: 0.72rem;
            border-radius: 0.16rem 0.16rem 0 0;
            background: #2DD4BF;
            clip-path: polygon(50% 0, 100% 65%, 100% 100%, 0 100%, 0 65%);
            animation: roofPulse 1.7s ease-in-out infinite alternate;
        }}

        .hero-home-icon::after {{
            content: "";
            position: absolute;
            left: 0.74rem;
            right: 0.74rem;
            bottom: 0.48rem;
            height: 0.9rem;
            border-radius: 0.16rem;
            background:
                linear-gradient(90deg, #67E8F9 0 0.18rem, transparent 0.18rem 0.32rem, #67E8F9 0.32rem 0.5rem, transparent 0.5rem 0.64rem, #67E8F9 0.64rem);
        }}

        @keyframes roofPulse {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-0.18rem); filter: drop-shadow(0 0 0.45rem rgba(45,212,191,0.55)); }}
        }}

        @keyframes homeOrbit {{
            to {{ transform: rotate(360deg); }}
        }}

        .hero-cta-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1rem;
        }}

        .primary-cta, .secondary-cta {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 2.75rem;
            border-radius: 999px;
            padding: 0.82rem 1.1rem;
            font-weight: 950;
            text-decoration: none !important;
        }}

        .primary-cta {{
            color: #FFFFFF !important;
            background:
                linear-gradient(135deg, #3B5BFF 0%, #7C3AED 42%, #DB3AB7 72%, #FF8A2A 100%);
            border: 1px solid rgba(255, 255, 255, 0.64);
            box-shadow: 0 18px 38px rgba(124, 58, 237, 0.30), 0 0 0 5px rgba(219,58,183,0.12);
            position: relative;
            overflow: hidden;
        }}

        .primary-cta::after {{
            content: "";
            position: absolute;
            inset: 0 auto 0 -36%;
            width: 30%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.40), transparent);
            transform: skewX(-16deg);
            animation: ctaSweep 2.8s ease-in-out infinite;
        }}

        @keyframes ctaSweep {{
            0%, 42% {{ left: -36%; }}
            80%, 100% {{ left: 110%; }}
        }}

        .secondary-cta {{
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.44);
            background: rgba(15, 23, 42, 0.36);
            backdrop-filter: blur(12px);
        }}

        .hero-cinematic-scene {{
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 28px;
            background:
                radial-gradient(circle at 48% 38%, rgba(236,72,153,0.34), transparent 13rem),
                radial-gradient(circle at 62% 62%, rgba(45,212,191,0.22), transparent 14rem),
                radial-gradient(circle at 82% 20%, rgba(251,191,36,0.20), transparent 9rem),
                linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05), 0 28px 58px rgba(2,6,23,0.28);
            backdrop-filter: blur(14px);
            padding: 0;
            position: relative;
            min-height: 20.8rem;
            overflow: hidden;
            animation: heroFloat 5.4s ease-in-out infinite alternate;
        }}

        .hero-cinematic-scene::before {{
            content: "";
            position: absolute;
            width: 28rem;
            height: 28rem;
            right: 7%;
            top: 11%;
            border-radius: 999px;
            background:
                radial-gradient(circle, rgba(196,181,253,0.30), rgba(45,212,191,0.12) 42%, transparent 66%);
            z-index: 1;
            pointer-events: none;
        }}

        .hero-cinematic-scene::after {{
            content: "";
            position: absolute;
            inset: 10% 6% 16% 12%;
            border: 1px solid rgba(125,211,252,0.16);
            border-radius: 50%;
            transform: rotate(-12deg);
            z-index: 2;
            animation: orbitGlow 16s linear infinite reverse;
        }}

        .hero-asset-wrap {{
            position: absolute;
            right: 9%;
            bottom: -9%;
            width: min(23.5rem, 72%);
            height: 23.5rem;
            overflow: visible;
            border-radius: 18px;
            opacity: 1;
            transform: none;
            z-index: 3;
            display: block;
        }}

        .hero-asset-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            object-position: center bottom;
            display: block;
            filter: drop-shadow(0 30px 45px rgba(2,6,23,0.40)) saturate(1.08) contrast(1.03);
            animation: heroImageDrift 7s ease-in-out infinite alternate;
        }}

        .hero-orbit {{
            position: absolute;
            border-radius: 999px;
            border: 1px dashed rgba(125, 211, 252, 0.24);
            z-index: 2;
            animation: orbitGlow 18s linear infinite;
        }}

        .hero-orbit.one {{ width: 18rem; height: 18rem; right: 16%; top: 9%; }}
        .hero-orbit.two {{ width: 28rem; height: 14rem; right: 3%; top: 28%; transform: rotate(-14deg); animation-duration: 22s; }}

        .hero-data-orb {{
            position: absolute;
            z-index: 4;
            border-radius: 999px;
            box-shadow: 0 18px 34px rgba(2, 6, 23, 0.26);
            animation: nodeFloat 3.6s ease-in-out infinite alternate;
        }}

        .hero-data-orb.teal {{ width: 3.7rem; height: 3.7rem; left: 12%; top: 18%; background: linear-gradient(135deg, #2DD4BF, #7DD3FC); }}
        .hero-data-orb.purple {{ width: 4.2rem; height: 4.2rem; right: 5%; top: 16%; background: linear-gradient(135deg, #C084FC, #EC4899); animation-delay: 0.4s; }}
        .hero-data-orb.blue {{ width: 1.85rem; height: 1.85rem; right: 33%; bottom: 7%; background: linear-gradient(135deg, #60A5FA, #A78BFA); animation-delay: 0.8s; }}

        .hero-floating-card {{
            position: absolute;
            z-index: 5;
            min-width: 8.2rem;
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 18px;
            background: rgba(15,23,42,0.58);
            backdrop-filter: blur(16px);
            padding: 0.74rem 0.82rem;
            color: #F8FAFC;
            box-shadow: 0 18px 34px rgba(2,6,23,0.26);
            animation: chipRise 4s ease-in-out infinite alternate;
        }}

        .hero-floating-card span {{
            display: block;
            color: rgba(203,213,225,0.80);
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 900;
        }}

        .hero-floating-card strong {{
            display: block;
            color: #F8FAFC;
            font-size: 0.98rem;
            margin-top: 0.2rem;
        }}

        .hero-floating-card.score {{ right: 4%; bottom: 12%; animation-delay: 0.35s; }}
        .hero-floating-card.lab {{ left: 7%; top: 16%; animation-delay: 0.7s; }}
        .hero-floating-card.grounding {{ left: 7%; bottom: 12%; }}

        .hero-data-stage {{
            display: none;
            position: absolute;
            inset: 0.95rem;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.30);
            background:
                linear-gradient(135deg, rgba(15,23,42,0.76), rgba(8,47,73,0.44)),
                radial-gradient(circle at 78% 18%, rgba(96,165,250,0.22), transparent 8rem),
                radial-gradient(circle at 20% 80%, rgba(45,212,191,0.26), transparent 9rem);
            overflow: hidden;
            z-index: 3;
        }}

        .hero-data-stage::before {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.10) 1px, transparent 1px),
                linear-gradient(0deg, rgba(255,255,255,0.08) 1px, transparent 1px);
            background-size: 38px 38px;
            opacity: 0.42;
            animation: gridDrift 9s linear infinite;
        }}

        @keyframes gridDrift {{
            from {{ transform: translate(0,0); }}
            to {{ transform: translate(38px,38px); }}
        }}

        .data-node {{
            position: absolute;
            z-index: 2;
            min-width: 5.4rem;
            border: 1px solid rgba(255,255,255,0.36);
            border-radius: 999px;
            background: rgba(255,255,255,0.20);
            backdrop-filter: blur(14px);
            color: #FFFFFF;
            font-weight: 950;
            padding: 0.52rem 0.72rem;
            text-align: center;
            box-shadow: 0 14px 28px rgba(15,23,42,0.18);
            animation: nodeFloat 3.6s ease-in-out infinite alternate;
        }}

        .data-node.raw {{ left: 7%; top: 22%; }}
        .data-node.bronze {{ left: 32%; top: 44%; animation-delay: 0.2s; }}
        .data-node.silver {{ right: 30%; top: 25%; animation-delay: 0.4s; }}
        .data-node.gold {{ right: 8%; top: 48%; animation-delay: 0.6s; background: rgba(45,212,191,0.26); }}

        @keyframes nodeFloat {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-0.45rem); }}
        }}

        .pipeline-line {{
            position: absolute;
            z-index: 1;
            height: 0.22rem;
            border-radius: 999px;
            background: linear-gradient(90deg, transparent, #FFFFFF, transparent);
            opacity: 0.72;
            transform-origin: left center;
            overflow: hidden;
        }}

        .pipeline-line::after {{
            content: "";
            position: absolute;
            inset: 0 auto 0 -35%;
            width: 35%;
            background: linear-gradient(90deg, transparent, #2DD4BF, transparent);
            animation: packetMove 1.7s linear infinite;
        }}

        .pipeline-line.one {{ left: 18%; top: 35%; width: 24%; transform: rotate(20deg); }}
        .pipeline-line.two {{ left: 42%; top: 43%; width: 22%; transform: rotate(-22deg); animation-delay: 0.2s; }}
        .pipeline-line.three {{ right: 16%; top: 42%; width: 22%; transform: rotate(22deg); animation-delay: 0.4s; }}

        @keyframes packetMove {{
            from {{ left: -35%; }}
            to {{ left: 100%; }}
        }}

        .ai-core {{
            position: absolute;
            z-index: 3;
            left: 50%;
            top: 70%;
            transform: translate(-50%, -50%);
            width: 6.2rem;
            height: 6.2rem;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.44);
            background:
                radial-gradient(circle, rgba(255,255,255,0.88) 0 16%, rgba(96,165,250,0.84) 17% 35%, rgba(45,212,191,0.55) 36% 52%, rgba(15,23,42,0.42) 53%);
            box-shadow: 0 0 0 0 rgba(96,165,250,0.35), 0 18px 40px rgba(15,23,42,0.22);
            animation: corePulse 2.1s ease-out infinite;
        }}

        .ai-core::after {{
            content: "IQ";
            position: absolute;
            inset: 0;
            display: grid;
            place-items: center;
            color: #0B1220;
            font-weight: 950;
        }}

        @keyframes corePulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(96,165,250,0.36), 0 18px 40px rgba(15,23,42,0.22); }}
            100% {{ box-shadow: 0 0 0 1.2rem rgba(96,165,250,0), 0 18px 40px rgba(15,23,42,0.22); }}
        }}

        .data-chart {{
            position: absolute;
            z-index: 2;
            right: 6%;
            top: 9%;
            display: flex;
            align-items: end;
            gap: 0.35rem;
            height: 4.5rem;
            padding: 0.7rem;
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 14px;
            background: rgba(255,255,255,0.16);
            backdrop-filter: blur(12px);
        }}

        .data-chart span {{
            width: 0.55rem;
            border-radius: 999px 999px 0 0;
            background: linear-gradient(180deg, #2DD4BF, #38BDF8);
            animation: chartPulse 1.4s ease-in-out infinite alternate;
        }}

        .data-chart span:nth-child(1) {{ height: 1.1rem; }}
        .data-chart span:nth-child(2) {{ height: 2.3rem; animation-delay: 0.15s; }}
        .data-chart span:nth-child(3) {{ height: 3.4rem; animation-delay: 0.3s; }}
        .data-chart span:nth-child(4) {{ height: 2.7rem; animation-delay: 0.45s; }}

        @keyframes chartPulse {{
            to {{ transform: scaleY(0.74); opacity: 0.72; }}
        }}

        @keyframes heroFloat {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-0.55rem); }}
        }}

        .hero-terminal {{
            display: none;
            position: absolute;
            z-index: 4;
            left: 6%;
            bottom: 6.6rem;
            width: min(18rem, 66%);
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 14px;
            background: rgba(15,23,42,0.54);
            backdrop-filter: blur(16px);
            padding: 0.75rem;
            color: #E0F2FE;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.78rem;
            box-shadow: 0 18px 34px rgba(15,23,42,0.20);
        }}

        .hero-terminal div {{
            color: #E0F2FE;
            line-height: 1.7;
        }}

        .hero-terminal div::before {{
            content: ">";
            color: #2DD4BF;
            margin-right: 0.45rem;
        }}

        @keyframes heroImageDrift {{
            from {{ transform: translateX(0) scale(1); }}
            to {{ transform: translateX(-0.55rem) scale(1.025); }}
        }}

        .hero-visual-overlay {{
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(15, 23, 42, 0.28), rgba(15, 23, 42, 0.08) 48%, rgba(15, 23, 42, 0.02)),
                linear-gradient(180deg, transparent, rgba(15, 23, 42, 0.12));
            border-radius: 18px;
            z-index: 1;
            pointer-events: none;
        }}

        .hero-visual-panel {{
            position: absolute;
            left: 1rem;
            right: 1rem;
            bottom: 1rem;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
            z-index: 5;
        }}

        .hero-visual-chip {{
            border: 1px solid rgba(255, 255, 255, 0.34);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.24);
            backdrop-filter: blur(14px);
            padding: 0.65rem;
            color: #FFFFFF;
            font-weight: 950;
            min-height: 4rem;
            box-shadow: 0 12px 26px rgba(15,23,42,0.12);
            animation: chipRise 4s ease-in-out infinite alternate;
        }}

        .hero-visual-chip:nth-child(2) {{
            animation-delay: 0.4s;
        }}

        .hero-visual-chip:nth-child(3) {{
            animation-delay: 0.8s;
        }}

        @keyframes chipRise {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-0.35rem); }}
        }}

        .hero-data-ribbon {{
            position: absolute;
            left: 1.1rem;
            top: 1rem;
            display: flex;
            gap: 0.35rem;
            z-index: 5;
        }}

        .hero-data-ribbon span {{
            width: 0.45rem;
            height: 1.9rem;
            border-radius: 999px;
            background: linear-gradient(180deg, #FFFFFF, rgba(255,255,255,0.18));
            animation: dataBounce 1.6s ease-in-out infinite alternate;
        }}

        .hero-data-ribbon span:nth-child(2) {{ animation-delay: 0.2s; }}
        .hero-data-ribbon span:nth-child(3) {{ animation-delay: 0.4s; }}
        .hero-data-ribbon span:nth-child(4) {{ animation-delay: 0.6s; }}

        @keyframes dataBounce {{
            from {{ transform: scaleY(0.55); opacity: 0.55; }}
            to {{ transform: scaleY(1.05); opacity: 1; }}
        }}

        .hero-visual-chip span {{
            display: block;
            color: rgba(255, 255, 255, 0.78);
            font-size: 0.75rem;
            text-transform: uppercase;
        }}

        .dashboard-card strong {{
            color: #FFFFFF;
        }}

        .dashboard-mini-chart {{
            display: flex;
            align-items: end;
            gap: 0.35rem;
            height: 3.2rem;
            margin-top: 0.65rem;
        }}

        .dashboard-mini-chart span {{
            flex: 1;
            border-radius: 999px 999px 0 0;
            background: rgba(255, 255, 255, 0.72);
        }}

        .dashboard-flow-line {{
            height: 0.4rem;
            border-radius: 999px;
            background: linear-gradient(90deg, #FFFFFF, rgba(255, 255, 255, 0.28));
            margin-top: 0.55rem;
        }}

        .hero-badge-row, .hero-stat-strip, .arch-flow {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.55rem;
            margin-top: 1rem;
        }}

        .hero-badge {{
            color: #F8FAFC !important;
            border-color: rgba(255, 255, 255, 0.26);
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(12px);
        }}

        .arch-flow {{
            border: 1px solid rgba(255, 255, 255, 0.28);
            border-radius: 8px;
            padding: 0.7rem;
            background: rgba(255, 255, 255, 0.13);
        }}

        .arch-flow-step {{
            color: #FFFFFF;
            font-weight: 850;
        }}

        .arch-flow-arrow {{
            color: #DBEAFE;
            font-weight: 950;
        }}

        .hero-stat-strip {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }}

        .hero-stat-card {{
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            background: var(--bg-card);
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
        }}

        .hero-stat-card strong {{
            display: block;
            color: var(--accent-blue);
            font-size: 1.8rem;
            line-height: 1;
        }}

        .product-card, .premium-card, .premium-section, .gradient-card, .glass-card,
        .role-card, .flow-step-card, .feature-highlight-card,
        .persona-card, .quick-start-card, .ai-report-card,
        .ai-section-card, .ai-question-card, .resource-card,
        .readiness-metric-card, .director-brief-card,
        .risk-heatmap-card, .coaching-action-card, .visual-card,
        .loading-card, .empty-state-card {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            color: var(--text-primary);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
            padding: 1rem;
            margin: 0.75rem 0;
            position: relative;
            overflow: hidden;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }}

        .premium-card::before, .premium-section::before, .glass-card::before {{
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-teal), var(--accent-purple), var(--accent-amber));
            background-size: 240% 100%;
            animation: accentTrack 4.5s ease-in-out infinite alternate;
        }}

        .premium-card:hover, .premium-section:hover, .glass-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 22px 48px rgba(15, 23, 42, 0.12);
            border-color: color-mix(in srgb, var(--accent-blue) 42%, var(--border));
        }}

        @keyframes accentTrack {{
            from {{ background-position: 0% 50%; }}
            to {{ background-position: 100% 50%; }}
        }}

        .product-card, .feature-highlight-card,
        .role-card, .resource-card,
        .readiness-metric-card {{
            height: 12rem;
            overflow-y: auto;
        }}

        .gradient-card {{
            background: linear-gradient(135deg, color-mix(in srgb, var(--accent-blue) 11%, var(--bg-card)), color-mix(in srgb, var(--accent-teal) 10%, var(--bg-card)));
        }}

        .product-card, .feature-highlight-card {{
            position: relative;
            overflow: hidden;
            min-height: 8rem;
            border-top: 4px solid var(--accent-blue);
            background:
                linear-gradient(145deg, color-mix(in srgb, var(--accent-blue) 9%, var(--bg-card)), var(--bg-card));
        }}

        .product-card::after, .feature-highlight-card::after {{
            content: "";
            position: absolute;
            right: -2.2rem;
            top: -2.2rem;
            width: 6.5rem;
            height: 6.5rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--accent-teal) 16%, transparent);
        }}

        .feature-highlight-card strong, .product-card strong {{
            display: block;
            margin-top: 0.35rem;
            font-size: 1.05rem;
        }}

        .feature-highlight-card p, .product-card p {{
            position: relative;
            z-index: 1;
            color: var(--text-secondary);
        }}

        .feature-showcase-grid {{
            display: grid;
            grid-template-columns: 1.35fr 0.9fr 0.9fr;
            gap: 0.9rem;
            margin-top: 1rem;
            align-items: stretch;
        }}

        .feature-showcase-grid .feature-highlight-card {{
            height: auto;
            min-height: 11rem;
            border-radius: 18px;
            border-left: 5px solid var(--accent-blue);
            border-top: 1px solid var(--border);
            background:
                radial-gradient(circle at 85% 18%, color-mix(in srgb, var(--accent-blue) 16%, transparent), transparent 7rem),
                linear-gradient(145deg, color-mix(in srgb, var(--accent-teal) 8%, var(--bg-card)), var(--bg-card));
        }}

        .feature-showcase-grid .feature-highlight-card:first-child {{
            grid-row: span 2;
            min-height: 23rem;
            border-left-color: var(--accent-teal);
            background:
                radial-gradient(circle at 88% 14%, color-mix(in srgb, var(--accent-teal) 22%, transparent), transparent 8rem),
                linear-gradient(145deg, color-mix(in srgb, var(--accent-blue) 12%, var(--bg-card)), var(--bg-card));
        }}

        .feature-showcase-grid .feature-highlight-card:nth-child(3) {{
            border-left-color: var(--accent-purple);
        }}

        .feature-showcase-grid .feature-highlight-card:nth-child(4) {{
            grid-column: span 2;
            border-left-color: var(--accent-amber);
            background:
                radial-gradient(circle at 92% 18%, color-mix(in srgb, var(--accent-amber) 14%, transparent), transparent 7rem),
                linear-gradient(145deg, color-mix(in srgb, var(--accent-blue) 8%, var(--bg-card)), var(--bg-card));
        }}

        .glass-card {{
            background: color-mix(in srgb, var(--bg-card) 82%, transparent);
            backdrop-filter: blur(12px);
        }}

        .section-kicker {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            color: var(--accent-teal);
            font-size: 0.78rem;
            font-weight: 950;
            text-transform: uppercase;
        }}

        .section-kicker::before {{
            content: "";
            width: 0.65rem;
            height: 0.65rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--accent-amber), var(--accent-teal));
            box-shadow: 0 0 0 5px color-mix(in srgb, var(--accent-teal) 10%, transparent);
            animation: titleSignal 1.8s ease-in-out infinite alternate;
        }}

        .section-heading {{
            position: relative;
            display: block;
            width: fit-content;
            font-size: clamp(1.65rem, 3vw, 2.35rem);
            font-weight: 950;
            margin: 0.2rem 0 0.25rem;
        }}

        .section-heading::after {{
            content: "";
            position: absolute;
            left: 0;
            right: 22%;
            bottom: -0.18rem;
            height: 0.22rem;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-teal), var(--accent-amber));
            opacity: 0.72;
            animation: headingGlow 2.8s ease-in-out infinite alternate;
        }}

        @keyframes headingGlow {{
            from {{ transform: scaleX(0.72); opacity: 0.48; }}
            to {{ transform: scaleX(1); opacity: 0.9; }}
        }}

        @keyframes titleSignal {{
            from {{ transform: scale(0.82); opacity: 0.72; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}

        .role-card {{
            border-left: 5px solid var(--accent-blue);
        }}

        .role-card strong, .persona-card strong {{
            display: block;
            margin-bottom: 0.35rem;
        }}

        .role-card span, .persona-card span {{
            display: block;
            line-height: 1.45;
        }}

        .foundry-integration-grid, .flow-step-grid,
        .unique-features-grid, .persona-grid,
        .manager-dashboard-grid, .resource-grid {{
            display: grid;
            gap: 0.85rem;
        }}

        .foundry-integration-grid, .unique-features-grid,
        .persona-grid, .manager-dashboard-grid {{
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }}

        .flow-step-grid {{
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }}

        .resource-grid {{
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }}

        .resource-reference-note {{
            border: 1px solid color-mix(in srgb, var(--accent-teal) 40%, var(--border));
            border-radius: 8px;
            background: color-mix(in srgb, var(--accent-teal) 8%, var(--bg-card));
            padding: 0.75rem 0.85rem;
            margin: 0.75rem 0;
            color: var(--text-secondary);
            font-weight: 850;
        }}

        .roadmap-week-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            align-items: stretch;
            gap: 0.85rem;
            margin: 0.75rem 0;
        }}

        .roadmap-week-card {{
            height: 17rem;
            overflow-y: auto;
            scrollbar-width: thin;
        }}

        .roadmap-week-card .ai-section-body {{
            max-height: 11.5rem;
            overflow-y: auto;
            padding-right: 0.25rem;
        }}

        .roadmap-path {{
            position: relative;
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 0.8rem 0 1rem;
        }}

        .roadmap-path::before {{
            content: "";
            position: absolute;
            left: 7%;
            right: 7%;
            top: 2rem;
            height: 3px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-teal), var(--accent-purple));
            opacity: 0.42;
        }}

        .roadmap-node {{
            position: relative;
            z-index: 1;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            padding: 0.85rem;
            min-height: 5rem;
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
        }}

        .roadmap-node-marker {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.25rem;
            height: 2.25rem;
            border-radius: 999px;
            color: #FFFFFF;
            font-weight: 950;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-teal));
            margin-bottom: 0.45rem;
        }}

        .roadmap-node strong {{
            display: block;
        }}

        .flow-step-card {{
            border-top: 4px solid var(--accent-blue);
            min-height: 0;
        }}

        .how-steps-grid {{
            display: grid;
            grid-template-columns: repeat(7, minmax(7rem, 1fr));
            gap: 0.35rem;
            margin-top: 2.2rem;
            position: relative;
            align-items: start;
            padding: 1.2rem 0.2rem 3.4rem;
            min-height: 23rem;
        }}

        .how-steps-grid::before {{
            content: "";
            position: absolute;
            left: 4%;
            right: 4%;
            top: 7.25rem;
            height: 7rem;
            border-radius: 999px;
            border-top: 0.42rem solid color-mix(in srgb, var(--accent-teal) 54%, transparent);
            border-bottom: 0.42rem solid color-mix(in srgb, var(--accent-purple) 38%, transparent);
            transform: skewY(-3deg);
            opacity: 0.9;
            pointer-events: none;
        }}

        .how-steps-grid::after {{
            content: "";
            position: absolute;
            left: 6%;
            right: 6%;
            top: 10.25rem;
            height: 0.32rem;
            border-radius: 999px;
            background:
                linear-gradient(90deg, var(--accent-blue), var(--accent-teal), var(--accent-green), var(--accent-amber), var(--accent-purple));
            box-shadow: 0 0 22px color-mix(in srgb, var(--accent-teal) 20%, transparent);
            animation: pathGlow 3.2s ease-in-out infinite alternate;
            pointer-events: none;
        }}

        @keyframes pathGlow {{
            from {{ opacity: 0.6; filter: saturate(0.9); }}
            to {{ opacity: 1; filter: saturate(1.35); }}
        }}

        .how-step-card {{
            position: relative;
            min-height: 12.2rem;
            overflow: visible;
            padding: 0.85rem 0.68rem 0.9rem;
            border: 1px solid color-mix(in srgb, var(--accent-teal) 20%, var(--border));
            border-radius: 24px;
            background:
                radial-gradient(circle at 50% 0%, color-mix(in srgb, var(--step-color, var(--accent-teal)) 13%, transparent), transparent 5rem),
                linear-gradient(180deg, color-mix(in srgb, var(--bg-card) 90%, transparent), color-mix(in srgb, var(--bg-card-inner) 60%, transparent));
            backdrop-filter: blur(14px);
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.07);
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
            z-index: 2;
            text-align: center;
        }}

        .how-step-card:nth-child(odd) {{
            margin-top: 0;
        }}

        .how-step-card:nth-child(even) {{
            margin-top: 6.3rem;
        }}

        .how-step-card:hover {{
            transform: translateY(-6px) scale(1.02);
            border-color: color-mix(in srgb, var(--step-color, var(--accent-teal)) 52%, var(--border));
            box-shadow: 0 24px 52px rgba(15, 23, 42, 0.14);
        }}

        .how-step-top {{
            display: grid;
            justify-content: center;
            align-items: center;
            gap: 0.35rem;
            margin-bottom: 0.55rem;
        }}

        .how-step-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 3.1rem;
            height: 3.1rem;
            flex: 0 0 auto;
            border-radius: 999px;
            color: #FFFFFF !important;
            font-weight: 950;
            font-size: 1.15rem;
            background: linear-gradient(135deg, var(--step-color, var(--accent-teal)), color-mix(in srgb, var(--step-color, var(--accent-teal)) 55%, #07111F));
            box-shadow: 0 10px 22px color-mix(in srgb, var(--step-color, var(--accent-teal)) 30%, transparent);
            animation: stepPulse 1.9s ease-in-out infinite alternate;
        }}

        @keyframes stepPulse {{
            from {{ box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-blue) 15%, transparent); }}
            to {{ box-shadow: 0 0 0 11px transparent; }}
        }}

        .how-step-icon {{
            position: relative;
            width: 2.35rem;
            height: 1.55rem;
            flex: 0 0 auto;
            justify-self: center;
            border-radius: 0.62rem;
            border: 1px solid color-mix(in srgb, var(--step-color, var(--accent-teal)) 44%, var(--border));
            background:
                radial-gradient(circle at 30% 44%, var(--step-color, var(--accent-teal)) 0 0.13rem, transparent 0.15rem),
                radial-gradient(circle at 54% 44%, var(--step-color, var(--accent-teal)) 0 0.13rem, transparent 0.15rem),
                radial-gradient(circle at 78% 44%, var(--step-color, var(--accent-teal)) 0 0.13rem, transparent 0.15rem),
                color-mix(in srgb, var(--step-color, var(--accent-teal)) 8%, var(--bg-card-inner));
            animation: miniModule 2.6s ease-in-out infinite alternate;
        }}

        .how-step-icon::before {{
            content: "";
            position: absolute;
            left: 0.36rem;
            right: 0.36rem;
            top: -0.45rem;
            height: 0.34rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--step-color, var(--accent-teal)) 65%, transparent);
        }}

        @keyframes miniModule {{
            from {{ transform: translateY(0); opacity: 0.74; }}
            to {{ transform: translateY(-0.18rem); opacity: 1; }}
        }}

        .how-step-title {{
            color: var(--text-primary);
            font-size: 0.9rem;
            font-weight: 950;
            line-height: 1.25;
            margin-bottom: 0.25rem;
        }}

        .how-step-desc {{
            color: var(--text-secondary);
            font-size: 0.77rem;
            line-height: 1.25;
        }}

        .bottom-resource-shell {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--accent-blue) 7%, var(--bg-card)), color-mix(in srgb, var(--accent-teal) 6%, var(--bg-card)));
            padding: 1rem;
            margin-top: 1.25rem;
        }}

        .career-map-shell {{
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: 8px;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--accent-blue) 8%, var(--bg-card)), color-mix(in srgb, var(--accent-purple) 8%, var(--bg-card))),
                var(--bg-card);
            box-shadow: 0 18px 42px rgba(15, 23, 42, 0.10);
            padding: 1.15rem;
            margin: 1rem 0;
        }}

        .mission-map-shell {{
            scroll-margin-top: 1.2rem;
        }}

        .mission-path {{
            position: relative;
        }}

        .mission-card {{
            border: 1px solid var(--border);
        }}

        .mission-level, .mission-title, .mission-focus,
        .mission-skills, .mission-unlock, .mission-arrow {{
            color: inherit;
        }}

        .career-map-shell::before {{
            content: "";
            position: absolute;
            left: 2rem;
            right: 2rem;
            top: 50%;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-teal), var(--accent-purple));
            opacity: 0.28;
            pointer-events: none;
        }}

        .career-map-header {{
            position: relative;
            z-index: 1;
            margin-bottom: 1rem;
        }}

        .career-map-grid {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
            gap: 0.75rem;
            align-items: stretch;
        }}

        .career-mission-card {{
            border: 1px solid var(--border);
            border-top: 4px solid var(--accent-blue);
            border-radius: 8px;
            background: color-mix(in srgb, var(--bg-card) 94%, transparent);
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.10);
            padding: 0.95rem;
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }}

        .career-mission-card:hover {{
            transform: translateY(-4px);
            border-color: color-mix(in srgb, var(--accent-teal) 58%, var(--border));
            box-shadow: 0 22px 44px rgba(15, 23, 42, 0.14);
        }}

        .career-level-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 2.2rem;
            height: 2.2rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-teal));
            color: #FFFFFF;
            font-weight: 950;
            margin-bottom: 0.65rem;
        }}

        .career-role-title {{
            color: var(--text-primary);
            font-weight: 950;
            font-size: 1.02rem;
            line-height: 1.25;
            margin-bottom: 0.55rem;
        }}

        .career-focus,
        .career-ai-activity,
        .career-unlock {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card-inner);
            padding: 0.55rem 0.65rem;
            margin-top: 0.5rem;
            color: var(--text-secondary);
            line-height: 1.42;
        }}

        .career-skill-list {{
            margin-top: 0.55rem;
            color: var(--text-secondary);
            line-height: 1.45;
        }}

        .career-skill-list span {{
            display: inline-flex;
            border: 1px solid var(--border);
            border-radius: 999px;
            background: var(--bg-card-inner);
            padding: 0.22rem 0.5rem;
            margin: 0.14rem;
            font-size: 0.78rem;
            font-weight: 800;
        }}

        .career-unlock {{
            border-color: color-mix(in srgb, var(--accent-purple) 44%, var(--border));
            background: color-mix(in srgb, var(--accent-purple) 10%, var(--bg-card));
            color: var(--text-primary);
            font-weight: 900;
        }}

        .career-arrow {{
            align-self: center;
            justify-self: center;
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 999px;
            border: 1px solid color-mix(in srgb, var(--accent-teal) 44%, var(--border));
            background: var(--bg-card);
            position: relative;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08);
        }}

        .career-arrow::before {{
            content: "";
            position: absolute;
            left: 0.72rem;
            top: 0.72rem;
            width: 0.62rem;
            height: 0.62rem;
            border-top: 2px solid var(--accent-teal);
            border-right: 2px solid var(--accent-teal);
            transform: rotate(45deg);
        }}

        .career-map-note {{
            position: relative;
            z-index: 1;
            margin-top: 1rem;
            color: var(--text-secondary);
            border-left: 4px solid var(--accent-teal);
            padding: 0.7rem 0.85rem;
            background: var(--bg-card-inner);
            border-radius: 8px;
            font-weight: 700;
        }}

        .flow-step-number, .ai-question-number {{
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-teal));
            color: #FFFFFF;
            font-weight: 950;
            margin-bottom: 0.55rem;
        }}

        .flow-step-title, .resource-card-title, .resource-title, .ai-section-heading {{
            font-weight: 950;
            color: var(--text-primary);
        }}

        .ai-report-note, .ai-mini-flow {{
            border: 1px solid var(--border);
            background: var(--bg-card-inner);
            border-radius: 8px;
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            color: var(--text-secondary);
            font-weight: 800;
        }}

        .ai-mini-flow {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.45rem;
            align-items: center;
            padding: 0.6rem;
        }}

        .ai-flow-step {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            padding: 0.5rem 0.6rem;
            color: var(--text-primary);
            min-height: 3.5rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            line-height: 1.25;
        }}

        .ai-flow-step em {{
            color: var(--text-muted);
            font-style: normal;
            font-size: 0.72rem;
            font-weight: 900;
            text-transform: uppercase;
        }}

        .ai-flow-arrow {{
            display: none;
        }}

        .ai-section-card {{
            border-left: 5px solid var(--accent-blue);
            background: var(--bg-card);
            margin: 0.55rem 0;
            padding: 0.85rem;
            max-height: 20rem;
            overflow-y: auto;
        }}

        .ai-section-body {{
            margin-top: 0.4rem;
            line-height: 1.55;
            font-size: 0.95rem;
        }}

        .check-row {{
            display: block;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card-inner);
            padding: 0.48rem 0.6rem;
            margin: 0.28rem 0;
            line-height: 1.35;
        }}

        .check-row::before {{
            content: "";
            display: inline-block;
            width: 0.42rem;
            height: 0.42rem;
            border-radius: 999px;
            background: var(--accent-teal);
            color: var(--accent-teal);
            font-weight: 950;
            margin-right: 0.45rem;
        }}

        .ai-highlight {{
            color: var(--text-primary);
            background: color-mix(in srgb, var(--accent-teal) 18%, transparent);
            border: 1px solid color-mix(in srgb, var(--accent-teal) 36%, transparent);
            border-radius: 999px;
            padding: 0.04rem 0.32rem;
            font-weight: 850;
        }}

        .ai-risk-card {{
            border-left: 5px solid var(--accent-red) !important;
            background: color-mix(in srgb, var(--accent-red) 8%, var(--bg-card));
        }}

        .ai-strength-card {{
            border-left: 5px solid var(--accent-green) !important;
            background: color-mix(in srgb, var(--accent-green) 8%, var(--bg-card));
        }}

        .ai-gap-card {{
            border-left: 5px solid var(--accent-purple) !important;
            background: color-mix(in srgb, var(--accent-purple) 8%, var(--bg-card));
        }}

        .ai-action-card {{
            border-left: 5px solid var(--accent-blue) !important;
            background: color-mix(in srgb, var(--accent-blue) 8%, var(--bg-card));
        }}

        .ai-resource-card {{
            border-left: 5px solid var(--accent-teal) !important;
            background: color-mix(in srgb, var(--accent-teal) 8%, var(--bg-card));
        }}

        .ai-status-ready, .status-ready {{
            color: var(--accent-green);
            border-color: color-mix(in srgb, var(--accent-green) 48%, var(--border));
            background: color-mix(in srgb, var(--accent-green) 12%, var(--bg-card));
        }}

        .ai-status-revision, .status-revision {{
            color: var(--accent-amber);
            border-color: color-mix(in srgb, var(--accent-amber) 48%, var(--border));
            background: color-mix(in srgb, var(--accent-amber) 12%, var(--bg-card));
        }}

        .ai-status-risk, .status-risk {{
            color: var(--accent-red);
            border-color: color-mix(in srgb, var(--accent-red) 48%, var(--border));
            background: color-mix(in srgb, var(--accent-red) 12%, var(--bg-card));
        }}

        .resource-card-icon {{
            font-size: 0.78rem;
            color: var(--accent-teal);
            font-weight: 950;
            margin-bottom: 0.35rem;
        }}

        .resource-card-type, .resource-type-chip {{
            display: inline-flex;
            width: fit-content;
            border: 1px solid color-mix(in srgb, var(--accent-teal) 40%, var(--border));
            border-radius: 999px;
            background: color-mix(in srgb, var(--accent-teal) 10%, var(--bg-card));
            padding: 0.22rem 0.52rem;
            color: var(--accent-teal);
            font-size: 0.74rem;
            font-weight: 950;
            text-transform: uppercase;
        }}

        .resource-card-description, .resource-description {{
            margin-top: 0.35rem;
            line-height: 1.45;
        }}

        .resource-card-link, .resource-link {{
            display: inline-flex;
            margin-top: 0.65rem;
            padding: 0.44rem 0.65rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            color: var(--accent-blue) !important;
            text-decoration: none !important;
            font-weight: 900;
            background: var(--bg-card-inner);
        }}

        .readiness-pulse {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.9rem 0;
        }}

        .pulse-label {{
            display: block;
            color: var(--text-muted);
            font-size: 0.76rem;
            font-weight: 850;
            text-transform: uppercase;
        }}

        .pulse-value {{
            display: block;
            color: var(--text-primary);
            font-weight: 950;
            margin-top: 0.16rem;
        }}

        .pulse-item {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            padding: 0.75rem;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.07);
        }}

        .pulse-dot {{
            display: inline-block;
            width: 0.52rem;
            height: 0.52rem;
            border-radius: 999px;
            background: var(--accent-teal);
            box-shadow: 0 0 0 0 color-mix(in srgb, var(--accent-teal) 42%, transparent);
            animation: pulseDot 1.8s ease-out infinite;
            margin-right: 0.35rem;
        }}

        @keyframes pulseDot {{
            to {{ box-shadow: 0 0 0 10px transparent; }}
        }}

        .capability-meter {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            padding: 1rem;
            margin: 0.85rem 0;
        }}

        .capability-meter-track {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.45rem;
            margin-top: 0.75rem;
        }}

        .capability-meter-step {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card-inner);
            padding: 0.55rem;
            font-weight: 850;
            text-align: center;
        }}

        .capability-meter-step.active {{
            color: #FFFFFF;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-teal));
            border-color: transparent;
        }}

        .ai-agent-timeline {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.6rem;
            margin: 0.75rem 0;
        }}

        .ai-agent-timeline.is-inline {{
            margin-top: 0.75rem;
        }}

        .agent-timeline-step {{
            border: 1px solid var(--border);
            border-top: 3px solid var(--accent-teal);
            border-radius: 8px;
            background: var(--bg-card-inner);
            padding: 0.6rem;
            font-weight: 850;
        }}

        .sidebar-nav {{
            display: grid;
            gap: 0.52rem;
            margin: 0.65rem 0 1rem;
        }}

        .sidebar-brand-card {{
            position: relative;
            overflow: hidden;
            border: 1px solid color-mix(in srgb, var(--accent-blue) 22%, var(--border));
            border-radius: 22px;
            background:
                radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--accent-blue) 18%, transparent), transparent 6rem),
                linear-gradient(135deg, color-mix(in srgb, var(--bg-card) 86%, transparent), color-mix(in srgb, var(--bg-card-inner) 74%, transparent));
            padding: 0.95rem;
            margin: 0.2rem 0 1rem;
            box-shadow: 0 16px 34px rgba(15, 23, 42, 0.08);
        }}

        .sidebar-brand-card::after {{
            content: "";
            position: absolute;
            width: 5rem;
            height: 5rem;
            right: -1.7rem;
            top: -1.7rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--accent-teal) 22%, transparent);
            animation: logoFloat 3.4s ease-in-out infinite alternate;
        }}

        .sidebar-brand-logo {{
            position: relative;
            z-index: 1;
            width: 2.65rem;
            height: 2.65rem;
            border-radius: 14px;
            background:
                linear-gradient(135deg, var(--accent-blue), var(--accent-teal));
            box-shadow: 0 12px 24px color-mix(in srgb, var(--accent-blue) 24%, transparent);
            margin-bottom: 0.65rem;
        }}

        .sidebar-brand-logo::before {{
            content: "";
            position: absolute;
            left: 0.62rem;
            right: 0.62rem;
            top: 0.55rem;
            height: 0.72rem;
            clip-path: polygon(50% 0, 100% 65%, 100% 100%, 0 100%, 0 65%);
            background: #FFFFFF;
            opacity: 0.92;
        }}

        .sidebar-brand-logo::after {{
            content: "";
            position: absolute;
            left: 0.72rem;
            right: 0.72rem;
            bottom: 0.55rem;
            height: 0.85rem;
            border-radius: 0.18rem;
            background:
                linear-gradient(90deg, rgba(255,255,255,0.92) 0 0.18rem, transparent 0.18rem 0.32rem, rgba(255,255,255,0.92) 0.32rem 0.5rem, transparent 0.5rem 0.64rem, rgba(255,255,255,0.92) 0.64rem);
        }}

        .sidebar-brand-title {{
            position: relative;
            z-index: 1;
            color: var(--text-primary);
            font-weight: 950;
            font-size: 1.05rem;
        }}

        .sidebar-brand-subtitle {{
            position: relative;
            z-index: 1;
            color: var(--text-secondary);
            font-size: 0.78rem;
            font-weight: 750;
            margin-top: 0.18rem;
        }}

        .sidebar-nav a {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            position: relative;
            overflow: hidden;
            border: 1px solid color-mix(in srgb, var(--border) 88%, transparent);
            border-radius: 20px;
            background:
                radial-gradient(circle at 0% 50%, color-mix(in srgb, var(--accent-teal) 11%, transparent), transparent 5rem),
                linear-gradient(135deg, color-mix(in srgb, var(--bg-card) 90%, transparent), color-mix(in srgb, var(--bg-card-inner) 70%, transparent));
            backdrop-filter: blur(12px);
            color: var(--text-primary) !important;
            padding: 0.78rem 0.86rem;
            text-decoration: none !important;
            font-weight: 900;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
            transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
        }}

        .sidebar-nav a::before {{
            content: "";
            width: 0.54rem;
            height: 0.54rem;
            flex: 0 0 auto;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--accent-teal), #F472B6);
            box-shadow: 0 0 0 5px color-mix(in srgb, var(--accent-teal) 12%, transparent);
        }}

        .sidebar-nav a::after {{
            content: "";
            position: absolute;
            inset: 0 auto 0 -40%;
            width: 38%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
            transform: skewX(-14deg);
            transition: left 260ms ease;
        }}

        .sidebar-nav a:hover {{
            transform: translateX(0.22rem) translateY(-1px);
            border-color: color-mix(in srgb, var(--accent-teal) 34%, var(--border));
            background:
                radial-gradient(circle at 0% 50%, color-mix(in srgb, var(--accent-teal) 16%, transparent), transparent 6rem),
                linear-gradient(135deg, color-mix(in srgb, var(--accent-purple) 8%, var(--bg-card)), color-mix(in srgb, var(--accent-teal) 8%, var(--bg-card)));
            box-shadow: 0 18px 34px rgba(15, 23, 42, 0.09);
        }}

        .sidebar-nav a:hover::after {{
            left: 100%;
        }}

        .sidebar-nav a:first-child {{
            border-color: color-mix(in srgb, var(--accent-teal) 28%, var(--border));
            background:
                radial-gradient(circle at 0% 50%, color-mix(in srgb, var(--accent-teal) 18%, transparent), transparent 6rem),
                linear-gradient(135deg, color-mix(in srgb, var(--accent-blue) 8%, var(--bg-card)), color-mix(in srgb, var(--accent-teal) 8%, var(--bg-card)));
        }}

        .sidebar-nav a:first-child::before {{
            animation: homePulse 1.45s ease-in-out infinite alternate;
        }}

        @keyframes homePulse {{
            from {{ box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent-teal) 20%, transparent); }}
            to {{ box-shadow: 0 0 0 10px transparent; }}
        }}

        .workspace-header, .ai-workspace-shell {{
            border: 0;
            border-radius: 0;
            background:
                radial-gradient(circle at 0% 50%, color-mix(in srgb, var(--accent-teal) 8%, transparent), transparent 12rem);
            padding: 0.45rem 0 0.15rem;
            margin: 0.55rem 0 0.8rem;
            box-shadow: none;
            position: relative;
            overflow: hidden;
        }}

        .workspace-header::after, .ai-workspace-shell::after {{
            display: none;
        }}

        .ai-command-center {{
            position: relative;
            overflow: hidden;
            border: 1px solid color-mix(in srgb, #EC4899 32%, var(--border));
            border-radius: 34px;
            background:
                radial-gradient(circle at 50% 10%, color-mix(in srgb, #EC4899 26%, transparent), transparent 18rem),
                radial-gradient(circle at 15% 72%, color-mix(in srgb, var(--accent-teal) 20%, transparent), transparent 14rem),
                radial-gradient(circle at 88% 32%, color-mix(in srgb, var(--accent-amber) 15%, transparent), transparent 11rem),
                linear-gradient(145deg, color-mix(in srgb, var(--bg-card) 82%, #0F172A), color-mix(in srgb, var(--bg-card-inner) 72%, #312E81));
            padding: clamp(1rem, 3vw, 2.15rem);
            margin: 1.1rem 0 1.4rem;
            text-align: center;
            box-shadow: 0 34px 78px rgba(15, 23, 42, 0.20), 0 0 0 7px color-mix(in srgb, #EC4899 7%, transparent);
        }}

        .ai-command-center::before {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 18% 42%, color-mix(in srgb, var(--accent-teal) 16%, transparent) 0 0.35rem, transparent 0.38rem),
                radial-gradient(circle at 78% 34%, color-mix(in srgb, #EC4899 15%, transparent) 0 0.28rem, transparent 0.3rem),
                linear-gradient(115deg, transparent 0 42%, rgba(255,255,255,0.11) 50%, transparent 58%);
            opacity: 0.58;
            animation: heroLightWave 7.5s ease-in-out infinite alternate;
            pointer-events: none;
        }}

        @keyframes commandGrid {{
            from {{ background-position: 0 0, 0 0; }}
            to {{ background-position: 44px 44px, 44px 44px; }}
        }}

        .ai-command-inner {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: minmax(150px, 0.25fr) minmax(320px, 0.75fr);
            gap: 1.4rem;
            align-items: center;
            max-width: 980px;
            margin: 0 auto;
        }}

        .ai-command-robot {{
            min-width: 0;
            display: flex;
            justify-content: center;
        }}

        .ai-command-robot img {{
            width: min(13.5rem, 90%);
            filter: drop-shadow(0 28px 34px rgba(2,6,23,0.26));
            animation: heroImageDrift 5s ease-in-out infinite alternate;
        }}

        .ai-command-content {{
            text-align: center;
        }}

        .ai-command-characters {{
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 1;
        }}

        .ai-character {{
            position: absolute;
            width: 4.2rem;
            height: 4.8rem;
            border-radius: 999px 999px 1.2rem 1.2rem;
            background:
                radial-gradient(circle at 36% 26%, #FFFFFF 0 0.16rem, transparent 0.18rem),
                radial-gradient(circle at 62% 26%, #FFFFFF 0 0.16rem, transparent 0.18rem),
                linear-gradient(180deg, var(--char-a, var(--accent-teal)), color-mix(in srgb, var(--char-b, var(--accent-blue)) 70%, #07111F));
            box-shadow: 0 18px 32px rgba(15,23,42,0.16);
            opacity: 0.86;
            animation: characterFloat 4.8s ease-in-out infinite alternate;
        }}

        .ai-character::before {{
            content: "";
            position: absolute;
            left: 0.85rem;
            right: 0.85rem;
            top: 2.15rem;
            height: 0.3rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.72);
        }}

        .ai-character::after {{
            content: "";
            position: absolute;
            left: 50%;
            bottom: -0.95rem;
            width: 5.4rem;
            height: 1.1rem;
            border-radius: 999px;
            transform: translateX(-50%);
            background: color-mix(in srgb, var(--char-a, var(--accent-teal)) 16%, transparent);
            filter: blur(2px);
        }}

        .ai-character.one {{
            --char-a: var(--accent-teal);
            --char-b: var(--accent-blue);
            left: 3.4%;
            bottom: 1.15rem;
        }}

        .ai-character.two {{
            --char-a: var(--accent-green);
            --char-b: var(--accent-teal);
            right: 4.2%;
            top: 1.4rem;
            width: 3.6rem;
            height: 4.15rem;
            animation-delay: 0.7s;
        }}

        .ai-data-bubble {{
            position: absolute;
            border-radius: 1rem;
            border: 1px solid color-mix(in srgb, var(--accent-teal) 32%, var(--border));
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--bg-card) 66%, transparent), color-mix(in srgb, var(--accent-blue) 12%, transparent));
            backdrop-filter: blur(14px);
            box-shadow: 0 16px 34px rgba(15,23,42,0.12);
            animation: bubbleDrift 5.5s ease-in-out infinite alternate;
        }}

        .ai-data-bubble::before {{
            content: "";
            position: absolute;
            inset: 0.7rem;
            border-radius: 999px;
            background:
                linear-gradient(90deg, var(--accent-teal) 0 32%, transparent 32% 42%, var(--accent-green) 42% 64%, transparent 64% 74%, var(--accent-blue) 74%);
        }}

        .ai-data-bubble.one {{
            width: 5.6rem;
            height: 2.7rem;
            left: 17%;
            top: 1.3rem;
        }}

        .ai-data-bubble.two {{
            width: 6.4rem;
            height: 3rem;
            right: 14%;
            bottom: 1.05rem;
            animation-delay: 0.9s;
        }}

        @keyframes characterFloat {{
            from {{ transform: translateY(0) rotate(-2deg); }}
            to {{ transform: translateY(-0.55rem) rotate(2deg); }}
        }}

        @keyframes bubbleDrift {{
            from {{ transform: translateY(0) translateX(0); opacity: 0.66; }}
            to {{ transform: translateY(-0.45rem) translateX(0.35rem); opacity: 1; }}
        }}

        .ai-command-title {{
            color: var(--text-primary);
            font-size: clamp(2rem, 4.2vw, 3.8rem);
            line-height: 1;
            font-weight: 950;
            margin-bottom: 0.6rem;
        }}

        .ai-command-copy {{
            color: var(--text-secondary);
            font-size: 1rem;
            line-height: 1.45;
            max-width: 30rem;
            margin: 0 auto;
        }}

        .ai-command-prompt {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            border: 1px solid color-mix(in srgb, var(--accent-blue) 30%, var(--border));
            border-radius: 999px;
            background: color-mix(in srgb, var(--bg-card) 88%, transparent);
            box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent-teal) 10%, transparent), 0 16px 38px rgba(15,23,42,0.10);
            padding: 0.45rem 0.55rem 0.45rem 1rem;
            margin-top: 1rem;
            width: min(100%, 40rem);
            margin-left: auto;
            margin-right: auto;
        }}

        .ai-command-placeholder {{
            color: var(--text-muted);
            font-weight: 800;
            text-align: left;
        }}

        .ai-command-button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 2.8rem;
            border-radius: 999px;
            padding: 0.7rem 1rem;
            color: #FFFFFF !important;
            text-decoration: none !important;
            font-weight: 950;
            white-space: nowrap;
            background: linear-gradient(135deg, #3B5BFF 0%, #7C3AED 40%, #DB3AB7 72%, #FF8A2A 100%);
            box-shadow: 0 18px 38px rgba(219,58,183,0.30), 0 0 0 5px color-mix(in srgb, #FF8A2A 11%, transparent);
        }}

        .ai-command-button,
        .ai-command-button:visited,
        .ai-command-button:hover,
        .ai-command-button:active {{
            color: #FFFFFF !important;
        }}

        @keyframes sectionSweep {{
            0%, 35% {{ left: -24%; }}
            72%, 100% {{ left: 120%; }}
        }}

        .workspace-tabs {{
            margin-top: 0.6rem;
        }}

        .workspace-input-panel, .workspace-output-panel {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card);
            padding: 0.9rem;
            margin: 0.75rem 0;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
        }}

        .empty-state-icon {{
            display: none;
        }}

        .empty-state-title {{
            font-weight: 950;
            font-size: 1.05rem;
        }}

        .empty-state-copy {{
            color: var(--text-secondary);
            margin-top: 0.3rem;
        }}

        .score-number {{
            color: var(--accent-blue);
            font-size: 3.2rem;
            font-weight: 950;
            line-height: 1;
        }}

        .readiness-bar-strip {{
            height: 0.85rem;
            display: flex;
            overflow: hidden;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--bg-card-inner);
            margin: 0.75rem 0;
        }}

        .readiness-bar-strip span {{
            display: block;
            height: 100%;
        }}

        .action-timeline {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.8rem 0;
        }}

        .timeline-step {{
            border: 1px solid var(--border);
            border-top: 4px solid var(--accent-purple);
            border-radius: 8px;
            background: var(--bg-card-inner);
            padding: 0.8rem;
        }}

        .loading-pulse-bar {{
            height: 0.45rem;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-teal), var(--accent-purple));
            background-size: 240% 100%;
            animation: pulsebar 1.4s ease-in-out infinite alternate;
            margin-bottom: 0.75rem;
        }}

        @keyframes pulsebar {{
            from {{ background-position: 0% 50%; }}
            to {{ background-position: 100% 50%; }}
        }}

        .loading-arch-mini-flow {{
            color: var(--text-muted);
            font-weight: 800;
            margin-top: 0.45rem;
        }}

        .stButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.62);
            background:
                radial-gradient(circle at 18% 24%, rgba(255,255,255,0.18), transparent 2.8rem),
                linear-gradient(135deg, #3B5BFF 0%, #7C3AED 42%, #DB3AB7 72%, #FF8A2A 100%);
            color: #F8FAFC !important;
            font-weight: 950;
            min-height: 3rem;
            min-width: min(100%, 21rem);
            padding: 0.78rem 1.25rem;
            box-shadow:
                0 16px 32px rgba(124, 58, 237, 0.24),
                0 0 0 6px rgba(255, 138, 42, 0.10),
                inset 0 1px 0 rgba(255,255,255,0.18);
            position: relative;
            overflow: hidden;
            letter-spacing: 0;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }}

        .stButton > button *,
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }}

        .stButton {{
            display: flex;
            justify-content: center;
        }}

        .stButton > button::after {{
            content: "";
            position: absolute;
            inset: 0 auto 0 -42%;
            width: 30%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.34), transparent);
            transform: skewX(-16deg);
            transition: left 320ms ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.82);
            box-shadow:
                0 22px 44px rgba(219, 58, 183, 0.25),
                0 0 0 7px rgba(59, 91, 255, 0.12),
                inset 0 1px 0 rgba(255,255,255,0.22);
        }}

        .stButton > button:hover::after {{
            left: 112%;
        }}

        .stButton > button:active {{
            transform: translateY(0);
        }}

        [data-testid="stTabs"] {{
            margin-top: 1rem;
            position: relative;
        }}

        [data-testid="stTabs"] [role="tablist"] {{
            --active-tab-left: 0.5rem;
            --active-tab-width: calc(20% - 0.616rem);
            gap: 0.52rem;
            border-bottom: none;
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            background:
                radial-gradient(circle at 9% 28%, rgba(59,91,255,0.22), transparent 9rem),
                radial-gradient(circle at 66% 14%, rgba(219,58,183,0.18), transparent 10rem),
                radial-gradient(circle at 92% 56%, rgba(255,138,42,0.18), transparent 9rem),
                linear-gradient(135deg, color-mix(in srgb, var(--bg-card) 82%, transparent), color-mix(in srgb, var(--bg-card-inner) 52%, transparent));
            border: 1px solid rgba(219,58,183,0.24);
            border-radius: 999px;
            padding: 0.5rem;
            box-shadow:
                0 22px 48px rgba(15,23,42,0.10),
                0 0 0 6px rgba(59,91,255,0.05),
                inset 0 0 0 1px rgba(255,255,255,0.10);
            overflow: hidden;
            scrollbar-width: none;
            position: relative;
            isolation: isolate;
        }}

        [data-testid="stTabs"] [role="tablist"]:has(> [role="tab"]:nth-child(1)[aria-selected="true"]),
        [data-testid="stTabs"] [role="tablist"]:has(div[data-baseweb="tab"]:nth-child(1)[aria-selected="true"]) {{
            --active-tab-left: 0.5rem;
        }}

        [data-testid="stTabs"] [role="tablist"]:has(> [role="tab"]:nth-child(2)[aria-selected="true"]),
        [data-testid="stTabs"] [role="tablist"]:has(div[data-baseweb="tab"]:nth-child(2)[aria-selected="true"]) {{
            --active-tab-left: calc(20% + 0.404rem);
        }}

        [data-testid="stTabs"] [role="tablist"]:has(> [role="tab"]:nth-child(3)[aria-selected="true"]),
        [data-testid="stTabs"] [role="tablist"]:has(div[data-baseweb="tab"]:nth-child(3)[aria-selected="true"]) {{
            --active-tab-left: calc(40% + 0.308rem);
        }}

        [data-testid="stTabs"] [role="tablist"]:has(> [role="tab"]:nth-child(4)[aria-selected="true"]),
        [data-testid="stTabs"] [role="tablist"]:has(div[data-baseweb="tab"]:nth-child(4)[aria-selected="true"]) {{
            --active-tab-left: calc(60% + 0.212rem);
        }}

        [data-testid="stTabs"] [role="tablist"]:has(> [role="tab"]:nth-child(5)[aria-selected="true"]),
        [data-testid="stTabs"] [role="tablist"]:has(div[data-baseweb="tab"]:nth-child(5)[aria-selected="true"]) {{
            --active-tab-left: calc(80% + 0.116rem);
        }}

        [data-testid="stTabs"] [role="tablist"]::after {{
            content: "";
            position: absolute;
            top: 0.42rem;
            bottom: 0.42rem;
            left: var(--active-tab-left);
            width: var(--active-tab-width);
            border-radius: 999px;
            background:
                radial-gradient(circle at 20% 22%, rgba(255,255,255,0.34), transparent 2.8rem),
                linear-gradient(135deg, rgba(59,91,255,0.92), rgba(124,58,237,0.92) 36%, rgba(219,58,183,0.9) 72%, rgba(255,138,42,0.86));
            opacity: 0.9;
            z-index: 0;
            pointer-events: none;
            box-shadow:
                0 18px 36px rgba(219,58,183,0.22),
                0 0 0 5px rgba(255,138,42,0.08),
                inset 0 1px 0 rgba(255,255,255,0.28);
            transition:
                left 520ms cubic-bezier(0.16, 1, 0.3, 1),
                width 520ms cubic-bezier(0.16, 1, 0.3, 1),
                opacity 260ms ease,
                box-shadow 360ms ease;
        }}

        [data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar {{
            display: none;
        }}

        [data-testid="stTabs"] [data-baseweb="tab-highlight"],
        [data-testid="stTabs"] [data-baseweb="tab-border"],
        [data-testid="stTabs"] [role="tablist"] + div,
        [data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{
            display: none !important;
        }}

        div[data-baseweb="tab"] {{
            position: relative;
            overflow: hidden;
            border-radius: 999px !important;
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--bg-card) 88%, transparent), color-mix(in srgb, var(--tab-accent, #DB3AB7) 9%, var(--bg-card)));
            border: 1px solid color-mix(in srgb, var(--tab-accent, #DB3AB7) 18%, var(--border));
            color: var(--text-primary);
            opacity: 1 !important;
            min-height: 3.65rem;
            padding: 0.46rem 1.05rem 0.46rem 0.66rem;
            box-shadow: 0 10px 24px rgba(15,23,42,0.05);
            transition:
                transform 420ms cubic-bezier(0.16, 1, 0.3, 1),
                border-color 360ms ease,
                box-shadow 420ms ease,
                background 420ms ease,
                filter 420ms ease;
            width: 100%;
            z-index: 3;
        }}

        [data-testid="stTabs"] [role="tab"] {{
            position: relative !important;
            z-index: 4 !important;
            opacity: 1 !important;
        }}

        div[data-baseweb="tab"]::before {{
            content: "";
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background:
                radial-gradient(circle at 50% 50%, #FFFFFF 0 0.17rem, transparent 0.18rem),
                conic-gradient(from 120deg, var(--tab-accent, var(--accent-teal)), color-mix(in srgb, var(--tab-accent, var(--accent-teal)) 45%, var(--accent-green)), var(--accent-blue), var(--tab-accent, var(--accent-teal)));
            box-shadow: 0 0 0 4px color-mix(in srgb, var(--tab-accent, var(--accent-teal)) 10%, transparent), 0 8px 16px rgba(15,23,42,0.10);
            margin-right: 0.48rem;
            flex: 0 0 auto;
            animation: tabOrb 3.6s linear infinite;
        }}

        div[data-baseweb="tab"]::after {{
            content: "";
            position: absolute;
            left: 1.28rem;
            top: 0.76rem;
            width: 0.42rem;
            height: 0.42rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--tab-accent, var(--accent-teal)) 74%, #FFFFFF);
            box-shadow:
                0.48rem 0.74rem 0 -0.08rem color-mix(in srgb, var(--tab-accent, var(--accent-teal)) 60%, #FFFFFF),
                -0.45rem 0.72rem 0 -0.1rem color-mix(in srgb, var(--accent-green) 72%, #FFFFFF);
            opacity: 0.9;
            animation: tabSpark 1.8s ease-in-out infinite alternate;
            pointer-events: none;
        }}

        [data-testid="stTabs"] [role="tab"] > div,
        div[data-baseweb="tab"] > div,
        button[data-baseweb="tab"] > div {{
            position: relative;
            z-index: 5;
        }}

        @keyframes tabOrb {{
            to {{ transform: rotate(360deg); }}
        }}

        @keyframes tabSpark {{
            from {{ transform: translateY(0); opacity: 0.55; }}
            to {{ transform: translateY(-0.12rem); opacity: 1; }}
        }}

        [data-testid="stTabs"] [role="tab"],
        [data-testid="stTabs"] [role="tab"] *,
        div[data-baseweb="tab"],
        div[data-baseweb="tab"] * {{
            color: var(--text-primary) !important;
            -webkit-text-fill-color: var(--text-primary) !important;
            opacity: 1 !important;
        }}

        div[data-baseweb="tab"] p {{
            font-weight: 900 !important;
            white-space: nowrap;
        }}

        div[data-baseweb="tab"]:hover {{
            transform: translateY(-2px);
            border-color: color-mix(in srgb, var(--tab-accent, var(--accent-teal)) 54%, var(--border));
            box-shadow: 0 18px 32px rgba(15,23,42,0.10);
        }}

        div[data-baseweb="tab"][aria-selected="true"],
        [role="tab"][aria-selected="true"] {{
            background:
                linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
            background-size: 100% 100% !important;
            border-color: transparent;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.30);
            transform: translateY(-2px) scale(1.008);
        }}

        div[data-baseweb="tab"][aria-selected="true"],
        div[data-baseweb="tab"][aria-selected="true"] *,
        button[data-baseweb="tab"][aria-selected="true"],
        button[data-baseweb="tab"][aria-selected="true"] *,
        [data-testid="stTabs"] [role="tab"][aria-selected="true"],
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] *,
        div[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] p,
        [role="tab"][aria-selected="true"] p {{
            color: #07111F !important;
            -webkit-text-fill-color: #07111F !important;
            opacity: 1 !important;
            mix-blend-mode: normal !important;
            filter: none !important;
        }}

        [data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] span,
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] div,
        button[data-baseweb="tab"][aria-selected="true"] p,
        div[data-baseweb="tab"][aria-selected="true"] p {{
            position: relative !important;
            z-index: 20 !important;
            color: #07111F !important;
            -webkit-text-fill-color: #07111F !important;
            font-weight: 950 !important;
            text-shadow:
                0 1px 0 rgba(255, 255, 255, 0.62),
                0 0 10px rgba(255, 255, 255, 0.48) !important;
        }}

        div[data-baseweb="tab"][aria-selected="true"]::before,
        [role="tab"][aria-selected="true"]::before {{
            background:
                radial-gradient(circle at 50% 50%, #07111F 0 0.17rem, transparent 0.18rem),
                conic-gradient(from 120deg, #FFFFFF, var(--accent-green), var(--tab-accent, var(--accent-teal)), #FFFFFF);
        }}

        div[data-baseweb="tab"][aria-selected="true"]::after,
        [role="tab"][aria-selected="true"]::after {{
            background: rgba(255,255,255,0.64);
            box-shadow:
                0.48rem 0.74rem 0 -0.08rem rgba(255,255,255,0.58),
                -0.45rem 0.72rem 0 -0.1rem rgba(255,255,255,0.52);
        }}

        div[data-baseweb="tab"]:nth-child(1) {{ --tab-accent: #3B5BFF; }}
        div[data-baseweb="tab"]:nth-child(2) {{ --tab-accent: #7C3AED; }}
        div[data-baseweb="tab"]:nth-child(3) {{ --tab-accent: #DB3AB7; }}
        div[data-baseweb="tab"]:nth-child(4) {{ --tab-accent: #FF8A2A; }}
        div[data-baseweb="tab"]:nth-child(5) {{ --tab-accent: #22D3EE; }}

        div[data-baseweb="tab"]:nth-child(2)::before {{
            border-radius: 0.55rem;
            background:
                linear-gradient(90deg, transparent 0 23%, #FFFFFF 23% 30%, transparent 30% 48%, #FFFFFF 48% 55%, transparent 55%),
                linear-gradient(135deg, var(--tab-accent), color-mix(in srgb, var(--tab-accent) 40%, var(--accent-green)));
        }}

        div[data-baseweb="tab"]:nth-child(3)::before {{
            border-radius: 0.45rem;
            background:
                linear-gradient(90deg, #FFFFFF 0 0.22rem, transparent 0.22rem 0.48rem, #FFFFFF 0.48rem 0.7rem, transparent 0.7rem),
                linear-gradient(135deg, var(--tab-accent), #07111F);
        }}

        div[data-baseweb="tab"]:nth-child(4)::before {{
            border-radius: 0.65rem;
            background:
                radial-gradient(circle at 35% 42%, #FFFFFF 0 0.12rem, transparent 0.13rem),
                radial-gradient(circle at 65% 42%, #FFFFFF 0 0.12rem, transparent 0.13rem),
                linear-gradient(135deg, var(--tab-accent), color-mix(in srgb, var(--tab-accent) 35%, var(--accent-blue)));
        }}

        div[data-baseweb="tab"]:nth-child(5)::before {{
            clip-path: polygon(50% 0, 96% 28%, 96% 72%, 50% 100%, 4% 72%, 4% 28%);
            border-radius: 0;
            background:
                radial-gradient(circle at 50% 50%, #FFFFFF 0 0.15rem, transparent 0.16rem),
                linear-gradient(135deg, var(--tab-accent), var(--accent-teal));
        }}

        textarea, input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] div,
        [data-testid="stNumberInput"] input,
        [data-testid="stRadio"] label {{
            background: var(--bg-card) !important;
            border-color: var(--border) !important;
            color: var(--text-primary) !important;
        }}

        [data-testid="stSelectbox"] > div {{
            border-radius: 14px !important;
            border: 1px solid color-mix(in srgb, var(--accent-amber) 38%, var(--border)) !important;
            background:
                radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--accent-amber) 13%, transparent), transparent 5rem),
                linear-gradient(135deg, color-mix(in srgb, var(--bg-card) 94%, transparent), color-mix(in srgb, var(--accent-blue) 5%, var(--bg-card))) !important;
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08), inset 0 0 0 1px color-mix(in srgb, var(--accent-amber) 8%, transparent);
            position: relative;
            overflow: hidden;
            transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
        }}

        [data-testid="stSelectbox"] > div:hover {{
            transform: translateY(-1px);
            border-color: color-mix(in srgb, var(--accent-amber) 62%, var(--border)) !important;
            box-shadow: 0 18px 36px rgba(15, 23, 42, 0.10), 0 0 0 4px color-mix(in srgb, var(--accent-amber) 9%, transparent);
        }}

        [data-testid="stSelectbox"] label,
        [data-testid="stNumberInput"] label,
        [data-testid="stTextArea"] label {{
            color: var(--text-primary) !important;
            font-weight: 850 !important;
        }}

        [data-testid="stSelectbox"]:focus-within > div,
        [data-testid="stNumberInput"]:focus-within input,
        [data-testid="stTextArea"]:focus-within textarea {{
            border-color: var(--accent-amber) !important;
            box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-amber) 18%, transparent) !important;
        }}

        [data-testid="stRadio"] * {{
            color: var(--text-primary) !important;
        }}

        [data-testid="stCheckbox"] {{
            border: 0;
            background: transparent;
            padding: 0;
            min-height: auto;
            box-shadow: none;
        }}

        [data-testid="stCheckbox"] label {{
            font-weight: 850 !important;
            cursor: pointer;
        }}

        [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p {{
            color: var(--text-primary) !important;
            font-weight: 850 !important;
        }}

        .st-key-theme_switch_button {{
            display: flex;
            justify-content: flex-end;
            align-items: center;
            min-height: 3.7rem;
        }}

        .st-key-theme_switch_button .stButton {{
            display: flex;
            justify-content: flex-end;
            width: 100%;
        }}

        .st-key-theme_switch_button button {{
            position: relative;
            width: 6.1rem !important;
            min-width: 6.1rem !important;
            height: 3.05rem !important;
            min-height: 3.05rem !important;
            border-radius: 999px !important;
            border: 2px solid color-mix(in srgb, var(--accent-teal) 42%, #A1ABBB) !important;
            background: {toggle_track} !important;
            color: transparent !important;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.22), 0 18px 34px rgba(15,23,42,0.12) !important;
            overflow: hidden;
            font-size: 0 !important;
            padding: 0 !important;
        }}

        .st-key-theme_switch_button button::before {{
            content: "{toggle_icon}";
            position: absolute;
            left: 0.28rem;
            top: 0.25rem;
            width: 2.36rem;
            height: 2.36rem;
            border-radius: 999px;
            display: grid;
            place-items: center;
            transform: {toggle_knob};
            color: {toggle_icon_color};
            background: {"linear-gradient(180deg, #FDE68A 0%, #FBBF24 100%)" if theme == "Dark Mode" else "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)"};
            box-shadow: 0 7px 16px rgba(15,23,42,0.18);
            font-size: 1rem;
            transition: transform 220ms ease, background 180ms ease, color 180ms ease;
            z-index: 2;
        }}

        .st-key-theme_switch_button button::after {{
            content: "";
            position: absolute;
            right: 1.05rem;
            top: 0.82rem;
            width: 0.25rem;
            height: 0.25rem;
            border-radius: 999px;
            background: #FDE047;
            box-shadow: 0.72rem 0.72rem 0 #FDE047, 1.1rem -0.05rem 0 rgba(253,224,71,0.92);
            opacity: {toggle_star_opacity};
            transition: opacity 180ms ease;
        }}

        .st-key-theme_switch_button button:hover {{
            transform: translateY(-1px);
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.22), 0 22px 42px rgba(15,23,42,0.16) !important;
        }}

        .st-key-theme_switch_button button > div {{
            color: transparent !important;
            opacity: 0 !important;
            font-size: 0 !important;
        }}

        .st-key-theme_switch_button button * {{
            color: transparent !important;
            opacity: 0 !important;
            font-size: 0 !important;
        }}

        pre, code {{
            white-space: pre-wrap;
            background: var(--bg-card-inner) !important;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary) !important;
        }}

        .ai-table-card {{
            display: grid;
            gap: 0.5rem;
        }}

        .ai-table-row {{
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-card-inner);
            padding: 0.55rem 0.65rem;
        }}

        .ai-table-row strong {{
            display: block;
            color: var(--accent-blue);
            margin-bottom: 0.2rem;
        }}

        @media (max-width: 960px) {{
            .hero-grid, .hero-stat-strip, .foundry-integration-grid, .flow-step-grid,
            .unique-features-grid, .persona-grid, .manager-dashboard-grid,
            .resource-grid, .action-timeline, .roadmap-week-grid,
            .feature-showcase-grid, .readiness-pulse, .capability-meter-track, .ai-agent-timeline,
            .ai-command-inner, .ai-mini-flow, .roadmap-path {{
                grid-template-columns: 1fr;
            }}
            .career-map-shell::before {{
                display: none;
            }}
            .career-map-grid {{
                grid-template-columns: 1fr;
            }}
            .career-arrow {{
                width: 100%;
                height: 1.1rem;
                border: none;
                box-shadow: none;
                background: transparent;
            }}
            .career-arrow::before {{
                left: calc(50% - 0.31rem);
                top: 0.1rem;
                transform: rotate(135deg);
            }}
            .hero-cinematic-scene {{
                min-height: 24rem;
            }}
            .hero-asset-wrap {{
                width: 80%;
                right: 0;
            }}
            .ai-command-content {{
                text-align: center;
            }}
            .ai-command-copy,
            .ai-command-prompt {{
                margin-left: auto;
                margin-right: auto;
            }}
            .hero-visual-panel {{
                grid-template-columns: 1fr;
            }}
            .hero-visual-chip {{
                min-height: auto;
            }}
            .roadmap-path::before {{
                display: none;
            }}
            .how-steps-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
                padding-bottom: 1rem;
                min-height: auto;
            }}
            .how-steps-grid::before {{
                display: none;
            }}
            .how-step-card {{
                min-height: 12rem;
                max-height: none;
                overflow: visible;
            }}
            .how-step-card:nth-child(even) {{
                margin-top: 0;
            }}
            .brand-shell {{
                align-items: flex-start;
                flex-wrap: wrap;
            }}
            .product-card, .feature-highlight-card,
            .role-card, .resource-card,
            .readiness-metric-card {{
                height: auto;
                max-height: 14rem;
            }}
            .feature-showcase-grid .feature-highlight-card:first-child,
            .feature-showcase-grid .feature-highlight-card:nth-child(4) {{
                grid-column: auto;
                grid-row: auto;
                min-height: 11rem;
            }}
        }}

        @media (max-width: 1100px) {{
            .career-map-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 700px) {{
            .how-steps-grid {{
                grid-template-columns: 1fr;
            }}
            .how-step-card {{
                min-height: auto;
                max-height: none;
                overflow: visible;
            }}
            .career-map-grid {{
                grid-template-columns: 1fr;
            }}
            .career-mission-card {{
                height: auto;
                max-height: 18rem;
            }}
            .hero-cta-row a {{
                width: 100%;
            }}
            .topbar-brand-card, .top-toggle-shell {{
                min-height: auto;
            }}
            .hero-mini-nav-links {{
                display: none;
            }}
            .hero-shell {{
                min-height: auto;
                width: 100%;
                margin-left: 0;
            }}
            .hero-floating-card {{
                position: relative;
                left: auto !important;
                right: auto !important;
                bottom: auto !important;
                top: auto !important;
                display: inline-block;
                margin: 0.4rem;
            }}
            .hero-terminal {{
                display: none;
            }}
            .ai-command-prompt {{
                border-radius: 20px;
                flex-direction: column;
                align-items: stretch;
                padding: 0.8rem;
            }}
            .ai-command-button {{
                width: 100%;
            }}
            
        }}
        
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header():
    st.markdown(
        """
        <div class="brand-shell">
          <div class="brand-logo-mark" aria-label="DataDojo IQ logo"></div>
          <div class="brand-text-block">
            <div class="brand-wordmark"><span class="brand-data">Data</span><span class="brand-dojo">Dojo</span> <span class="brand-iq">IQ</span></div>
            <div class="brand-subtitle">Foundry-powered Data Engineering Readiness</div>
          </div>
          <div class="brand-badge">Foundry IQ Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    left, right = st.columns([0.76, 0.24])
    with left:
        st.markdown(
            """
            <div class="topbar-brand-card topbar-brand">
              <div class="brand-logo-mark" aria-label="DataDojo IQ logo"></div>
              <div class="brand-text-block">
                <div class="brand-wordmark"><span class="brand-data">Data</span><span class="brand-dojo">Dojo</span> <span class="brand-iq">IQ</span></div>
                <div class="brand-subtitle">Foundry-powered Data Engineering Readiness</div>
              </div>
              <div class="brand-badge">Foundry IQ Platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        current_mode = "Dark Mode" if st.session_state["theme"] == "Dark Mode" else "Light Mode"
        current_dark = st.session_state["theme"] == "Dark Mode"
        if st.button(current_mode.upper(), key="theme_switch_button"):
            next_dark = not current_dark
            st.session_state["theme"] = "Dark Mode" if next_dark else "Light Mode"
            st.query_params["theme"] = "dark" if next_dark else "light"
            st.rerun()


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-card">
              <div class="sidebar-brand-logo"></div>
              <div class="sidebar-brand-title">DataDojo IQ</div>
              <div class="sidebar-brand-subtitle">Foundry-powered readiness</div>
            </div>
            <div class="sidebar-nav">
              <a href="#home">Home</a>
              <a href="#how-it-works">How It Works</a>
              <a href="#mission-map">Mission Map</a>
              <a href="#foundry-integration">Foundry Integration</a>
              <a href="#ai-workspace">AI Workspace</a>
              <a href="#resources">Resources</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("### Global Context")
        role = st.selectbox("Role", ROLES)
        domain = st.selectbox("Domain", DOMAINS)
        data_product = st.selectbox("Data Product", DATA_PRODUCTS)
        st.markdown("---")
        st.markdown("### Project Identity")
        st.write("Challenge Track: Reasoning Agents")
        st.write("Microsoft Layer: Foundry IQ")
        st.write("Agent: DataDojo-IQ-Orchestrator")
        st.write("Data Policy: Synthetic data only")
    return role, domain, data_product


def foundry_spinner():
    st.markdown(
        """
        <div class="loading-card">
          <div class="loading-pulse-bar"></div>
          <p>Generating grounded response from synthetic Data Engineering knowledge files...</p>
          <div class="loading-arch-mini-flow">Foundry Agent is reviewing the synthetic knowledge base.</div>
          <div class="ai-agent-timeline">
            <div class="agent-timeline-step">User Request</div>
            <div class="agent-timeline-step">Foundry Agent</div>
            <div class="agent-timeline-step">Foundry IQ Grounding</div>
            <div class="agent-timeline-step">Response Generated</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.spinner("🤖 Foundry Agent is consulting the Foundry IQ Vector Index...")


def render_empty_state(icon, title="Ready when you are", message="Configure your inputs above and click Generate to receive a Foundry-grounded response."):
    st.markdown(
        f"""
        <div class="empty-state-card">
          <div class="empty-state-icon"></div>
          <div class="section-kicker">{safe_text(icon)}</div>
          <div class="empty-state-title">{safe_text(title)}</div>
          <div class="empty-state-copy">{safe_text(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def call_foundry(prompt):
    policy = """
Safety requirements:
- Use only generic synthetic Data Engineering examples.
- Do not use real company names, real table names, named enterprise source systems, customer data, employee data, credentials, messages, secrets, or confidential information.
- Keep all domains, data products, tables, learners, and scenarios fictional and generic.
Response style:
- Do not mention Streamlit, hackathon submission details, app architecture, or the request pipeline.
- Do not include process, architecture, or generation-metadata sections.
- Do not return markdown tables.
- Prefer short numbered sections with concise bullets.
- Return only the learning, assessment, practice, manager, or director content requested.
"""
    return ask_foundry_agent(f"{policy}\n\n{prompt}")


def highlight_keywords(text):
    output = safe_text(text)
    for keyword in sorted(KEYWORDS, key=len, reverse=True):
        pattern = re.compile(rf"(?<![\w>])({re.escape(keyword)})(?![\w<])", re.IGNORECASE)
        output = pattern.sub(r'<span class="ai-highlight">\1</span>', output)
    output = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", output)
    return output


def status_badge_html(status):
    label = str(status or "Not Ready")
    if label == "Ready":
        css = "ai-status-ready"
    elif "Needs Revision" in label:
        css = "ai-status-revision"
    else:
        css = "ai-status-risk"
    return f'<span class="status-badge {css}">{safe_text(label)}</span>'


def readiness_from_score(score):
    if score >= 75:
        return "Ready"
    if score >= 60:
        return "Needs Revision"
    return "Not Ready"


def normalize_status(status):
    value = str(status or "")
    if "Ready" in value and "Revision" not in value and "Not" not in value:
        return "Ready"
    if "Needs Revision" in value:
        return "Needs Revision"
    return "Not Ready"


def section_icon(title):
    title_lower = title.lower()
    for key, icon in SECTION_ICONS.items():
        if key in title_lower:
            return icon
    return "Insight"


def card_class_for_title(title):
    text = title.lower()
    if "risk" in text or "missing" in text or "weak" in text:
        return "ai-section-card ai-risk-card"
    if "strength" in text or "correct" in text:
        return "ai-section-card ai-strength-card"
    if "gap" in text:
        return "ai-section-card ai-gap-card"
    if "resource" in text or "sources" in text:
        return "ai-section-card ai-resource-card"
    if "recommend" in text or "fix" in text or "action" in text or "next" in text:
        return "ai-section-card ai-action-card"
    return "ai-section-card"


def split_sections(text):
    raw = str(text or "").strip()
    if not raw:
        return []
    raw = re.sub(r"```(?:markdown|text)?|```", "", raw).strip()
    parts = re.split(r"\n\s*(?=(?:#{1,4}\s*)?\d{0,2}[\.\)]?\s*[A-Z][A-Za-z /\-&]+:?\s*$)", raw, flags=re.MULTILINE)
    sections = []
    for part in parts:
        lines = [line.strip() for line in part.splitlines() if line.strip()]
        if not lines:
            continue
        heading = re.sub(r"^#{1,6}\s*", "", lines[0])
        heading = re.sub(r"^\d{1,2}[\.\)]\s*", "", heading).strip(": ")
        body = "\n".join(lines[1:]).strip()
        if body:
            sections.append((heading, body))
    return sections


def should_skip_ai_line(line):
    blocked = [
        "streamlit app",
        "grounded response",
        "generated by microsoft foundry",
        "reasoning agents challenge",
        "hackathon",
        "synthetic data only",
    ]
    lowered = line.lower()
    if "foundry agent" in lowered and "streamlit" in lowered:
        return True
    return any(item in lowered for item in blocked)


def body_to_html(body):
    rows = []
    table_rows = []
    for raw_line in str(body or "").splitlines():
        line = re.sub(r"^#{1,6}\s*", "", raw_line.strip())
        line = re.sub(r"^\*\*(.*?)\*\*:?\s*$", r"\1", line)
        if not line:
            continue
        if should_skip_ai_line(line):
            continue
        if "|" in line:
            cells = [cell.strip() for cell in line.strip("|").split("|") if cell.strip()]
            if not cells or all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                continue
            if len(cells) >= 2:
                table_rows.append(
                    f'<div class="ai-table-row"><strong>{highlight_keywords(cells[0])}</strong><span>{highlight_keywords(" | ".join(cells[1:]))}</span></div>'
                )
                continue
        if re.match(r"^[-*]\s+", line):
            rows.append(f'<span class="check-row">{highlight_keywords(re.sub(r"^[-*]\s+", "", line))}</span>')
        elif re.match(r"^\d+[\.\)]\s+", line):
            item = re.sub(r"^\d+[\.\)]\s+", "", line)
            rows.append(f'<span class="check-row">{highlight_keywords(item)}</span>')
        else:
            rows.append(f"<p>{highlight_keywords(line)}</p>")
    if table_rows:
        rows.append(f'<div class="ai-table-card">{"".join(table_rows)}</div>')
    return "".join(rows) or f"<p>{highlight_keywords(body)}</p>"


def format_foundry_response(response_text: str) -> str:
    sections = split_sections(response_text)
    if not sections:
        return f'<div class="ai-section-card"><div class="ai-section-body">{body_to_html(response_text)}</div></div>'

    html = ""
    for title, body in sections:
        label = section_icon(title)
        html += (
            f'<div class="{card_class_for_title(title)}">'
            f'<div class="ai-section-heading"><span class="resource-chip">{safe_text(label)}</span> {safe_text(title)}</div>'
            f'<div class="ai-section-body">{body_to_html(body)}</div>'
            "</div>"
        )
    return html


def render_foundry_response_card(title: str, response_text: str):
    st.markdown(
        f"""
        <div class="ai-report-card">
          <div class="ai-report-note">🤖 Foundry Agent | Foundry IQ grounded guidance</div>
          <h3>{safe_text(title)}</h3>
          {format_foundry_response(response_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_resource_cards(labels=None):
    keywords = " ".join(str(label).lower() for label in (labels or []))
    selected = []
    if labels:
        for key, resources in RESOURCE_CATALOG.items():
            if key in keywords:
                selected.extend(resources)
        for resource_group in RESOURCE_CATALOG.values():
            for resource in resource_group:
                searchable = f'{resource["title"]} {resource["description"]}'.lower()
                if any(str(label).lower() in searchable for label in labels):
                    selected.append(resource)
    if not selected:
        selected = (
            RESOURCE_CATALOG["metadata"]
            + RESOURCE_CATALOG["quality"]
            + RESOURCE_CATALOG["sql"]
            + RESOURCE_CATALOG["foundry"]
        )
    unique = []
    seen = set()
    for resource in selected:
        if resource["url"] not in seen:
            seen.add(resource["url"])
            unique.append(resource)
    cards = ""
    for resource in unique[:6]:
        cards += (
            '<div class="resource-card">'
            '<div class="resource-card-icon">External learning resource</div>'
            f'<div class="resource-type-chip">{safe_text(resource["type"])}</div>'
            f'<div class="resource-title">{safe_text(resource["title"])}</div>'
            f'<div class="resource-description">{safe_text(resource["description"])}</div>'
            f'<a class="resource-link" href="{safe_text(resource["url"])}" target="_blank" rel="noopener">Open resource</a>'
            "</div>"
        )
    st.markdown(f'<div class="resource-grid">{cards}</div>', unsafe_allow_html=True)


def render_resource_reference_note():
    st.markdown(
        """
        <div class="resource-reference-note">
          Foundry may recommend revision topics in the feedback. Refer to the External Learning Resources section at the bottom of this page to learn and practice with clickable public links.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_chips(text):
    candidates = []
    for line in str(text or "").splitlines():
        if "source" in line.lower() or "knowledge" in line.lower() or "vector" in line.lower():
            clean = re.sub(r"^[\s\-*\d\.\):]+", "", line).strip()
            if clean:
                candidates.append(clean[:120])
    if not candidates:
        candidates = ["Synthetic Data Engineering knowledge files", "Foundry IQ Vector Index"]
    chips = "".join(f'<span class="ai-source-chip">{safe_text(item)}</span>' for item in candidates[:6])
    st.markdown(chips, unsafe_allow_html=True)


def render_hero():
    hero_asset = asset_data_uri("datadojo_robot.png") or asset_data_uri("hero_banner_transparent.png") or asset_data_uri("hero_banner.png")
    hero_image = f'<div class="hero-asset-wrap"><img src="{hero_asset}" alt="DataDojo IQ readiness visual"></div>' if hero_asset else ""
    st.markdown(
        f"""
        <div id="home"></div>
        <div class="hero-shell">
          <div class="hero-mini-nav">
            <div>DataDojo IQ</div>
            <div class="hero-mini-nav-links">
              <span>Roadmaps</span>
              <span>Assessment</span>
              <span>Config Lab</span>
              <span>Insights</span>
            </div>
          </div>
          <div class="hero-grid">
            <div class="hero-left">
              <div class="hero-home-mark"><span class="hero-home-icon"><span></span></span><span>AI Readiness Command Center</span></div>
              <div class="hero-tagline">From KT Calls to Data Engineering Readiness</div>
              <h1 class="hero-title">DataDojo <span>IQ</span></h1>
              <p class="hero-copy">A Foundry-powered readiness command center for learning paths, scored assessments, config labs, and leadership insights.</p>
              <div class="hero-badge-row">
                <span class="hero-badge">Foundry IQ</span>
                <span class="hero-badge">AI Readiness</span>
                <span class="hero-badge">Synthetic Data Only</span>
              </div>
              <div class="hero-cta-row">
                <a href="#ai-workspace" class="primary-cta">Start AI Readiness Journey</a>
                <a href="#how-it-works" class="secondary-cta">View How It Works</a>
              </div>
            </div>
            <div class="hero-right">
              <div class="hero-cinematic-scene">
                <div class="hero-orbit one"></div>
                <div class="hero-orbit two"></div>
                <div class="hero-data-orb teal"></div>
                <div class="hero-data-orb purple"></div>
                <div class="hero-data-orb blue"></div>
                {hero_image}
                <div class="hero-floating-card grounding">
                  <span>Grounding</span>
                  <strong>Foundry IQ</strong>
                </div>
                <div class="hero-floating-card lab">
                  <span>Practice</span>
                  <strong>Config Lab</strong>
                </div>
                <div class="hero-floating-card score">
                  <span>Readiness</span>
                  <strong>AI Score</strong>
                </div>
                <div class="hero-terminal">
                  <div>Ingest Synthetic Context</div>
                  <div>Ground With Foundry IQ</div>
                  <div>Generate Readiness Action</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_readiness_pulse(role):
    roadmap_status = "Generated" if st.session_state.get("generated_roadmap") else "Ready to generate"
    quiz_status = st.session_state.get("readiness_status") or "Not started"
    config_status = "Completed" if st.session_state.get("config_score") is not None else "Not started"
    manager_status = "Generated" if st.session_state.get("manager_response") else "Awaiting results"
    items = [
        ("Role Selected", role),
        ("AI Roadmap", roadmap_status),
        ("Quiz Readiness", quiz_status),
        ("Config Lab", config_status),
        ("Manager Insight", manager_status),
    ]
    cards = "".join(
        '<div class="pulse-item">'
        '<span class="pulse-dot"></span>'
        f'<span class="pulse-label">{safe_text(label)}</span>'
        f'<span class="pulse-value">{safe_text(value)}</span>'
        '</div>'
        for label, value in items
    )
    st.markdown(f'<div class="readiness-pulse">{cards}</div>', unsafe_allow_html=True)


def render_ai_command_center():
    robot_asset = asset_data_uri("datadojo_robot.png")
    robot_image = (
        f'<img src="{robot_asset}" alt="DataDojo IQ AI readiness assistant">'
        if robot_asset
        else '<div class="empty-state-icon"></div>'
    )
    st.markdown(
        f"""
        <div class="ai-command-center">
          <div class="ai-command-characters" aria-hidden="true">
            <div class="ai-character one"></div>
            <div class="ai-character two"></div>
            <div class="ai-data-bubble one"></div>
            <div class="ai-data-bubble two"></div>
          </div>
          <div class="ai-command-inner">
            <div class="ai-command-robot">{robot_image}</div>
            <div class="ai-command-content">
              <div class="section-kicker">Foundry Agent Ready</div>
              <div class="ai-command-title">Ask the readiness agent</div>
              <div class="ai-command-copy">One context. One AI flow. Roadmap, quiz, lab, and insight generation powered by Foundry IQ.</div>
              <div class="ai-command-prompt">
                <span class="ai-command-placeholder">Build my Data Engineering readiness journey</span>
                <a class="ai-command-button" href="#learning-roadmap-anchor">Start AI Journey</a>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_capability_meter(role):
    role_index = {
        "Junior Data Engineer": 0,
        "Data Engineer": 1,
        "Senior Data Engineer / Manager": 2,
        "Director": 3,
    }.get(role, 0)
    labels = ["Beginner", "Developing", "Ready", "Leader"]
    steps = "".join(
        f'<div class="capability-meter-step {"active" if idx <= role_index else ""}">{safe_text(label)}</div>'
        for idx, label in enumerate(labels)
    )
    st.markdown(
        '<div class="capability-meter">'
        '<div class="section-kicker">Capability Meter</div>'
        '<div class="section-heading">Role Growth Signal</div>'
        f'<div class="capability-meter-track">{steps}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_agent_activity_timeline():
    st.markdown(
        """
        <div class="ai-agent-timeline">
          <div class="agent-timeline-step">User Request</div>
          <div class="agent-timeline-step">🤖 Foundry Agent</div>
          <div class="agent-timeline-step">Foundry IQ Grounding</div>
          <div class="agent-timeline-step">Response Generated</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_role_hierarchy_visual():
    cards = []
    labels = [
        ("Junior Data Engineer", "Task-level execution inside a data product", "Owns task execution"),
        ("Data Engineer", "Runs one synthetic data product end-to-end", "Owns a data product"),
        ("Senior DE / Manager", "Manages domain readiness and team standards", "Owns domain/team readiness"),
        ("Director", "Oversees multiple domains and maturity patterns", "Owns strategic readiness"),
    ]
    for title, desc, owner in labels:
        cards.append(
            f'<div class="role-card"><strong>{safe_text(title)}</strong><span>{safe_text(desc)}</span><div class="resource-chip">{safe_text(owner)}</div></div>'
        )
    st.markdown(
        f"""
        <div class="premium-card">
          <div class="section-kicker">Role Hierarchy</div>
          <div class="section-heading">Junior to Engineer to Manager to Director</div>
          <div class="foundry-integration-grid">{''.join(cards)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_foundry_integration_block():
    cards = [
        ("🤖", "Foundry Agent", "Routes learner, lab, manager, and director prompts through the readiness orchestrator."),
        ("IQ", "Foundry IQ Grounding", "Uses uploaded synthetic Data Engineering knowledge files as the intelligence layer."),
        ("DE", "Readiness Reasoning", "Turns role, domain, score, and config evidence into next-step guidance."),
        ("SAFE", "Synthetic-Only Policy", "Keeps examples generic and avoids confidential or real-world operational data."),
    ]
    html = "".join(
        f'<div class="product-card"><div class="career-level-badge">{safe_text(icon)}</div><strong>{safe_text(title)}</strong><p>{safe_text(desc)}</p></div>'
        for icon, title, desc in cards
    )
    st.markdown(
        f"""
        <div id="foundry-integration"></div>
        <div class="premium-card">
          <div class="section-kicker">Foundry Integration</div>
          <div class="section-heading">Foundry IQ Command Center</div>
          <p class="section-copy">Every workflow is grounded, interpreted, and turned into practical readiness action.</p>
          <div class="foundry-integration-grid">{html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_it_works():
    steps = [
        ("Choose Context", "Use the left menu to select role, domain, and data product.", "var(--accent-teal)"),
        ("Set Skill", "Pick target skill and confidence level.", "var(--accent-blue)"),
        ("Generate Roadmap", "Create a Foundry IQ plan.", "var(--accent-green)"),
        ("Take AI Quiz", "Answer grounded questions.", "var(--accent-amber)"),
        ("Get Feedback", "Review score and gaps.", "var(--accent-purple)"),
        ("Practice Config Lab", "Solve a pipeline scenario.", "var(--accent-teal)"),
        ("View Insights", "Summarize readiness risks.", "var(--accent-blue)"),
    ]
    step_cards = "".join(
        f'<div class="how-step-card" style="--step-color:{accent}">'
        '<div class="how-step-top">'
        f'<div class="how-step-number">{i}</div>'
        '<div class="how-step-icon" aria-hidden="true"></div>'
        '</div>'
        f'<div class="how-step-title">{safe_text(title)}</div>'
        f'<div class="how-step-desc">{safe_text(desc)}</div>'
        '</div>'
        for i, (title, desc, accent) in enumerate(steps, 1)
    )
    features = [
        ("Roadmap", "Role-specific learning plans", "Four-week paths based on role, domain, product, skill, hours, and confidence."),
        ("Assessment", "AI-generated readiness checks", "Grounded quiz questions, automatic scoring, answer review, and targeted feedback."),
        ("Config Lab", "Scenario practice evaluator", "Synthetic pipeline challenges with score-style feedback and best-practice corrections."),
        ("Leadership", "Manager and director briefs", "Roll learner results into domain readiness, risks, coaching actions, and 30-day plans."),
    ]
    feature_cards = "".join(
        f'<div class="feature-highlight-card"><div class="section-kicker">{safe_text(label)}</div><strong>{safe_text(title)}</strong><p>{safe_text(desc)}</p></div>'
        for label, title, desc in features
    )
    st.markdown(
        f"""
        <div id="how-it-works"></div>
        <div class="how-it-works-shell premium-card">
          <div class="section-kicker">How It Works</div>
          <div class="section-heading">How It Works</div>
          <p class="section-copy">Choose context, generate grounded learning, prove readiness, and roll the results up into manager and director views.</p>
          <div class="how-steps-grid">
            {step_cards}
          </div>
        </div>
        <div class="premium-card">
          <div class="section-kicker">Product Highlights</div>
          <div class="section-heading">Built Like a Readiness Product, Not a Form</div>
          <div class="feature-showcase-grid">{feature_cards}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_career_mission_map():
    missions = [
        {
            "level": "01",
            "role": "Junior Data Engineer",
            "focus": "Task execution and pipeline basics",
            "skills": ["metadata configuration", "validation", "basic troubleshooting"],
            "activity": "Learning roadmap, quiz, config practice",
            "unlock": "Data Product Ownership",
            "accent": "var(--accent-blue)",
        },
        {
            "level": "02",
            "role": "Data Engineer",
            "focus": "Own one data product",
            "skills": ["load strategy", "data quality", "transformations", "monitoring"],
            "activity": "Scenario labs and readiness assessment",
            "unlock": "Domain Leadership",
            "accent": "var(--accent-teal)",
        },
        {
            "level": "03",
            "role": "Senior Data Engineer / Manager",
            "focus": "Guide team and domain readiness",
            "skills": ["architecture review", "delivery risk", "coaching", "standards"],
            "activity": "Manager insights and team action plan",
            "unlock": "Multi-domain Strategy",
            "accent": "var(--accent-purple)",
        },
        {
            "level": "04",
            "role": "Director",
            "focus": "Oversee multiple domains",
            "skills": ["capability maturity", "governance", "strategic readiness"],
            "activity": "Executive readiness brief",
            "unlock": "Enterprise Data Excellence",
            "accent": "var(--accent-blue)",
        },
    ]

    cards = []
    for index, mission in enumerate(missions):
        skills = "".join(f"<span>{safe_text(skill)}</span>" for skill in mission["skills"])
        cards.append(
            '<div class="career-mission-card mission-card" style="border-top-color:'
            f'{mission["accent"]}">'
            f'<div class="career-level-badge mission-level">{safe_text(mission["level"])}</div>'
            f'<div class="career-role-title mission-title">{safe_text(mission["role"])}</div>'
            f'<div class="career-focus mission-focus"><strong>Mission Focus:</strong> {safe_text(mission["focus"])}</div>'
            f'<div class="career-skill-list mission-skills"><strong>Key Skills:</strong><br>{skills}</div>'
            f'<div class="career-ai-activity"><strong>AI Activity:</strong> {safe_text(mission["activity"])}</div>'
            f'<div class="career-unlock mission-unlock"><strong>Unlocks:</strong> {safe_text(mission["unlock"])}</div>'
            "</div>"
        )
        if index < len(missions) - 1:
            cards.append('<div class="career-arrow mission-arrow" aria-hidden="true"></div>')

    mission_html = "".join(cards)
    st.markdown(
        '<div id="mission-map"></div>'
        '<section class="career-map-shell mission-map-shell">'
        '<div class="career-map-header">'
        '<div class="section-kicker">Data Engineering Career Mission Map</div>'
        '<div class="section-heading">Career Mission Map</div>'
        '<p class="section-copy">Follow the Data Engineering readiness journey from task execution to enterprise leadership.</p>'
        '</div>'
        f'<div class="career-map-grid mission-path">{mission_html}</div>'
        '<div class="career-map-note">Each level unlocks more advanced Foundry-powered readiness workflows, from individual practice to team and executive insights.</div>'
        '</section>',
        unsafe_allow_html=True,
    )


def render_role_context_flow(role, domain, data_product, target_skill):
    items = [("Role", role), ("Domain", domain), ("Product", data_product), ("Skill", target_skill), ("Output", "Readiness plan")]
    flow = []
    for index, (label, value) in enumerate(items):
        flow.append(f'<span class="ai-flow-step"><em>{safe_text(label)}</em><strong>{safe_text(value)}</strong></span>')
        if index < len(items) - 1:
            flow.append('<span class="ai-flow-arrow">to</span>')
    st.markdown(f'<div class="ai-mini-flow">{"".join(flow)}</div>', unsafe_allow_html=True)


def extract_week_cards(response_text):
    cards = []
    pattern = re.compile(r"(Week\s*[1-4].*?)(?=Week\s*[1-4]|\Z)", re.IGNORECASE | re.DOTALL)
    for match in pattern.findall(str(response_text or "")):
        lines = [line.strip(" -*") for line in match.splitlines() if line.strip()]
        if lines:
            cards.append({"title": lines[0], "body": "\n".join(lines[1:])})
    fallback = [
        ("Week 1", "Topic: Role foundations\nGoal: Understand responsibilities\nPractice Task: Map the selected data product workflow\nResource: Metadata Pipeline Practice Guide\nReadiness Checkpoint: Explain the workflow"),
        ("Week 2", "Topic: Load rules\nGoal: Apply metadata and load type decisions\nPractice Task: Configure incremental logic\nResource: Load Type Rules Cheat Sheet\nReadiness Checkpoint: Validate keys and watermarks"),
        ("Week 3", "Topic: Troubleshooting\nGoal: Diagnose failures and risks\nPractice Task: Fix a schema mismatch\nResource: Pipeline Troubleshooting Playbook\nReadiness Checkpoint: Document cause and fix"),
        ("Week 4", "Topic: Readiness validation\nGoal: Prove skill readiness\nPractice Task: Complete assessment and scenario lab\nResource: Data Quality Rule Design Practice\nReadiness Checkpoint: Reach Ready status or revision plan"),
    ]
    while len(cards) < 4:
        title, body = fallback[len(cards)]
        cards.append({"title": title, "body": body})
    return cards[:4]


def render_learning_roadmap_visual(response_text, role, domain, data_product, target_skill):
    weeks = extract_week_cards(response_text)
    path_nodes = "".join(
        f'<div class="roadmap-node"><div class="roadmap-node-marker">{index}</div><strong>{safe_text(week["title"])}</strong></div>'
        for index, week in enumerate(weeks, 1)
    )
    st.markdown(f'<div class="roadmap-path">{path_nodes}</div>', unsafe_allow_html=True)
    html = ""
    for index, week in enumerate(weeks, 1):
        html += (
            '<div class="ai-section-card roadmap-week-card">'
            f'<span class="resource-chip">WEEK {index}</span>'
            f'<div class="ai-section-heading">{safe_text(week["title"])}</div>'
            f'<div class="ai-section-body">{body_to_html(week["body"])}</div>'
            "</div>"
    )
    st.markdown(f'<div class="roadmap-week-grid">{html}</div>', unsafe_allow_html=True)
    render_resource_reference_note()


def parse_quiz_json(raw_text: str):
    raw = str(raw_text or "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        start = raw.index("[")
        end = raw.rindex("]") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        pass
    try:
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    return None


def render_quiz_cards(quiz):
    answers = {}
    for index, question in enumerate(quiz):
        st.markdown(
            f"""
            <div class="ai-question-card">
              <div class="ai-question-number">Q{index + 1}</div>
              <h4>{safe_text(question.get("question"))}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        answer = st.radio(
            "Choose:",
            question.get("options", []),
            index=None,
            key=f"quiz_answer_{index}",
        )
        answers[index] = answer
        st.markdown(f'<span class="ai-source-chip">{safe_text(question.get("source_focus", "Synthetic knowledge files"))}</span>', unsafe_allow_html=True)
    return answers


def calculate_quiz_score(quiz, answers):
    correct = 0
    for index, question in enumerate(quiz):
        if answers.get(index) == question.get("correct_answer"):
            correct += 1
    score = round((correct / max(len(quiz), 1)) * 100)
    return score, readiness_from_score(score)


def render_score_card(score, status, title="Readiness Score"):
    st.markdown(
        f"""
        <div class="premium-card">
          <div class="section-kicker">{safe_text(title)}</div>
          <div class="score-number">{int(score)}%</div>
          {status_badge_html(status)}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(min(max(score, 0), 100) / 100)


def render_question_review_card(index, question, selected):
    correct = question.get("correct_answer")
    is_correct = selected == correct
    result = "Correct" if is_correct else "Needs Review"
    card_class = "ai-question-card ai-strength-card" if is_correct else "ai-question-card ai-risk-card"
    st.markdown(
        f"""
        <div class="{card_class}">
          <div class="ai-question-number">Q{index + 1}</div>
          <h4>{safe_text(question.get("question"))}</h4>
          <p><strong>Selected answer:</strong> {safe_text(selected)} - {safe_text(result)}</p>
          <p><strong>Correct answer:</strong> {safe_text(correct)}</p>
          <p>{highlight_keywords(question.get("explanation", ""))}</p>
          <span class="ai-source-chip">{safe_text(question.get("source_focus", "Synthetic knowledge files"))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quiz_results(quiz, answers, feedback):
    score = st.session_state["quiz_score"]
    status = st.session_state["readiness_status"]
    render_score_card(score, status)
    st.markdown("### Question Review")
    for index, question in enumerate(quiz):
        render_question_review_card(index, question, answers.get(index))
    if feedback:
        render_foundry_response_card("Foundry Assessment Feedback", feedback)
        render_resource_reference_note()


def extract_score_from_feedback(text):
    raw = str(text or "")
    patterns = [
        r"score\s*(?:out\s*of\s*100)?\s*[:\-]\s*(\d{1,3})(?:\s*/\s*100)?",
        r"(\d{1,3})\s*/\s*100",
        r"(\d{1,3})\s*%\s*(?:readiness|score)",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, flags=re.I)
        if match:
            return min(int(match.group(1)), 100)
    return None


def is_substantive_config_answer(answer):
    clean = re.sub(r"\s+", " ", str(answer or "")).strip()
    words = re.findall(r"[A-Za-z0-9_]+", clean)
    return len(clean) >= 60 and len(words) >= 10


def store_learner_result(**kwargs):
    existing = st.session_state.get("learner_results") or {}
    history = existing.get("history", [])
    history.append(kwargs)
    existing.update(kwargs)
    existing["history"] = history[-10:]
    st.session_state["learner_results"] = existing


def render_config_scenario(scenario_text):
    render_foundry_response_card("Config Practice Scenario", scenario_text)
    with st.expander("Hints and Source Focus", expanded=False):
        render_source_chips(scenario_text)
    render_resource_reference_note()


def render_config_feedback(feedback):
    score = st.session_state.get("config_score")
    if score is not None:
        render_score_card(score, readiness_from_score(score), "Config Practice Score")
    else:
        st.info("Foundry feedback did not include a clearly parseable numeric score, so no score was stored for manager/director rollups.")
    render_foundry_response_card("Config Practice Feedback", feedback)
    render_resource_reference_note()


def readiness_counts(results):
    history = (results or {}).get("history", [])
    if not history:
        return {"Ready": 0, "Needs Revision": 0, "Not Ready": 0}
    counts = {"Ready": 0, "Needs Revision": 0, "Not Ready": 0}
    for item in history:
        status = normalize_status(item.get("readiness_status") or item.get("assessment_status"))
        counts[status] += 1
    return counts


def render_manager_dashboard(response, results):
    counts = readiness_counts(results)
    total = max(sum(counts.values()), 1)
    ready_pct = round((counts["Ready"] / total) * 100)
    rev_pct = round((counts["Needs Revision"] / total) * 100)
    risk_pct = max(0, 100 - ready_pct - rev_pct)
    st.markdown(
        f"""
        <div class="ai-report-note">Readiness counts below are calculated from learner assessment/config sessions stored in this Streamlit session. If demo mode is enabled, they are labeled synthetic demo learners.</div>
        <div class="manager-dashboard-grid">
          <div class="readiness-metric-card"><strong>Ready</strong><div class="score-number">{counts["Ready"]}</div></div>
          <div class="readiness-metric-card"><strong>Needs Revision</strong><div class="score-number">{counts["Needs Revision"]}</div></div>
          <div class="readiness-metric-card"><strong>Not Ready</strong><div class="score-number">{counts["Not Ready"]}</div></div>
          <div class="readiness-metric-card"><strong>Learner Records Used</strong><div class="score-number">{total}</div></div>
        </div>
        <div class="readiness-bar-strip">
          <span style="width:{ready_pct}%; background:var(--accent-green)"></span>
          <span style="width:{rev_pct}%; background:var(--accent-amber)"></span>
          <span style="width:{risk_pct}%; background:var(--accent-red)"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_foundry_response_card("Manager Insights", response)


def render_director_brief(response):
    st.markdown(
        """
        <div class="director-brief-card">
          <div class="section-kicker">Director Readiness Brief</div>
          <div class="section-heading">Executive Readiness Summary</div>
          <p class="section-copy">Domain-level risk themes, capability maturity, governance risks, and next 30-day actions.</p>
        </div>
        <div class="action-timeline">
          <div class="timeline-step"><strong>Week 1</strong><p>Confirm domain readiness risks</p></div>
          <div class="timeline-step"><strong>Week 2</strong><p>Prioritize training and coaching</p></div>
          <div class="timeline-step"><strong>Week 3</strong><p>Review governance and quality controls</p></div>
          <div class="timeline-step"><strong>Week 4</strong><p>Report maturity movement</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_foundry_response_card("Director Readiness Brief", response)


def build_learning_prompt(role, domain, data_product, target_skill, available_hours, confidence_level):
    return f"""
Create a role-specific Data Engineering learning roadmap for:
Role: {role}
Domain: {domain}
Data Product: {data_product}
Target Skill: {target_skill}
Available Study Hours Per Week: {available_hours}
Current Confidence Level: {confidence_level}

Use the attached synthetic Data Engineering knowledge files through Foundry IQ.
Return:
1. Role responsibility summary
2. Skill gap analysis
3. Four-week learning roadmap. Use headings Week 1, Week 2, Week 3, Week 4. For each week include Topic, Goal, Practice task, Resource suggestion, and Readiness checkpoint.
4. Weekly practice tasks
5. Resources to practice
6. Readiness checkpoints
7. Next topic recommendation
8. Sources used
Do not use markdown tables.
"""


def build_quiz_prompt(role, target_skill, difficulty, num_questions):
    return f"""
Generate {num_questions} multiple choice quiz questions for:
Role: {role}
Target Skill: {target_skill}
Difficulty: {difficulty}

Ground questions in the attached synthetic Data Engineering knowledge files.
Focus on: pipeline configuration, load type rules, metadata-driven pipelines,
troubleshooting, data quality, architecture, and governance.

Return STRICTLY as JSON array:
[
  {{
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "correct_answer": "A. ...",
    "explanation": "...",
    "source_focus": "..."
  }}
]
Return JSON only. No markdown, no preamble, no explanation outside the JSON.
"""


def build_assessment_feedback_prompt(role, target_skill, score, status, answers_json):
    return f"""
The learner completed a readiness assessment.
Role: {role}
Target Skill: {target_skill}
Score: {score}%
Readiness Status: {status}
Questions and learner answers: {answers_json}

Use the attached synthetic Data Engineering knowledge files.
Return:
1. Score interpretation
2. Strength areas
3. Weak areas
4. Recommended revision resources (if score is low)
5. Next topic recommendation (if score is good)
6. Suggested practice tasks
7. Sources used
Do not use markdown tables.
"""


def build_config_scenario_prompt(role, scenario_type, difficulty):
    return f"""
Generate one realistic synthetic Data Engineering config practice scenario for:
Role: {role}
Scenario Type: {scenario_type}
Difficulty: {difficulty}

Use the attached synthetic knowledge files.
Return:
1. Scenario background
2. Business requirement
3. Current configuration or issue
4. Expected learner task
5. Evaluation criteria
6. Hints
7. Sources used
Do not use markdown tables.
"""


def build_config_eval_prompt(role, scenario_type, difficulty, scenario_text, learner_answer):
    return f"""
Evaluate this learner answer for the synthetic Data Engineering config scenario.
Role: {role}
Scenario Type: {scenario_type}
Difficulty: {difficulty}
Scenario: {scenario_text}
Learner Answer: {learner_answer}

Use the attached synthetic knowledge files.
Important scoring rule:
- If the learner answer is vague, too short, generic, or does not explain concrete configuration decisions, assign 0 to 20.
- Do not give a high score unless the answer clearly addresses the requirement, configuration/issue, validation, risk, and expected fix.
Return:
1. Score out of 100
2. Readiness status
3. Correct decisions
4. Missing items
5. Risk in the answer
6. Recommended fix
7. Best practice answer
8. Resources to revise
9. Sources used
Do not use markdown tables.
"""


def build_manager_prompt(domain, team_size, focus_area, stored_results):
    return f"""
Generate manager-level readiness insights for a synthetic Data Engineering team.
Domain: {domain}
Team Size: {team_size}
Focus Area: {focus_area}
Synthetic learner results: {json.dumps(stored_results, indent=2)}

Use the attached synthetic Data Engineering knowledge files.
Return:
1. Team readiness summary
2. Readiness distribution (Ready / Needs Revision / Not Ready counts)
3. Role-based skill gaps
4. Data product risks
5. Recommended team revision plan
6. Coaching actions by role level
7. Escalation points for Director
8. Sources used
Do not use markdown tables.
"""


def build_director_prompt(num_domains, strategic_focus, risk_tolerance, stored_results):
    return f"""
Generate a director-level readiness brief for multiple synthetic Data Engineering domains.
Number of Domains: {num_domains}
Strategic Focus: {strategic_focus}
Risk Tolerance: {risk_tolerance}
Synthetic team readiness data: {json.dumps(stored_results, indent=2)}

Use the attached synthetic Data Engineering knowledge files.
Return:
1. Executive readiness summary
2. Domain-level risk themes
3. Capability maturity view
4. Strategic recommendations
5. Investment or training priorities
6. Governance risks
7. Next 30-day action plan
8. Sources used
Do not use markdown tables.
"""


init_state()
apply_theme_from_query_params()
inject_theme_css(st.session_state["theme"])
role, domain, data_product = render_sidebar()
render_theme_toggle()

render_hero()
render_readiness_pulse(role)
render_capability_meter(role)
render_role_hierarchy_visual()
render_foundry_integration_block()
render_how_it_works()
render_career_mission_map()

st.markdown(
    """
    <div id="ai-workspace"></div>
    <div class="premium-card">
      <div class="section-kicker">AI Readiness Workspace</div>
      <div class="section-heading">AI Readiness Workspace</div>
      <p class="section-copy">Generate roadmaps, assessments, config practice, and readiness insights using Microsoft Foundry and Foundry IQ.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
render_ai_command_center()

tab_learning, tab_assessment, tab_config, tab_manager, tab_director = st.tabs(
    ["Learning Roadmap", "AI Assessment", "Config Lab", "Manager Insights", "Director View"]
)

with tab_learning:
    st.markdown(
        '<div id="learning-roadmap-anchor"></div><div class="workspace-header"><div class="section-kicker">Learning Roadmap</div><div class="section-heading">AI Learning Roadmap</div><p class="section-copy">Generate a role-specific four-week learning path grounded in synthetic Data Engineering knowledge.</p></div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        target_skill = st.selectbox("Target Skill", TARGET_SKILLS, key="roadmap_skill")
    with col2:
        available_hours = st.slider("Available study hours/week", 1, 20, 6)
    with col3:
        confidence_level = st.selectbox("Confidence level", ["Beginner", "Intermediate", "Advanced"])
    render_role_context_flow(role, domain, data_product, target_skill)
    if st.button("Generate AI Learning Roadmap", type="primary"):
        with foundry_spinner():
            st.session_state["generated_roadmap"] = call_foundry(
                build_learning_prompt(role, domain, data_product, target_skill, available_hours, confidence_level)
            )
    if st.session_state["generated_roadmap"]:
        render_learning_roadmap_visual(st.session_state["generated_roadmap"], role, domain, data_product, target_skill)
    else:
        render_empty_state("Learning Path")

with tab_assessment:
    st.markdown(
        '<div class="workspace-header"><div class="section-kicker">AI Assessment</div><div class="section-heading">AI Readiness Assessment</div><p class="section-copy">Generate a quiz, answer without defaults selected, and receive automatic readiness scoring.</p></div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        assessment_skill = st.selectbox("Target Skill", TARGET_SKILLS, key="assessment_skill")
    with col2:
        difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"], key="assessment_difficulty")
    with col3:
        num_questions = st.selectbox("Number of questions", [3, 5, 7], index=1)

    if st.button("Generate AI Quiz", type="primary"):
        with foundry_spinner():
            raw = call_foundry(build_quiz_prompt(role, assessment_skill, difficulty, num_questions))
        parsed = parse_quiz_json(raw)
        st.session_state["raw_quiz_response"] = raw
        st.session_state["generated_quiz"] = parsed
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_score"] = None
        st.session_state["readiness_status"] = None
        st.session_state["assessment_feedback"] = None
        if parsed is None:
            st.warning("Could not parse quiz JSON. Showing raw Foundry-grounded response below.")

    quiz = st.session_state["generated_quiz"]
    if isinstance(quiz, list) and quiz:
        answers = render_quiz_cards(quiz)
        if st.button("Submit Assessment", type="primary"):
            if any(answer is None for answer in answers.values()):
                st.warning("Please answer all questions before submitting.")
            else:
                score, status = calculate_quiz_score(quiz, answers)
                st.session_state["quiz_answers"] = answers
                st.session_state["quiz_score"] = score
                st.session_state["readiness_status"] = status
                answer_payload = {
                    "questions": quiz,
                    "learner_answers": {f"Q{idx + 1}": answer for idx, answer in answers.items()},
                }
                with foundry_spinner():
                    st.session_state["assessment_feedback"] = call_foundry(
                        build_assessment_feedback_prompt(role, assessment_skill, score, status, json.dumps(answer_payload, indent=2))
                    )
                store_learner_result(
                    role=role,
                    domain=domain,
                    data_product=data_product,
                    target_skill=assessment_skill,
                    quiz_score=score,
                    readiness_status=status,
                )
    elif st.session_state["raw_quiz_response"]:
        render_foundry_response_card("Raw Foundry Quiz Response", st.session_state["raw_quiz_response"])
    else:
        render_empty_state("Assessment")

    if st.session_state["quiz_score"] is not None and isinstance(quiz, list):
        render_quiz_results(quiz, st.session_state["quiz_answers"], st.session_state["assessment_feedback"])

with tab_config:
    st.markdown(
        '<div class="workspace-header"><div class="section-kicker">Config Lab</div><div class="section-heading">Config Practice Lab</div><p class="section-copy">Practice realistic synthetic pipeline scenarios and receive score-style evaluator feedback.</p></div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        scenario_type = st.selectbox("Scenario type", SCENARIO_TYPES)
    with col2:
        config_difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"], key="config_difficulty")

    if st.button("Generate AI Config Scenario", type="primary"):
        with foundry_spinner():
            st.session_state["generated_config_scenario"] = call_foundry(
                build_config_scenario_prompt(role, scenario_type, config_difficulty)
            )
        st.session_state["config_feedback"] = None
        st.session_state["config_score"] = None
        st.session_state["config_answer"] = ""

    if st.session_state["generated_config_scenario"]:
        st.markdown('<div class="section-kicker">Challenge</div>', unsafe_allow_html=True)
        render_config_scenario(st.session_state["generated_config_scenario"])
        st.session_state["config_answer"] = st.text_area(
            "Your Answer / Config Solution",
            value=st.session_state["config_answer"],
            height=200,
        )
        if st.button("Submit to Foundry Config Evaluator", type="primary"):
            if not is_substantive_config_answer(st.session_state["config_answer"]):
                st.warning("Please add a more complete config solution before submitting. Include the decision, expected configuration changes, validation checks, and risk handling.")
            else:
                with foundry_spinner():
                    feedback = call_foundry(
                        build_config_eval_prompt(
                            role,
                            scenario_type,
                            config_difficulty,
                            st.session_state["generated_config_scenario"],
                            st.session_state["config_answer"],
                        )
                )
                st.session_state["config_feedback"] = feedback
                st.session_state["config_score"] = extract_score_from_feedback(feedback)
                if st.session_state["config_score"] is not None:
                    store_learner_result(
                        role=role,
                        domain=domain,
                        data_product=data_product,
                        target_skill=scenario_type,
                        config_score=st.session_state["config_score"],
                        readiness_status=readiness_from_score(st.session_state["config_score"]),
                    )
    else:
        render_empty_state("Config Practice")

    if st.session_state["config_feedback"]:
        render_config_feedback(st.session_state["config_feedback"])

with tab_manager:
    st.markdown(
        '<div class="workspace-header"><div class="section-kicker">Manager Insights</div><div class="section-heading">Manager Insights</div><p class="section-copy">Summarize stored learner sessions or clearly labeled synthetic demo learners into readiness actions.</p></div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        manager_domain = st.selectbox("Domain", DOMAINS, key="manager_domain", index=DOMAINS.index(domain))
    with col2:
        team_size = st.number_input("Team size", min_value=1, max_value=50, value=6)
    with col3:
        focus_area = st.selectbox("Focus area", TARGET_SKILLS, key="manager_focus")

    session_results = st.session_state["learner_results"]
    has_session_results = bool((session_results or {}).get("history"))
    use_demo_team = st.checkbox(
        "Use synthetic demo learners for manager dashboard",
        value=False,
        help="Enable this only for a demo when no assessment/config sessions have been completed yet.",
    )
    if has_session_results:
        stored_results = session_results
        st.info("Using learner records captured in this Streamlit session.")
    elif use_demo_team:
        stored_results = {
            "demo_data": True,
            "history": [
                {"role": sample_role, "domain": manager_domain, "quiz_score": score, "readiness_status": status}
                for sample_role, score, status in [
                    ("Junior Data Engineer", 82, "Ready"),
                    ("Data Engineer", 68, "Needs Revision"),
                    ("Senior Data Engineer / Manager", 74, "Needs Revision"),
                    ("Director", 88, "Ready"),
                ]
            ],
        }
        st.info("Using synthetic demo learner data. These are not real people or real employees.")
    else:
        stored_results = {"history": []}
        render_empty_state(
            "Manager Insights",
            message="No learner records are stored yet. Complete an assessment/config practice first, or enable synthetic demo learners above.",
        )
    if st.button("Generate AI Manager Insights", type="primary"):
        if not has_session_results and not use_demo_team:
            st.warning("No learner records are available yet. Complete an assessment/config practice first, or enable synthetic demo learners.")
        else:
            with foundry_spinner():
                st.session_state["manager_response"] = call_foundry(
                    build_manager_prompt(manager_domain, team_size, focus_area, stored_results)
                )

    if st.session_state["manager_response"]:
        render_manager_dashboard(st.session_state["manager_response"], stored_results)

with tab_director:
    st.markdown(
        '<div class="workspace-header"><div class="section-kicker">Director View</div><div class="section-heading">Director View</div><p class="section-copy">Create a multi-domain executive readiness brief with strategic risks and 30-day actions.</p></div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        num_domains = st.number_input("Number of domains", min_value=1, max_value=10, value=3)
    with col2:
        strategic_focus = st.selectbox("Strategic focus", ["Reliability", "Delivery Readiness", "Data Quality", "Governance", "Platform Adoption"])
    with col3:
        risk_tolerance = st.selectbox("Risk tolerance", ["Low", "Medium", "High"], index=1)

    director_data = st.session_state["learner_results"] if (st.session_state["learner_results"] or {}).get("history") else {
        "history": [],
        "domain_context": DOMAINS[: int(num_domains)],
        "note": "No learner records are stored yet. Use this as a synthetic domain-planning brief, not a people-count dashboard.",
    }
    if st.button("Generate Director Readiness Brief", type="primary"):
        with foundry_spinner():
            st.session_state["director_response"] = call_foundry(
                build_director_prompt(num_domains, strategic_focus, risk_tolerance, director_data)
            )

    if st.session_state["director_response"]:
        render_director_brief(st.session_state["director_response"])
    else:
        render_empty_state("Director View", message="Generate a director-level readiness brief across synthetic domains.")

st.markdown(
    """
    <div id="resources"></div>
    <div class="bottom-resource-shell">
      <div class="section-kicker">Resources</div>
      <div class="section-heading">External Learning Resources</div>
      <p class="section-copy">Refer to the below resources to learn and revise. These are static public learning links; AI feedback only recommends the topics to focus on.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
render_resource_cards()

st.markdown(
    """
    <div style="
        width: fit-content;
        margin: 3rem auto 1.5rem auto;
        padding: 0.85rem 1.4rem;
        text-align: center;
        border: 1px solid var(--border);
        border-radius: 999px;
        background: color-mix(in srgb, var(--bg-card) 94%, transparent);
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 750;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
    ">
        <span style="margin: 0 0.18rem;">DataDojo IQ</span>
        <span style="margin: 0 0.18rem;">•</span>
        <span style="margin: 0 0.18rem;">Microsoft Foundry</span>
        <span style="margin: 0 0.18rem;">•</span>
        <span style="margin: 0 0.18rem;">Synthetic Data Only</span>
        <span style="margin: 0 0.18rem;">•</span>
        <strong style="
            margin: 0 0.18rem;
            color: var(--accent-blue);
            font-weight: 950;
        ">
            Built by Rishitha © 2026
        </strong>
    </div>
    """,
    unsafe_allow_html=True,
)
