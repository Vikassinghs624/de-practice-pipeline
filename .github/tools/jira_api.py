#!/usr/bin/env python3
"""
.github/tools/jira_api.py -- Real Jira REST API CLI tool.

Talks directly to your actual Jira Cloud instance. No local storage --
every command hits the real API and reflects instantly in the Jira UI.

Setup (one time):
    pip install requests python-dotenv
    Add to your .env file (never commit this file):
        JIRA_EMAIL=you@example.com
        JIRA_TOKEN=your_api_token
        JIRA_BASE_URL=https://yoursite.atlassian.net
        JIRA_PROJECT_KEY=SCRUM

Usage:
    python .github/tools/jira_api.py create "Ticket summary" "Optional description"
    python .github/tools/jira_api.py show SCRUM-6
    python .github/tools/jira_api.py transitions SCRUM-6
    python .github/tools/jira_api.py move SCRUM-6 "In Progress"
    python .github/tools/jira_api.py comment SCRUM-6 "Working on this now"
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.environ.get("JIRA_EMAIL")
TOKEN = os.environ.get("JIRA_TOKEN")
BASE_URL = os.environ.get("JIRA_BASE_URL")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")

AUTH = (EMAIL, TOKEN) if EMAIL and TOKEN else None
HEADERS = {"Content-Type": "application/json"}


def _require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        print(f"Missing required environment variable(s): {', '.join(missing)}")
        print("Set them in your .env file (see script docstring for the full list).")
        sys.exit(1)


def cmd_create(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL", "JIRA_PROJECT_KEY")
    if not args:
        print('Usage: create "Summary" ["Description"]')
        sys.exit(1)
    summary = args[0]
    description = args[1] if len(args) > 1 else "Created via terminal (jira_api.py)"

    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ],
            },
            "issuetype": {"name": "Task"},
        }
    }
    resp = requests.post(f"{BASE_URL}/rest/api/3/issue", auth=AUTH, headers=HEADERS, json=payload)
    if resp.status_code >= 300:
        print(f"Failed to create ticket ({resp.status_code}):")
        print(resp.text)
        sys.exit(1)
    data = resp.json()
    key = data["key"]
    print(f"Created ticket: {key}")
    print(f"View it at: {BASE_URL}/browse/{key}")


def cmd_show(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if not args:
        print("Usage: show TICKET-KEY")
        sys.exit(1)
    key = args[0]
    resp = requests.get(f"{BASE_URL}/rest/api/3/issue/{key}", auth=AUTH, headers=HEADERS)
    if resp.status_code >= 300:
        print(f"Failed to fetch ticket ({resp.status_code}): {resp.text}")
        sys.exit(1)
    data = resp.json()
    fields = data["fields"]
    print(f"Key:      {key}")
    print(f"Summary:  {fields['summary']}")
    print(f"Status:   {fields['status']['name']}")
    print(f"Assignee: {fields['assignee']['displayName'] if fields.get('assignee') else 'Unassigned'}")
    print(f"URL:      {BASE_URL}/browse/{key}")


def cmd_transitions(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if not args:
        print("Usage: transitions TICKET-KEY")
        sys.exit(1)
    key = args[0]
    resp = requests.get(f"{BASE_URL}/rest/api/3/issue/{key}/transitions", auth=AUTH, headers=HEADERS)
    if resp.status_code >= 300:
        print(f"Failed to fetch transitions ({resp.status_code}): {resp.text}")
        sys.exit(1)
    data = resp.json()
    print(f"Available transitions for {key}:")
    for t in data["transitions"]:
        print(f"  id={t['id']:<5} -> {t['name']}")


def cmd_move(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if len(args) < 2:
        print('Usage: move TICKET-KEY "Status Name"')
        sys.exit(1)
    key, target_status = args[0], args[1]

    resp = requests.get(f"{BASE_URL}/rest/api/3/issue/{key}/transitions", auth=AUTH, headers=HEADERS)
    if resp.status_code >= 300:
        print(f"Failed to fetch transitions ({resp.status_code}): {resp.text}")
        sys.exit(1)
    transitions = resp.json()["transitions"]
    match = next((t for t in transitions if t["name"].lower() == target_status.lower()), None)
    if not match:
        available = ", ".join(t["name"] for t in transitions)
        print(f"No transition named '{target_status}' found. Available: {available}")
        sys.exit(1)

    resp2 = requests.post(
        f"{BASE_URL}/rest/api/3/issue/{key}/transitions",
        auth=AUTH,
        headers=HEADERS,
        json={"transition": {"id": match["id"]}},
    )
    if resp2.status_code >= 300:
        print(f"Failed to transition ticket ({resp2.status_code}): {resp2.text}")
        sys.exit(1)
    print(f"{key}: moved to '{target_status}'")
    print(f"View it at: {BASE_URL}/browse/{key}")


def cmd_comment(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if len(args) < 2:
        print('Usage: comment TICKET-KEY "Comment text"')
        sys.exit(1)
    key, text = args[0], " ".join(args[1:])
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
        }
    }
    resp = requests.post(
        f"{BASE_URL}/rest/api/3/issue/{key}/comment", auth=AUTH, headers=HEADERS, json=payload
    )
    if resp.status_code >= 300:
        print(f"Failed to add comment ({resp.status_code}): {resp.text}")
        sys.exit(1)
    print(f"Comment added to {key}")


COMMANDS = {
    "create": cmd_create,
    "show": cmd_show,
    "transitions": cmd_transitions,
    "move": cmd_move,
    "comment": cmd_comment,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])#!/usr/bin/env python3
"""
.github/tools/jira_api.py -- Real Jira REST API CLI tool.

