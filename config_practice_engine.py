def generate_config_task(role):
    tasks = {
        "Junior Data Engineer": {
            "task": "Create a basic metadata pipeline configuration for a synthetic activity dataset.",
            "requirements": {
                "source_system": "Synthetic_Source_A",
                "source_entity": "activity_events",
                "target_layer": "bronze",
                "load_type": "APPEND",
                "required_fields": ["source_system", "source_entity", "target_layer", "load_type"],
            },
        },
        "Data Engineer": {
            "task": "Create a curated layer configuration for a synthetic operational metrics dataset using UPSERT.",
            "requirements": {
                "source_system": "Synthetic_Source_B",
                "source_entity": "operational_metrics",
                "target_layer": "silver",
                "load_type": "UPSERT",
                "primary_keys": ["metric_id", "business_date"],
                "watermark_column": "last_updated_at",
            },
        },
        "Senior Data Engineer / Manager": {
            "task": "Review a synthetic UPSERT configuration and identify risks related to duplicate keys and schema evolution.",
            "requirements": {
                "source_system": "Synthetic_Source_C",
                "source_entity": "forecast_signals",
                "target_layer": "silver",
                "load_type": "UPSERT",
                "primary_keys": ["signal_id", "business_date"],
                "risk_checks": ["duplicate_keys", "schema_evolution", "merge_conflict"],
            },
        },
        "Director": {
            "task": "Review readiness risks across synthetic data products and prioritize governance actions.",
            "requirements": {
                "domains": ["Sales Analytics", "Supply Chain Analytics", "Operations Analytics"],
                "architecture_focus": ["governance", "lineage", "data_quality", "delivery_readiness"],
            },
        },
    }

    return tasks.get(role, tasks["Junior Data Engineer"])


def evaluate_config_answer(answer, role):
    feedback = []
    score = 100
    answer_lower = answer.lower()
    answer_upper = answer.upper()

    if role == "Junior Data Engineer":
        if "bronze" not in answer_lower:
            feedback.append("Bronze layer is missing.")
            score -= 25
        if "synthetic_source_a" not in answer_lower:
            feedback.append("Synthetic source system is missing.")
            score -= 25
        if "activity_events" not in answer_lower:
            feedback.append("Synthetic source entity is missing.")
            score -= 25
        if "APPEND" not in answer_upper:
            feedback.append("Load type APPEND is missing.")
            score -= 25

    elif role == "Data Engineer":
        if "UPSERT" not in answer_upper:
            feedback.append("Load type UPSERT is missing.")
            score -= 25
        if "metric_id" not in answer_lower or "business_date" not in answer_lower:
            feedback.append("Primary keys metric_id and business_date are required.")
            score -= 25
        if "last_updated_at" not in answer_lower:
            feedback.append("Watermark column last_updated_at is missing.")
            score -= 25
        if "silver" not in answer_lower:
            feedback.append("Silver layer is missing.")
            score -= 25

    elif role == "Senior Data Engineer / Manager":
        if "duplicate" not in answer_lower:
            feedback.append("Duplicate key risk is not mentioned.")
            score -= 25
        if "schema" not in answer_lower:
            feedback.append("Schema evolution risk is not mentioned.")
            score -= 25
        if "merge" not in answer_lower:
            feedback.append("Merge conflict risk is not mentioned.")
            score -= 25
        if "primary" not in answer_lower and "key" not in answer_lower:
            feedback.append("Primary key check is not mentioned.")
            score -= 25

    elif role == "Director":
        if "governance" not in answer_lower:
            feedback.append("Governance risk is not mentioned.")
            score -= 25
        if "quality" not in answer_lower:
            feedback.append("Data quality risk is not mentioned.")
            score -= 25
        if "readiness" not in answer_lower:
            feedback.append("Delivery readiness is not mentioned.")
            score -= 25
        if "priority" not in answer_lower and "investment" not in answer_lower:
            feedback.append("Prioritization or investment action is not mentioned.")
            score -= 25

    if not feedback:
        feedback.append("Answer looks valid for the selected role and synthetic task.")

    return max(score, 0), feedback
