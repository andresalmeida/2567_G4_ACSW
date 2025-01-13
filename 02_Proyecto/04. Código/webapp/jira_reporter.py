from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

JIRA_URL = "https://espe-team-gqcx22bz.atlassian.net"
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")


def create_jira_ticket(summary, description):
    url = f"{JIRA_URL}/rest/api/2/issue/"
    headers = {
        "Content-Type": "application/json",
    }
    auth = (JIRA_USER, JIRA_API_TOKEN)

    payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": "Bug"
            }
        }
    }

    response = requests.post(url, headers=headers, auth=auth, json=payload)

    if response.status_code == 201:
        print("✅ Ticket creado con éxito:", response.json()["key"])
    else:
        print("❌ Error al crear ticket:", response.text)
