import json


def load_team_progress():
    with open("synthetic_data/team_progress.json", "r") as file:
        return json.load(file)


def generate_manager_summary():
    data = load_team_progress()
    summaries = []

    for team in data:
        readiness_percentage = round((team["ready_count"] / team["learners"]) * 100, 2)

        if readiness_percentage >= 75:
            status = "Strong readiness"
        elif readiness_percentage >= 50:
            status = "Moderate readiness"
        else:
            status = "Readiness risk"

        summary = {
            "team_id": team["team_id"],
            "role": team["role"],
            "summary": f"{team['ready_count']} out of {team['learners']} learners are ready.",
            "readiness_percentage": readiness_percentage,
            "status": status,
            "risk_area": team["highest_risk_area"],
            "recommendation": f"Schedule focused revision on {team['highest_risk_area']}."
        }

        summaries.append(summary)

    return summaries