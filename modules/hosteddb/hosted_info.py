#!/usr/bin/env python2.6
# encoding=utf-8

import json
import sys
import os
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from hosted_access import HostedAccess
from utils import logger

def hosted_get_pacfileurl(account=1, version=1):
    '''
    Get Pac file URL from hosted RS.

    Params:
        account: Account ID.
        version: Version of the resource, default value 1.

    Return:
        Pac file URL
        Exception message
    '''
    access_obj = HostedAccess()
    filter_rule = {"filter" : "objectclass=hostedwebpolicy"}
    resource = '/rs/v-%d/account-%d/search' % (int(version), int(account))
    result = access_obj.do_access(resource, 'GET', filter_rule)
    if result.code == 200:
        return result.content
    else:
        return ''
    pass


def hosted_get_pacfileurl_by_email(account, email):
    '''
    Get Pac file URL from hosted RS.

    Params:
        account: Account ID.
        email: user email.

    Return:
        Pac file URL
        Exception message
    '''
    access_obj = HostedAccess()
    filter_rule = '{"base":"account=%d","filter":"(&(objectClass=hostedUser)(mail=%s))"}' % (int(account), email)
    resource = '/rs/v-1/search'
    result = access_obj.do_access(resource, 'POST', filter_rule)
    if result.code == 200:
        return result.content
    else:
        return ''
    pass

def hosted_get_customer_account(account=1):
    '''
    Get Websense customer account from hosted RS.

    Params:
        account: Account ID.

    Return:
        Websense customer account info
        Exception message
    '''
    access_obj = HostedAccess()
    filter_rule = '{"base" : "account=%d", "filter" : "(objectclass=websenseCustomerAccount)"}' % int(account)
    resource = '/rs/v-1/search'
    result = access_obj.do_access(resource, 'POST', filter_rule)
    if result.code == 200:
        return result.content
    else:
        return ''

def hosted_replace_rs_attr(key=None, value=None, account=1):
    '''
    Replace RS attribute.

    Params:
        key: attribute name
        value: attribute value
        account: Account ID.

    Return:
        Websense customer account info
        Exception message
    '''
    access_obj = HostedAccess()
    filter_rule = '{"method":"modify","params":[{"attribute":"%s", "type":"replace", "values":["%s"]}]}' % (key, value)
    resource = '/rs/v-1/account-%d' % int(account)
    result = access_obj.do_access(resource, 'POST', filter_rule)
    if result.code == 200:
        return True
    else:
        return False
