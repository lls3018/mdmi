#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: request_dispatcher.py
# Purpose:
# Creation Date: 13-02-2014
# Last Modified: Fri Feb 28 18:29:08 2014
# Created by:
#---------------------------------------------------

import re
import sys

from datetime import datetime

if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger

from request_handler import HttpRequestHandlerFactory

HEADER_COMPLETE = 0
HEADER_NOT_COMPLETE = 1
HEADER_ERROR = -1

HTTP_STATUS = {
    200: "OK",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    408: "Request Timeout",
    411: "Length Required",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable",
    505: "HTTP Version Not Supported",
}

class BaseRequestDispatcher(object):
    def __init__(self):
        self._body = ''
        self._header = None
        #self._body_length = 0
        #self._content_length = 0

        self._response_code = 0
        self._response_body = ""
        self._response_header = {}

    def is_header_empty(self, data):
        return not self._header

    def is_body_empty(self):
        return not self._body;

    def is_nothing_received(self):
        # the self._header contains 'content-length' at least, if data has already parsed.
        return not self._body and not self._header 

    def is_body_complete(self):
        return self._header and (len(self._body) >= self._header['content-length'])

    def is_already_parsed(self):
        # the self._header contains 'content-length' at least, if data has already parsed.
        return self._header

    def append_data(self, data):
        self._body += data

    def do_parse(self):
        pass

    def do_handle(self):
        pass

    def generate_response(self):
        pass

class HttpRequestDispatcher(BaseRequestDispatcher):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.delimiter = "\r\n\r\n" 
        self._response_code = 200
        self._response_header = {
                "Date": "",
                "Server": "User and Group plugin service",
                "Content-Length": 0,
                }
        # self.__metanate_cache = task_cache
        # self.__status = status

    def has_complete_header(self, data):
        return self.delimiter in data

    def do_parse(self):
        header_end = self._body.find(self.delimiter)
        if header_end == -1:
            return HEADER_NOT_COMPLETE  # not receive complete header yet.

        header_end += len(self.delimiter)
        header = self._body[:header_end]

        # Pop the first line for further processing
        pos = header.find("\r\n")
        request_lines = header[:pos].split()
        header_lines = header[pos + 2:]
        if len(request_lines) != 3:
            self._response_code = 400
            self._response_body = 'the first line of request must be in form of "<method> <path> HTTP/1.1"'
            return HEADER_ERROR

        if request_lines[2].upper() != 'HTTP/1.1':
            self._response_code = 505
            self._response_body = 'The request version must be HTTP/1.1'
            return HEADER_ERROR

        self._method = request_lines[0]
        self._path = request_lines[1]

        self._header = dict([(h[0].lower(), h[1]) for h in re.findall(r"(?P<name>.*?):[ \t]*(?P<value>.*?)\r\n", header_lines)])
        if not self._header.has_key('content-length'):
            self._header['content-length'] = 0
        else:
            self._header['content-length'] = int(self._header['content-length'])
        logger.debug('request line: %s', request_lines)
        logger.debug('request header: %s', self._header)

        self._body = self._body[header_end:]
        logger.debug('request body: %s', self._body)

        return HEADER_COMPLETE

    def do_handle(self):
        try:
            clazz = HttpRequestHandlerFactory.get_request_handler(self._method, self._path)
            if clazz:
                handler = clazz(self._header, self._body)
                handler.do_handle()
                self._response_code = handler.get_response_code()
                self._response_body = handler.get_response_body()
                self._response_header.update(handler.get_response_header())
            else:
                self._response_code = 400
                self._response_body = 'the service do not support your request in method: %s and path: %s' % (self._method, self._path)
        except KeyError as e:
            logger.error('save client data to cache failed: %s', e)
            self._response_code = 400
            self._response_body = 'The header parameters must contains "Account", "Sync", "SyncSource"'
        except Exception as e:
            logger.error('save client data to cache failed: %s', e)
            self._response_code = 500
            self._response_body = 'server error in saving client data into cache'

    def generate_response(self):
        if not self.is_body_complete():
            self._response_code = 400
            self._response_body = 'please send http request to me'

        status_line = "HTTP/1.1 %s %s" % (self._response_code, HTTP_STATUS.get(self._response_code, "Bad Request"))
        self._response_header['Content-Length'] = len(self._response_body)
        self._response_header['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        response_headers = [": ".join([str(key), str(value)]) for key, value in self._response_header.iteritems()]
        response_headers.insert(0, status_line)

        response_header = "\r\n".join(response_headers)

        return "\r\n\r\n".join([response_header, self._response_body])
