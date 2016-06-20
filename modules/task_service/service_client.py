# -*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: client.py
# Purpose:
# Creation Date: 17-12-2013
# Last Modified: Wed Feb 19 00:43:22 2014
# Created by:
#---------------------------------------------------
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
import socket
import json

from utils import logger

def send_socket_request(data):
    logger.info('To process socket request. data: ' + json.dumps(data))
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        command = ''
        content = ''
        
        sock.connect("/var/run/mdmi/task_service.sock")
        if 'sync_type' not in data or data['sync_type'] == 'metanate':
            account = data['account']
            trans_type = data['trans_type']
            sync_source = data['sync_source']
            content = json.dumps(data)
            command = "PUT /metanate HTTP/1.1\r\nAccount:%s\r\nSync:%s\r\nSyncSource:%s\r\nContent-Length:%s\r\n\r\n" \
                % (account, trans_type, sync_source, len(content))
        elif data['sync_type'] == 'hybrid':
            account = data['account']
            content = json.dumps(data)
            command = "PUT /hybrid HTTP/1.1\r\nAccount:%s\r\nSyncType:hybrid\r\nContent-Length:%d\r\n\r\n" \
                % (account, len(content))
        sock.send(command)
        sock.send(content)
        response = sock.recv(1024)
        logger.info('response content: %s' % response)
        status = get_response_status(response)
        return (status >= 200 and status < 300)
    # except Exception, e:
    #    logger.error(e)
    #    return False
    finally:
        sock.close()

def get_service_status():
    logger.info('Get service status request.')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect("/var/run/mdmi/task_service.sock")
        command = "GET /status HTTP/1.1\r\n\r\n"
        sock.send(command)
        response = sock.recv(1024)
        logger.info('response content: %s' % response)
        # body = get_response_body(response)
        return response
    # except Exception, e:
    #    logger.error(e)
    #    return False
    finally:
        sock.close()

def get_response_status(response):
   first_line = response.splitlines()[0]
   bits = first_line.split()
   return int(bits[1])

if __name__ == '__main__':
    print send_socket_request({'account': 86, 'trans_type': 'Users',
        'sync_source': 'MDM', 'func': 'add_user', 'parameters':{'foo': 'blahblahblah'}})
