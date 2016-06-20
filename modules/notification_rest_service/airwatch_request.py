#!/usr/bin/python

import web
import sys
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
import json
from utils import logger
from utils import monitorutils
from notification_rest_service.airwatch_handler import AirwatchHandler
from notification_rest_service.server_internal_exception import ServerInternalException
from notification_rest_service.authentication_failure_exception import AuthenticationFailureException

class AirwatchRequest:
    '''
    class AirwatchRequest
    
    Attributes:
        None

    Notes:
        execute() take requests sent from AW and delegate to airwatch_handler
    '''

    def __init__(self, version, type):
        if version != "1":
            raise web.NotFound("Not support Version %s" % version)

        self.type = type
        self.version = version

    def execute(self):
        try:
            dict = {"data": web.data(), "headers": {"Content-Type": web.ctx.env.get('CONTENT_TYPE')}, "type": self.type}
            AirwatchHandler(dict).handle()
            monitorutils.count_task("notificationrestservice", True)
            return web.OK()
        except AuthenticationFailureException, e:
            logger.error('Notification REST Service - %s' % e)
            monitorutils.count_task("notificationrestservice", False)
            raise web.Unauthorized()
        except ValueError, e:
            logger.error('Notification REST Service - %s' % e)
            monitorutils.count_task("notificationrestservice", False)
            raise web.NotAcceptable()
        except KeyError, e:
            logger.error('Notification REST Service - %s' % e)
            monitorutils.count_task("notificationrestservice", False)
            raise web.NotAcceptable()
        except ServerInternalException, e:
            logger.error('Notification REST Service - %s' % e)
            monitorutils.count_task("notificationrestservice", False)
            raise web.InternalError() 
        except Exception, e:
            logger.error('Notification REST Service - %s' % e)
            monitorutils.count_task("notificationrestservice", False)
            raise web.InternalError()
