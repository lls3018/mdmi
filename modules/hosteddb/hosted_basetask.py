#!/usr/bin/env python
# encoding=utf-8

import json
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger


class HostedBaseTask(object):
    '''
    class HostedBaseTask
        This class implements the task information and operations in the TaskQueue

    Attributes:
        m_tasks_list: List of tasks
        m_tasks_num: Number of tasks
    
    Notes:
        All sections in the basetask list as follows:
        owner, priority, enqueue_timestamp, account, name, tags, http_last_modified, task_retries, payload_base64

        tags and payload_base64 would be parsed in the subclass.
    '''
    def __init__(self):
        self.m_tasks_list = []
        self.m_tasks_num = 0
        pass

    def do_parse(self, datastr):
        '''
        Parses data string into base task struct dict.
        
        Params:
            datastr: Task struct string.

        Return:
            LIST of the task struct dict.
            Number of the tasks
            Exception message.
        '''
        try:
            jsonobj = json.loads(datastr, encoding="utf-8")
            if (isinstance(jsonobj, dict)): #error message is a dict
                if (jsonobj.has_key('ErrorCode')):
                    logger.error('No valid task found, error message from response: %s' % datastr)
                return [], 0
            #tasks in a List
            self.m_tasks_num = len(jsonobj)
            idx = 0
            # format base task structure
            while idx < self.m_tasks_num:
                if not jsonobj[idx].has_key('name'):
                    # Not as task structure
                    self.m_tasks_num = idx
                    break

                item = {
                        'owner' : jsonobj[idx]['owner'],
                        'priority' : jsonobj[idx].get('priority'),
                        'enqueue_timestamp' : jsonobj[idx]['enqueue_timestamp'],
                        'account' : int(jsonobj[idx]['account']),
                        'name' : int(jsonobj[idx]['name']),
                        'tags' : jsonobj[idx].get('tags'),
                        'task_retries' : int(jsonobj[idx]['task_retries']),
                        'payload_base64' : jsonobj[idx].get('payload_base64'),
                        }
                self.m_tasks_list.append(item)
                idx = idx + 1

            return self.m_tasks_list, self.m_tasks_num

        except Exception, e:
            logger.error(e)
            raise Exception('Invalid input! %s' % e)
        pass

    def get_base_tasks(self):
        '''
        Get tasks list parsed in the object
        
        Params:
            None
    
        Return:
            LIST of the task struct dict.
            Number of the tasks
        '''
        return self.m_tasks_list, self.m_tasks_num
        pass

    def erase(self):
        '''
        Erase tasks list parsed in the object
        
        Params:
            None
    
        Return:
            None
        '''
        self.m_tasks_list = []
        self.m_tasks_num = 0
        pass

# end of HostedBaseTask

