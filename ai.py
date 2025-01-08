# Note: Replace **<YOUR_APPLICATION_TOKEN>** with your actual Application token


import requests
from typing import Optional
import os
import json
from langflow.load import run_flow_from_json

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "499748ce-785c-4b8e-adcc-88d17abdd100"
APPLICATION_TOKEN = os.getenv("LANGFLOW_TOKEN")

def dict_to_string(obj, level=0):
    strings = []
    indent = "  " * level  # Indentation for nested levels
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                nested_string = dict_to_string(value, level + 1)
                strings.append(f"{indent}{key}: {nested_string}")
            else:
                strings.append(f"{indent}{key}: {value}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            nested_string = dict_to_string(item, level + 1)
            strings.append(f"{indent}Item {idx + 1}: {nested_string}")
    else:
        strings.append(f"{indent}{obj}")

    return ", ".join(strings)

TWEAKS = {
  "TextInput-PdKbc": {
    "input_value": "question"
  },

  "TextInput-7ElUl": {
    "input_value": "profile"
  },
  
}

result = run_flow_from_json(flow="Ask AI.json",
                            input_value="message",
                            session_id="", # provide a session id if you want to use session state
                            fallback_to_env_vars=True, # False by default
                            tweaks=TWEAKS)


def get_diet(profile, goals):
    TWEAKS = {
    "TextInput-B0SqW": {
        "input_value": dict_to_string(profile)
    },
    
    "TextInput-teaG0": {
        "input_value": ", ".join(goals)
    }
    }
    return run_flow("", tweaks=TWEAKS, application_token=APPLICATION_TOKEN)

def run_flow(message: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> dict:
    
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/diet"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return json.loads(response.json()["outputs"][0]["outputs"][0]["results"]["text"]["data"]["text"])



