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

class EnrollmentDecisionTask(HostedBaseTask):
    '''
    class EnrollmentDicisionTask
        This class implements the task information and operations for enrollment decision task queue

    Attributes:
        None
    
    Notes:
        All sections in the basetask list as follows:
        owner, priority, enqueue_timestamp, account, name, tags, http_last_modified, task_retries, payload_base64

        tags and payload_base64 would be parsed in the subclass.
    '''
    def __init__(self, account=1, creator=1, type=1, data=None):
        tqconn = HostedTaskQueue()
        
        jdata = json.loads(data)
        tags = []
        tags.append("creator=" + str(creator))
        tags.append("deviceId=" + jdata['Device']['Udid'])
        tags.append("owner=" + jdata['User']['Email'])
        tags.append("type=" + str(type))
        tags.append("status=1")
        tags.append("restServiceFlag=1")
        
        payload_base64 = base64.b64encode(data)

        result = tqconn.do_add(tqname='enrollment', namespace='mobile', account=account, payload=payload_base64, tags=tags)
        if result.code == 200 or result.code == 201:
            logger.info('Notification REST Service - Add enrollment decision task success!')
        else:
            raise ServerInternalException('Add enrollment decision task failed!')
