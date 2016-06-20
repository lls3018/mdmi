'''
Created on Aug 7, 2013

@author: harlan
'''

class CommonHandler(object):
    '''
    class CommonHandler
        This class is a template method class which provide three hook method(pre_process, process and post_process) so that
        subclasses can implement these hook methods according to their specific requirements

    Attributes:
        None
    '''

    def __init__(self, dict):
        self.dict = dict

    def handle(self):
        self.pre_process()
        self.process()
        self.post_process()

    def pre_process(self):
        pass

    def process(self):
        pass

    def post_process(self):
        pass
