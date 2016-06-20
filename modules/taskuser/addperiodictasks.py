#!/usr/bin/python
import os
import sys
if '/opt/mdmi/modules/' not in sys.path:
    sys.path.append('/opt/mdmi/modules/')

from utils import logger
from hosteddb.hosted_account import HostedAccount
from hosteddb.hosted_taskqueue import HostedTaskQueue
from taskuser.usergroupcommon import TASK_QUEUE_USERGROUP_PERIODIC  
from taskuser.usergroupcommon import ACCOUNT_BLACK_SPIDER   


def main():

    #estimate localhost is master
    result =  os.path.exists('/etc/sysconfig/mes.primary')
    if result:
        logger.info('Start adding periodic usergroup sync tasks.')
        hosted_account = HostedAccount(ACCOUNT_BLACK_SPIDER)
        #acct_nums = hosted_account.get_airwatch_account_ids()
        acct_nums = hosted_account.get_airwatch_hosted_account_ids()
        success = 0
        failure = 0
        if acct_nums:
            for n in acct_nums:
                try:
                    task_num = HostedTaskQueue().do_get_task_total(tqname=TASK_QUEUE_USERGROUP_PERIODIC, account=int(n))
                    if int(task_num):
                        logger.info('Another machine has added periodic sync tasks. Abort adding.')
                        break
                    logger.info('To add periodic usergroup sync task for account %s.', n)
                    HostedTaskQueue().do_add(tqname=TASK_QUEUE_USERGROUP_PERIODIC, account=int(n))
                    success += 1
                    logger.info('Added periodic usergroup sync task for account %s.', n)
                except Exception as e:
                    failure += 1
                    logger.error('Add periodic usergroup sync task for account %s failed. %s', n, e)
                    logger.error(e)
        logger.info('END adding periodic usergroup sync tasks. %d success, %d failure.', success, failure)
    else:
        logger.info('localhost is not master')

if __name__ == '__main__':
    main()
