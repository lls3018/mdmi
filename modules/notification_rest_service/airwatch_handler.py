'''
Created on Aug 7, 2013

@author: harlan
'''
import os
import sys
import json
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
from utils import logger
from request import Request
from common_handler import CommonHandler
from hosteddb.hosted_user import HostedUser
from hosteddb.hosted_account import HostedAccount
from simple_task_factory import SimpleTaskFactory
from server_internal_exception import ServerInternalException
from authentication_failure_exception import AuthenticationFailureException

class AirwatchHandler(CommonHandler):
    '''
    class AirwatchHandler
        This class is a subclass of CommonHandler which implement three hook methods(pre_process, process and post_process)
        of CommondHandler

    Attributes:
        None

    Notes:
        pre_process() check if http request is invalid
        process() get admin info
        post_process() add task into specific task queue
    '''

    def __init__(self, dict):
        self.request = Request(data=dict['data'])
        super(AirwatchHandler, self).__init__(dict)

    def pre_process(self):
        content_type = None
        if self.dict["headers"].has_key('Content-Type'):
            content_type = self.dict["headers"]["Content-Type"]
        if not content_type or content_type.find('application/json') < 0:
            raise ValueError("Notification REST Service - Content-Type: %s in HTTP Header does not support!" % content_type)

        logger.debug("Notification REST Service - Content-Type: %s", content_type)

    def process(self):
        account = os.environ.get('hosted_account')
        
        #estimate the device version 
        if self.dict["type"] == 'install':
            data_info = json.loads(self.request.data)       
            logger.debug('Notification REST Service - Device :%s', data_info['Device'])
            version = data_info['Device']['OperatingSystem']
            version_1 = int(version.split('.')[0])       
            logger.debug('Notification REST Service - Device version: %s %s', data_info['Device']['Platform'], version) 
            
            if data_info['Device']['Platform'] == 'Apple' and version_1 < 7:
                raise ValueError('Notification REST Service - IOS Device Vsersion: %s  Not Support' %version)
            elif data_info['Device']['Platform'] == 'Android' and version_1 < 4:
                raise ValueError('Notification REST Service - Android Device Vsersion: %s  Not Support' %version)


        #distinguish hosted or hybird account
        account_info = HostedAccount(account).get_airwatch_credential()
        if account_info['enabledServices'].find('wdCategories') >= 0:
            data = json.loads(self.request.data)
            data['User'].update({'enabledServices' : 'wdCategories'})
            self.request.data = json.dumps(data)
            logger.debug("account:%s is Hosted account", account)
        else:
            data = json.loads(self.request.data)
            data['User'].update({'enabledServices' : 'hyPE'})
            self.request.data = json.dumps(data)
            logger.debug("account:%s is Hybrid account", account)

        logger.debug('data info:%s', self.request.data)

        self.request.account_id = int(account)
        del  os.environ['hosted_account']

    def post_process(self):
        SimpleTaskFactory.create_task(self.request, self.dict["type"])
