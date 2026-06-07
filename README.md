# DataDojo IQ

From KT calls to DataOps readiness.

DataDojo IQ is a multi-agent Data Engineering readiness platform built for the Microsoft Foundry Reasoning Agents challenge. It helps data engineering teams convert learning content, role expectations, assessments, and pipeline practice into a structured readiness workspace for learners and managers.

## Problem

Data engineering teams often depend on repeated KT calls, scattered documentation, and manual readiness checks. New team members may struggle to understand pipeline architecture, load strategies, configuration standards, troubleshooting patterns, and governance expectations.

## Solution

DataDojo IQ provides a multi-agent readiness workflow that helps learners understand required skills, generate study plans, complete role-based assessments, practice pipeline configuration scenarios, and view manager-level readiness insights.

## Challenge Track

Reasoning Agents

## Microsoft IQ Layer

Foundry IQ

## Microsoft Tools Used

- Microsoft Foundry
- Foundry IQ
- GitHub Copilot
- Python
- Streamlit

## Agent Workflow

1. User Profile
2. Role Skill Mapper Agent
3. Learning Path Curator Agent
4. Study Plan Generator Agent
5. Assessment Agent
6. Config Practice Evaluator Agent
7. Manager Insights Agent

## Features

- Professional landing page
- Role-based learning plan
- Grounded assessment placeholder
- Pipeline configuration practice
- Readiness scoring
- Manager insights dashboard
- Dark theme support
- Synthetic data only

## Microsoft Foundry Setup

DataDojo IQ uses Microsoft Foundry to create and test the DataDojo-IQ-Orchestrator agent.

Foundry setup:
- Project: datadojo-iq
- Agent: DataDojo-IQ-Orchestrator
- Model: gpt-4.1-mini
- Knowledge grounding: uploaded synthetic Data Engineering documents through vector index

Knowledge files:
- dataops_learning_guide.md
- pipeline_config_rules.md
- load_type_rules.md
- troubleshooting_guide.md
- certification_requirements.md

The agent uses these synthetic documents to generate role-based learning plans, grounded assessment questions, configuration feedback, and readiness recommendations.

## How to Run

```bash
pip install -r requirements.txt
python -m streamlit run app.py
