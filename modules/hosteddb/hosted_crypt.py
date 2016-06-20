# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from urllib import urlencode
from hosteddb.hosted_access import HostedAccess

def encrypt(phrase, version=1):
    '''
    Encrypt phrases.
    
    Params:
        phrase : The specifc string would be encrypted.
        version : Version of the resource.

    Return:
        The encrypted string.

    Notes:
        This is an operation throw network, the caller should catch the exceptions if failed.
    '''
    rest = HostedAccess()
    resource = "/cr/v-%d/encrypt?%s" % (version, urlencode({"p": phrase}))
    result = rest.do_access(resource, method_name="GET")

    if result.code == 200 and result.content_length > 0:
        return result.content
    # return orginal string if failed.
    return phrase

def decrypt(phrase, version=1):
    '''
    Decrypt phrases.
    
    Params:
        phrase : The specifc string would be decrypted.
        version : Version of the resource.

    Return:
        The decrypted string.

    Notes:
        This is an operation throw network, the caller should catch the exceptions if failed.
    '''
    rest = HostedAccess()
    resource = "/cr/v-%d/decrypt?%s" % (version, urlencode({"p": phrase}))
    result = rest.do_access(resource, method_name="GET")

    if result.code == 200 and result.content_length > 0:
        return result.content

    return phrase

