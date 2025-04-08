###
#
#
#
###
from app.pytas.http import TASClient

from .base import TASModel
from .users import User

PROJECT_TYPES = (
    (0, "Research"),
    (2, "Startup"),
    (4, "Educational"),
    (1, "Institutional"),
    (6, "Partner"),
)


class Project(TASModel):
    _resource_uri = "projects/"
    _fields = [
        "id",
        "title",
        "chargeCode",
        "typeId",
        "description",
        "source",
        "fieldId",
        "piId",
        "allocations",
    ]

    def __populate(self, data):
        self.__dict__.update(data)

        self.pi = User(initial=data["pi"])

        allocations = []
        for alloc in data["allocations"]:
            allocations.append(Allocation(initial=alloc))
        self.allocations = allocations

    def __init__(self, id=None, initial={}):
        super(Project, self).__init__()
        if id is not None:
            api = TASClient()
            remote_data = api.project(id)
            self.__populate(remote_data)
        else:
            self.__populate(initial)

    def __str__(self):
        return getattr(self, "chargeCode", "<new project>")

    def as_dict(self):
        proj_dict = {f: getattr(self, f, None) for f in self._fields}
        proj_dict["allocations"] = [a.as_dict() for a in self.allocations]
        return proj_dict

    @classmethod
    def list(cls, username=None, group=None):
        """
        Returns a list for projects for the given username or group.
        An argument for username or group is required and only one
        may be provided.
        """
        if username is None and group is None:
            raise TypeError("Argument username or group is required")
        if username is not None and group is not None:
            raise TypeError("One one of username or group can be passed")

        api = TASClient()
        if username:
            data = api.projects_for_user(username)
        elif group:
            data = api.projects_for_group(group)
        return list(cls(initial=d) for d in data)

    def save(self):
        api = TASClient()
        if self.is_new():
            created = api.create_project(self.as_dict())
            self.__populate(initial=created)

    def get_users(self):
        api = TASClient()
        user_data = api.get_project_users(self.id)
        return list(User(initial=u) for u in user_data)

    def add_user(self, username):
        api = TASClient()
        return api.add_project_user(self.id, username)

    def remove_user(self, username):
        api = TASClient()
        return api.del_project_user(self.id, username)


class Allocation(TASModel):
    _resource_uri = "allocations/"
    _fields = [
        "computeUsed",
        "computeAllocated",
        "computeRequested",
        "dateRequested",
        "dateReviewed",
        "decisionSummary",
        "end",
        "id",
        "justification",
        "memoryUsed",
        "memoryAllocated",
        "memoryRequested",
        "project",
        "projectId",
        "requestor",
        "requestorId",
        "resource",
        "resourceId",
        "reviewer",
        "reviewerId",
        "start",
        "status",
        "storageUsed",
        "storageAllocated",
        "storageRequested",
    ]

    def __init__(self, initial={}):
        super(Allocation, self).__init__()
        self.__populate(initial)

    def __populate(self, data):
        self.__dict__.update(data)

    @property
    def percentComputeUsed(self):
        used = getattr(self, "computeUsed", 0)
        alloc = getattr(self, "computeAllocated", 0)
        if alloc > 0:
            return (used / alloc) * 100
        return 0


class AllocationApproval(object):
    pass
