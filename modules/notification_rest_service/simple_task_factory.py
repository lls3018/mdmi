'''
Created on Aug 7, 2013

@author: harlan
'''
import sys
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
from request import Request
from user_group_sync_task import UserGroupSyncTask
from enrollment_decision_task import EnrollmentDecisionTask

class SimpleTaskFactory(object):
    '''
    class SimpleTaskFactory
        This class is a simple task factoryclass which generate different tasks according to different request type

    Attributes:
        None
    '''

    @classmethod
    def create_task(cls, request, type="install"):
        data = request.data
        request_id = request.request_id
        account_id = request.account_id

        if type == "install":
            # Add task into the User and Group sync task queue
            UserGroupSyncTask(account=account_id, data=data)
        elif type == "remove":
            # Add task into the Enrollment Decision task queue
            EnrollmentDecisionTask(account=account_id, type=2, data=data)
        else:
            raise ValueError("Notification REST Service - action type %s does not support!" % type)
