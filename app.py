import base64
from html import escape
import json
import os

import streamlit as st

from agents import map_role_to_skills, generate_study_plan
from assessment_engine import generate_questions, calculate_readiness
from config_practice_engine import generate_config_task, evaluate_config_answer
from manager_insights import generate_manager_summary


ASSETS = {
    "hero": "assets/hero_banner.png",
    "hero_transparent": "assets/hero_banner_transparent.png",
    "learner": "assets/learner_plan.png",
    "assessment": "assets/assessment.png",
    "config": "assets/config_practice.png",
    "manager": "assets/manager_dashboard.png",
}

st.set_page_config(
    page_title="DataDojo IQ",
    page_icon=ASSETS["hero"] if os.path.exists(ASSETS["hero"]) else None,
    layout="wide",
    initial_sidebar_state="expanded",
)


ROLES = [
    "Junior Data Engineer",
    "Data Engineer",
    "Senior Data Engineer",
    "Data Architect",
]

TARGET_SKILLS = [
    "Metadata Pipeline Configuration",
    "Incremental Load Design",
    "Advanced Pipeline Troubleshooting",
    "Lakehouse Architecture Standards",
    "Data Modeling and Governance",
]

AGENT_FLOW = [
    {
        "title": "User Profile",
        "caption": "Captures role, available hours, and readiness goal.",
        "x": 12,
        "y": 74,
        "color": "#6757F5",
    },
    {
        "title": "Role Skill Mapper Agent",
        "caption": "Maps the learner role to the skills needed for DataOps work.",
        "x": 24,
        "y": 54,
        "color": "#14B8A6",
    },
    {
        "title": "Learning Path Curator Agent",
        "caption": "Selects the right topics from the grounded learning base.",
        "x": 36,
        "y": 67,
        "color": "#F97316",
    },
    {
        "title": "Study Plan Generator Agent",
        "caption": "Converts skill gaps into a practical four-week plan.",
        "x": 49,
        "y": 34,
        "color": "#8B5CF6",
    },
    {
        "title": "Assessment Agent",
        "caption": "Generates role-specific readiness questions and scoring.",
        "x": 64,
        "y": 69,
        "color": "#EF4444",
    },
    {
        "title": "Config Practice Evaluator Agent",
        "caption": "Reviews pipeline configuration answers and gives feedback.",
        "x": 78,
        "y": 48,
        "color": "#0EA5E9",
    },
    {
        "title": "Manager Insights Agent",
        "caption": "Summarizes team readiness, risks, and next actions.",
        "x": 91,
        "y": 24,
        "color": "#D97706",
    },
]

MICROSOFT_STACK = [
    "Microsoft Foundry",
    "Foundry IQ",
    "Python",
    "Streamlit",
    "GitHub Copilot",
]


