class MDMiBaseError(Exception):
    """ 
        Base exception implementation
    """
    def __init__(self, code, reason, content=''):
        super(MDMiBaseError, self).__init__(code, reason, content)

    def to_json(self):
        # TODO
        pass
        #return '"ErrorCode": "{0}", "Reason": "{1}", "Message": "{2}"'.format(*self.args).join(['{', '}'])

    def to_xml(self):
        # TODO
        pass

    def __str__(self):
        return "ErrorCode: {0} - Message: {1}: {2}".format(*self.args)

class MDMiHttpError(MDMiBaseError):
    """ 
        Exception of http error.
    """
    pass

class MDMiInvalidParameterError(MDMiBaseError):
    """ 
        Exception of invalid parameter error.
    """
    pass

class MDMiTaskHandleFatalError(Exception):
    """ 
        Exception of fatal error.
    Fatal error when handling tasks with plugin, the task should be thrown to error queue.
    """
    pass

class MDMiTaskHandleFailWarning(Exception):
    """ 
        Exception of warning.
    Fail warning when handling tasks with plugin, the task should be thrown to retry queue.
    """
    pass

