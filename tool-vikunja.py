"""
title: Vikunja task management
author: thompsonsj
author_url: https://github.com/thompsonsj
git_url: https://github.com/thompsonsj/open-webui-tool-vikunja
description: Create, review, update and delete tasks in your Vikunja install/account.
required_open_webui_version: 0.6.3
version: 0.1.0
license: MIT
"""

import os
import requests
from datetime import datetime, timedelta
import json
from pydantic import BaseModel, Field

PRIORITY_MAP = {4: "Critical", 3: "High", 2: "Medium", 1: "Low", 0: "None"}

class Tools:
    class Valves(BaseModel):
        domain: str = Field("", description="Domain where Vikunja is installed, e.g. https://try.vikunja.io")
        authToken: str = Field("", description="API key")

    def __init__(self):
        self.valves = self.Valves()

    def get_project_id(self, project_title: str = None) -> int:
        """
        Retrieves the project ID based on a fuzzy match of the title.
        """
        # If project title is provided for matching, use the default project ID
        if not project_title:
            return 1
        url = f"{self.valves.domain}/api/v1/projects"
        headers = {"Authorization": f"Bearer {self.valves.authToken}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json()

        for project in projects:
            if project["title"].lower() == project_title.lower():
                return project["id"]

        # If no matching project title is found, use the default project ID
        return 1

    def get_vikunja_tasks(self) -> str:
        """
        Retrieves active tasks from Vikunja for a specific project.
        """
        url = (
            f"{self.valves.domain}/api/v1/projects/{self.valves.projectId}/tasks"
        )
        headers = {"Authorization": f"Bearer {self.valves.authToken}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tasks = response.json()
        formatted_tasks = []
        for task in tasks:
            formatted_task = {
                "id": task["id"],
                "created_at": task["created"],
                "content": task["title"],
                "priority": PRIORITY_MAP.get(task["priority"], "Unknown"),
                "due": task.get("due_date"),
                "labels": task["labels"],
                "description": task["description"],
            }
            formatted_tasks.append(formatted_task)
        return f"```json\n{json.dumps(formatted_tasks)}\n```"

    def update_vikunja_task(
        self,
        task_id: int,
        content: str = None,
        priority: int = 0,
        due_date: datetime = None,
        project_id: int = None,
    ) -> str:
        """
        Updates a specific task in Vikunja.
        """
        url = f"{self.valves.domain}/api/v1/projects/{project_id}/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {self.valves.authToken}"}
        data = {}
        if content:
            data["title"] = content
        if priority:
            data["priority"] = priority
        if due_date:
            data["due_date"] = due_date.isoformat()
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return f"Updated task {task_id} successfully."

    def create_vikunja_task(
        self,
        content: str,
        priority: int = 0,
        due_date: str = None,
        project_id: int = None,
        project_title: str = None
    ) -> str:
        """
        Creates a new task in Vikunja.
        """
        if not project_id:
            project_id = self.get_project_id(project_title)
        url = (
            f"{self.valves.domain}/api/v1/projects/{project_id}/tasks"
        )
        headers = {"Authorization": f"Bearer {self.valves.authToken}"}
        data = {
            "title": content,
            "priority": priority,
        }
        if due_date is not None:
            date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            data["due_date"] = date_obj.isoformat() + "Z"
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return f"Created task with ID {response.json()['id']} successfully."