def inject_custom_css(theme_mode):
    dark_theme_css = ""
    if theme_mode == "Black theme":
        dark_theme_css = """
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 255, 255, 0.08), transparent 30rem),
                linear-gradient(180deg, #050505 0%, #111111 52%, #050505 100%);
            color: #F8FAFC;
        }

        h1, h2, h3,
        .brand-name,
        .feature-card-title,
        .agent-title,
        .metric-value,
        .stack-pill,
        .info-card h3 {
            color: #F8FAFC;
        }

        .section-copy,
        .brand-tag,
        .feature-card-text,
        .agent-caption,
        .metric-title,
        .workspace-visual-copy,
        .info-card p,
        .info-card li,
        .small-note,
        .footer-note {
            color: #CBD5E1;
        }

        .metric-card,
        .agent-card,
        .stack-pill,
        .info-card,
        .workspace-intro {
            background: #151515;
            border-color: #2F2F2F;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.34);
        }

        a.feature-card {
    display: flex;
    flex-direction: column;
    height: 26rem;
    min-height: 26rem;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 12px;
    background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(239, 246, 255, 0.78) 100%);
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
    transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    cursor: pointer;
    text-decoration: none !important;
    outline: none;
    position: relative;
    color: inherit !important;
}

a.feature-card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 4px;
    background: linear-gradient(90deg, #0F62FE, #10B981, #F59E0B, #8B5CF6);
    opacity: 0.95;
    z-index: 2;
}

a.feature-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
        120deg,
        transparent 0%,
        rgba(255, 255, 255, 0.0) 38%,
        rgba(255, 255, 255, 0.34) 50%,
        rgba(255, 255, 255, 0.0) 62%,
        transparent 100%
    );
    transform: translateX(-120%);
    transition: transform 520ms ease;
    pointer-events: none;
}

a.feature-card:hover {
    transform: translateY(-3px);
    border-color: #BFDBFE;
    box-shadow: 0 18px 34px rgba(15, 23, 42, 0.12);
}

a.feature-card:hover::after {
    transform: translateX(120%);
}

a.feature-card:focus-visible {
    border-color: var(--blue);
    box-shadow: 0 0 0 4px rgba(15, 98, 254, 0.18), 0 18px 34px rgba(15, 23, 42, 0.12);
}

.feature-image {
    width: 100%;
    height: 9.6rem;
    min-height: 9.6rem;
    object-fit: cover;
    object-position: center;
    display: block;
    background: #F8FAFC;
    border-bottom: 1px solid var(--line);
    padding: 0;
}

.feature-card-body {
    display: flex !important;
    flex: 1 1 auto !important;
    flex-direction: column !important;
    padding: 1rem 1.05rem 1.05rem;
}

.feature-card-title,
.feature-card-text {
    display: block;
}

.feature-card-title {
    margin: 0;
    color: var(--navy);
    font-size: 1.18rem;
    font-weight: 850;
    line-height: 1.2;
    min-height: 3rem;
}

.feature-card-text {
    color: var(--slate);
    line-height: 1.5;
    margin: 0.55rem 0 0;
    font-size: 0.92rem;
    min-height: 7.2rem;
}

        .hero-panel {
            background: linear-gradient(135deg, #000000 0%, #151515 48%, #262626 100%);
            border: 1px solid #2F2F2F;
        }

        .hero-visual {
            background: transparent;
        }

        .roadmap-shell,
        .roadmap-stage,
        .road-detail-panel,
        .road-name-card {
            background: #101010;
            border-color: #2F2F2F;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02), 0 18px 38px rgba(0, 0, 0, 0.36);
        }

        .road-base {
            stroke: #6D5DF5;
        }

        .road-edge {
            stroke: #A78BFA;
            opacity: 0.22;
        }

        .curved-road {
            filter: drop-shadow(0 16px 30px rgba(0, 0, 0, 0.36));
        }

        .road-name {
            color: #F8FAFC;
            text-shadow: none;
        }

        .road-detail {
            background: #151515;
            border-color: #2F2F2F;
        }

        .workspace-visual-card {
            background: #151515;
            border-color: #2F2F2F;
        }

        .workspace-visual-title {
            color: #F8FAFC;
        }

        .config-code {
            background: #0B1220;
            border-color: #2F2F2F;
            color: #E5E7EB;
        }

        .road-name,
        .road-name-card {
            color: #F8FAFC;
        }

        .brand-data,
        .brand-iq {
            color: #60A5FA;
        }

        .brand-dojo {
            color: #34D399;
        }

        div[data-baseweb="tab"] {
            background: #151515;
            border-color: #2F2F2F;
            color: #CBD5E1;
        }

        div[data-baseweb="tab"][aria-selected="true"] {
            background: #050505;
            color: #FFFFFF;
            border-top-color: #FFFFFF;
        }

        label,
        [data-testid="stMarkdownContainer"],
        [data-testid="stSelectbox"] *,
        [data-testid="stSlider"] *,
        [data-testid="stTextArea"] *,
        [data-testid="stTabs"] * {
            color: #E5E7EB;
        }

        [data-testid="stSelectbox"] div,
        [data-testid="stTextArea"] textarea {
            background: #151515;
            border-color: #2F2F2F;
            color: #F8FAFC;
        }

        .theme-slider.dark {
            background: radial-gradient(circle at 76% 34%, #F8FAFC 0 0.42rem, transparent 0.46rem),
                        radial-gradient(circle at 28% 30%, rgba(255,255,255,0.8) 0 0.08rem, transparent 0.1rem),
                        radial-gradient(circle at 42% 68%, rgba(255,255,255,0.65) 0 0.07rem, transparent 0.09rem),
                        linear-gradient(135deg, #020617 0%, #172554 100%);
        }

        .theme-slider.dark::before {
            left: calc(100% - 2.55rem);
            background: #E5E7EB;
        }

        .theme-slider.dark {
            color: #E5E7EB;
        }

        .feature-action {
            border-top-color: #2F2F2F;
        }

        .feature-card .feature-action span:last-child {
            color: #93C5FD;
        }

        .live-chip {
            color: #A7F3D0;
            background: rgba(16, 185, 129, 0.14);
            border-color: rgba(167, 243, 208, 0.42);
        }
        """

    st.markdown(
        """
        <style>
        :root {
            --navy: #0B1220;
            --navy-2: #111827;
            --blue: #0F62FE;
            --blue-2: #2563EB;
            --sky: #EAF2FF;
            --slate: #475569;
            --muted: #64748B;
            --line: #E2E8F0;
            --panel: #FFFFFF;
            --soft: #F8FAFC;
            --success: #047857;
            --warning: #B45309;
            --danger: #B91C1C;
        }

        html {
            scroll-behavior: smooth;
        }

        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        section.main,
        * {
            scroll-behavior: smooth !important;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15, 98, 254, 0.10), transparent 30rem),
                linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 54%, #F8FAFC 100%);
            color: var(--navy);
        }

        .block-container {
            max-width: 1220px;
            padding-top: 3.6rem;
            padding-bottom: 3rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B1220 0%, #111827 100%);
        }

        section[data-testid="stSidebar"] * {
            color: #E5E7EB;
        }

        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] li {
            color: #CBD5E1;
        }

        .top-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 0 0 1.25rem;
        }

        .brand-logo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.45rem;
            height: 2.45rem;
            border-radius: 10px;
            background: #FFFFFF;
            border: 1px solid var(--line);
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
            position: relative;
        }

        .brand-logo::before,
        .brand-logo::after {
            content: "";
            position: absolute;
            border-radius: 999px;
            background: linear-gradient(180deg, #0F62FE, #10B981);
        }

        .brand-logo::before {
            width: 0.52rem;
            height: 1.55rem;
            left: 0.72rem;
            bottom: 0.48rem;
        }

        .brand-logo::after {
            width: 0.52rem;
            height: 1rem;
            right: 0.72rem;
            bottom: 0.48rem;
        }

        .brand-wordmark {
            display: grid;
            gap: 0.05rem;
        }

        .brand-name {
            color: var(--navy);
            font-size: 1.18rem;
            font-weight: 900;
            line-height: 1;
        }

        .brand-data {
            color: #0F62FE;
        }

        .brand-dojo {
            color: #10B981;
        }

        .brand-iq {
            color: var(--navy);
        }

        .brand-tag {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 750;
        }

        .sidebar-brand {
            margin: 0 0 1rem;
        }

        .sidebar-brand .brand-logo {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(191, 219, 254, 0.24);
            box-shadow: none;
        }

        .sidebar-brand .brand-iq,
        .sidebar-brand .brand-tag {
            color: #E5E7EB;
        }

        .theme-label {
            color: #E5E7EB;
            font-size: 0.82rem;
            font-weight: 850;
            margin: 0.5rem 0 0.35rem;
        }

        .theme-slider {
            margin-bottom: 0.9rem;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            height: 3rem;
            border: 1px solid rgba(191, 219, 254, 0.36);
            border-radius: 999px;
            background: linear-gradient(135deg, #93C5FD 0%, #DBEAFE 100%);
            cursor: pointer;
            overflow: hidden;
            padding: 0 0.85rem;
            color: #0B1220 !important;
            font-size: 0.82rem;
            font-weight: 900;
            text-decoration: none !important;
            transition: box-shadow 160ms ease, border-color 160ms ease, transform 160ms ease;
        }

        .theme-slider:hover {
            border-color: rgba(255, 255, 255, 0.58);
            box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
            transform: translateY(-1px);
        }

        .theme-slider::before {
            content: "";
            position: absolute;
            top: 0.35rem;
            left: 0.4rem;
            width: 2.15rem;
            height: 2.15rem;
            border-radius: 999px;
            background: #FBBF24;
            box-shadow: 0 7px 16px rgba(0, 0, 0, 0.22);
            transition: left 180ms ease, background 180ms ease;
            z-index: 1;
        }

        .theme-option {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            z-index: 2;
            pointer-events: none;
        }

        .sidebar-nav {
            display: grid;
            gap: 0.55rem;
            margin-top: 0.35rem;
        }

        .sidebar-nav a {
            display: block;
            color: #DBEAFE !important;
            text-decoration: none !important;
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 8px;
            padding: 0.58rem 0.7rem;
            background: rgba(255, 255, 255, 0.05);
            font-weight: 700;
        }

        .sidebar-nav a:hover {
            background: rgba(15, 98, 254, 0.22);
            border-color: rgba(191, 219, 254, 0.45);
        }

        h1, h2, h3 {
            color: var(--navy);
            letter-spacing: 0;
        }

        h1 {
            font-size: 4.2rem;
            line-height: 1;
            margin-bottom: 0.8rem;
        }

        h2 {
            font-size: 2rem;
            margin-top: 0.6rem;
            margin-bottom: 0.5rem;
        }

        h3 {
            font-size: 1.15rem;
        }

        .hero-panel {
            border-radius: 8px;
            background:
                radial-gradient(circle at 82% 12%, rgba(125, 211, 252, 0.18), transparent 22rem),
                linear-gradient(135deg, rgba(11, 18, 32, 0.98) 0%, rgba(15, 58, 122, 0.98) 52%, rgba(15, 98, 254, 0.98) 100%);
            box-shadow: 0 20px 48px rgba(15, 23, 42, 0.18);
            padding: 2.4rem;
            margin: 0 0 1.5rem;
            color: #FFFFFF;
            overflow: hidden;
        }

        .hero-content {
            display: grid;
            grid-template-columns: minmax(0, 0.92fr) minmax(360px, 1.08fr);
            gap: 2rem;
            align-items: center;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            width: fit-content;
            border: 1px solid rgba(191, 219, 254, 0.45);
            border-radius: 999px;
            padding: 0.36rem 0.72rem;
            background: rgba(255, 255, 255, 0.10);
            color: #DBEAFE;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 1rem;
        }

        .hero-panel h1,
        .hero-panel h2,
        .hero-panel p {
            color: #FFFFFF;
        }

        .hero-tagline {
            color: #BFDBFE;
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }

        .hero-copy {
            max-width: 760px;
            color: #E5E7EB;
            font-size: 1.05rem;
            line-height: 1.7;
            margin-bottom: 1.35rem;
        }

        .hero-visual {
            background: transparent;
            border: none;
            border-radius: 8px;
            box-shadow: none;
            padding: 0;
            position: relative;
            min-height: 24rem;
        }

        .hero-visual img {
            display: block;
            width: 100%;
            max-height: 29rem;
            height: auto;
            border-radius: 6px;
            object-fit: contain;
            margin: 0 auto;
            filter: drop-shadow(0 24px 34px rgba(0, 0, 0, 0.24));
            animation: heroFloat 5s ease-in-out infinite;
        }

        .live-activity {
            position: absolute;
            left: 1.2rem;
            bottom: 1.2rem;
            display: grid;
            gap: 0.55rem;
            width: min(18rem, 58%);
            border: 1px solid rgba(191, 219, 254, 0.4);
            border-radius: 8px;
            background: rgba(11, 18, 32, 0.78);
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.22);
            backdrop-filter: blur(12px);
            padding: 0.8rem;
        }

        .activity-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.7rem;
            color: #E5E7EB;
            font-size: 0.78rem;
            font-weight: 800;
        }

        .activity-dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 999px;
            background: #34D399;
            box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.75);
            animation: pulseDot 1.8s ease-out infinite;
        }

        .activity-bar {
            height: 0.45rem;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.18);
        }

        .activity-bar span {
            display: block;
            width: 62%;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #22C55E, #60A5FA, #FBBF24);
            animation: activityLoad 3.2s ease-in-out infinite alternate;
        }

        @keyframes heroFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }

        @keyframes pulseDot {
            0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.75); }
            100% { box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
        }

        @keyframes activityLoad {
            from { width: 42%; }
            to { width: 92%; }
        }

        .cta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            align-items: center;
        }

        .cta-button {
            display: inline-flex;
            justify-content: center;
            align-items: center;
            min-height: 2.75rem;
            border-radius: 8px;
            padding: 0.7rem 1.05rem;
            text-decoration: none !important;
            font-weight: 800;
            border: 1px solid transparent;
        }

        .cta-primary {
            background: #FFFFFF;
            color: #0F3A7A !important;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.20);
        }

        .cta-secondary {
            background: rgba(255, 255, 255, 0.10);
            color: #FFFFFF !important;
            border-color: rgba(255, 255, 255, 0.32);
        }

        .section-kicker {
            color: var(--blue);
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 0.2rem;
        }

        .section-copy {
            color: var(--slate);
            font-size: 1rem;
            line-height: 1.65;
            margin: 0 0 1.1rem;
        }

        a.feature-card {
            display: flex;
            flex-direction: column;
            height: auto;
            min-height: 0;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 8px;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(239, 246, 255, 0.72) 100%);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
            cursor: pointer;
            text-decoration: none !important;
            outline: none;
            position: relative;
            color: inherit !important;
        }

        a.feature-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 4px;
            background: linear-gradient(90deg, #0F62FE, #10B981, #F59E0B, #8B5CF6);
            opacity: 0.95;
        }

        a.feature-card::after {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, transparent 0%, rgba(255, 255, 255, 0.0) 38%, rgba(255, 255, 255, 0.34) 50%, rgba(255, 255, 255, 0.0) 62%, transparent 100%);
            transform: translateX(-120%);
            transition: transform 520ms ease;
            pointer-events: none;
        }

        a.feature-card:hover {
            transform: translateY(-3px);
            border-color: #BFDBFE;
            box-shadow: 0 18px 34px rgba(15, 23, 42, 0.12);
        }

        a.feature-card:hover::after {
            transform: translateX(120%);
        }

        a.feature-card:focus-visible {
            border-color: var(--blue);
            box-shadow: 0 0 0 4px rgba(15, 98, 254, 0.18), 0 18px 34px rgba(15, 23, 42, 0.12);
        }

        .feature-action {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-top: 0.4rem;
            border-top: 1px solid var(--line);
            padding-top: 0.8rem;
            color: var(--blue);
            font-size: 0.84rem;
            font-weight: 850;
        }

        .feature-action span:last-child {
            color: var(--blue);
        }

        .live-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            color: #047857;
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            border-radius: 999px;
            padding: 0.22rem 0.5rem;
            font-size: 0.74rem;
            font-weight: 850;
        }

        .live-chip::before {
            content: "";
            width: 0.42rem;
            height: 0.42rem;
            border-radius: 999px;
            background: #10B981;
            animation: pulseDot 1.8s ease-out infinite;
        }

        .feature-image {
            width: 100%;
            height: 10rem;
            object-fit: contain;
            display: block;
            background:
                radial-gradient(circle at 72% 32%, rgba(15, 98, 254, 0.10), transparent 12rem),
                linear-gradient(180deg, #F8FAFC 0%, #EEF6FF 100%);
            border-bottom: 1px solid var(--line);
            padding: 0.7rem;
        }

        .feature-card-body {
            display: flex !important;
            flex: 1 1 auto !important;
            flex-direction: column !important;
            gap: 0.65rem;
            padding: 1rem 1.05rem 1.05rem;
        }

        .feature-card-title,
        .feature-card-text {
            display: block;
        }

        .feature-card-title {
            margin: 0;
            color: var(--navy);
            font-size: 1.24rem;
            font-weight: 850;
            line-height: 1.18;
        }

        .feature-card-text {
            flex: 0 0 auto;
            color: var(--slate);
            line-height: 1.55;
            margin: 0;
            font-size: 0.95rem;
            min-height: 0;
        }

        .metric-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #FFFFFF;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
            padding: 1.05rem;
            min-height: 6.2rem;
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }

        .metric-card:hover,
        .stack-pill:hover,
        .agent-card:hover {
            transform: translateY(-3px);
            border-color: #93C5FD;
            box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);
        }

        .metric-title {
            color: var(--muted);
            font-size: 0.86rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            color: var(--blue);
            font-size: 1.65rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .agent-flow-grid {
            display: none;
        }

        #platform-capabilities,
        #multi-agent-flow,
        #microsoft-stack,
        #workspace {
            scroll-margin-top: 5rem;
        }

        .roadmap-shell {
            position: relative;
            border: 1px solid var(--line);
            border-radius: 8px;
            background:
                radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.16), transparent 18rem),
                linear-gradient(135deg, #EEF2FF 0%, #F8FAFC 46%, #E0F2FE 100%);
            box-shadow: 0 16px 38px rgba(15, 23, 42, 0.07);
            padding: 1.35rem;
            margin: 1.1rem 0 1.7rem;
            overflow: hidden;
        }

        .roadmap-layout {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 20rem;
            gap: 1rem;
            align-items: stretch;
        }

        .roadmap-stage {
            position: relative;
            min-height: 24rem;
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 8px;
            background:
                radial-gradient(circle at 16% 18%, rgba(139, 92, 246, 0.12), transparent 16rem),
                linear-gradient(135deg, rgba(255, 255, 255, 0.45), rgba(239, 246, 255, 0.42));
            overflow: hidden;
        }

        .curved-road {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            display: block;
            filter: drop-shadow(0 16px 28px rgba(15, 23, 42, 0.14));
        }

        .road-base {
            fill: none;
            stroke: #7C6FF2;
            stroke-width: 48;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .road-edge {
            fill: none;
            stroke: #574CE8;
            stroke-width: 58;
            stroke-linecap: round;
            stroke-linejoin: round;
            opacity: 0.28;
        }

        .road-lane {
            fill: none;
            stroke: rgba(255, 255, 255, 0.78);
            stroke-width: 5;
            stroke-linecap: round;
            stroke-linejoin: round;
            stroke-dasharray: 22 18;
            animation: laneMove 1.5s linear infinite;
        }

        .road-node {
            filter: drop-shadow(0 8px 14px rgba(15, 23, 42, 0.22));
        }

        @keyframes laneMove {
            to { stroke-dashoffset: -50; }
        }

        .road-stop {
            position: absolute;
            left: var(--x);
            top: var(--y);
            transform: translate(-50%, -50%);
            z-index: 2;
        }

        .road-pin {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2.85rem;
            height: 2.85rem;
            border: 3px solid #FFFFFF;
            border-radius: 999px 999px 999px 0;
            background: var(--pin);
            color: #FFFFFF;
            box-shadow: 0 12px 20px rgba(15, 23, 42, 0.22);
            cursor: pointer;
            font-weight: 900;
            transform: rotate(-45deg);
            transition: transform 160ms ease, box-shadow 160ms ease;
            text-decoration: none !important;
        }

        .road-pin span {
            transform: rotate(45deg);
        }

        .road-pin:hover,
        .road-pin.is-selected {
            transform: rotate(-45deg) scale(1.08);
            box-shadow: 0 16px 28px rgba(15, 23, 42, 0.30);
        }

        .road-name {
            display: none;
            position: absolute;
            left: 50%;
            width: 8.1rem;
            transform: translateX(-50%);
            color: var(--navy);
            font-size: 0.68rem;
            font-weight: 900;
            line-height: 1.2;
            text-align: center;
            text-shadow: 0 1px 0 rgba(255, 255, 255, 0.72);
        }

        .road-name.label-below {
            top: 3.05rem;
        }

        .road-name.label-above {
            bottom: 3.05rem;
        }

        .road-detail-panel {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #FFFFFF;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            padding: 1rem;
        }

        .road-detail {
            display: grid;
            min-height: 100%;
            border: 1px solid var(--line);
            border-radius: 8px;
            background:
                radial-gradient(circle at top right, rgba(15, 98, 254, 0.10), transparent 12rem),
                #FFFFFF;
            padding: 1rem;
            align-content: center;
            gap: 0.55rem;
        }

        .road-detail-index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 999px;
            background: var(--pin);
            color: #FFFFFF;
            font-weight: 900;
            box-shadow: 0 10px 18px rgba(15, 23, 42, 0.18);
        }

        .road-label-grid {
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
            gap: 0.55rem;
            margin-top: 0.9rem;
        }

        .road-name-card {
            display: block;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.78);
            color: var(--navy);
            padding: 0.62rem;
            font-size: 0.72rem;
            font-weight: 850;
            line-height: 1.2;
            min-height: 3.3rem;
            text-decoration: none !important;
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }

        .road-name-card span {
            display: block;
            color: var(--blue);
            font-size: 0.68rem;
            margin-bottom: 0.25rem;
        }

        .road-name-card:hover,
        .road-name-card.is-selected {
            border-color: #93C5FD;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.10);
            transform: translateY(-1px);
        }

        @keyframes detailIn {
            from { opacity: 0; transform: translateY(0.35rem); }
            to { opacity: 1; transform: translateY(0); }
        }

        .agent-title {
            color: var(--navy);
            font-size: 0.95rem;
            font-weight: 850;
            line-height: 1.25;
            margin-bottom: 0.45rem;
        }

        .agent-caption {
            color: var(--slate);
            font-size: 0.84rem;
            line-height: 1.45;
        }

        .stack-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.8rem;
            margin: 1rem 0 1.4rem;
        }

        .stack-pill {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #FFFFFF;
            color: var(--navy);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
            padding: 0.85rem;
            text-align: center;
            font-weight: 800;
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }

        .info-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #FFFFFF;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
            padding: 1rem;
            margin-bottom: 0.9rem;
        }

        .workspace-intro {
            border: 1px solid var(--line);
            border-radius: 8px;
            background:
                radial-gradient(circle at 92% 18%, rgba(15, 98, 254, 0.10), transparent 16rem),
                #FFFFFF;
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.07);
            padding: 1.15rem;
            margin: 1.1rem 0 1rem;
        }

        .workspace-visual-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #FFFFFF;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.07);
            padding: 0.8rem;
            margin-top: 0.2rem;
        }

        .workspace-visual-card img {
            display: block;
            width: 100%;
            border-radius: 6px;
            border: 1px solid var(--line);
            background: #F8FAFC;
        }

        .workspace-visual-title {
            color: var(--navy);
            font-weight: 850;
            margin-top: 0.7rem;
        }

        .workspace-visual-copy {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.45;
            margin-top: 0.2rem;
        }

        .info-card h3 {
            margin-top: 0;
            margin-bottom: 0.5rem;
        }

        .info-card p,
        .info-card li {
            color: var(--slate);
            line-height: 1.6;
        }

        .info-card ul {
            margin: 0.7rem 0 0;
            padding-left: 1.2rem;
        }

        .info-card li {
            margin-bottom: 0.45rem;
        }

        .config-code {
            margin: 0.8rem 0 0;
            padding: 0.85rem;
            border-radius: 8px;
            border: 1px solid var(--line);
            background: #F8FAFC;
            color: var(--navy);
            overflow-x: auto;
            font-size: 0.86rem;
            line-height: 1.45;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.34rem 0.72rem;
            font-weight: 850;
            font-size: 0.86rem;
            border: 1px solid transparent;
        }

        .badge-ready {
            color: var(--success);
            background: #ECFDF5;
            border-color: #A7F3D0;
        }

        .badge-revision {
            color: var(--warning);
            background: #FFFBEB;
            border-color: #FDE68A;
        }

        .badge-not-ready {
            color: var(--danger);
            background: #FEF2F2;
            border-color: #FECACA;
        }

        .small-note {
            color: var(--muted);
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }

        .stButton > button {
            background: var(--blue);
            color: white;
            border: 1px solid var(--blue);
            border-radius: 8px;
            padding: 0.65rem 1rem;
            font-weight: 800;
            box-shadow: 0 8px 18px rgba(15, 98, 254, 0.18);
        }

        .stButton > button:hover {
            background: var(--blue-2);
            color: white;
            border-color: var(--blue-2);
        }

        div[data-baseweb="tab-list"] {
            gap: 0.55rem;
            border-bottom: 1px solid var(--line);
        }

        div[data-baseweb="tab"] {
            background: #F1F5F9;
            border: 1px solid #E2E8F0;
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            padding: 0.72rem 1.05rem;
            font-weight: 800;
        }

        div[data-baseweb="tab"][aria-selected="true"] {
            background: #FFFFFF;
            color: var(--blue);
            border-top: 3px solid var(--blue);
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div,
        div[data-testid="stSlider"] {
            border-radius: 8px;
        }

        .footer-note {
            text-align: center;
            color: var(--muted);
            font-size: 0.92rem;
            margin-top: 2rem;
        }

        @media (max-width: 900px) {
            .stack-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            h1 {
                font-size: 3rem;
            }

            .hero-content {
                grid-template-columns: 1fr;
            }

            .hero-visual {
                max-width: 720px;
            }

            .agent-flow-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .curved-road {
                display: none;
            }

            .roadmap-shell {
                min-height: auto;
            }

            .roadmap-stage {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 1rem;
                min-height: auto;
            }

            .road-stop {
                position: relative;
                left: auto;
                top: auto;
                transform: none;
                min-height: 12.5rem;
                border: 1px solid var(--line);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.62);
                padding: 1rem;
                overflow: visible;
            }

            .road-name {
                position: static;
                width: auto;
                transform: none;
                text-align: left;
                margin-top: 0.75rem;
            }

            .road-name.label-above,
            .road-name.label-below {
                top: auto;
                bottom: auto;
            }

        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .stack-grid {
                grid-template-columns: 1fr;
            }

            .hero-panel {
                padding: 1.35rem;
            }

            h1 {
                font-size: 2.55rem;
            }

            .agent-flow-grid,
            .roadmap-layout {
                grid-template-columns: 1fr;
            }

            .road-label-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .roadmap-stage {
                min-height: 24rem;
            }
        }

        """
        + dark_theme_css
        + """
        </style>
        """,
        unsafe_allow_html=True,
    )


