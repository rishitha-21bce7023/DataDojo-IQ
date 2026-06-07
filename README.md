# DataDojo IQ

**From KT calls to DataOps readiness.**

DataDojo IQ is a multi-agent Data Engineering readiness platform built for the Microsoft Foundry Reasoning Agents challenge. It helps data engineering teams convert learning content, role expectations, assessments, and pipeline practice into a structured readiness workspace for learners and managers.

The project includes a polished Streamlit frontend connected to a Microsoft Foundry agent. The Foundry agent uses uploaded synthetic Data Engineering knowledge documents through a vector index as the Foundry IQ grounding layer.

---

## Problem

Data engineering teams often depend on repeated KT calls, scattered documentation, and manual readiness checks. New team members may struggle to understand pipeline architecture, load strategies, configuration standards, troubleshooting patterns, and governance expectations.

This creates common issues such as:

* Inconsistent onboarding experience
* Repeated explanation of the same concepts
* Manual readiness tracking
* Weak visibility for managers
* Gaps in understanding pipeline configuration and load rules

---

## Solution

DataDojo IQ provides a multi-agent readiness workflow that helps learners understand required skills, generate study plans, complete role-based assessments, practice pipeline configuration scenarios, and view manager-level readiness insights.

The platform combines:

* Streamlit for the learner and manager interface
* Microsoft Foundry for the cloud reasoning agent
* Foundry IQ vector index for grounded knowledge retrieval
* Synthetic Data Engineering knowledge files for safe demo content

---

## Challenge Track

**Reasoning Agents**

---

## Microsoft IQ Layer

**Foundry IQ**

Foundry IQ is used as the grounding layer through an uploaded vector index of synthetic Data Engineering documents. The Foundry agent retrieves from these documents to generate grounded assessment questions, configuration feedback, learning guidance, and readiness recommendations.

---

## Microsoft Tools Used

* Microsoft Foundry
* Foundry IQ
* GitHub Copilot
* Python
* Streamlit
* Azure AI Projects SDK

---

## Architecture

```text
Streamlit App
    ↓
DataDojo IQ frontend workflow
    ↓
Microsoft Foundry Agent
DataDojo-IQ-Orchestrator
    ↓
Foundry IQ Vector Index
Synthetic Data Engineering knowledge files
    ↓
Grounded response
    ↓
Streamlit App
```

---

## Agent Workflow

1. **User Profile Agent**
   Captures learner role, target skill, available study hours, and readiness goal.

2. **Role Skill Mapper Agent**
   Maps selected role to expected Data Engineering skills.

3. **Learning Path Curator Agent**
   Selects relevant learning topics from the grounded knowledge base.

4. **Study Plan Generator Agent**
   Converts learning needs into a practical four-week plan.

5. **Assessment Agent**
   Generates role-specific readiness questions grounded in Foundry IQ knowledge files.

6. **Config Practice Evaluator Agent**
   Reviews pipeline configuration answers and provides feedback.

7. **Manager Insights Agent**
   Summarizes synthetic team readiness, risk areas, and recommended actions.

---

## Features

* Professional landing page
* Multi-agent roadmap
* Role-based learning plan
* Streamlit to Microsoft Foundry agent connection
* Foundry IQ grounded assessment generation
* Pipeline configuration practice
* Foundry-powered configuration feedback
* Readiness scoring
* Manager insights dashboard
* Dark theme support
* Synthetic data only

---

## Microsoft Foundry Setup

DataDojo IQ uses Microsoft Foundry to create and test the `DataDojo-IQ-Orchestrator` agent.

### Foundry setup

* Project: `datadojo-iq`
* Agent: `DataDojo-IQ-Orchestrator`
* Model: `gpt-4.1-mini`
* Knowledge grounding: uploaded synthetic Data Engineering documents through vector index
* Frontend integration: Streamlit calls the Foundry agent using the Azure AI Projects SDK

### Knowledge files

The following synthetic knowledge files are used for grounding:

* `dataops_learning_guide.md`
* `pipeline_config_rules.md`
* `load_type_rules.md`
* `troubleshooting_guide.md`
* `certification_requirements.md`

The agent uses these documents to generate:

* Role-based learning plans
* Grounded assessment questions
* Pipeline configuration feedback
* Readiness recommendations
* Manager-level learning insights

---

## Streamlit and Foundry Integration

The Streamlit application connects directly to the Microsoft Foundry agent.

When a user clicks **Ask Foundry Agent** in the Assessment or Config Practice section:

1. Streamlit sends the prompt to the `DataDojo-IQ-Orchestrator` agent.
2. The Foundry agent uses the uploaded vector index as the Foundry IQ grounding layer.
3. The agent generates a grounded response.
4. The response is displayed back inside the Streamlit interface.

This creates a complete frontend to Foundry reasoning workflow.

---

## Project Structure

```text
DataDojo-IQ/
│
├── app.py
├── foundry_client.py
├── agents.py
├── assessment_engine.py
├── config_practice_engine.py
├── manager_insights.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│   ├── hero_banner.png
│   ├── hero_banner_transparent.png
│   ├── learner_plan.png
│   ├── assessment.png
│   ├── config_practice.png
│   └── manager_dashboard.png
│
├── knowledge_base/
│   ├── dataops_learning_guide.md
│   ├── pipeline_config_rules.md
│   ├── load_type_rules.md
│   ├── troubleshooting_guide.md
│   └── certification_requirements.md
│
└── synthetic_data/
    └── team_progress.json
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
AZURE_AI_PROJECT_ENDPOINT=your_foundry_project_endpoint
AZURE_AI_AGENT_NAME=DataDojo-IQ-Orchestrator
AZURE_AI_AGENT_VERSION=latest
AZURE_TENANT_ID=your_azure_tenant_id
```

Do not commit `.env` to GitHub.

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/rishitha-21bce7023/DataDojo-IQ.git
cd DataDojo-IQ
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Create `.env`

Add the required Foundry endpoint, agent name, agent version, and tenant ID.

### 5. Run the Streamlit app

```bash
python -m streamlit run app.py
```

---

## Demo Flow

A typical demo can show:

1. DataDojo IQ landing page
2. Multi-agent readiness roadmap
3. Role-based learning plan generation
4. Local assessment question generation
5. Foundry IQ grounded assessment response
6. Pipeline configuration practice
7. Foundry-powered configuration feedback
8. Manager insights dashboard
9. Microsoft Foundry agent and vector index setup

---

## Data Safety

This project uses only synthetic data and generic sample scenarios.

It does not include:

* Real employee data
* Real customer data
* PII
* Credentials
* Confidential company data
* Proprietary internal documents
* Real project table names or internal system names

All learning content, role examples, configuration examples, and team readiness data are synthetic and created only for demonstration.

---

## Responsible AI Considerations

DataDojo IQ follows these safety principles:

* Uses synthetic data only
* Avoids confidential or personal information
* Keeps manager insights aggregated
* Grounds Foundry responses in approved synthetic knowledge files
* Clearly separates demo logic from production usage
* Provides human-readable feedback and readiness status

---

## Submission Summary

DataDojo IQ demonstrates a multi-agent Data Engineering readiness workflow using Microsoft Foundry and Foundry IQ. It connects a polished Streamlit frontend with a Microsoft Foundry agent that uses synthetic knowledge documents as a vector-index grounding layer. The result is a safe, demoable, and practical enterprise learning readiness platform for learners and managers.
