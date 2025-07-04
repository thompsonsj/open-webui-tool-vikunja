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
        authToken: str = Field("", description="API key")
        projectId: str = Field("", description="Project ID")

    def __init__(self):
        self.valves = self.Valves()

    def get_todoist_tasks(self) -> str:
        """
        Retrieves active tasks from Vikunja for a specific project.
        """
        url = (
            f"https://todo.thompsonsj.com/api/v1/projects/{self.valves.projectId}/tasks"
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

    def update_todoist_task(
        self,
        task_id: int,
        content: str = None,
        priority: int = 0,
        due_date: datetime = None,
    ) -> str:
        """
        Updates a specific task in Vikunja.
        """
        url = f"https://todo.thompsonsj.com/api/v1/projects/{self.valves.projectId}/tasks/{task_id}"
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

    def create_todoist_task(self, content: str, priority: int = 0) -> str:
        """
        Creates a new task in Vikunja.
        """
        url = (
            f"https://todo.thompsonsj.com/api/v1/projects/{self.valves.projectId}/tasks"
        )
        headers = {"Authorization": f"Bearer {self.valves.authToken}"}
        data = {
            "title": content,
            "priority": priority,
        }
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return f"Created task with ID {response.json()['id']} successfully."