Talks directly to your actual Jira Cloud instance. No local storage --
every command hits the real API and reflects instantly in the Jira UI.

Setup (one time):
    pip install requests python-dotenv
    Add to your .env file (never commit this file):
        JIRA_EMAIL=you@example.com
        JIRA_TOKEN=your_api_token
        JIRA_BASE_URL=https://yoursite.atlassian.net
        JIRA_PROJECT_KEY=SCRUM

Usage:
    python .github/tools/jira_api.py create "Ticket summary" "Optional description"
    python .github/tools/jira_api.py show SCRUM-6
    python .github/tools/jira_api.py transitions SCRUM-6
    python .github/tools/jira_api.py move SCRUM-6 "In Progress"
    python .github/tools/jira_api.py comment SCRUM-6 "Working on this now"
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.environ.get("JIRA_EMAIL")
TOKEN = os.environ.get("JIRA_TOKEN")
BASE_URL = os.environ.get("JIRA_BASE_URL")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")

AUTH = (EMAIL, TOKEN) if EMAIL and TOKEN else None
HEADERS = {"Content-Type": "application/json"}


def _require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        print(f"Missing required environment variable(s): {', '.join(missing)}")
        print("Set them in your .env file (see script docstring for the full list).")
        sys.exit(1)


def cmd_create(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL", "JIRA_PROJECT_KEY")
    if not args:
        print('Usage: create "Summary" ["Description"]')
        sys.exit(1)
    summary = args[0]
    description = args[1] if len(args) > 1 else "Created via terminal (jira_api.py)"

    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ],
            },
            "issuetype": {"name": "Task"},
        }
    }
    resp = requests.post(f"{BASE_URL}/rest/api/3/issue", auth=AUTH, headers=HEADERS, json=payload)
    if resp.status_code >= 300:
        print(f"Failed to create ticket ({resp.status_code}):")
        print(resp.text)
        sys.exit(1)
    data = resp.json()
    key = data["key"]
    print(f"Created ticket: {key}")
    print(f"View it at: {BASE_URL}/browse/{key}")


def cmd_show(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if not args:
        print("Usage: show TICKET-KEY")
        sys.exit(1)
    key = args[0]
    resp = requests.get(f"{BASE_URL}/rest/api/3/issue/{key}", auth=AUTH, headers=HEADERS)
    if resp.status_code >= 300:
        print(f"Failed to fetch ticket ({resp.status_code}): {resp.text}")
        sys.exit(1)
    data = resp.json()
    fields = data["fields"]
    print(f"Key:      {key}")
    print(f"Summary:  {fields['summary']}")
    print(f"Status:   {fields['status']['name']}")
    print(f"Assignee: {fields['assignee']['displayName'] if fields.get('assignee') else 'Unassigned'}")
    print(f"URL:      {BASE_URL}/browse/{key}")


def cmd_transitions(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if not args:
        print("Usage: transitions TICKET-KEY")
        sys.exit(1)
    key = args[0]
    resp = requests.get(f"{BASE_URL}/rest/api/3/issue/{key}/transitions", auth=AUTH, headers=HEADERS)
    if resp.status_code >= 300:
        print(f"Failed to fetch transitions ({resp.status_code}): {resp.text}")
        sys.exit(1)
    data = resp.json()
    print(f"Available transitions for {key}:")
    for t in data["transitions"]:
        print(f"  id={t['id']:<5} -> {t['name']}")


def cmd_move(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if len(args) < 2:
        print('Usage: move TICKET-KEY "Status Name"')
        sys.exit(1)
    key, target_status = args[0], args[1]

    resp = requests.get(f"{BASE_URL}/rest/api/3/issue/{key}/transitions", auth=AUTH, headers=HEADERS)
    if resp.status_code >= 300:
        print(f"Failed to fetch transitions ({resp.status_code}): {resp.text}")
        sys.exit(1)
    transitions = resp.json()["transitions"]
    match = next((t for t in transitions if t["name"].lower() == target_status.lower()), None)
    if not match:
        available = ", ".join(t["name"] for t in transitions)
        print(f"No transition named '{target_status}' found. Available: {available}")
        sys.exit(1)

    resp2 = requests.post(
        f"{BASE_URL}/rest/api/3/issue/{key}/transitions",
        auth=AUTH,
        headers=HEADERS,
        json={"transition": {"id": match["id"]}},
    )
    if resp2.status_code >= 300:
        print(f"Failed to transition ticket ({resp2.status_code}): {resp2.text}")
        sys.exit(1)
    print(f"{key}: moved to '{target_status}'")
    print(f"View it at: {BASE_URL}/browse/{key}")


def cmd_comment(args):
    _require_env("JIRA_EMAIL", "JIRA_TOKEN", "JIRA_BASE_URL")
    if len(args) < 2:
        print('Usage: comment TICKET-KEY "Comment text"')
        sys.exit(1)
    key, text = args[0], " ".join(args[1:])
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
        }
    }
    resp = requests.post(
        f"{BASE_URL}/rest/api/3/issue/{key}/comment", auth=AUTH, headers=HEADERS, json=payload
    )
    if resp.status_code >= 300:
        print(f"Failed to add comment ({resp.status_code}): {resp.text}")
        sys.exit(1)
    print(f"Comment added to {key}")


COMMANDS = {
    "create": cmd_create,
    "show": cmd_show,
    "transitions": cmd_transitions,
    "move": cmd_move,
    "comment": cmd_comment,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])