'''
Created on Aug 8, 2013

@author: harlan
'''

import json

class Request(object):
    '''
    class Request
        Model class represents Request object

    Attributes:
        None
    '''

    def __init__(self, request_id=None, data=None, account_id=None):
        self.request_id = request_id
        self.data = data
        self.account_id = account_id
