from pytas.http import TASClient
from pytas.models.base import TASModel


class Institution(TASModel):
    _resource_uri = "institutions/"

    def __init__(self, id=None, initial={}):
        super(Institution, self).__init__()
        if id is not None:
            api = TASClient()
            initial = api.get_institution(id)
            self.__populate(initial)
        else:
            self.__populate(initial)

    def __str__(self):
        return getattr(self, "name", "<new institution>")

    def __populate(self, data):
        self.__dict__.update(data)

    @classmethod
    def list(cls):
        api = TASClient()
        institutions = []
        data = api.institutions()
        for inst in data:
            institutions.append(cls(initial=data))

    @property
    def departments(self):
        depts = []
        if self.id:
            api = TASClient()
            data = api.get_departments(self.id)
            for dept in data:
                depts.append(Department(initial=dept))
        return depts


class Department(TASModel):
    def __init__(self, id=None, initial={}):
        super(Department, self).__init__()
        if id is not None:
            api = TASClient()
            initial = api.get_department(id, id)
            self.__populate(initial)
        else:
            self.__populate(initial)

    def __str__(self):
        return getattr(self, "name", "<new department>")

    def __populate(self, data):
        self.__dict__.update(data)
