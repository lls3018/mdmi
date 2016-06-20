#!/usr/bin/env python2.6
# encoding=utf-8

from hosted_access import HostedAccess
import json
import base64
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger
from utils.error import MDMiHttpError

TQRES_TEMPLATE_STR = '/tq/v-%d/account-%d/namespace-%s/taskqueue-%s'

class HostedTaskQueue(object):
    '''
    class HostedTaskQueue
        This class implements the access to TaskQueue
    
    Attributes:
        m_wrest: Instance object of class HostedAccess
    '''
    def __init__(self):
        self.m_wrest = HostedAccess()
        pass

    def do_add(self, tqname=None, namespace='mobile', account=1, version=1, payload=None, tags=None, priority='low', delay=0):
        '''
        Insert one task into the specific task queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            payload: Base64 encode string.
            tags: Tags in the task.
            priority: Priority of the task.
            delay: If delay is set, the lease request will not see the added task in [delay] seconds.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        resource = '/'.join([resource, 'addtask'])
        if delay > 0:
            resource += '?delay=%s' % delay
        data = json.dumps({'payload_base64' : payload, 'tags' : tags, 'priority' : priority}, encoding="utf-8")
        logger.debug('Add task - resource:%s, data:%s' % (resource, data))
        return self.m_wrest.do_access(resource, 'POST', data=data, headers=None)

    def do_bulk_add(self, tqname=None, namespace='mobile', account=1, version=1, taskslist=[]):
        '''
        Insert tasks into the specific task queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            taskslist: task structures in list. 
                For example: [
                                {
                                    "payload_base64": "TXkgbGl0dGxlIHRhc2sK",
                                    "tags": ["state=red", "watchthis", "code=41"],
                                    "priority" : "high"
                                },
                                ...
                            ]

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        #check data is available
        assert(tqname)
        assert(isinstance(taskslist, list))
        for task in taskslist:
            assert(isinstance(task, dict))
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        resource = '/'.join([resource, 'addtasks'])
        data = json.dumps(taskslist, encoding="utf-8")
        logger.debug('Add %d tasks - resource:%s, data:%s' % (len(taskslist), resource, data))
        return self.m_wrest.do_access(resource, 'POST', data=data, headers=None)

    def do_delete(self, tqname=None, namespace='mobile', account=1, version=1, taskname=0):
        '''
        Delete task from specific task queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            taskname: Name of the specific task.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        temp = 'task-%s' % taskname
        resource = '/'.join([resource, temp])
        logger.debug('Delete task - resource:%s' % (resource))
        return self.m_wrest.do_access(resource, 'DELETE', data=None, headers=None)

    def do_bulk_delete(self, tqname=None, namespace='mobile', account=1, version=1, numslist=[]):
        '''
        Delete tasks by bulk mode from specific task queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            numslist: List of task ids

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        assert(isinstance(numslist, list))
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        resource = '/'.join([resource, 'deletetasks'])
        data = json.dumps(numslist, encoding="utf-8")
        logger.debug('Delete %d tasks - resource:%s, data:%s' % (len(numslist), resource, data))
        return self.m_wrest.do_access(resource, 'POST', data=data, headers=None)


    def do_update(self, tqname=None, namespace='mobile', account=1, version=1, taskname=0, payload=None, tags=None, priority='low', enqueuetime=''):
        '''
        Modify seciton value of one task.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            taskname: Name of the specific task.
            payload: Base64 encode string.
            tags: Tags in the task.
            priority: Priority of the task.
            enqueuetime: Last modify time.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        assert(payload and tags)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        temp = 'task-%s' % taskname
        resource = '/'.join([resource, temp])
        data = json.dumps({'payload_base64' : payload, 'tags' : tags, 'priority' : priority}, encoding="utf-8")
        header = self.m_wrest.generate_default_header()
        header.update({'If-Unmodified-Since' : enqueuetime})
        logger.debug('Update task - resource:%s, header:%s, data:%s' % (resource, header, data))
        return self.m_wrest.do_access(resource, 'PUT', data=data, headers=header)

    def do_get(self, tqname=None, namespace='mobile', account=1, version=1, taskname=0):
        '''
        Get one task information from the specific task queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            taskname: Name of the specific task.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        temp = 'task-%s' % taskname
        resource = '/'.join([resource, temp])
        logger.debug('Get task - resource:%s' % (resource))
        return self.m_wrest.do_access(resource, 'GET', data=None, headers=None)

    def do_get_many(self, tqname=None, namespace='mobile', account=1, version=1, tasknum=0, tags=None):
        '''
        Get a bulk of tasks' information from the specific task queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            tasknum: Number of the tasks that expected.
            tags: Search conditions.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        resource = '/'.join([resource, 'search?numTasks=%s'])
        resource = resource % tasknum
        resource = '&'.join([resource, 'orderby=priority'])
        if tags:
            data = json.dumps({'tags' : tags}, encoding="utf-8")
        else:
            data = tags
        logger.debug('Get tasks - resource:%s, data:%s' % (resource, data))
        return self.m_wrest.do_access(resource, 'POST', data=data, headers=None)

    def do_lease(self, tqname=None, namespace='mobile', account=1, version=1, tasknum=0, tags=None, leasesec=10):
        '''
        Acquire a lease on the topmost {numTask} unowned tasks in the specified queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            tasknum: Number of the tasks that expected.
            tags: Search conditions.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        resource = '/'.join([resource, 'lease?numTasks=%s'])
        resource = resource % tasknum
        resource = '&'.join([resource, 'leaseSecs=%s'])
        resource = resource % leasesec
        if tags:
            data = json.dumps({'tags' : tags}, encoding="utf-8")
        else:
            data = tags
        logger.debug('Lease tasks - resource:%s, data:%s' % (resource, data))
        return self.m_wrest.do_access(resource, 'POST', data=data, headers=None)

    def do_get_taskqueue(self, tqname=None, namespace='mobile', account=1, version=1):
        '''
        Get the specific taskqueue. If the task queue exists, return True, else return False.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
        Return:
            True: get task queue success.
            False: get task queue failed.
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        logger.debug('Get one taskqueue - name:%s, resource:%s' % (tqname, resource))
        try:
            result = self.m_wrest.do_access(resource, 'GET', data=None, headers=None)
            if result.code >= 200 and result.code < 300:
                logger.debug('Task Queue exists!')
                return True
        except MDMiHttpError, e:
            logger.debug('Task Queue NOT exists! %s' % str(e))
            return False

    def do_establish_taskqueue(self, tqname=None, namespace='mobile', account=1, version=1, description=None):
        '''
        Establish one taskqueue. If the task queue exists, the establishment would been cancelled.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            description: Description for the task queue
        Return:
            True: Establish success.
            False: Establish failed.
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        logger.debug('Establish one taskqueue - name:%s, resource:%s, description:%s' % (tqname, resource, description))
        result = self.do_get_taskqueue(tqname, namespace, account, version)
        if result == True:
            logger.debug('Task Queue exists, canceling the establishment!')
            return True
        else:
            if isinstance(description, basestring):
                description = {'description' : description}
            elif isinstance(description, dict):
                pass
            else:
                logger.error('Establish Task Queue failed! Unknow description type!')
                return False
            data = json.dumps(description)
            result = self.m_wrest.do_access(resource, 'PUT', data=data, headers=None)
            if result.code >= 200 and result.code < 300:
                logger.debug('Establish Task Queue success!')
                return True
            #MDMiHttpError would be raised if result.code was not in the range(200, 299)  

    def do_delete_taskqueue(self, tqname=None, namespace='mobile', account=1, version=1):
        '''
        Delete the specific task queue

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        logger.debug('Delete task queue - resource:%s' % (resource))
        result = self.do_get_taskqueue(tqname, namespace, account, version)
        if result == True:
            result = self.m_wrest.do_access(resource, 'DELETE', data=None, headers=None)
            if result.code >= 200 and result.code < 300:
                logger.debug('Delete Task Queue success!')
                return True
        else:
            logger.debug('Delete task queue failed! task queue:%s is not existing.' % tqname)
            return False

    def do_get_task_total(self, tqname=None, namespace='mobile', account=1, version=1, tags=None):
        '''
        Get total number of the specific task queue.

        Params:
            tqname: Name of task queue.
            namespace: Namespace of the task queue.
            account: Account ID.
            version: Version of the resource, default value 1.
            tags: Search conditions.

        Return:
            Total number of tasks on this taskqueue
            Exception message
        '''
        assert(tqname)
        resource = TQRES_TEMPLATE_STR % (version, account, namespace, tqname)
        resource = '/'.join([resource, 'stats'])
        if tags:
            data = json.dumps({'tags' : tags}, encoding="utf-8")
        else:
            data = tags
        logger.debug('Get total tasks number - resource:%s, data:%s' % (resource, data))
        result = self.m_wrest.do_access(resource, 'POST', data=data, headers=None)
        if result.code >= 200 and result.code < 300:
            logger.debug('Get Task Queue stats success!')
            try: #parse stat data
                tqs = json.loads(result.content)
                total_tasks = tqs.get('total_tasks')
                return total_tasks
            except Exception, e:
                logger.error('Get Task Queue stats Failed! %s' % repr(e))
        #MDMiHttpError would be raised if result.code was not in the range(200, 299)
        pass

    def format_tq_tags(self, source=None, *items):
        '''
        Format tags members for task queue operation commands.

        Params:
            source : Input tags list. If this param is empty, the interface would create a new one.
            *items : The specific items of the tags.

        Return:
            List of the tags
        '''
        if source: 
            assert(isinstance(source, list))
            retval = source
        else:
            retval = []

        for item in items:
            retval.append(item)

        return retval

    def format_tq_payload(self, source=None, encode=False, **keyval):
        '''
        Format payload members for task queue operation commands.

        Params:
            source : Input payload dict. If this param is empty, the interface would create a new one.
            encode : Enable/Disable encoding. Default value is false. It would remove '\n' when enable encoding.
                    Converts data to json str at first, then with base64 encoding.
            keyval : Key name and value of the specific payload.

        Return:
            dict of the payload
            Str with base64 encoded.
            Exception message
        '''
        if source:
            assert(isinstance(source, dict))
            retval = source
        else:
            retval = {}

        retval.update(keyval)  # append key
        if encode:
            # convert into json
            try:
                retval = json.dumps(retval)
            except Exception, e:
                logger.error('Encoding payload error: %s!' % e)
                raise Exception(e)

            # base64
            retval = base64.encodingstring(retval).replace("\n", '')

        return retval


