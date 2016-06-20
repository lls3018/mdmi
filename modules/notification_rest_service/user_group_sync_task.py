#!/usr/bin/env python2.6
# encoding=utf-8

import sys
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
import json
import base64
from utils import logger
from hosteddb.hosted_basetask import HostedBaseTask
from hosteddb.hosted_taskqueue import HostedTaskQueue
from server_internal_exception import ServerInternalException

class UserGroupSyncTask(HostedBaseTask):
    '''
    class UserGroupSyncTask
        This class implements the task information and operations for user group sync task queue

    Attributes:
        None
    
    Notes:
        All sections in the basetask list as follows:
        owner, priority, enqueue_timestamp, account, name, tags, http_last_modified, task_retries, payload_base64

        tags and payload_base64 would be parsed in the subclass.
    '''
    def __init__(self, account=1, creator=1, type=1, data=None):
        tqconn = HostedTaskQueue()

        tags = []
        tags.append("reties=0")
        tags.append("type=" + str(type))
        tags.append("creator=" + str(creator))
        tags.append("restServiceFlag=1")

        payload = {}
        payload.update({'requestPayload': data})
        tmpdict = self.analyse_payload(data)
        payload.update(tmpdict)
        payload = json.dumps(payload)

        payload_base64 = base64.b64encode(payload)

        result = tqconn.do_add(tqname='usergroup', namespace='mobile', account=account, payload=payload_base64, tags=tags)
        if result.code == 200 or result.code == 201:
            logger.info('Notification REST Service - Add user sync task success!')
        else:
            raise ServerInternalException('Add user sync task failed!')
    
    def analyse_payload(self, payload):
        jobj = json.loads(payload)
        if jobj.has_key("Device"):
            device_id = jobj["Device"]["Udid"]
        else:
            device_id = ""

        if jobj.has_key("User"):
            email = jobj["User"]["Email"]
        else:
            email = ""

        return {'deviceId' : device_id, 'email' : email}
