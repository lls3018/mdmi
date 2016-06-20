#!/usr/bin/python

import sys
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
import os
import json
import hmac
import base64
import binascii
from utils import logger
from hosteddb.hosted_crypt import decrypt
from hosteddb.hosted_user import HostedUser
from notification_rest_service.authentication_failure_exception import AuthenticationFailureException

def check_password(environ, user, password):
    '''
    Authentication incoming request
    :param environ: A object passed by mod_wsgi
    :param user: User section in Basic Authentication
    :param password: Password section in Basic Authentication
    
    Notes: Do not change this function name.
    '''
    try:
        if not user or not password:
            raise AuthenticationFailureException("Email or Password is None!")

        logger.info('Notification REST Service - Start off basic authentication')
        logger.info('Notification REST Service - user: %s', user)
        admin_user = dict()
        # The superclass of HostedUser needs accountId to initial object
        admin_user = HostedUser(1).get_admin_by_cn(user + " (admin)")

        basic_auth = authenticate_admin(admin_user["dn"], password)
        encrypt_account = authenticate_encrypted_string(admin_user['attributes']['account'], environ['REQUEST_URI'])

        os.environ['hosted_account'] = admin_user['attributes']['account']
        logger.info('Notification REST Service - Authentication: Basic auth: %s, Encrypt account: %s', basic_auth, encrypt_account)
        return basic_auth & encrypt_account
    except Exception, e:
        logger.error('Notification REST Service - Authentication Failure: %s', e)
        return False

def authenticate_encrypted_string(hosted_account, url):
    encrypted_account = url.split('/')[2].rstrip("%20")
    plain_account = decrypt(encrypted_account)
    account = json.loads(plain_account)['accountid']

    return account == hosted_account

def authenticate_admin(dn, password):
    encoded_password = generate_hmac(password)
    credential = dn + ":" + encoded_password
    logger.debug("Notification REST Service - credential info: %s", credential)
    base64_encoded = base64.b64encode(credential)
    return HostedUser(1).auth_admin(base64_encoded)

def generate_hmac(password):
    salt = "opensaysme"
    hashed = hmac.new(salt, password.strip())
    return binascii.b2a_base64(hashed.digest())[:-1].rstrip("=").replace("\n", "")
