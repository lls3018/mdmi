#!/usr/bin/env python2.6
#encoding=utf-8

class AuthenticationFailureException(Exception):
    '''
    class AuthenticationFailureException
        Customized exception, this exception throws when authentication failed 

    Attributes:
        None
    '''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
