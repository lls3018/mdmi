#!/usr/bin/python
#Filename: ensure_task_queue_exist.py

import sys
sys.path.append('/opt/mdmi/modules')
from utils import logger
from hosteddb.hosted_taskqueue import HostedTaskQueue
from usergroupcommon import TASK_QUEUE_ENROLLMENT 
from usergroupcommon import TASK_QUEUE_USERGROUP  
from usergroupcommon import TASK_QUEUE_USERGROUP_ERROR   
from usergroupcommon import TASK_QUEUE_USERGROUP_PENDING    
from usergroupcommon import TASK_QUEUE_USERGROUP_RETRY     
from usergroupcommon import TASK_QUEUE_USERGROUP_PERIODIC

def establish_taskqueue(tqname, data):
    result = HostedTaskQueue().do_establish_taskqueue(tqname=tqname, description=data)
    if not result:
        logger.error('Task Queue %s established failed!' % tqname)
    else:
        logger.info('Task Queue %s established success!' % tqname)

if __name__ == '__main__':
    establish_taskqueue(TASK_QUEUE_ENROLLMENT, {"description": "enrollment decision", "max_leases": 30})
    establish_taskqueue(TASK_QUEUE_USERGROUP_ERROR, {"description": "user/group sync error", "max_leases": 30})
    establish_taskqueue(TASK_QUEUE_USERGROUP_PENDING, {"description": "user/group sync pending", "max_leases": 30})
    establish_taskqueue(TASK_QUEUE_USERGROUP_RETRY, {"description": "user/group sync retry", "max_leases": 30})
    establish_taskqueue(TASK_QUEUE_USERGROUP, {"description": "user/group", "max_leases": 30})
    establish_taskqueue(TASK_QUEUE_USERGROUP_PERIODIC, {"description": "user/group periodic sync", "max_leases": 30})
