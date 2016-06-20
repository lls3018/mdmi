#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: request_handler.py
# Purpose:
# Creation Date: 06-01-2014
# Last Modified: Fri Feb 14 00:23:08 2014
# Created by:
#---------------------------------------------------

import sys

if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger

HANDLE_COMPLETE = 0
HANDLE_NOT_COMPLETE = 1
HANDLE_ERROR = -1

class HttpRequestHandler(object):
    def __init__(self, header, body):
        self._header = header
        self._body = body
        self._response_code = 200
        self._response_body = ''
        self._response_header = {}

    def do_handle(self):
        pass

    def get_response_code(self):
        return self._response_code

    def get_response_body(self):
        return self._response_body

    def get_response_header(self):
        return self._response_header

from service_variables import g_task_cache

class MetanateRequestHandler(HttpRequestHandler):
    def do_handle(self):
        if not self._header:
            logger.error('metanate task request header is null')
            self._response_code = 400
            self._response_body = 'The header parameters must contains "Account", "Sync", "SyncSource", "Content-Length"'

            return HANDLE_ERROR

        if not 'account' in self._header or not 'sync' in self._header \
           or not 'syncsource' in self._header or not 'content-length' in self._header:
            logger.error('the metanate request header must contains "Account", "Sync" and "Content-Length"')
            logger.error('the request data from client is invalid')
            self._response_code = 400
            self._response_body = 'The header parameters must contains "Account", "Sync", "SyncSource", "Content-Length"'
            
            return HANDLE_ERROR

        g_task_cache.put_data(self._body)
        self._response_code = 200
        self._response_body = ''

        return HANDLE_COMPLETE
    
class HybridRequestHandler(HttpRequestHandler):
    def do_handle(self):
        if not self._header :
            logger.error('hybrid task request header is null')
            self._response_code = 400
            self._response_body = 'The header parameters must contains "SyncType", "Account", "Content-Length"'

            return HANDLE_ERROR

        if not 'account' in self._header or not 'synctype' in self._header:
            logger.error('the hybrid request header must contains "SyncType", "Account", "Content-Length"')
            self._response_code = 400
            self._response_body = 'The header parameters must contains "SyncType", "Account", "Content-Length"'

        g_task_cache.put_data(self._body)
        self._response_code = 200
        self._response_body = ''

        return HANDLE_COMPLETE

from service_variables import g_service_status

class StatusRequestHandler(HttpRequestHandler):
    def do_handle(self):
        self._response_code = 200
        self._response_body = g_service_status.get_json_content()
        self._response_header['Content-Type'] = "application/json"

        return HANDLE_COMPLETE

request_handler_classes = {
        'PUT /metanate': MetanateRequestHandler,
        'PUT /hybrid': HybridRequestHandler,
        'GET /status': StatusRequestHandler,
    }

class HttpRequestHandlerFactory:
    @classmethod
    def get_request_handler(cls, method, path):
        global request_handler_classes
        clazz = request_handler_classes.get(' '.join([method.upper(), path]))
        return clazz