def local_image_uri(path):
    if not os.path.exists(path):
        return ""

    extension = os.path.splitext(path)[1].lower().replace(".", "")
    mime_type = "jpeg" if extension in {"jpg", "jpeg"} else extension
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/{mime_type};base64,{encoded}"


def image_if_exists(path, caption=None):
    if os.path.exists(path):
        st.image(path, width="stretch", caption=caption)


def render_workspace_visual(path, title, description):
    image_uri = local_image_uri(path)
    if not image_uri:
        return
    st.markdown(
        (
            '<div class="workspace-visual-card">'
            f'<img src="{image_uri}" alt="{escape(title)}">'
            f'<div class="workspace-visual-title">{escape(title)}</div>'
            f'<div class="workspace-visual-copy">{escape(description)}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def info_card(title, body_html):
    st.markdown(
        f'<div class="info-card"><h3>{escape(title)}</h3>{body_html}</div>',
        unsafe_allow_html=True,
    )


def html_list(items):
    return "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in items) + "</ul>"


def show_metric_card(title, value):
    st.markdown(
        f'<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def render_top_brand():
    st.markdown(
        (
            '<div class="top-brand">'
            '<div class="brand-logo" aria-hidden="true"></div>'
            '<div class="brand-wordmark">'
            '<div class="brand-name"><span class="brand-data">Data</span><span class="brand-dojo">Dojo</span> <span class="brand-iq">IQ</span></div>'
            '<div class="brand-tag">Foundry-powered DataOps readiness</div>'
            '</div></div>'
        ),
        unsafe_allow_html=True,
    )


def brand_markup(extra_class=""):
    return (
        f'<div class="top-brand {extra_class}">'
        '<div class="brand-logo" aria-hidden="true"></div>'
        '<div class="brand-wordmark">'
        '<div class="brand-name"><span class="brand-data">Data</span><span class="brand-dojo">Dojo</span> <span class="brand-iq">IQ</span></div>'
        '<div class="brand-tag">Foundry-powered DataOps readiness</div>'
        '</div></div>'
    )


def badge_class(status):
    normalized = status.lower()
    if "ready" == normalized or "strong" in normalized:
        return "badge-ready"
    if "revision" in normalized or "moderate" in normalized:
        return "badge-revision"
    return "badge-not-ready"


def show_status_badge(status):
    st.markdown(status_badge_html(status), unsafe_allow_html=True)


def status_badge_html(status):
    label = status
    if status == "Strong readiness":
        label = "Ready"
    elif status == "Moderate readiness":
        label = "Needs Revision"
    elif status == "Readiness risk":
        label = "Not Ready"

    return f'<span class="badge {badge_class(status)}">{escape(label)}</span>'


def feature_card(title, description, image_path, tab_label):
    image_src = local_image_uri(image_path)
    image_html = f'<img class="feature-image" src="{image_src}" alt="{escape(title)}">' if image_src else ""

    st.markdown(
        (
            f'<a class="feature-card" href="#workspace" target="_self" data-scroll-target="workspace" data-tab-label="{escape(tab_label)}">'
            f'{image_html}'
            '<span class="feature-card-body">'
            f'<span class="feature-card-title">{escape(title)}</span>'
            f'<span class="feature-card-text">{escape(description)}</span>'
            '<span class="feature-action"><span class="live-chip">Live</span><span>Open workflow -></span></span>'
            '</span>'
            '</a>'
        ),
        unsafe_allow_html=True,
    )


def render_hero():
    hero_image = ASSETS["hero_transparent"] if os.path.exists(ASSETS["hero_transparent"]) else ASSETS["hero"]
    hero_src = local_image_uri(hero_image)
    hero_visual = ""
    if hero_src:
        hero_visual = (
            f'<div class="hero-visual"><img src="{hero_src}" alt="DataDojo IQ readiness workspace illustration">'
            '<div class="live-activity">'
            '<div class="activity-row"><span>Foundry IQ grounding</span><span class="activity-dot"></span></div>'
            '<div class="activity-bar"><span></span></div>'
            '<div class="activity-row"><span>Agents evaluating readiness</span><span>Live</span></div>'
            '</div></div>'
        )

    st.markdown(
        (
            '<section class="hero-panel"><div class="hero-content"><div>'
            '<div class="eyebrow">Reasoning Agents Challenge</div>'
            '<h1>DataDojo IQ</h1>'
            '<div class="hero-tagline">From KT calls to DataOps readiness</div>'
            '<p class="hero-copy">A multi-agent Data Engineering readiness platform using Microsoft Foundry and '
            'Foundry IQ. Transform KT material, role expectations, assessments, and pipeline practice into a '
            'polished readiness workspace for learners and managers.</p>'
            '<div class="cta-row">'
            '<a class="cta-button cta-primary" href="#workspace" data-scroll-target="workspace" data-tab-label="Learner Plan">Start Readiness Workflow</a>'
            '<a class="cta-button cta-secondary" href="#multi-agent-flow" data-scroll-target="multi-agent-flow">Explore Agent Flow</a>'
            '</div></div>'
            f'{hero_visual}'
            '</div></section>'
        ),
        unsafe_allow_html=True,
    )


def render_feature_section():
    st.markdown('<div id="platform-capabilities"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Platform Capabilities</div>', unsafe_allow_html=True)
    st.markdown("## Built for Data Engineering Readiness")
    st.markdown(
        """
        <p class="section-copy">
            The experience is organized around the moments that matter after knowledge-transfer calls:
            identify role gaps, generate focused learning plans, assess readiness, practice realistic
            pipeline configuration, and surface team-level insights.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        feature_card(
            "Role-based Learning",
            "Maps each learner role to practical Data Engineering skills and turns available study time into a focused four-week plan.",
            ASSETS["learner"],
            "Learner Plan",
        )

    with col2:
        feature_card(
            "Grounded Assessments",
            "Generates role-specific practice questions designed to be grounded by Foundry IQ knowledge sources.",
            ASSETS["assessment"],
            "Assessment",
        )

    with col3:
        feature_card(
            "Pipeline Config Practice",
            "Gives learners hands-on metadata, load strategy, medallion, and governance configuration scenarios.",
            ASSETS["config"],
            "Config Practice",
        )

    with col4:
        feature_card(
            "Manager Insights",
            "Summarizes readiness percentage, risk areas, and recommended revision focus using synthetic team data.",
            ASSETS["manager"],
            "Manager Insights",
        )


def render_flow_section():
    st.markdown('<div id="multi-agent-flow"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">How It Works</div>', unsafe_allow_html=True)
    st.markdown("## Multi-agent Readiness Roadmap")

    st.markdown(
        """
        <style>
        .agent-target {
            position: absolute;
            width: 1px;
            height: 1px;
            opacity: 0;
            pointer-events: none;
        }

        .road-pin {
            text-decoration: none !important;
        }

        .road-detail-card {
            display: none;
            animation: detailIn 180ms ease;
        }

        .road-detail-card.default-detail {
            display: grid;
        }

        .roadmap-shell:has(#agent-step-1:target) .road-detail-card,
        .roadmap-shell:has(#agent-step-2:target) .road-detail-card,
        .roadmap-shell:has(#agent-step-3:target) .road-detail-card,
        .roadmap-shell:has(#agent-step-4:target) .road-detail-card,
        .roadmap-shell:has(#agent-step-5:target) .road-detail-card,
        .roadmap-shell:has(#agent-step-6:target) .road-detail-card,
        .roadmap-shell:has(#agent-step-7:target) .road-detail-card {
            display: none;
        }

        .roadmap-shell:has(#agent-step-1:target) .detail-1,
        .roadmap-shell:has(#agent-step-2:target) .detail-2,
        .roadmap-shell:has(#agent-step-3:target) .detail-3,
        .roadmap-shell:has(#agent-step-4:target) .detail-4,
        .roadmap-shell:has(#agent-step-5:target) .detail-5,
        .roadmap-shell:has(#agent-step-6:target) .detail-6,
        .roadmap-shell:has(#agent-step-7:target) .detail-7 {
            display: grid;
        }

        .roadmap-shell:has(#agent-step-1:target) .pin-1,
        .roadmap-shell:has(#agent-step-2:target) .pin-2,
        .roadmap-shell:has(#agent-step-3:target) .pin-3,
        .roadmap-shell:has(#agent-step-4:target) .pin-4,
        .roadmap-shell:has(#agent-step-5:target) .pin-5,
        .roadmap-shell:has(#agent-step-6:target) .pin-6,
        .roadmap-shell:has(#agent-step-7:target) .pin-7 {
            transform: rotate(-45deg) scale(1.08);
            box-shadow: 0 16px 28px rgba(15, 23, 42, 0.30);
        }

        .roadmap-shell:has(#agent-step-1:target) .default-pin,
        .roadmap-shell:has(#agent-step-2:target) .default-pin,
        .roadmap-shell:has(#agent-step-3:target) .default-pin,
        .roadmap-shell:has(#agent-step-4:target) .default-pin,
        .roadmap-shell:has(#agent-step-5:target) .default-pin,
        .roadmap-shell:has(#agent-step-6:target) .default-pin,
        .roadmap-shell:has(#agent-step-7:target) .default-pin {
            transform: rotate(-45deg);
            box-shadow: 0 12px 20px rgba(15, 23, 42, 0.22);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    road_svg = (
        '<svg class="curved-road" viewBox="0 0 1120 460" preserveAspectRatio="none" role="img" aria-label="Curved multi-agent readiness roadmap">'
        '<path class="road-edge" d="M120 338 C220 230 290 332 390 244 C486 158 584 362 686 232 C778 112 858 250 950 128 C1014 48 1062 42 1100 18" />'
        '<path class="road-base" d="M120 338 C220 230 290 332 390 244 C486 158 584 362 686 232 C778 112 858 250 950 128 C1014 48 1062 42 1100 18" />'
        '<path class="road-lane" d="M120 338 C220 230 290 332 390 244 C486 158 584 362 686 232 C778 112 858 250 950 128 C1014 48 1062 42 1100 18" />'
        '</svg>'
    )

    target_html = "".join(
        f'<span id="agent-step-{index + 1}" class="agent-target"></span>'
        for index in range(len(AGENT_FLOW))
    )

    stop_html = "".join(
        (
            f'<div class="road-stop" style="--x:{step["x"]}%;--y:{step["y"]}%;--pin:{step["color"]};">'
            f'<a class="road-pin pin-{index + 1} {"default-pin is-selected" if index == 0 else ""}" '
            f'href="#agent-step-{index + 1}" target="_self" aria-label="{escape(step["title"])}">'
            f'<span>{index + 1}</span>'
            '</a>'
            f'<div class="road-name {"label-below" if index % 2 == 0 else "label-above"}">{escape(step["title"])}</div>'
            '</div>'
        )
        for index, step in enumerate(AGENT_FLOW)
    )

    detail_html = "".join(
        (
            f'<div class="road-detail road-detail-card detail-{index + 1} {"default-detail" if index == 0 else ""}" '
            f'style="--pin:{step["color"]};">'
            f'<div class="road-detail-index">{index + 1}</div>'
            f'<div class="agent-title">{escape(step["title"])}</div>'
            f'<div class="agent-caption">{escape(step["caption"])}</div>'
            '</div>'
        )
        for index, step in enumerate(AGENT_FLOW)
    )

    label_html = "".join(
        (
            f'<a class="road-name-card" href="#agent-step-{index + 1}" target="_self">'
            f'<span>Step {index + 1}</span>{escape(step["title"])}'
            '</a>'
        )
        for index, step in enumerate(AGENT_FLOW)
    )

    st.markdown(
        (
            '<div class="roadmap-shell">'
            f'{target_html}'
            '<div class="roadmap-layout">'
            '<div class="roadmap-stage">'
            f'{road_svg}{stop_html}'
            '</div>'
            f'<div class="road-detail-panel">{detail_html}</div>'
            '</div>'
            f'<div class="road-label-grid">{label_html}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

def render_stack_section():
    st.markdown('<div id="microsoft-stack"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Microsoft Stack</div>', unsafe_allow_html=True)
    st.markdown("## Hackathon Architecture")
    stack_html = '<div class="stack-grid">'
    for item in MICROSOFT_STACK:
        stack_html += f'<div class="stack-pill">{item}</div>'
    stack_html += "</div>"
    st.markdown(stack_html, unsafe_allow_html=True)


def render_theme_selector():
    with st.sidebar:
        st.markdown(brand_markup("sidebar-brand"), unsafe_allow_html=True)
        st.markdown('<div class="theme-label">Theme</div>', unsafe_allow_html=True)

        dark_enabled = st.toggle("Dark theme", value=False, key="theme_toggle")

        theme_mode = "Black theme" if dark_enabled else "White theme"
        return theme_mode


def install_smooth_scroll_handler():
    st.html(
        """
        <script>
        const bindSmoothScroll = () => {
          try {
            const doc = document;
            const openWorkflowTab = (label) => {
              if (!label) return;
              const candidates = Array.from(doc.querySelectorAll('[role="tab"], button, [data-baseweb="tab"]'));
              const normalize = (value) => (value || '').replace(/\\s+/g, ' ').trim();
              const tab = candidates.find((node) => normalize(node.textContent) === label);
              if (tab) tab.click();
            };
            doc.querySelectorAll('[data-scroll-target]').forEach((link) => {
              if (link.dataset.smoothBound === 'true') return;
              link.dataset.smoothBound = 'true';
              link.addEventListener('click', (event) => {
                const targetId = link.getAttribute('data-scroll-target');
                const target = doc.getElementById(targetId);
                const tabLabel = link.getAttribute('data-tab-label');
                if (!target) return;
                event.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                window.setTimeout(() => openWorkflowTab(tabLabel), 460);
                history.replaceState(null, '', `#${targetId}`);
              });
            });
          } catch (error) {
            // Native anchor fallback remains in place if parent access is unavailable.
          }
        };
        bindSmoothScroll();
        setTimeout(bindSmoothScroll, 600);
        setTimeout(bindSmoothScroll, 1400);
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Hackathon Summary")
        st.markdown("**Challenge:** Reasoning Agents")
        st.markdown("**IQ Layer:** Foundry IQ")
        st.markdown("**Data Policy:** Synthetic data only")
        st.markdown("---")
        st.markdown("### Navigation")
        st.markdown(
            '<div class="sidebar-nav">'
            '<a href="#platform-capabilities">Platform Capabilities</a>'
            '<a href="#multi-agent-flow">Agent Flow</a>'
            '<a href="#microsoft-stack">Microsoft Stack</a>'
            '<a href="#workspace">Interactive Workspace</a>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("### Agent Modules")
        st.markdown("- Role Skill Mapper Agent")
        st.markdown("- Learning Path Curator Agent")
        st.markdown("- Study Plan Generator Agent")
        st.markdown("- Assessment Agent")
        st.markdown("- Config Practice Evaluator Agent")
        st.markdown("- Manager Insights Agent")


theme_mode = render_theme_selector()
inject_custom_css(theme_mode)
render_sidebar()
install_smooth_scroll_handler()
render_top_brand()
render_hero()

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
with metric_col1:
    show_metric_card("Roles Covered", "4")
with metric_col2:
    show_metric_card("Agent Flow Steps", "7")
with metric_col3:
    show_metric_card("Challenge Track", "Reasoning")
with metric_col4:
    show_metric_card("Data Policy", "Synthetic")

st.markdown("")
render_feature_section()
st.markdown("")
render_flow_section()
st.markdown("")
render_stack_section()

st.markdown('<div id="workspace"></div>', unsafe_allow_html=True)
st.markdown(
    (
        '<div class="workspace-intro">'
        '<div class="section-kicker">Interactive Workspace</div>'
        '<h2>Try the DataDojo IQ Workflow</h2>'
        '<p class="section-copy">Generate learner plans, practice assessments, evaluate pipeline configuration answers, '
        'and review synthetic manager insights from one focused readiness workspace.</p>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Learner Plan",
        "Assessment",
        "Config Practice",
        "Manager Insights",
    ]
)

with tab1:
    st.markdown("## Learner Plan")
    st.markdown(
        '<div class="small-note">Role Skill Mapper Agent + Study Plan Generator Agent</div>',
        unsafe_allow_html=True,
    )

    top1, top2 = st.columns([1.2, 1], gap="large")

    with top1:
        role = st.selectbox("Select Role", ROLES)
        target_skill = st.selectbox("Target Skill", TARGET_SKILLS)
        available_hours = st.slider("Available study hours per week", 1, 20, 8)

        if st.button("Generate Learning Plan"):
            skills = map_role_to_skills(role)
            plan = generate_study_plan(role, available_hours)

            info_card(
                "Role Summary",
                (
                    f"<p><strong>Selected role:</strong> {escape(role)}</p>"
                    f"<p><strong>Target skill:</strong> {escape(target_skill)}</p>"
                    f"<p><strong>Available hours per week:</strong> {available_hours}</p>"
                    f"<p><strong>Recommended pace:</strong> {escape(plan['pace'].title())}</p>"
                ),
            )

            info_card("Required Skills", html_list(skills))

            plan_items = [
                f"<li><strong>{escape(key.replace('_', ' ').title())}:</strong> {escape(str(value))}</li>"
                for key, value in plan.items()
                if key != "pace"
            ]
            info_card("4-Week Study Plan", "<ul>" + "".join(plan_items) + "</ul>")

    with top2:
        render_workspace_visual(
            ASSETS["learner"],
            "Learning Plan Workspace",
            "Turns a selected role, target skill, and study capacity into a focused readiness path.",
        )

with tab2:
    st.markdown("## Assessment")
    st.markdown('<div class="small-note">Assessment Agent</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        role_for_assessment = st.selectbox("Assessment Role", ROLES, key="assessment_role")

        if st.button("Generate Practice Questions"):
            questions = generate_questions(role_for_assessment)

            question_items = [
                f"{index}. {question['question']}"
                for index, question in enumerate(questions, start=1)
            ]
            info_card(
                "Practice Questions",
                html_list(question_items)
                + "<p><strong>Grounding note:</strong> In the final Foundry version, these questions will be grounded using Foundry IQ knowledge documents.</p>",
            )

        score = st.slider("Enter practice score", 0, 100, 70)
        readiness = calculate_readiness(score)

        info_card(
            "Readiness Result",
            f"<p><strong>Practice Score:</strong> {score}</p><p><strong>Readiness Status:</strong> {status_badge_html(readiness)}</p>",
        )

    with col2:
        render_workspace_visual(
            ASSETS["assessment"],
            "Assessment Workspace",
            "Generates role-specific readiness questions and converts scores into clear status signals.",
        )

with tab3:
    st.markdown("## Config Practice")
    st.markdown(
        '<div class="small-note">Config Practice Evaluator Agent</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        role_for_task = st.selectbox("Select Role for Config Challenge", ROLES, key="task_role")

        if st.button("Generate Config Challenge"):
            task = generate_config_task(role_for_task)

            requirements = escape(json.dumps(task["requirements"], indent=2))
            info_card(
                "Practice Task",
                f"<p>{escape(task['task'])}</p><pre class=\"config-code\">{requirements}</pre>",
            )

        answer = st.text_area("Paste your answer here", height=180)

        if st.button("Evaluate Answer"):
            score, feedback = evaluate_config_answer(answer, role_for_task)
            readiness = calculate_readiness(score)

            info_card(
                "Evaluation Summary",
                f"<p><strong>Score:</strong> {score}</p>"
                f"<p><strong>Readiness Status:</strong> {status_badge_html(readiness)}</p>"
                "<h3>Feedback</h3>"
                + html_list(feedback),
            )

    with col2:
        render_workspace_visual(
            ASSETS["config"],
            "Configuration Practice Workspace",
            "Evaluates pipeline metadata, load strategy, and governance configuration answers.",
        )

with tab4:
    st.markdown("## Manager Insights")
    st.markdown('<div class="small-note">Manager Insights Agent</div>', unsafe_allow_html=True)

    left, right = st.columns([1.2, 1], gap="large")

    with left:
        if st.button("Generate Manager Summary"):
            summaries = generate_manager_summary()

            for item in summaries:
                info_card(
                    f"{item['team_id']} - {item['role']}",
                    f"<p>{escape(item['summary'])}</p>"
                    f"<p><strong>Readiness Percentage:</strong> {item['readiness_percentage']}%</p>"
                    f"<p><strong>Status:</strong> {status_badge_html(item['status'])}</p>"
                    f"<p><strong>Risk Area:</strong> {escape(item['risk_area'])}</p>"
                    f"<p><strong>Recommendation:</strong> {escape(item['recommendation'])}</p>",
                )

    with right:
        render_workspace_visual(
            ASSETS["manager"],
            "Manager Insights Workspace",
            "Summarizes synthetic team readiness, risk areas, and recommended revision focus.",
        )

st.markdown(
    '<div class="footer-note">Built for the Microsoft Foundry Reasoning Agents challenge using synthetic data only.</div>',
    unsafe_allow_html=True,
)
