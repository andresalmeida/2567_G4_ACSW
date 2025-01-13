from fastapi.testclient import TestClient
from app import app
import requests
from dotenv import load_dotenv
import os
from requests.auth import HTTPBasicAuth

load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = "GES"  # Cambia si tienes otro proyecto
JIRA_PARENT_TICKET = "GES-2"  # Ticket padre donde se guardarán las subtareas

def create_jira_ticket(summary, description):
    url = f"https://{JIRA_DOMAIN}.atlassian.net/rest/api/2/issue"
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Sub-task"},
            "parent": {"key": JIRA_PARENT_TICKET}
        }
    }
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, auth=auth, headers=headers)

    if response.status_code == 201:
        print(f"✅ Subtarea creada: {response.json()['key']}")
    else:
        print(f"❌ Error al crear subtarea: {response.status_code}, {response.text}")


def before_all(context):
    context.client = TestClient(app)


def after_step(context, step):
    if step.status == "failed":
        # Captura el nombre del escenario y paso que falló
        scenario_name = context.scenario.name if hasattr(context, "scenario") else "Escenario desconocido"
        step_name = step.name
        error_message = str(step.exception) if step.exception else "Sin detalles"

        # Crear una subtarea con más detalles
        create_jira_ticket(
            summary=f"⚠️ Error en: {scenario_name} - {step_name}",
            description=f"🔴 **Fallo en el paso**: '{step_name}'\n\n"
                        f"**Escenario**: {scenario_name}\n\n"
                        f"**Error**: {error_message}\n\n"
                        f"---\nVerifica el código y reproduce el error para más detalles."
        )
