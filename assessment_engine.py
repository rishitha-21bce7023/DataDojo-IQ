def generate_questions(role):
    question_bank = {
        "Junior Data Engineer": [
            {
                "question": "Which layer stores source data with minimal transformation?",
                "answer": "raw"
            },
            {
                "question": "Which layer standardizes data and stores technical metadata?",
                "answer": "bronze"
            },
            {
                "question": "Which load type requires primary key columns?",
                "answer": "upsert"
            },
            {
                "question": "Which column is commonly used to identify changed records in incremental loads?",
                "answer": "watermark"
            }
        ],
        "Data Engineer": [
            {
                "question": "Why are primary keys required for UPSERT logic?",
                "answer": "to match existing target records"
            },
            {
                "question": "What can happen if an incremental load uses the wrong watermark column?",
                "answer": "records can be missed or duplicated"
            },
            {
                "question": "Which tool is commonly used to orchestrate pipelines in Azure data workflows?",
                "answer": "ADF"
            },
            {
                "question": "Which layer usually contains curated business ready data?",
                "answer": "silver"
            }
        ],
        "Senior Data Engineer": [
            {
                "question": "What is a common cause of multiple source rows matching the same target row in MERGE?",
                "answer": "duplicate keys"
            },
            {
                "question": "Why is schema evolution important in reusable pipeline frameworks?",
                "answer": "source schemas can change over time"
            },
            {
                "question": "What should be optimized when a pipeline is processing high volume data slowly?",
                "answer": "performance"
            },
            {
                "question": "Why is root cause analysis important after repeated pipeline failures?",
                "answer": "to prevent recurring failures"
            }
        ],
        "Data Architect": [
            {
                "question": "What architecture pattern uses raw bronze silver and gold layers?",
                "answer": "medallion"
            },
            {
                "question": "Why is a semantic layer useful in enterprise data platforms?",
                "answer": "it gives business meaning to data"
            },
            {
                "question": "What does data lineage help teams understand?",
                "answer": "data flow and origin"
            },
            {
                "question": "Why are governance standards important in enterprise data architecture?",
                "answer": "to ensure consistency and trust"
            }
        ]
    }

    return question_bank.get(role, question_bank["Junior Data Engineer"])


def calculate_readiness(score):
    if score >= 75:
        return "Ready"
    if score >= 60:
        return "Needs Revision"
    return "Not Ready"