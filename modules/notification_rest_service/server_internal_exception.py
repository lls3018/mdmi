#!/usr/bin/env python2.6
# encoding=utf-8

class ServerInternalException(Exception):
    '''
    class ServerInternalException
        Customized exception, this exception throws when an issue is caused by Hosted Cluster Inside

    Attributes:
        None
    '''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
