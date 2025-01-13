import requests
from dotenv import load_dotenv
import os
from requests.auth import HTTPBasicAuth

load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

url = f"https://{JIRA_DOMAIN}.atlassian.net/rest/api/2/issue"
payload = {
    "fields": {
        "project": {"key": "GES"},
        "summary": "Prueba manual de subtarea",
        "description": "Esta es una subtarea creada desde la API para pruebas.",
        "issuetype": {"name": "Sub-task"},
        "parent": {"key": "GES-2"}
    }
}

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
response = requests.post(url, json=payload, auth=auth, headers=headers)
response = requests.post(url, json=payload, auth=auth, headers=headers)

if response.status_code == 201:
    print(f"✅ Subtarea creada: {response.json()['key']}")
else:
    print(f"❌ Error al crear subtarea: {response.status_code}, {response.text}")
