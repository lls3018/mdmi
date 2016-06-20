#!/usr/bin/python

import web
import sys
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
from notification_rest_service.airwatch_request import AirwatchRequest

urls = (
    '/.*/v(.+)/profile/install', 'AirwatchProfileInstallation',
    '/.*/v(.+)/profile/remove', 'AirwatchProfileRemoval',
    '/.*/v1', 'AirwatchConnectionTester',
)

class AirwatchProfileInstallation:
    def POST(self, version):
        AirwatchRequest(version, "install").execute()

class AirwatchProfileRemoval:
    def POST(self, version):
        AirwatchRequest(version, "remove").execute()

class AirwatchConnectionTester:
    def GET(self):
        return web.OK()

application = web.application(urls, globals()).wsgifunc()
