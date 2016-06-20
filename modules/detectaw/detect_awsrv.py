#! /usr/bin/python
# encoding = UTF-8

import os
import sys
import string
import json
import base64
sys.path.append("/opt/mdmi/modules")
from utils import logger
from hosteddb.hosted_account import HostedAccount
from airwatch.vpn_profile import AirwatchVPNProfile
from hosteddb.hosted_taskqueue import HostedTaskQueue
from utils.error import MDMiHttpError

MASTER_SERVER_FILE = '/etc/sysconfig/mes.primary'
DETECT_URL = '/API/v1/mdm'
SRV_FILE_PATH = '/etc/sysconfig/serviceconfig.json'

class MailTemplate(object):
    '''
    mail template
    '''
    def __init__(self):
        self.template = '''Content-Type: multipart/alternative;
    boundary="_000_6256F322EB496C49B29B9C4AF5E82D142CF7B746SBJEXCH1Bwebsen_"
MIME-Version: 1.0
To: <_rcptto_>
From: _displayfromname_ <_mailfrom_>
Subject: Cannot connect to AirWatch

--_000_6256F322EB496C49B29B9C4AF5E82D142CF7B746SBJEXCH1Bwebsen_
Content-Type: text/html; charset="us-ascii"
Content-Transfer-Encoding: 8bit

<html>
<body>
Websense&#174 TRITON&#174 AP-WEB is unable to connect to the AirWatch system. Please check if the AirWatch administrator's username, the API URL, or API key has changed. If any of these has changed, you need to update the information on the Mobile Device Management Account Setup page in the <a href="https://_portalurl_/portal">Cloud TRITON Manager</a> (Account Settings > Device Management > Mobile Device Management Account Setup).<br>
<br>
We recommend that you then go onto the AirWatch Console to check that the Websense VPN profile is installed on all devices (See the step "Install the VPN profile to devices" in the Getting Started Guide).
</body>
</html>

--_000_6256F322EB496C49B29B9C4AF5E82D142CF7B746SBJEXCH1Bwebsen_--
        '''

    def __del__(self):
        pass

    def get_mail_template(self):
        return self.template

class DetectAWService():

    def _get_cluster_portal_url(self):
        '''
        get portal url
        '''
        try:
            if os.path.exists(SRV_FILE_PATH):
                f = file(SRV_FILE_PATH)
                jobj = json.load(f)
                return jobj.get('portal')
            else:
                logger.error('can not get cluster portal url')
                return ''
        except Exception, e:
            logger.error('error when get portal url: %s' % repr(e))
            return ''
    
    def check_master_server(self):
        '''
            check whether the current server is master server
        '''
        return os.path.exists(MASTER_SERVER_FILE)

    def _get_accounts(self):
        logger.info("get all accounts start")
        accounts = []
        try:
            hosted_acc = HostedAccount()
            accounts = hosted_acc.get_airwatch_account_ids()
        except Exception, e:
            logger.error("get account from RS error %s " % repr(e))
        logger.info("get all accounts end")
        return accounts
        pass

    def _get_modify_admin(self, account):
        mails = []
        logger.info("get modify permission admins from account %d start" % account)
        try:
            hosted_user = HostedAccount(account)
            admins = hosted_user.get_admins()
            if isinstance(admins, list):
                if len(admins) > 0:
                    for admin in admins:
                        mail = self._check_permission(admin)
                        if mail:
                            mails.append(mail)
                else:
                    logger.error("no admin for the account %d" % account)
            else:
                mails.append(self._check_permission(admins))
        except Exception, e:
            logger.error("get modify permission admin error %s" % repr(e))
        logger.info("get modify permission admins from account %d end" % account)
        return mails
        pass

    def _check_permission(self, admin):
        mail = None
        try:
            if isinstance(admin["attributes"]["permissions"], list):
                permission = int(admin["attributes"]["permissions"][0])
            else:
                permission = int(admin["attributes"]["permissions"])
            if (permission & 2) == 2:
                if isinstance(admin["attributes"]["mail"], list):
                    mail = admin["attributes"]["mail"][0]
                else:
                    mail = admin["attributes"]["mail"]
        except Exception, e1:
            logger.info("get admin permission and mail fail %s " % repr(e1))
        return mail

    def detect_awsrv(self):
        accounts = self._get_accounts()
        if len(accounts) > 0:
            logger.info("account number is %d" % len(accounts))
            for account in accounts:
                account = int(account)
                logger.info("detect account %d access air watch service start" % account)
                try:
                    aw_base = AirwatchVPNProfile(account)
                    aw_base.detect_aw()
                    logger.info("account %d can access air watch service" % account)
                except MDMiHttpError, mex:
                    logger.error("detect air watch rest services error: %s " % repr(mex))
                    self._send_mail_toadmin(account, mex)
                except Exception, e:
                    logger.error("detect air watch rest services error: %s " % repr(e))
                logger.info("detect account %d access air watch service end" % account)
        pass

    def _send_mail_toadmin(self, account, mex):
        try:
            error_code = mex.args[0]
            error_reason = mex.args[1]
            if (error_code == 401) or (error_code == 403):
                logger.info("send mail to admin(account=%d) handle this error: %s, %s" % (account, error_code, error_reason))
                mails = self._get_modify_admin(account)
                logger.info("admins for account %d:" % account)
                logger.info(mails)
                if len(mails) > 0:
                    self._send_mail(mails, account)
                else:
                    logger.error("no admin need to mail")
            else:
                logger.info("other error, needn't to handle")
        except Exception, e:
            logger.error("send mail error %s" % repr(e))
        pass    
       
    def _send_mail(self, rcptto, account):
        logger.info("send mail start")
        hostedq = HostedTaskQueue()
        data = {}
        data["mailfrom"] = "bounce@websense.com"
        data["rcptto"] = rcptto

        portal_url = self._get_cluster_portal_url()
        data["substitutions"] = {
            "_displayfromname_": "Cloud Web Security Portal",
            "_portalurl_": portal_url
        } 
        data["template"] = self._get_template() 

        payload = json.dumps(data)
        payload_base64 = base64.encodestring(payload)
        hostedq.do_add(tqname='email', namespace='email', account=account, version=1, payload=payload_base64)
        logger.info("send mail end")
        pass

    def _get_template(self):
        email_obj = MailTemplate()
        content = email_obj.get_mail_template()
        return content
         

if __name__ == '__main__':
    logger.info('detect air watch service authentication information cronjob start...')
    try:
        detectaw = DetectAWService()
        logger.info('check whether current server is master')
        check_master = detectaw.check_master_server()
        if check_master:
            logger.info('current server is the master server')
            detectaw.detect_awsrv()
        else:
            logger.info('current server is not the master server')
    except Exception, e:
        logger.info('detect air watch rest service cronjob error %s' % repr(e))
    logger.info('detect air watch service authentication information cronjob end...')
