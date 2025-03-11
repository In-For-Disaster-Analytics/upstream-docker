###
#
#
#
###
import pytas.models.projects
from pytas.http import TASClient

from .base import TASModel


class User(TASModel):
    _resource_uri = "users/"

    def __init__(self, username=None, id=None, initial={}):
        super(User, self).__init__()
        _projects = []

        if username is not None or id is not None:
            api = TASClient()
            remote_data = api.get_user(id=id, username=username)
            self.__populate(remote_data)
            project_data = api.projects_for_user(username=self.username)
            for d in project_data:
                _projects.append(projects.Project(initial=d))
        else:
            self.__populate(initial)

    def __str__(self):
        return getattr(self, "username", "<new user>")

    def __populate(self, data):
        self.__dict__.update(data)

    @classmethod
    def authenticate(cls, username, password):
        api = TASClient()
        if api.authenticate(username, password):
            return cls(initial=api.get_user(username=username))

    # @property
    def projects(self):
        _projects = []
        if self.username:
            api = TASClient()
            project_data = api.projects_for_user(username=self.username)
            for d in project_data:
                _projects.append(projects.Project(initial=d))
        return _projects

    def save(self):
        pass

    def request_password_reset(self, source=None):
        if self.username:
            api = TASClient()
            return api.request_password_reset(self.username, source)
        else:
            raise Exception("Cannot reset password: username is not set")

    def confirm_password_reset(self, code, new_password, source=None):
        if self.username:
            api = TASClient()
            return api.confirm_password_reset(
                self.username, code, new_password, source
            )
        else:
            raise Exception("Cannot reset password: username is not set")

    def verify_user(self, code):
        api = TASClient()
        if api.verify_user(code):
            return True
        return False
