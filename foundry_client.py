import os

import streamlit as st
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient

load_dotenv()


def get_secret_value(key: str, default: str = "") -> str:
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return os.getenv(key, default)


def get_azure_credential():
    tenant_id = get_secret_value("AZURE_TENANT_ID")
    client_id = get_secret_value("AZURE_CLIENT_ID")
    client_secret = get_secret_value("AZURE_CLIENT_SECRET")

    if tenant_id and client_id and client_secret:
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

    return InteractiveBrowserCredential(tenant_id=tenant_id)


def ask_foundry_agent(user_prompt: str) -> str:
    endpoint = get_secret_value("AZURE_AI_PROJECT_ENDPOINT")
    agent_name = get_secret_value("AZURE_AI_AGENT_NAME")

    if not endpoint or not agent_name:
        return (
            "Foundry connection is not configured. "
            "Please add AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_AGENT_NAME."
        )

    try:
        with (
            get_azure_credential() as credential,
            AIProjectClient(
                endpoint=endpoint,
                credential=credential,
                allow_preview=True,
            ) as project_client,
        ):
            openai_client = project_client.get_openai_client(agent_name=agent_name)

            response = openai_client.responses.create(
                input=user_prompt,
            )

            return response.output_text or "No response was returned by the Foundry agent."

    except Exception as error:
        return f"Error while calling Foundry agent: {error}"