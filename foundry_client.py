import os

from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient

load_dotenv()


def ask_foundry_agent(user_prompt: str) -> str:
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    agent_name = os.getenv("AZURE_AI_AGENT_NAME")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    if not endpoint or not agent_name:
        return (
            "Foundry connection is not configured. "
            "Please add AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_AGENT_NAME in the .env file."
        )

    try:
        with (
            InteractiveBrowserCredential(tenant_id=tenant_id) as credential,
            AIProjectClient(
                endpoint=endpoint,
                credential=credential,
                allow_preview=True,
            ) as project_client,
        ):
            openai_client = project_client.get_openai_client(agent_name=agent_name)

            response = openai_client.responses.create(
                input=user_prompt
            )

            return response.output_text or "No response was returned by the Foundry agent."

    except Exception as error:
        return f"Error while calling Foundry agent: {error}"