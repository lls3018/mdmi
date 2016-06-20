# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils.rest_access import RESTAccess

class AirwatchRESTAccess(RESTAccess):
    def __init__(self, host, port=443, connection=None):
        self.host = host
        self.port = port
        super(AirwatchRESTAccess, self).__init__(host, port, connection)

    def do_access(self, resource, method_name="GET", data=None, headers=None):
        return super(AirwatchRESTAccess, self).do_access(resource, method_name, data, headers)
