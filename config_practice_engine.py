def generate_config_task(role):
    tasks = {
        "Junior Data Engineer": {
            "task": "Create a basic bronze layer configuration for a SAP material master table.",
            "requirements": {
                "source_system": "SAP_ECC",
                "source_table": "material_master",
                "target_layer": "bronze",
                "load_type": "APPEND",
                "required_fields": ["source_system", "source_table", "target_layer", "load_type"]
            }
        },
        "Data Engineer": {
            "task": "Create a silver layer configuration for a SAP material master table using UPSERT.",
            "requirements": {
                "source_system": "SAP_ECC",
                "source_table": "material_master",
                "target_layer": "silver",
                "load_type": "UPSERT",
                "primary_keys": ["mandt", "matnr"],
                "watermark_column": "updated_at"
            }
        },
        "Senior Data Engineer": {
            "task": "Review a silver UPSERT configuration and identify risks related to duplicate keys and schema evolution.",
            "requirements": {
                "source_system": "SAP_ECC",
                "source_table": "sales_order",
                "target_layer": "silver",
                "load_type": "UPSERT",
                "primary_keys": ["mandt", "vbeln"],
                "risk_checks": ["duplicate_keys", "schema_evolution", "merge_conflict"]
            }
        },
        "Data Architect": {
            "task": "Design a medallion architecture mapping for an enterprise logistics dataset.",
            "requirements": {
                "domain": "logistics",
                "layers": ["raw", "bronze", "silver", "gold"],
                "architecture_focus": ["governance", "semantic_layer", "lineage", "reporting_readiness"]
            }
        }
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
        if "SAP_ECC".lower() not in answer_lower and "sap" not in answer_lower:
            feedback.append("Source system SAP_ECC is missing.")
            score -= 25
        if "material_master" not in answer_lower:
            feedback.append("Source table material_master is missing.")
            score -= 25
        if "APPEND" not in answer_upper:
            feedback.append("Load type APPEND is missing.")
            score -= 25

    elif role == "Data Engineer":
        if "UPSERT" not in answer_upper:
            feedback.append("Load type UPSERT is missing.")
            score -= 25
        if "mandt" not in answer_lower or "matnr" not in answer_lower:
            feedback.append("Primary keys mandt and matnr are required.")
            score -= 25
        if "updated_at" not in answer_lower:
            feedback.append("Watermark column updated_at is missing.")
            score -= 25
        if "silver" not in answer_lower:
            feedback.append("Silver layer is missing.")
            score -= 25

    elif role == "Senior Data Engineer":
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

    elif role == "Data Architect":
        if "raw" not in answer_lower or "bronze" not in answer_lower or "silver" not in answer_lower or "gold" not in answer_lower:
            feedback.append("All medallion layers raw bronze silver gold should be mentioned.")
            score -= 25
        if "governance" not in answer_lower:
            feedback.append("Governance is not mentioned.")
            score -= 25
        if "semantic" not in answer_lower:
            feedback.append("Semantic layer is not mentioned.")
            score -= 25
        if "lineage" not in answer_lower:
            feedback.append("Lineage is not mentioned.")
            score -= 25

    if not feedback:
        feedback.append("Answer looks valid for the selected role and task.")

    return max(score, 0), feedback