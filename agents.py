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
            "Pipeline orchestration basics",
            "Transformation flow",
            "Schema mapping and error debugging"
        ],
        "Senior Data Engineer / Manager": [
            "Reusable pipeline framework design",
            "Complex merge and deduplication logic",
            "Schema evolution handling",
            "Performance optimization",
            "Advanced troubleshooting and team coaching"
        ],
        "Director": [
            "Lakehouse architecture standards",
            "Domain-level readiness governance",
            "Strategic capability planning",
            "Cross-domain data quality risk review",
            "Investment and training prioritization"
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
            "Learn orchestration and transformation flow",
            "Complete pipeline debugging and readiness assessment"
        ],
        "Senior Data Engineer / Manager": [
            "Design reusable pipeline framework patterns",
            "Practice schema evolution and complex merge handling",
            "Learn performance risk review and coaching patterns",
            "Complete team readiness and troubleshooting assessment"
        ],
        "Director": [
            "Review multi-domain readiness and governance standards",
            "Practice capability maturity and risk prioritization",
            "Learn cross-domain investment and training planning",
            "Complete director readiness brief review"
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
