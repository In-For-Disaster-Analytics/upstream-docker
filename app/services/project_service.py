import os

from app.pytas.http import TASClient
from app.pytas.models.schemas import PyTASUser, PyTASProject


class ProjectService:
    def __init__(self):
        self.client = TASClient(
            baseURL=os.getenv("tasURL"),
            credentials={
                "username": os.getenv("tasUser"),
                "password": os.getenv("tasSecret"),
            },
        )

    def get_projects_for_user(self, username: str) -> list[PyTASProject]:
        active_projects = []
        for p in self.client.projects_for_user(username=username):
            if p.allocations[0].status != "Inactive":
                active_projects.append(p)
        return active_projects


    def get_project_members(self, project_id: str) -> list[PyTASUser]:
        return self.client.get_project_members(project_id=project_id)
