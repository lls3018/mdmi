#-*- coding: utf-8 -*-
from httplib import HTTPSConnection
from urllib import urlencode
import json

import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger
from utils.error import MDMiHttpError

class RestResult(object):
    def __init__(self, code, reason="OK"):
        self.code = code
        self.reason = reason
    def __str__(self):
        base = 'Code: {0} - Message: {1}'.format(self.code, self.reason)
        try:
            content = self.content.strip()
            if content:
                return " - ".join([base, content])
            else:
                return base
        except:
            return base

class RESTConnection(HTTPSConnection, object):
    def __init__(self, host, port=443, use_secure=True, timeout=50):
        super(RESTConnection, self).__init__(host, port, timeout=timeout)
        self.opened = False

class RESTAccess(object):
    def __init__(self, host, port=443, connection=None):
        self.host = host
        self.port = port
        if connection:
            self.connection = connection
        else:
            self.connection = RESTConnection(host, port)
            self.self_conn = True
            logger.debug("Create connection with host %s and port %d", host, port)

    def __del__(self):
        if self.connection and self.self_conn:
            logger.debug('Close connection with host %s and port %d', self.host, self.port)
            self.connection.close()

    def do_access(self, resource, method_name="GET", data=None, headers=None):
        """request resource in specified HTTP method
        Parameters:
            resource: an absolute path which supplied by server.
            method_name: HTTP METHOD, can be 'GET', 'POST', 'PUT' or 'DELETE', the default is 'POST'
            data: the data should transfer to server.
            headers: HTTP headers, should in dict form.
        """
        headers = self.generate_http_headers(headers)
        logger.info('HTTP request method is: %s, headers: %s, and data is %s', method_name, headers, data)
        if method_name == "GET" and data:
            param = urlencode(data)
            resource = '?'.join([resource, param])
            logger.info("HTTP request resource is: %s", resource)
            #try:
            self.connection.request(method_name, resource, headers=headers)
            response = self.connection.getresponse()
            #except Exception as e:
            #    logger.error('request %s error: %s', resource, e)
            #    response = e
        else:
            if method_name == "POST" and not data:
                headers['Content-Length'] = 0
            logger.info("HTTP request resource is: %s", resource)
            #try:
            if isinstance(data, dict):
                data = json.dumps(data)
            self.connection.request(method_name, resource, data, headers)
            response = self.connection.getresponse()
            #except Exception as e:
            #    logger.error('request %s error: %s', resource, e)
            #    response = e

        result = self.parse_result(response)
        # this if-brance can make the passcode not appear in log file
        if not resource.startswith('/cr/'):
            logger.info("HTTP response from %s code:%s content_type:%s content_length:%s content:%s", self.host, result.code, result.content_type, result.content_length, result.content)
        else:
            logger.info("HTTP response from %s code:%s", self.host, result.code)
        if result.code < 200 or result.code >= 300:
            raise MDMiHttpError(result.code, result.reason, result.content)

        return result

    def generate_http_headers(self, headers):
        http_headers = {
            'Accept': 'application/json',
            'Connection' : 'Keep-Alive',
            #'Host': self.host,
        }

        if self.host:
            http_headers['Host'] = self.host

        if headers:
            http_headers.update(headers)

        return http_headers

    def parse_result(self, res):
        retcode = res.status
        result = RestResult(retcode, res.reason)
        content_type = res.getheader('Content-Type')
        if content_type and content_type.find(";"):
            types = content_type.split(";")
            for t in types:
                t = t.strip()
                if t.startswith('charset'):
                    result.charset = t
                else: result.content_type = t
        else: result.content_type = content_type
        content_length = res.getheader('Content_Length')
        if content_length:
            result.content_length = int(content_length)
            result.content = res.read()
            while len(result.content) < result.content_length:
                result.content += res.read()
        else:
            result.content = res.read()
            result.content_length = len(result.content)

        last_modified = res.getheader('Last-Modified')
        if last_modified:
            logger.info('HTTP response from %s, Last-Modified header is: %s', self.host, last_modified)
            result.last_modified = last_modified

        session_id = res.getheader('X-Schemus-Session')
        if session_id:
            logger.info('HTTP response from %s, X-Schemus-Session header is: %s', self.host, session_id)
            result.session_id = session_id

        return result
