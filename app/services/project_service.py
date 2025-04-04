import os

from app.api.v1.schemas.user import User
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

    def get_projects_for_user(self, user: User) -> list[PyTASProject]:
        active_projects = [
          u
          for u in self.client.projects_for_user(username=user.username)
          if u["allocations"][0]["status"] != "Inactive"
        ]
        return active_projects


    def get_project_members(self, project_id: str) -> list[PyTASUser]:
        return self.client.get_project_members(project_id=project_id)
