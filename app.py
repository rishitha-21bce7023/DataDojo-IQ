import base64
import hashlib
from html import escape
import json
import os
import re

import streamlit as st

from foundry_client import ask_foundry_agent
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
        "caption": "Maps the learner role to the skills needed for Data Engineering work.",
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
        .foundry-title,
        .foundry-response-title,
        .metric-value,
        .stack-pill,
        .info-card h3 {
            color: #F8FAFC;
        }

        .section-copy,
        .brand-tag,
        .feature-card-text,
        .agent-caption,
        .foundry-subtitle,
        .foundry-response-body,
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
        .foundry-section,
        .foundry-panel,
        .foundry-response-card,
        .foundry-flow-step,
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

        .foundry-badge {
            background: #101010;
            border-color: #2F2F2F;
            color: #DBEAFE;
        }

        .foundry-live-chip {
            background: rgba(16, 185, 129, 0.14);
            border-color: rgba(167, 243, 208, 0.42);
            color: #A7F3D0;
        }

        .foundry-flow-arrow {
            color: #93C5FD;
        }

        .foundry-signal-panel,
        .foundry-prompt-shell {
            background: #101010;
            border-color: #2F2F2F;
        }

        .foundry-signal-row {
            border-bottom-color: #2F2F2F;
            color: #CBD5E1;
        }

        .foundry-signal-row strong {
            color: #F8FAFC;
        }

        .foundry-cta.secondary {
            background: #101010;
            border-color: #2F2F2F;
            color: #93C5FD !important;
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

        .foundry-section,
        .foundry-panel,
        .foundry-response-card,
        .foundry-flow-step,
        .foundry-step-card,
        .foundry-signal-panel,
        .foundry-prompt-shell,
        .workflow-section-label,
        .info-card,
        .metric-card,
        .workspace-intro,
        .workspace-visual-card,
        .roadmap-shell,
        .road-detail-panel,
        .road-name-card,
        .stack-pill {
            background: #151515 !important;
            border-color: #334155 !important;
            color: #F8FAFC !important;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.34) !important;
        }

        a.feature-card,
        .feature-card-body,
        .road-detail {
            background: #111827 !important;
            border-color: #334155 !important;
            color: #F8FAFC !important;
        }

        .foundry-title,
        .foundry-response-title,
        .foundry-flow-step,
        .foundry-step-title,
        .foundry-response-body h3,
        .foundry-response-body h4,
        .workflow-section-title,
        .workspace-visual-title,
        .feature-card-title,
        .metric-value,
        .stack-pill,
        .info-card h1,
        .info-card h2,
        .info-card h3,
        .road-name-card,
        .road-detail .agent-title {
            color: #F8FAFC !important;
        }

        .foundry-subtitle,
        .foundry-response-body,
        .foundry-step-copy,
        .workflow-section-copy,
        .foundry-signal-row,
        .workspace-visual-copy,
        .feature-card-text,
        .metric-title,
        .info-card p,
        .info-card li,
        .road-detail .agent-caption,
        .section-copy,
        .small-note,
        .footer-note {
            color: #CBD5E1 !important;
        }

        .foundry-badge,
        .badge {
            background: #0B1220 !important;
            border-color: #334155 !important;
            color: #DBEAFE !important;
        }

        .foundry-live-chip,
        .live-chip {
            background: rgba(52, 211, 153, 0.14) !important;
            border-color: rgba(52, 211, 153, 0.55) !important;
            color: #A7F3D0 !important;
        }

        .foundry-flow-arrow,
        .foundry-kicker,
        .section-kicker {
            color: #60A5FA !important;
        }

        .foundry-signal-row {
            border-bottom-color: #334155 !important;
        }

        .foundry-signal-row strong {
            color: #F8FAFC !important;
        }

        .foundry-response-lead {
            background: rgba(96, 165, 250, 0.14) !important;
            color: #DBEAFE !important;
            border-left-color: #60A5FA !important;
        }

        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] *,
        label,
        [data-testid="stSelectbox"] *,
        [data-testid="stSlider"] *,
        [data-testid="stTextArea"] *,
        [data-testid="stTabs"] * {
            color: #E5E7EB !important;
        }

        [data-testid="stSelectbox"] div,
        [data-testid="stTextArea"] textarea,
        textarea,
        input {
            background: #111827 !important;
            border-color: #334155 !important;
            color: #F8FAFC !important;
        }

        [data-testid="stTextArea"] textarea::placeholder,
        input::placeholder {
            color: #94A3B8 !important;
        }

        .foundry-response-topnote {
            background: rgba(96, 165, 250, 0.13) !important;
            border-color: #334155 !important;
            color: #DBEAFE !important;
        }

        .foundry-mini-flow-step,
        .foundry-agent-step,
        .foundry-agent-node,
        .foundry-list-card,
        .foundry-section-card,
        .foundry-summary-card,
        .foundry-learning-card,
        .foundry-feedback-card,
        .foundry-insight-card,
        .foundry-risk-card,
        .foundry-gap-card,
        .foundry-action-card,
        .foundry-question-card,
        .score-summary-card,
        .source-chip,
        .foundry-source-chip {
            background: #0B1220 !important;
            border-color: #334155 !important;
            color: #F8FAFC !important;
        }

        .foundry-summary-card {
            border-left-color: #60A5FA !important;
            background: rgba(96, 165, 250, 0.10) !important;
        }

        .foundry-learning-card {
            border-left-color: #34D399 !important;
            background: rgba(52, 211, 153, 0.09) !important;
        }

        .foundry-feedback-card {
            border-left-color: #FBBF24 !important;
            background: rgba(251, 191, 36, 0.10) !important;
        }

        .foundry-insight-card {
            border-left-color: #A78BFA !important;
            background: rgba(167, 139, 250, 0.10) !important;
        }

        .foundry-risk-card {
            border-left-color: #F87171 !important;
            background: rgba(248, 113, 113, 0.09) !important;
        }

        .foundry-gap-card {
            border-left-color: #A78BFA !important;
            background: rgba(167, 139, 250, 0.10) !important;
        }

        .foundry-action-card {
            border-left-color: #34D399 !important;
            background: rgba(52, 211, 153, 0.09) !important;
        }

        .foundry-question-card {
            border-left-color: #60A5FA !important;
            background: rgba(96, 165, 250, 0.10) !important;
        }

        .foundry-section-heading {
            color: #F8FAFC !important;
        }

        .foundry-highlight,
        .foundry-keyword {
            background: rgba(96, 165, 250, 0.14) !important;
            border-color: #334155 !important;
            color: #DBEAFE !important;
        }

        .foundry-status-ready {
            background: rgba(52, 211, 153, 0.16) !important;
            border-color: rgba(52, 211, 153, 0.55) !important;
            color: #A7F3D0 !important;
        }

        .foundry-status-revision {
            background: rgba(251, 191, 36, 0.14) !important;
            border-color: rgba(251, 191, 36, 0.52) !important;
            color: #FDE68A !important;
        }

        .foundry-status-risk {
            background: rgba(248, 113, 113, 0.14) !important;
            border-color: rgba(248, 113, 113, 0.52) !important;
            color: #FECACA !important;
        }

        .foundry-status-info {
            background: rgba(96, 165, 250, 0.14) !important;
            border-color: rgba(96, 165, 250, 0.52) !important;
            color: #DBEAFE !important;
        }

        .foundry-mini-flow-arrow,
        .foundry-agent-arrow,
        .foundry-list-index,
        .score-summary-value {
            color: #60A5FA !important;
        }

        .foundry-question-number {
            background: #2563EB !important;
            color: #FFFFFF !important;
        }

        .score-summary-title {
            color: #F8FAFC !important;
        }

        .score-summary-note {
            color: #CBD5E1 !important;
        }

        .score-progress-track {
            background: #1E293B !important;
        }

        .score-progress-fill {
            background: linear-gradient(90deg, #60A5FA, #34D399) !important;
        }

        .foundry-mini-flow-arrow,
        .foundry-agent-arrow,
        .foundry-list-index {
            color: #60A5FA !important;
        }

        .stButton > button {
            background: #2563EB !important;
            border-color: #2563EB !important;
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] * {
            color: #E5E7EB !important;
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

        .foundry-section {
            border: 1px solid var(--line);
            border-radius: 12px;
            background:
                radial-gradient(circle at 88% 8%, rgba(15, 98, 254, 0.14), transparent 18rem),
                linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 54%, #EAF2FF 100%);
            box-shadow: 0 18px 42px rgba(15, 23, 42, 0.10);
            padding: 1.35rem;
            margin: 1.35rem 0 1.6rem;
        }

        .foundry-section-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .foundry-kicker {
            color: var(--blue);
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 0.25rem;
        }

        .foundry-title {
            color: var(--navy);
            font-size: 1.65rem;
            line-height: 1.15;
            font-weight: 900;
            margin: 0;
        }

        .foundry-subtitle {
            color: var(--slate);
            font-size: 0.98rem;
            line-height: 1.55;
            margin: 0.45rem 0 0;
        }

        .foundry-badge-row {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin: 1rem 0;
        }

        .foundry-badge {
            display: inline-flex;
            align-items: center;
            border: 1px solid #BFDBFE;
            border-radius: 999px;
            background: #EFF6FF;
            color: #1D4ED8;
            padding: 0.34rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 850;
        }

        .foundry-live-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.42rem;
            white-space: nowrap;
            border: 1px solid #A7F3D0;
            border-radius: 999px;
            background: #ECFDF5;
            color: #047857;
            padding: 0.42rem 0.7rem;
            font-size: 0.78rem;
            font-weight: 900;
        }

        .foundry-live-chip::before {
            content: "";
            width: 0.45rem;
            height: 0.45rem;
            border-radius: 999px;
            background: #10B981;
            animation: pulseDot 1.8s ease-out infinite;
        }

        .foundry-flow {
            display: grid;
            grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
            align-items: center;
            gap: 0.7rem;
            margin: 1rem 0;
        }

        .foundry-panel .foundry-flow {
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.7rem;
        }

        .foundry-panel .foundry-flow-arrow {
            display: none;
        }

        .foundry-architecture-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.45fr) minmax(18rem, 0.75fr);
            gap: 1rem;
            align-items: stretch;
            margin-top: 1rem;
        }

        .foundry-signal-panel {
            border: 1px solid var(--line);
            border-radius: 12px;
            background:
                radial-gradient(circle at top right, rgba(16, 185, 129, 0.12), transparent 10rem),
                rgba(255, 255, 255, 0.84);
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.07);
            padding: 1rem;
        }

        .foundry-signal-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            border-bottom: 1px solid var(--line);
            padding: 0.62rem 0;
            color: var(--slate);
            font-size: 0.86rem;
        }

        .foundry-signal-row:last-child {
            border-bottom: none;
        }

        .foundry-signal-row strong {
            color: var(--navy);
        }

        .foundry-cta-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.65rem;
            margin-top: 1rem;
        }

        .foundry-cta {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 2.65rem;
            border-radius: 8px;
            background: var(--blue);
            border: 1px solid var(--blue);
            color: #FFFFFF !important;
            padding: 0.62rem 0.9rem;
            font-weight: 900;
            text-decoration: none !important;
            box-shadow: 0 12px 24px rgba(15, 98, 254, 0.20);
        }

        .foundry-cta.secondary {
            background: #FFFFFF;
            color: var(--blue) !important;
            border-color: #BFDBFE;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.06);
        }

        .foundry-flow-step {
            min-height: 4.4rem;
            border: 1px solid var(--line);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.82);
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.06);
            padding: 0.8rem;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: var(--navy);
            font-weight: 900;
            line-height: 1.25;
        }

        .foundry-flow-arrow {
            color: var(--blue);
            font-weight: 900;
            font-size: 1.25rem;
        }

        .foundry-panel {
            border: 1px solid var(--line);
            border-radius: 12px;
            background:
                radial-gradient(circle at 92% 12%, rgba(15, 98, 254, 0.12), transparent 14rem),
                #FFFFFF;
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
            padding: 1rem;
            margin: 1.1rem 0 0;
            width: 100%;
        }

        .foundry-panel-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
        }

        .foundry-response-card {
            border: 1px solid var(--line);
            border-radius: 12px;
            background:
                radial-gradient(circle at 96% 0%, rgba(15, 98, 254, 0.10), transparent 15rem),
                #FFFFFF;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.08);
            padding: 1.05rem;
            margin: 1rem 0 0;
        }

        .foundry-response-topnote {
            border: 1px solid #BFDBFE;
            border-radius: 999px;
            background: #EFF6FF;
            color: #1D4ED8;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.78rem;
            font-weight: 850;
            padding: 0.42rem 0.72rem;
            margin-bottom: 0.85rem;
        }

        .foundry-response-topnote::before {
            content: "";
            width: 0.48rem;
            height: 0.48rem;
            border-radius: 999px;
            background: #10B981;
            box-shadow: 0 0 0 0.28rem rgba(16, 185, 129, 0.14);
        }

        .foundry-response-title {
            color: var(--navy);
            font-weight: 900;
            margin-bottom: 0.55rem;
            font-size: 1.12rem;
        }

        .foundry-response-body {
            color: var(--slate);
            line-height: 1.65;
            font-size: 0.95rem;
        }

        .foundry-response-body p {
            margin: 0.55rem 0;
        }

        .foundry-response-lead {
            border-left: 4px solid var(--blue);
            background: #EFF6FF;
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            margin-bottom: 0.85rem;
            color: var(--navy);
            font-weight: 750;
        }

        .foundry-mini-flow,
        .foundry-agent-flow {
            display: flex;
            align-items: stretch;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin: 0.75rem 0 1rem;
        }

        .foundry-mini-flow-step,
        .foundry-agent-step {
            border: 1px solid var(--line);
            border-radius: 10px;
            background: #FFFFFF;
            color: var(--navy);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            min-height: 3rem;
            padding: 0.65rem 0.8rem;
            font-weight: 900;
            line-height: 1.2;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
        }

        .foundry-mini-flow-arrow,
        .foundry-agent-arrow {
            display: flex;
            align-items: center;
            color: var(--blue);
            font-weight: 950;
            font-size: 1.05rem;
        }

        .foundry-section-heading {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            color: var(--navy);
            font-size: 1.06rem;
            line-height: 1.25;
            font-weight: 950;
            margin: 1.1rem 0 0.55rem;
        }

        .foundry-section-heading::before {
            content: "";
            width: 0.82rem;
            height: 0.82rem;
            border-radius: 0.25rem;
            background: linear-gradient(135deg, #0F62FE, #34D399);
            box-shadow: 0 0 0 0.24rem rgba(15, 98, 254, 0.11);
            flex: 0 0 auto;
        }

        .foundry-highlight,
        .foundry-keyword,
        .source-chip,
        .foundry-source-chip,
        .foundry-status-ready,
        .foundry-status-revision,
        .foundry-status-risk,
        .foundry-status-info {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            font-weight: 900;
            line-height: 1;
            white-space: nowrap;
            vertical-align: baseline;
        }

        .foundry-highlight,
        .foundry-keyword {
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            color: #1D4ED8;
            padding: 0.18rem 0.42rem;
            font-size: 0.86em;
        }

        .source-chip,
        .foundry-source-chip {
            background: #F8FAFC;
            border: 1px solid var(--line);
            color: var(--navy);
            margin: 0.22rem 0.3rem 0.22rem 0;
            padding: 0.42rem 0.62rem;
            font-size: 0.82rem;
        }

        .source-chip::before,
        .foundry-source-chip::before {
            content: "doc";
            margin-right: 0.38rem;
            color: var(--blue);
            font-size: 0.72rem;
            font-weight: 950;
            text-transform: uppercase;
        }

        .source-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin: 0.35rem 0 0.85rem;
        }

        .foundry-status-ready {
            background: #D1FAE5;
            border: 1px solid #A7F3D0;
            color: #047857;
            padding: 0.28rem 0.5rem;
        }

        .foundry-status-revision {
            background: #FEF3C7;
            border: 1px solid #FDE68A;
            color: #92400E;
            padding: 0.28rem 0.5rem;
        }

        .foundry-status-risk {
            background: #FEE2E2;
            border: 1px solid #FECACA;
            color: #B91C1C;
            padding: 0.28rem 0.5rem;
        }

        .foundry-status-info {
            background: #DBEAFE;
            border: 1px solid #BFDBFE;
            color: #1D4ED8;
            padding: 0.28rem 0.5rem;
        }

        .foundry-list-card,
        .foundry-section-card,
        .foundry-summary-card,
        .foundry-learning-card,
        .foundry-feedback-card,
        .foundry-insight-card,
        .foundry-risk-card,
        .foundry-gap-card,
        .foundry-action-card,
        .foundry-question-card {
            border: 1px solid var(--line);
            border-left: 5px solid var(--blue);
            border-radius: 10px;
            background: #FFFFFF;
            color: var(--slate);
            padding: 0.72rem 0.85rem;
            margin: 0.55rem 0;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
        }

        .foundry-summary-card {
            background: #EFF6FF;
            border-left-color: var(--blue);
        }

        .foundry-learning-card {
            background: #ECFDF5;
            border-left-color: #10B981;
        }

        .foundry-feedback-card {
            background: #FFFBEB;
            border-left-color: #F59E0B;
        }

        .foundry-insight-card {
            background: #F5F3FF;
            border-left-color: #8B5CF6;
        }

        .foundry-risk-card {
            border-left-color: #EF4444;
            background: #FFF7ED;
        }

        .foundry-gap-card {
            border-left-color: #8B5CF6;
            background: #F5F3FF;
        }

        .foundry-action-card {
            border-left-color: #10B981;
            background: #ECFDF5;
        }

        .foundry-question-card {
            display: grid;
            grid-template-columns: auto 1fr;
            align-items: start;
            gap: 0.7rem;
            background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%);
            border-left-color: #0F62FE;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }

        .foundry-question-card:hover {
            transform: translateY(-2px);
            border-color: #93C5FD;
            box-shadow: 0 12px 24px rgba(15, 98, 254, 0.12);
        }

        .foundry-question-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background: var(--blue);
            color: #FFFFFF;
            font-size: 0.85rem;
            font-weight: 950;
            box-shadow: 0 8px 18px rgba(15, 98, 254, 0.20);
        }

        .foundry-list-index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 1.55rem;
            height: 1.55rem;
            border-radius: 999px;
            margin-right: 0.48rem;
            background: #DBEAFE;
            color: #1D4ED8;
            font-size: 0.78rem;
            font-weight: 950;
        }

        .score-summary-card {
            border: 1px solid var(--line);
            border-radius: 12px;
            background:
                radial-gradient(circle at 96% 10%, rgba(15, 98, 254, 0.12), transparent 12rem),
                #FFFFFF;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.08);
            padding: 1rem;
            margin: 1rem 0 1.2rem;
        }

        .score-summary-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }

        .score-summary-title {
            color: var(--navy);
            font-weight: 950;
            font-size: 1rem;
        }

        .score-summary-value {
            color: var(--blue);
            font-weight: 950;
            font-size: 1.55rem;
        }

        .score-progress-track {
            width: 100%;
            height: 0.72rem;
            border-radius: 999px;
            overflow: hidden;
            background: #E2E8F0;
            margin: 0.75rem 0;
        }

        .score-progress-fill {
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #0F62FE, #10B981);
        }

        .score-summary-note {
            color: var(--slate);
            font-size: 0.9rem;
            line-height: 1.55;
            margin: 0;
        }

        .foundry-prompt-shell {
            border: 1px solid var(--line);
            border-top: none;
            border-radius: 0 0 12px 12px;
            background:
                linear-gradient(180deg, rgba(248, 250, 252, 0.86), #FFFFFF);
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
            padding: 0 1rem 1rem;
            margin: -0.05rem 0 1rem;
        }

        .foundry-steps {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 1rem;
        }

        .foundry-step-card {
            border: 1px solid var(--line);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.86);
            padding: 0.85rem;
            min-height: 6rem;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
        }

        .foundry-step-index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.75rem;
            height: 1.75rem;
            border-radius: 999px;
            background: var(--blue);
            color: #FFFFFF;
            font-weight: 900;
            margin-bottom: 0.45rem;
        }

        .foundry-step-title {
            color: var(--navy);
            font-weight: 900;
            margin-bottom: 0.2rem;
        }

        .foundry-step-copy {
            color: var(--slate);
            font-size: 0.86rem;
            line-height: 1.45;
        }

        .workflow-section-label {
            border: 1px solid var(--line);
            border-radius: 10px;
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(239, 246, 255, 0.74));
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
            padding: 0.9rem 1rem;
            margin: 1rem 0 1rem;
        }

        .workflow-section-label.local {
            border-left: 4px solid #64748B;
        }

        .workflow-section-label.foundry {
            border-left: 4px solid var(--blue);
        }

        .workflow-section-title {
            color: var(--navy);
            font-size: 1.16rem;
            font-weight: 900;
            margin-bottom: 0.25rem;
        }

        .workflow-section-copy {
            color: var(--slate);
            line-height: 1.5;
            font-size: 0.94rem;
        }

        .foundry-prompt-shell + div[data-testid="stTextArea"] textarea,
        .foundry-panel + div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextArea"] textarea[aria-label="Prompt sent to DataDojo-IQ-Orchestrator"] {
            border-radius: 10px;
            border: 1px solid #BFDBFE;
            background: #FFFFFF;
            box-shadow: inset 0 1px 0 rgba(15, 23, 42, 0.03);
        }

        .foundry-panel + div[data-testid="stTextArea"] + div[data-testid="stButton"] button,
        .foundry-prompt-shell + div[data-testid="stTextArea"] + div[data-testid="stButton"] button {
            width: 100%;
            min-height: 3rem;
            border-radius: 10px;
            background: linear-gradient(135deg, #0F62FE, #2563EB);
            box-shadow: 0 12px 26px rgba(15, 98, 254, 0.22);
        }

        .agent-flow-grid {
            display: none;
        }

        #platform-capabilities,
        #foundry-integration,
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
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
            color: #FFFFFF !important;
            line-height: 1;
            text-align: center;
            transform: rotate(45deg) translate(0.03rem, -0.03rem);
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

            .foundry-section-header {
                display: grid;
            }

            .foundry-architecture-grid {
                grid-template-columns: 1fr;
            }

            .foundry-flow {
                grid-template-columns: 1fr;
            }

            .foundry-flow-arrow {
                transform: rotate(90deg);
                justify-self: center;
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


def workflow_section_label(title, helper_text, section_type="local"):
    st.markdown(
        (
            f'<div class="workflow-section-label {escape(section_type)}">'
            f'<div class="workflow-section-title">{escape(title)}</div>'
            f'<div class="workflow-section-copy">{escape(helper_text)}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


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
            '<div class="brand-tag">Foundry-powered Data Engineering readiness</div>'
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
        '<div class="brand-tag">Foundry-powered Data Engineering readiness</div>'
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


def local_quick_readiness_status(score):
    if score >= 75:
        return "Ready"
    if score >= 60:
        return "Needs Revision"
    return "Not Ready"


def foundry_status_badge_html(status):
    status_class = {
        "Ready": "foundry-status-ready",
        "Needs Revision": "foundry-status-revision",
        "Not Ready": "foundry-status-risk",
    }.get(status, "foundry-status-info")
    return f'<span class="{status_class}">{escape(status)}</span>'


def render_assessment_score_summary(score):
    status = local_quick_readiness_status(score)
    st.markdown(
        (
            '<div class="score-summary-card">'
            '<div class="score-summary-top">'
            '<div>'
            '<div class="score-summary-title">Assessment Score Summary</div>'
            f'<div class="score-summary-value">Practice Score: {score}/100</div>'
            '</div>'
            f'<div>{foundry_status_badge_html(status)}</div>'
            '</div>'
            '<div class="score-progress-track">'
            f'<div class="score-progress-fill" style="width: {score}%;"></div>'
            '</div>'
            f'<p class="score-summary-note"><strong>Local quick status:</strong> {escape(status)}. '
            'Final readiness explanation is generated by the Foundry agent using grounded knowledge.</p>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def stable_prompt_suffix(*values):
    digest = hashlib.sha1("|".join(str(value) for value in values).encode("utf-8")).hexdigest()[:10]
    return f"_{digest}"


def build_learner_foundry_prompt(role, target_skill, available_hours, duration):
    skills = map_role_to_skills(role)
    local_plan = generate_study_plan(role, available_hours)
    plan_lines = [
        f"- {key.replace('_', ' ').title()}: {value}"
        for key, value in local_plan.items()
        if key != "pace"
    ]
    return (
        f"Create a grounded learning path for a {role} preparing for {target_skill}. "
        f"The learner has {available_hours} available study hours per week and requested a {duration} readiness path. "
        f"The local synthetic rules currently recommend a {local_plan['pace']} pace. "
        "Use the attached synthetic Data Engineering knowledge files and return:\n"
        "1. Requirement summary\n"
        "2. Required skills\n"
        "3. Learning plan\n"
        "4. Readiness checkpoints\n"
        "5. Recommended revision focus\n"
        "6. Next actions\n"
        "7. Sources used\n\n"
        "Local synthetic skill context:\n"
        + "\n".join(f"- {skill}" for skill in skills)
        + "\n\nLocal synthetic plan context:\n"
        + "\n".join(plan_lines)
    )


def generic_config_requirements(requirements):
    generic = {}
    for key, value in requirements.items():
        if key == "source_system":
            generic[key] = "synthetic_source_system"
        elif key == "source_table":
            generic[key] = "synthetic_source_entity"
        elif key == "primary_keys":
            generic[key] = ["synthetic_primary_key_1", "synthetic_primary_key_2"]
        elif key == "watermark_column":
            generic[key] = "synthetic_watermark_column"
        elif key == "domain":
            generic[key] = "synthetic_business_domain"
        else:
            generic[key] = value
    return generic


def generic_config_task_text(task_text):
    replacements = {
        "customer table": "synthetic source entity",
        "enterprise logistics dataset": "synthetic business domain dataset",
    }
    safe_text = task_text
    for original, replacement in replacements.items():
        safe_text = re.sub(re.escape(original), replacement, safe_text, flags=re.IGNORECASE)
    return safe_text


def build_config_foundry_prompt(role, task, answer):
    safe_requirements = generic_config_requirements(task["requirements"])
    safe_task = generic_config_task_text(task["task"])
    answer_text = answer.strip() or "No learner answer has been provided yet."
    local_score = None
    local_status = None
    local_feedback = []
    if answer.strip():
        local_score, local_feedback = evaluate_config_answer(answer, role)
        local_status = local_quick_readiness_status(local_score)

    local_eval_context = "Local synthetic evaluator has not scored this answer yet."
    if local_score is not None:
        local_eval_context = (
            f"Local synthetic evaluator score: {local_score}/100\n"
            f"Local quick status: {local_status}\n"
            "Local feedback:\n"
            + "\n".join(f"- {item}" for item in local_feedback)
        )

    return (
        f"Evaluate a pipeline configuration practice answer for a {role}. "
        "Use only generic synthetic Data Engineering wording. Do not include real source systems, real table names, "
        "customer data, employee data, credentials, or confidential details. "
        "Use the attached synthetic knowledge files and return:\n"
        "1. Requirement summary\n"
        "2. Config practice feedback\n"
        "3. Readiness status\n"
        "4. Readiness risks\n"
        "5. Skill gaps\n"
        "6. Recommended revision focus\n"
        "7. Next actions\n"
        "8. Sources used\n\n"
        f"Synthetic task: {safe_task}\n"
        "Generic requirements:\n"
        f"{json.dumps(safe_requirements, indent=2)}\n\n"
        "Learner answer:\n"
        f"{answer_text}\n\n"
        f"{local_eval_context}"
    )


def build_manager_foundry_prompt(summaries):
    summary_lines = []
    for item in summaries:
        summary_lines.append(
            (
                f"- Team segment {item['team_id']}: role={item['role']}, "
                f"readiness={item['readiness_percentage']}%, status={status_badge_label(item['status'])}, "
                f"risk_area={item['risk_area']}, recommendation={item['recommendation']}"
            )
        )

    return (
        "Generate manager-level readiness insights for a synthetic Data Engineering team. "
        "Use the attached synthetic knowledge files to ground readiness risks, skill gaps, recommended revision focus, "
        "and next actions. Do not include personal data, emails, employee data, credentials, or confidential details. Return:\n"
        "1. Requirement summary\n"
        "2. Manager insights\n"
        "3. Readiness risks\n"
        "4. Skill gaps\n"
        "5. Recommended revision focus\n"
        "6. Next actions\n"
        "7. Sources used\n\n"
        "Synthetic local manager summary context:\n"
        + "\n".join(summary_lines)
    )


def status_badge_label(status):
    if status == "Strong readiness":
        return "Ready"
    if status == "Moderate readiness":
        return "Needs Revision"
    if status == "Readiness risk":
        return "Not Ready"
    return status


def render_foundry_badges():
    badges = [
        "Microsoft Foundry",
        "Foundry IQ",
        "Vector Index",
        "Grounded Response",
        "Synthetic Data Only",
    ]
    badge_html = "".join(f'<span class="foundry-badge">{escape(badge)}</span>' for badge in badges)
    return f'<div class="foundry-badge-row">{badge_html}</div>'


def render_foundry_flow():
    steps = [
        "Streamlit App",
        "DataDojo-IQ-Orchestrator",
        "Foundry IQ Vector Index",
        "Grounded Response",
    ]
    flow_parts = []
    for index, step in enumerate(steps):
        flow_parts.append(f'<div class="foundry-flow-step">{escape(step)}</div>')
        if index < len(steps) - 1:
            flow_parts.append('<div class="foundry-flow-arrow">-&gt;</div>')
    return f'<div class="foundry-flow">{"".join(flow_parts)}</div>'


def render_foundry_steps():
    steps = [
        ("1", "Write prompt", "Use a synthetic Data Engineering scenario or keep the starter prompt."),
        ("2", "Run agent", "Send the request to DataDojo-IQ-Orchestrator in Microsoft Foundry."),
        ("3", "Review result", "Use the grounded response for learning, assessment, feedback, or insights."),
    ]
    step_html = "".join(
        (
            '<div class="foundry-step-card">'
            f'<div class="foundry-step-index">{escape(index)}</div>'
            f'<div class="foundry-step-title">{escape(title)}</div>'
            f'<div class="foundry-step-copy">{escape(copy)}</div>'
            '</div>'
        )
        for index, title, copy in steps
    )
    return f'<div class="foundry-steps">{step_html}</div>'


def render_foundry_response_card(title, response):
    body = format_foundry_response(response)
    mini_flow = render_foundry_mini_flow(
        ["Streamlit App", "Microsoft Foundry Agent", "Foundry IQ Vector Index", "Grounded Response"],
        "foundry-mini-flow",
        "foundry-mini-flow-step",
        "foundry-mini-flow-arrow",
    )
    st.markdown(
        (
            '<div class="foundry-response-card">'
            '<div class="foundry-response-topnote">Generated by Microsoft Foundry using synthetic Data Engineering knowledge files grounded through Foundry IQ.</div>'
            f'<div class="foundry-response-title">{escape(title)}</div>'
            f'{mini_flow}'
            f'<div class="foundry-response-body">{body}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_foundry_mini_flow(steps, wrapper_class, step_class, arrow_class):
    html_parts = []
    for index, step in enumerate(steps):
        if index:
            html_parts.append(f'<div class="{arrow_class}">-&gt;</div>')
        html_parts.append(f'<div class="{step_class}">{escape(step)}</div>')
    return f'<div class="{wrapper_class}">{"".join(html_parts)}</div>'


def format_foundry_response(response_text: str) -> str:
    response_text = str(response_text or "")
    known_headings = {
        "requirement summary",
        "agent workflow used",
        "learning plan",
        "practice questions",
        "grounded assessment questions",
        "expected answer focus",
        "score interpretation",
        "config practice feedback",
        "readiness status",
        "manager insights",
        "sources used",
        "readiness risks",
        "skill gaps",
        "recommended revision focus",
        "recommended revision areas",
        "next actions",
    }
    source_files = [
        "certification_requirements.md",
        "load_type_rules.md",
        "troubleshooting_guide.md",
        "pipeline_config_rules.md",
        "Data Engineering_learning_guide.md",
    ]

    def normalize_heading(line):
        stripped = line.strip().lstrip("#").strip().rstrip(":")
        return stripped

    def is_heading(line):
        normalized = normalize_heading(line).lower()
        return line.startswith("#") or normalized in known_headings

    def section_class(section):
        lowered = section.lower()
        if "practice question" in lowered or "assessment question" in lowered:
            return "foundry-question-card"
        if "risk" in lowered:
            return "foundry-risk-card"
        if "gap" in lowered:
            return "foundry-gap-card"
        if "action" in lowered or "recommend" in lowered or "revision" in lowered:
            return "foundry-action-card"
        if "learning" in lowered:
            return "foundry-learning-card"
        if "feedback" in lowered or "expected answer" in lowered:
            return "foundry-feedback-card"
        if "manager" in lowered or "insight" in lowered:
            return "foundry-insight-card"
        if "summary" in lowered or "status" in lowered or "score" in lowered:
            return "foundry-summary-card"
        return "foundry-list-card"

    def status_class(term):
        lowered = term.lower()
        if lowered == "ready":
            return "foundry-status-ready"
        if lowered == "needs revision":
            return "foundry-status-revision"
        if lowered in {"not ready", "risk"}:
            return "foundry-status-risk"
        return "foundry-status-info"

    def chip_sources(text):
        chips = []
        for source_file in source_files:
            if source_file.lower() in text.lower():
                chips.append(f'<span class="source-chip foundry-source-chip">{escape(source_file)}</span>')
        return "".join(chips)

    def highlight_terms(text):
        escaped = escape(text)
        terms = [
            "Microsoft Foundry",
            "Foundry IQ",
            "Vector Index",
            "Synthetic Data",
            "Needs Revision",
            "Not Ready",
            "Next Actions",
            "Recommendation",
            "schema evolution",
            "troubleshooting",
            "readiness",
            "INCREMENTAL",
            "UPSERT",
            "APPEND",
            "FULL",
            "primary keys",
            "primary key",
            "watermark",
            "Ready",
            "Risk",
        ]
        term_lookup = {term.lower(): term for term in terms}
        pattern = re.compile(
            r"(?<![\w>])("
            + "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
            + r")(?![\w<])",
            re.IGNORECASE,
        )

        def replace_term(match):
            matched = match.group(1)
            canonical = term_lookup.get(matched.lower(), matched)
            chip_class = (
                status_class(canonical)
                if canonical in {"Ready", "Needs Revision", "Not Ready", "Risk"}
                else "foundry-highlight"
            )
            return f'<span class="{chip_class} foundry-keyword">{matched}</span>'

        escaped = pattern.sub(replace_term, escaped)
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
        return escaped

    def render_heading(title):
        return f'<div class="foundry-section-heading">{escape(title)}</div>'

    def render_agent_flow():
        return render_foundry_mini_flow(
            [
                "User Request",
                "Role Skill Mapper",
                "Learning Path Curator",
                "Assessment Agent",
                "Config Practice Evaluator",
                "Manager Insights",
                "Grounded Response",
            ],
            "foundry-agent-flow",
            "foundry-agent-step foundry-agent-node",
            "foundry-agent-arrow",
        )

    lines = response_text.splitlines()
    html_parts = []
    lead_added = False
    current_section = ""

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if is_heading(line):
            current_section = normalize_heading(line)
            html_parts.append(render_heading(current_section))
            if current_section.lower() == "agent workflow used":
                html_parts.append(render_agent_flow())
            if current_section.lower() == "sources used":
                html_parts.append('<div class="source-chip-row">' + "".join(
                    f'<span class="source-chip foundry-source-chip">{escape(source_file)}</span>'
                    for source_file in source_files
                ) + "</div>")
            continue

        numbered_match = re.match(r"^(\d+)[.)]\s+(.*)$", line)
        bullet_match = re.match(r"^[-*]\s+(.*)$", line)
        if numbered_match or bullet_match:
            if numbered_match:
                marker = numbered_match.group(1)
                content = numbered_match.group(2)
            else:
                marker = ""
                content = bullet_match.group(1)

            source_chips = chip_sources(content)
            if current_section.lower() == "sources used" and source_chips:
                html_parts.append(source_chips)
            else:
                card_class = section_class(current_section)
                index_class = (
                    "foundry-question-number"
                    if card_class == "foundry-question-card"
                    else "foundry-list-index"
                )
                index_html = f'<span class="{index_class}">{escape(marker)}</span>' if marker else ""
                html_parts.append(
                    f'<div class="{card_class}">{index_html}<span>{highlight_terms(content)}</span></div>'
                )
        else:
            source_chips = chip_sources(line)
            if current_section.lower() == "sources used" and source_chips:
                html_parts.append(source_chips)
                continue
            class_name = "foundry-response-lead" if not lead_added else ""
            class_attr = f' class="{class_name}"' if class_name else ""
            if current_section:
                html_parts.append(
                    f'<div class="{section_class(current_section)}">{highlight_terms(line)}</div>'
                )
            else:
                html_parts.append(f"<p{class_attr}>{highlight_terms(line)}</p>")
            lead_added = True

    return "".join(html_parts) or "<p>No response returned by the Foundry agent.</p>"


def render_foundry_panel(
    title,
    subtitle,
    default_prompt,
    button_label,
    key_prefix,
    textarea_label="Prompt sent to DataDojo-IQ-Orchestrator",
    prompt_key_suffix="",
):
    if key_prefix == "assessment_foundry":
        st.markdown('<div id="foundry-agent-workspace"></div>', unsafe_allow_html=True)

    st.markdown(
        (
            '<div class="foundry-panel">'
            '<div class="foundry-panel-header">'
            '<div>'
            '<div class="foundry-kicker">Microsoft Foundry Agent</div>'
            f'<div class="foundry-title">{escape(title)}</div>'
            f'<p class="foundry-subtitle">{escape(subtitle)}</p>'
            '</div>'
            '<span class="foundry-live-chip">Live Connection</span>'
            '</div>'
            f'{render_foundry_badges()}'
            f'{render_foundry_steps()}'
            '<div class="foundry-signal-row"><span>Prompt route</span><strong>Streamlit -> DataDojo-IQ-Orchestrator -> Foundry IQ</strong></div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        (
            '<div class="foundry-prompt-shell">'
            '<div class="foundry-kicker">Grounded prompt workspace</div>'
            '<p class="foundry-subtitle">Review or edit the synthetic Data Engineering prompt, then send it to the Foundry reasoning agent.</p>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    prompt = st.text_area(
        textarea_label,
        value=default_prompt,
        height=130,
        key=f"{key_prefix}_prompt{prompt_key_suffix}",
    )

    if st.button(button_label, key=f"{key_prefix}_button"):
        with st.spinner("Calling Microsoft Foundry reasoning agent..."):
            try:
                response = ask_foundry_agent(prompt)
            except Exception as error:
                response = f"Foundry agent call failed: {error}"
        render_foundry_response_card("Grounded Foundry Response", response)


def render_foundry_integration_section():
    st.markdown('<div id="foundry-integration"></div>', unsafe_allow_html=True)
    st.markdown(
        (
            '<section class="foundry-section">'
            '<div class="foundry-section-header">'
            '<div>'
            '<div class="foundry-kicker">Live Microsoft Integration</div>'
            '<h2 class="foundry-title">Microsoft Foundry + Foundry IQ Integration</h2>'
            '<p class="foundry-subtitle">DataDojo IQ is directly connected to a Microsoft Foundry reasoning agent.</p>'
            '<div class="foundry-cta-row">'
            '<a class="foundry-cta" href="#foundry-agent-workspace" target="_self" data-scroll-target="foundry-agent-workspace" data-tab-label="Assessment">Ask Foundry Agent</a>'
            '<a class="foundry-cta secondary" href="#multi-agent-flow" target="_self" data-scroll-target="multi-agent-flow">View agent roadmap</a>'
            '</div>'
            '</div>'
            '<span class="foundry-live-chip">Live Connection</span>'
            '</div>'
            f'{render_foundry_badges()}'
            '<div class="foundry-architecture-grid">'
            '<div>'
            f'{render_foundry_flow()}'
            '<p class="foundry-subtitle">'
            'The Streamlit app sends prompts to the DataDojo-IQ-Orchestrator agent in Microsoft Foundry. '
            'The agent retrieves from uploaded synthetic Data Engineering knowledge files through the Foundry IQ '
            'vector index and returns grounded assessment questions, config feedback, and readiness recommendations.'
            '</p>'
            '</div>'
            '<div class="foundry-signal-panel">'
            '<div class="foundry-kicker">Grounding Trace</div>'
            '<div class="foundry-signal-row"><span>Agent</span><strong>DataDojo-IQ-Orchestrator</strong></div>'
            '<div class="foundry-signal-row"><span>Model</span><strong>gpt-4.1-mini</strong></div>'
            '<div class="foundry-signal-row"><span>Retrieval</span><strong>Foundry IQ Vector Index</strong></div>'
            '<div class="foundry-signal-row"><span>Policy</span><strong>Synthetic data only</strong></div>'
            '</div>'
            '</div>'
            '</section>'
        ),
        unsafe_allow_html=True,
    )


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
            '<div class="hero-tagline">From KT calls to Data Engineering readiness</div>'
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
            '<a href="#foundry-integration">Foundry Integration</a>'
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
render_foundry_integration_section()
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
    workflow_section_label(
        "Local Role-Based Learning Plan",
        "This section uses local synthetic rules to demonstrate the learner workflow.",
        "local",
    )

    role = st.selectbox("Select Role", ROLES)
    target_skill = st.selectbox("Target Skill", TARGET_SKILLS)
    available_hours = st.slider("Available study hours per week", 1, 20, 8)
    learning_duration = st.selectbox(
        "Learning path duration",
        ["2 weeks", "4 weeks", "6 weeks", "8 weeks"],
        index=1,
    )

    if st.button("Generate Learning Plan"):
        skills = map_role_to_skills(role)
        plan = generate_study_plan(role, available_hours)

        info_card(
            "Role Summary",
            (
                f"<p><strong>Selected role:</strong> {escape(role)}</p>"
                f"<p><strong>Target skill:</strong> {escape(target_skill)}</p>"
                f"<p><strong>Available hours per week:</strong> {available_hours}</p>"
                f"<p><strong>Requested Foundry duration:</strong> {escape(learning_duration)}</p>"
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

    workflow_section_label(
        "Microsoft Foundry Learning Path",
        "This section calls the DataDojo-IQ-Orchestrator agent and uses the Foundry IQ vector index for grounded recommendations.",
        "foundry",
    )
    learner_foundry_prompt = build_learner_foundry_prompt(
        role,
        target_skill,
        available_hours,
        learning_duration,
    )
    render_foundry_panel(
        "Microsoft Foundry Learning Path",
        "This section calls the DataDojo-IQ-Orchestrator agent and uses the Foundry IQ vector index for grounded recommendations.",
        learner_foundry_prompt,
        "Ask Foundry Learning Agent",
        "learner_foundry",
        prompt_key_suffix=stable_prompt_suffix(role, target_skill, available_hours, learning_duration),
    )

with tab2:
    st.markdown("## Assessment")
    workflow_section_label(
        "Local Readiness Assessment",
        "This section uses local synthetic question logic for quick readiness scoring.",
        "local",
    )

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
    render_assessment_score_summary(score)

    workflow_section_label(
        "Microsoft Foundry Grounded Assessment",
        "This section generates grounded questions from uploaded synthetic Data Engineering knowledge files.",
        "foundry",
    )
    assessment_foundry_prompt = (
        f"Generate five grounded assessment questions for a {role_for_assessment}. "
        "Focus on Data Engineering readiness, pipeline configuration, load type rules, troubleshooting, "
        f"and readiness scoring. The learner's current practice score is {score}. "
        "Interpret this score using the readiness threshold rules from the attached synthetic knowledge files. Return:\n"
        "1. Grounded assessment questions\n"
        "2. Expected answer focus\n"
        "3. Score interpretation\n"
        "4. Readiness status\n"
        "5. Recommended revision areas\n"
        "6. Next learning actions\n"
        "7. Sources used"
    )
    assessment_prompt_suffix = f"_{re.sub(r'[^a-zA-Z0-9]+', '_', role_for_assessment).strip('_')}_{score}"
    render_foundry_panel(
        "Microsoft Foundry Grounded Assessment",
        "This section generates grounded questions from uploaded synthetic Data Engineering knowledge files.",
        assessment_foundry_prompt,
        "Ask Foundry Assessment Agent",
        "assessment_foundry",
        prompt_key_suffix=assessment_prompt_suffix,
    )

with tab3:
    st.markdown("## Config Practice")
    workflow_section_label(
        "Local Pipeline Config Practice",
        "This section uses local scoring logic to evaluate a learner answer.",
        "local",
    )

    role_for_task = st.selectbox("Select Role for Config Challenge", ROLES, key="task_role")
    current_config_task = generate_config_task(role_for_task)

    if st.button("Generate Config Challenge"):
        requirements = escape(json.dumps(generic_config_requirements(current_config_task["requirements"]), indent=2))
        info_card(
            "Practice Task",
            f"<p>{escape(generic_config_task_text(current_config_task['task']))}</p><pre class=\"config-code\">{requirements}</pre>",
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

    workflow_section_label(
        "Microsoft Foundry Config Evaluator",
        "This section asks the Foundry agent to evaluate configuration decisions using the grounded knowledge layer.",
        "foundry",
    )
    config_foundry_prompt = build_config_foundry_prompt(role_for_task, current_config_task, answer)
    render_foundry_panel(
        "Microsoft Foundry Config Evaluator",
        "This section asks the Foundry agent to evaluate configuration decisions using the grounded knowledge layer.",
        config_foundry_prompt,
        "Ask Foundry Config Agent",
        "config_foundry",
        textarea_label="Edit or use this config scenario",
        prompt_key_suffix=stable_prompt_suffix(role_for_task, answer),
    )

with tab4:
    st.markdown("## Manager Insights")
    workflow_section_label(
        "Local Synthetic Manager Summary",
        "This section uses synthetic team progress data to demonstrate manager dashboard output.",
        "local",
    )

    manager_summaries = generate_manager_summary()
    if st.button("Generate Local Manager Summary"):
        for item in manager_summaries:
            info_card(
                f"{item['team_id']} - {item['role']}",
                f"<p>{escape(item['summary'])}</p>"
                f"<p><strong>Readiness Percentage:</strong> {item['readiness_percentage']}%</p>"
                f"<p><strong>Status:</strong> {status_badge_html(item['status'])}</p>"
                f"<p><strong>Risk Area:</strong> {escape(item['risk_area'])}</p>"
                f"<p><strong>Recommendation:</strong> {escape(item['recommendation'])}</p>",
            )

    workflow_section_label(
        "Microsoft Foundry Manager Insights",
        "This section asks the Foundry agent to generate grounded team-level readiness insights from synthetic knowledge files.",
        "foundry",
    )
    manager_foundry_prompt = build_manager_foundry_prompt(manager_summaries)
    render_foundry_panel(
        "Microsoft Foundry Manager Insights",
        "This section asks the Foundry agent to generate grounded team-level readiness insights from synthetic knowledge files.",
        manager_foundry_prompt,
        "Ask Foundry Manager Agent",
        "manager_foundry",
        textarea_label="Edit or use this manager insight request",
        prompt_key_suffix=stable_prompt_suffix(len(manager_summaries), manager_foundry_prompt),
    )

st.markdown(
    '<div class="footer-note">A Microsoft Foundry Reasoning Agents project by Rishitha, built safely with synthetic data only.</div>',
    unsafe_allow_html=True,
)
