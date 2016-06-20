# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

import json
import base64
import urllib

from hosteddb.hosted_account import HostedAccount
from hosteddb.hosted_crypt import decrypt

from utils import logger

from airwatch.awrest_access import AirwatchRESTAccess

class AirwatchBase(object):
    def __init__(self, account_id, callback_url=None):
        self.account_id = account_id
        self.aw_headers = self._get_config(account_id)
        if callback_url:
            (self.aw_headers['Host'], self.aw_headers['Port']) = self.parse_callback_url(callback_url)
        self.rest = AirwatchRESTAccess(self.aw_headers['Host'], self.aw_headers['Port'])

    def __del__(self):
        try:
            if self.rest:
                del self.rest
        except Exception as e:
            logger.warning("error when del obj")
            raise Exception(e)

    def _parse_result(self, data):
        if data.content_length > 0:
            if data.content_type == "application/json":
                return json.loads(data.content)

        return data.content

    def parse_param(self, data):
        if isinstance(data, dict):
            return json.dumps(data)
        
        return data

    def convert_to_xml(self, data):
        format = ['<BulkInput xmlns="http://www.air-watch.com/servicemodel/resources"><BulkValues>',
                  '</BulkValues></BulkInput>']

        if isinstance(data, (list, tuple)):
            value = '<Value>%s</Value>' * len(data) % tuple(data)
            return value.join(format)
        else:
            return None

    def parse_callback_url(self, callback_url):
        proto, rest = urllib.splittype(callback_url)
        host, rest = urllib.splithost(rest)
        host, port = urllib.splitport(host)
        if not port:
            port = 443
        return host, port

    def _strip_hostname(self, url):
        while url and isinstance(url, list):
            url = url[0]

        # strip / and whitespace from url
        hostname = url.strip('/ \t\r\n')

        # TODO other protocol should be also supported?
        protocols = ('http://', 'https://')
        for p in protocols:
            if hostname.startswith(p):
                hostname = hostname[len(p):]
                break

        return hostname

    def _strip_value(self, value, to_strip=True):
        while value and isinstance(value, (list, tuple, set)):
            value = value[0]

        if to_strip:
            return value.strip(" \t\r\n")
        else:
            return value

    def _get_config(self, account_id):
        # TODO the default value should not specific
        credential = {
            'Host': '',
            'Port': 443,
            'aw-tenant-code': '',
            'Authorization': '',
            'Content-Type': 'application/json',
        }

        account = HostedAccount(account_id)
        # get mdmUrl, mdmUsername, mdmPassword, mdmToken from hosteddb
        c = account.get_airwatch_credential()

        try:
            credential['Host'] = self._strip_hostname(c['mdmUrl'])
            username = self._strip_value(c['mdmUsername'])
            # the airwatch password in hosted was encrypted.
            password = decrypt(self._strip_value(c['mdmPassword'], False))
            credential['Authorization'] = " ".join(['Basic', base64.b64encode(':'.join([username, password]))])
            credential['aw-tenant-code'] = self._strip_value(c['mdmToken'])
        except Exception as e:
            logger.warning('Error when getting airwatch credential: %s', e)
            raise Exception(e)

        return credential
