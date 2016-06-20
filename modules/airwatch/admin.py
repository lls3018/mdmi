# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from airwatch.base import AirwatchBase

class AirwatchAdmin(AirwatchBase):
    def __init__(self, account_id):
        super(AirwatchAdmin, self).__init__(account_id)

    def __del__(self):
        super(AirwatchAdmin, self).__del__()

    def create(self, data):
        resource = "/API/v1/system/admins/addadminuser"
        result = self.rest.do_access(resource, "POST", self.parse_param(data), headers=self.aw_headers)

        body = self._parse_result(result)
        if isinstance(body, dict) and body.has_key('Value'): return body['Value']
        else: return body

    def get(self, admin_id):
        resource = "/API/v1/system/admins/{id}".format(id=admin_id)
        result = self.rest.do_access(resource, "GET", headers=self.aw_headers)

        body = self._parse_result(result)
        if isinstance(body["Id"], dict) and body["Id"].has_key('Value'):
            body["Id"] = body["Id"]["Value"]

        return body

    def modify(self, admin_id, data=None, http_method="POST", method_name="update"):
        resource = "/API/v1/system/admins/{id}/{method}".format(id=admin_id, method=method_name)
        result = self.rest.do_access(resource, http_method, self.parse_param(data), headers=self.aw_headers)

        body = self._parse_result(result)
        if body: return body
        else: return admin_id

    def update(self, admin_id, data):
        return self.modify(admin_id, data)

    def changepassword(self, admin_id, data):
        return self.modify(admin_id, data, method_name=self.changepassword.__name__)

    def addrole(self, admin_id, data):
        return self.modify(admin_id, data, method_name=self.addrole.__name__)

    def removerole(self, admin_id, data):
        return self.modify(admin_id, data, method_name=self.removerole.__name__)

    def delete(self, admin_id):
        return self.modify(admin_id, None, "DELETE", self.delete.__name__)
