# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

import json
import base64
from time import time

from utils import logger
from utils.configure import MDMiConfigParser
from utils.configure import MDMI_USERCFG_FILE
from utils.configure import SERVICECONFIG_FILE
from utils.rest_access import RESTAccess
from utils.stringutils import get_admin_name_from_dn
from hosteddb.hosted_crypt import decrypt

from metanate import templates

class MRESTAccess(RESTAccess):
    """ IMPORTANT: If you use this class in multiple thread, 
        please create object in every thread,
        a session will be belongs to a thread,
        It can not share session in multiple thread.
        If you want share an object of this class in multiple thread,
        please be sure to create session and close session only once in a thread,
        all the threads can do 'ADD', 'REPLACE' or 'REMOVE' operations any times.

    """
    def __init__(self, account_id, host=None, port=443):
        if not host:
            cfgobj = MDMiConfigParser(cfgfile=MDMI_USERCFG_FILE, isjson=True)
            host = cfgobj.read('metanate_host').get('metanate_host')
        self.host = host
        self.port = port
        self.session_id = None
        self.directory_lookup_time = 0
        self.delta_calc_time = 0
        self.sync_time = 0
        self.commit_time = 0
        self.log_msg = ""
        self.account_id = account_id
        self.counts = {'ADD':0, 'REPLACE':0, 'REMOVE':0, 'RETRIEVE':0}

        conf = MDMiConfigParser(MDMI_USERCFG_FILE, isjson=True)
        info = conf.read()
        if isinstance(info, dict) and info.has_key('user') and info.has_key('metanate_password'):
            password = decrypt(info['metanate_password'])
            user = get_admin_name_from_dn(info['user'])
            self.authorization = ' '.join(['Basic', base64.b64encode(':'.join([user, password]))])
        else:
            self.authorization = ''

        super(self.__class__, self).__init__(host, port)

    def __del__(self):
        pass

    def do_access(self, resource, method_name='POST', data=None, headers=None):
        """request resource in specified HTTP method
        Parameters:
            resource: an absolute path which supplied by server.
            method_name: HTTP METHOD, can be 'GET', 'POST', 'PUT' or 'DELETE', the default is 'POST'
            data: the data should transfer to server.
            headers: HTTP headers, should in dict form.
        """
        boundary = templates.generate_boundary()
        http_headers = self._generate_headers(boundary)
        if headers:
            http_headers.update(headers)
        if data:
            body = self._generate_post_body(data, boundary)
        else:
            body = ""
            http_headers.pop('Content-Type')

        logger.info('metanate request body: %s', body)
        r = super(self.__class__, self).do_access(resource, method_name='POST', data=body, headers=http_headers)

        if r.code == 200:
            if not self.session_id:
                self.session_id = r.session_id
                logger.info('HTTP response header X-Schemus-Session is: %s', self.session_id)
            if r.content_type == "text/ldif":
                r.content = templates.parse_ldif(r.content)
            elif r.content == "application/json":
                r.content = json.loads(r.content)
        else:
            logger.error('metanate request: %s error occurred: %s: %s', resource, r.code, r.content)
            r.content = {'ErrorCode': r.code, 'Message': r.reason, 'Detail': r.content}

        return r

    def _process_ldif(self, action, ldif, count=1):
        headers = {'X-SYNC-ACCOUNT': self.account_id}
        r = self.do_access('/'.join(['/sync', action]), data=ldif, headers=headers)
        self.counts[action] += count

        return r

    def create_session(self, object_class, sync_source='MDM'):
        """create an metanate session for further use
        Parameters:
            object_class: 'Users' or 'Groups'
            sync_source: 'MDM' or 'Directory'
        """
        resource = '/sync/CREATESESSION'
        ldif = templates.generate_ldif('CREATESESSION', use_template=True, sync_source=sync_source, object_class=object_class)
        logger.info("create session POST data: %s", ldif)

        headers = {'X-SYNC-ACCOUNT': self.account_id}
        r = self.do_access(resource, data=ldif, headers=headers)
        return r

    def close_session(self):
        """close an metanate session, it is always called in the end of session.
        """
        if not self.session_id:
            return None

        resource = '/sync/CLOSESESSION'
        ldif = templates.generate_ldif('CLOSESESSION', use_template=True, additions=self.counts['ADD'],
                        deletions=self.counts['REMOVE'], directory_lookup_time=self.directory_lookup_time,
                        delta_calc_time=self.delta_calc_time, sync_time=self.sync_time,
                        commit_time=self.commit_time,
                        total_time=(self.directory_lookup_time + self.delta_calc_time
                                    + self.sync_time + self.commit_time),
                        log_msg=self.log_msg)

        logger.info("close session %s POST data: %s", self.session_id, ldif)

        r = self.do_access(resource, data=ldif)
        self.session_id = None
        return r

    def add(self, **kwargs):
        """add user or group to metanate
        Parameters:
            **kwargs: all items of a dict which should contain user or group info.
        """
        ldif = templates.generate_ldif('ADD', **kwargs)
        logger.info("add %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('ADD', ldif)

    def add_list(self, array):
        """add users or groups to metanate
        Parameters:
            array: a list contains dict, the dict should contains user or group info.
        """
        ldif = templates.generate_ldif_from_list('ADD', array)
        logger.info("add %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('ADD', ldif, len(array))

    def replace(self, **kwargs):
        """replace user or group to metanate
        Parameters:
            **kwargs: all items of a dict which should contain user or group info.
        """
        ldif = templates.generate_ldif('REPLACE', **kwargs)
        logger.info("replace %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('REPLACE', ldif)

    def replace_list(self, array):
        """replace users or groups to metanate
        Parameters:
            array: a list contains dict, the dict should contains user or group info.
        """
        ldif = templates.generate_ldif_from_list('REPLACE', array)
        logger.info("replace %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('REPLACE', ldif, len(array))

    def remove(self, **kwargs):
        """remove user or group to metanate
        Parameters:
            **kwargs: all items of a dict which should contain user or group info.
        """
        ldif = templates.generate_ldif('REMOVE', **kwargs)
        logger.info("remove %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('REMOVE', ldif)

    def remove_list(self, array):
        """remove users or groups to metanate
        Parameters:
            array: a list contains dict, the dict should contains user or group info.
        """
        ldif = templates.generate_ldif_from_list('REMOVE', array)
        logger.info("remove %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('REMOVE', ldif, len(array))

    def retrieve(self, **kwargs):
        """retrieve user or group to metanate
        Parameters:
            **kwargs: all items of a dict which should contain user or group info.
        """
        ldif = templates.generate_ldif('RETRIEVE', **kwargs)
        logger.info("retrieve %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('RETRIEVE', ldif)

    def retrieve_list(self, array):
        """retrieve users or groups to metanate
        Parameters:
            array: a list contains dict, the dict should contains user or group info.
        """
        ldif = templates.generate_ldif_from_list('RETRIEVE', array)
        logger.info("retrieve %s POST data: %s", self.session_id, ldif)
        return self._process_ldif('RETRIEVE', ldif, len(array))

    def commit(self):
        """commit a metanate session, it will be executed only once in one session
        """
        resource = '/sync/COMMIT'
        ldif = templates.generate_ldif('COMMIT')

        logger.info("commit %s POST data: %s", self.session_id, ldif)

        headers = {'X-SYNC-ACCOUNT': self.account_id}
        begin = time()
        r = self.do_access(resource, data=ldif, headers=headers)
        end = time()
        self.commit_time += (end - begin)
        return r

    def _generate_post_body(self, data, boundary):
        sub_headers = self._generate_sub_headers()
        body_header = "\r\n".join("%s: %s" % i for i in sub_headers.iteritems())
        body_header = body_header + "\r\n"

        if boundary:
            return "--{0}\r\n"\
                "{1}\r\n"\
                "{2}\r\n"\
                "--{0}--".format(boundary, body_header, data)
        else:
            return ""

    def _generate_headers(self, boundary):
        # get metanate username and password from configure file(mes.json)
        http_headers = {
            # TODO hard code the authorization - enrollment-service:Qaqa1234
            'Authorization': self.authorization,
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
            'Accept': '*/*',
        }
        
        if self.session_id:
            http_headers['X-Schemus-Session'] = self.session_id

        return http_headers

    def _generate_sub_headers(self):
        sub_headers = {
            'Content-Disposition': 'form-data; name="request"; filename="request"',
            'Content-Type': 'text/ldif',
        }

        return sub_headers
