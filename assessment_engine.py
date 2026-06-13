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
        "Senior Data Engineer / Manager": [
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
        "Director": [
            {
                "question": "What should a director review when readiness varies across multiple domains?",
                "answer": "cross-domain risk"
            },
            {
                "question": "What should be prioritized when repeated data quality gaps slow delivery?",
                "answer": "capability building"
            },
            {
                "question": "What does domain-level governance help teams maintain?",
                "answer": "consistency and trust"
            },
            {
                "question": "What type of plan should guide the next month after readiness risks are found?",
                "answer": "30-day action plan"
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
