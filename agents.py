def map_role_to_skills(role):
    role_skills = {
        "Junior Data Engineer": [
            "Medallion architecture",
            "Basic SQL for data validation",
            "Metadata JSON configuration",
            "Load type basics",
            "Primary key and watermark rules",
            "Basic pipeline debugging"
        ],
        "Data Engineer": [
            "Metadata driven pipeline development",
            "UPSERT and incremental load logic",
            "ADF orchestration basics",
            "Databricks transformation flow",
            "Schema mapping and error debugging"
        ],
        "Senior Data Engineer": [
            "Reusable pipeline framework design",
            "Complex merge and deduplication logic",
            "Schema evolution handling",
            "Performance optimization",
            "Advanced troubleshooting and root cause analysis"
        ],
        "Data Architect": [
            "Lakehouse architecture standards",
            "Medallion architecture design",
            "Data modeling and governance",
            "Semantic layer design",
            "Enterprise data quality and lineage rules"
        ]
    }

    return role_skills.get(role, [])


def generate_study_plan(role, available_hours):
    if available_hours < 5:
        pace = "light"
    elif available_hours <= 10:
        pace = "standard"
    else:
        pace = "accelerated"

    role_focus = {
        "Junior Data Engineer": [
            "Learn medallion architecture and basic pipeline flow",
            "Practice metadata JSON configuration and layer rules",
            "Learn load types primary keys and watermark basics",
            "Complete basic troubleshooting and readiness assessment"
        ],
        "Data Engineer": [
            "Understand metadata driven pipeline development",
            "Practice UPSERT and incremental load design",
            "Learn ADF orchestration and Databricks transformation flow",
            "Complete pipeline debugging and readiness assessment"
        ],
        "Senior Data Engineer": [
            "Design reusable pipeline framework patterns",
            "Practice schema evolution and complex merge handling",
            "Learn performance optimization and root cause analysis",
            "Complete advanced troubleshooting assessment"
        ],
        "Data Architect": [
            "Review lakehouse and medallion architecture standards",
            "Practice data modeling and governance scenarios",
            "Learn semantic layer and lineage design",
            "Complete architecture readiness assessment"
        ]
    }

    weeks = role_focus.get(role, role_focus["Junior Data Engineer"])

    return {
        "pace": pace,
        "week_1": weeks[0],
        "week_2": weeks[1],
        "week_3": weeks[2],
        "week_4": weeks[3]
    }