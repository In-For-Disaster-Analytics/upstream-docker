###
#
#
#
###
import json

class TASModel(object):
    _resource_uri = None
    _fields = None

    def __init__(self):
        self.id = None

    def is_new(self):
        return self.id is None

    def get_uri(self):
        if self.id:
            return '%s%s' % (self._resource_uri, self.id)
        else:
            return self._resource_uri

    def as_dict(self):
        if self._fields:
            return {f:getattr(self, f, None) for f in self._fields}
        return self.__dict__

    def as_json(self, indent=None):
        return json.dumps(self, default=lambda o: o.as_dict() ,
                                          sort_keys=True, indent=indent)