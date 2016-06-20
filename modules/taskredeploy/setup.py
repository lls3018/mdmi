#! /usr/bin/python
# fileName: setup.py
#encoding=utf-8

import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger
from hosteddb.hosted_taskqueue import HostedTaskQueue

class SetUp(object):
    """
    initialize taskqueues 'iosredeploy', 'iosredeployretry', 'iosredeployerror'
    """
    def init_plugin_task_queues(self):
        '''
        initialize deployment task queues
        '''
        task_queue_list = ['nonproxieddestchangeretry', 'nonproxieddestchangeerror', 'iosredeploy', 'iosredeployetry', 'iosredeployerror', 'mobiledeltabus', 'mobiledeltabusretry', 'mobiledeltabuserror']
        for tq in task_queue_list:
            self.create_task_queue(tq)

    def create_task_queue(self, qName):
        '''
        Create task queue in DB
        '''
        try:
            tq = HostedTaskQueue()
            data = {"description" : "iOS device redeployment task queue", "max_leases" : "30", "max_age" : "0"}
            logger.info("initialize task queue start")
            if not tq.do_get_taskqueue(tqname = qName):
                result = tq.do_establish_taskqueue(tqname=qName, description=data)
                if not result:
                    logger.error("taskqueue '%s' establish failed!" % qName)
                else:
                    logger.info("taskqueue '%s' initialize success!" % qName)
            else:
                logger.debug('task queue %s already exists' % qName)
        except Exception, e:
            logger.error("initialize taskqueue '%s' error: %s" % (qName, e))
            raise Exception("initialize taskqueue '%s' error" % qName)

if __name__ == '__main__':
    try:
        sp = SetUp()
        sp.init_plugin_task_queues()
        sys.exit(0)
    except Exception, e:
        logger.error("initialize deployment retry and error queue error %s" % e)
        sys.exit(1)
