#! /usr/bin/python
# fileName: taskutils.py
# encoding= utf-8

import os
import sys
import base64
import json
import re
sys.path.append("/opt/mdmi/modules/")
from hosteddb.hosted_taskqueue import HostedTaskQueue
from utils import logger
from utils.error import MDMiHttpError

TASK_STATUS_DICT = {
                    'normal':'status=1',
                    'retry':'status=2',
                    'error':'status=3'
                    }
class TaskUtils(object):
    '''
        common interface for enrollment TQP, iOS deployment TQP, Android TQP
    '''
    def __init__(self, jtask, retry_qname, error_qname):
        assert isinstance(jtask, dict), 'task invalid'
        self.m_created = jtask.get('created')
        self.m_enqueue_timestamp = jtask.get('enqueue_timestamp')
        self.m_creator = jtask.get('creator')
        self.m_name = jtask.get('name')
        self.m_account = jtask.get('account')
        self.m_payload_base64 = jtask.get('payload_base64')
        self.m_payload = base64.decodestring(self.m_payload_base64)
        self.m_tags = jtask.get('tags')
        self.m_lease_timestamp = jtask.get('lease_timestamp')
        self.m_owner = jtask.get('owner')
        self.m_task_retries = jtask.get('task_retries')
        self.m_priority = jtask.get('priority')

        self.m_retry_qname = retry_qname
        self.m_error_qname = error_qname
        pass

    def __del__(self):
        pass

    def move_task_to_errorqueue(self, error_msg):
        hostedTQ = HostedTaskQueue()
        if type(self.m_tags)!=list:
            logger.error('task tags is not a list:[%s]' % self.m_tags)
            raise Exception('tags type error in move_task_to_errorqueue')
        if TASK_STATUS_DICT['normal'] in self.m_tags:
            self.m_tags.remove(TASK_STATUS_DICT['normal'])
        if TASK_STATUS_DICT['retry'] in self.m_tags:
            self.m_tags.remove(TASK_STATUS_DICT['retry'])
        self.m_tags.append(TASK_STATUS_DICT['error'])

        tag_error = 'error_msg_base64=%s' % base64.encodestring(error_msg).replace('\n', '')
        self.m_tags.append(tag_error)
        try:
            hostedTQ.do_add(tqname=self.m_error_qname, namespace='mobile', account=int(self.m_account), version=1, payload=self.m_payload_base64, tags=self.m_tags, priority = self.m_priority)
        except MDMiHttpError, e:
            logger.debug('add error task failed:%s, will try to create error queue' % repr(e))
            error_qname_list = [
            {'name' : 'enrollmentError', 'settings' : {"description" : "Enrollment Decision Error task queue", "max_leases" : "30", "max_age" : "0"}}
            ]
            tqo = TaskQueueUtils(error_qname_list)
            tqo.init_task_queue()
            del tqo

            hostedTQ.do_add(tqname=self.m_error_qname, namespace='mobile', account=int(self.m_account), version=1, payload=self.m_payload_base64, tags=self.m_tags, priority = self.m_priority)
        finally:
            del hostedTQ

        logger.info('add task to error queue success')

    def move_task_to_retryqueue(self):
        hostedTQ = HostedTaskQueue()
        if type(self.m_tags)!=list:
            logger.error('task tags is not a list:[%s]' % self.m_tags)
            raise Exception('tags type error in move_task_to_retryqueue')

        if not TASK_STATUS_DICT['retry'] in self.m_tags:
            if TASK_STATUS_DICT['normal'] in self.m_tags:
                self.m_tags.remove(TASK_STATUS_DICT['normal'])
            self.m_tags.append(TASK_STATUS_DICT['retry'])
            hostedTQ.do_add(tqname=self.m_retry_qname, namespace='mobile', account=int(self.m_account), version=1, payload=self.m_payload_base64, tags=self.m_tags, priority = self.m_priority)
            logger.debug('enrollment.py - add task to retry queue success')

    def _get_tags_item(self, prefix):
        ret = None

        for item in self.m_tags:
            if re.match(prefix, item):
                ret = item[len(prefix):]
                break

        return ret

    def get_task_creator(self):
        '''
            This is the component which created this task defined as
            1 - Notification Service
            2 - User and Group Service
            3 - User and Group Sync TQP
            4 - Enrollment Decision TQP
            5 - iOS Deployment TQP
            6 - Android Deployment TQP
        '''
        return self._get_tags_item('creator=')
        pass

    def get_task_deviceId(self):
        '''
            Device UDID
        '''
        return self._get_tags_item('deviceId=')
        pass

    def get_task_owner(self):
        '''
            Email address of this end user
        '''
        return self._get_tags_item('owner=')
        pass

    def get_task_type(self):
        '''
            Type of task defined as
            1 - Enrollment
            2 - De-enrollment
            3 - Wipe
            4 - Enterprise Wipe
            5 - Compliance status changed
            6 - Compromise status changed
        '''
        return self._get_tags_item('type=')
        pass

    def get_task_status(self):
        '''
            status of task defined as
            1 - Normal task
            2 - Retry task
            3 - Error task
        '''
        return self._get_tags_item('status=')
        pass

    def get_task_restServiceFlag(self):
        '''
            tasks come from rest service if this attribute exist in tags.
        '''
        return self._get_tags_item('restServiceFlag=')
        pass

    def check_os_type_version(self):
        pass

class TaskQueueUtils(object):
    '''
        task queue init interface
    '''
    def __init__(self, qname_list):
        '''
            qname_dict:
                [
                    {'name' : 'enrollment', 'settings' : {"description" : "Enrollment Decision task queue", "max_leases" : "30", "max_age" : "0"}},
                    {'name' : 'enrollmentRetry', 'settings' : {"description" : "Enrollment Decision Retry task queue", "max_leases" : "30", "max_age" : "0"}},
                    {'name' : 'enrollmentError', 'settings' : {"description" : "Enrollment Decision Error task queue", "max_leases" : "30", "max_age" : "0"}},
                ]
        '''
        self.m_qname_list = qname_list

    def init_task_queue(self):
        if len(self.m_qname_list) > 0:
            tqobj = HostedTaskQueue()
            for tq in self.m_qname_list:
                try:
                    if tq.has_key('name') and tq.has_key('settings'):
                        result = tqobj.do_establish_taskqueue(tqname=tq['name'], description=tq['settings'])
                        if result:
                            logger.debug('Task Queue %s initialize ok!' % tq['name'])
                        else:
                            logger.error('Task Queue %s initialize failed!' % tq['name'])
                    else:
                        logger.error('Unknow task queue setting! Value is %s' % repr(tq))
                except Exception, e:
                    logger.error(e)
                    raise Exception("Initialize task queue error!")
            del tqobj
