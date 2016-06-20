#-*- coding: utf-8 -*-

#import os
from ConfigParser import SafeConfigParser
import logging
from logging.handlers import SysLogHandler  #, TimedRotatingFileHandler

class _MDMiLogger(logging.Logger, object):
    def __init__(self, name, level=logging.DEBUG):
        super(_MDMiLogger, self).__init__(name, level)

    def convert(self, args):
        if isinstance(args, tuple):
            new_args = []
            for a in args:
                if isinstance(a, unicode):
                    new_args.append(a.encode('utf-8'))
                elif isinstance(a, tuple):
                    new_args.append(self.convert(a))
                else:
                    new_args.append(a)

            return tuple(new_args)
        else:
            return args

    def makeRecord(self, *args, **kwargs):
        return super(_MDMiLogger, self).makeRecord(*self.convert(args), **kwargs)

class _MDMiLogHandler(SysLogHandler):
    def emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the syslog server. If
        exception information is present, it is NOT sent to the server.
        """
        msg = self.format(record)
        """
        We need to convert record level to lowercase, maybe this will
        change in the future.
        """
        msg = self.log_format_string % (
            self.encodePriority(self.facility,
                                self.mapPriority(record.levelname)),
                                msg)
        # Treat unicode messages as required by RFC 5424
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        msg = msg[:2048] # syslog can only write 2048 bytes once a time
        try:
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except Exception:
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            else:
                self.socket.sendto(msg, self.address)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def _has_handler(handlers, cls):
    for h in handlers:
        if isinstance(h, cls):
            return True

    return False

logging.setLoggerClass(_MDMiLogger)
logger = logging.getLogger('MDMi')

if not _has_handler(logger.handlers, _MDMiLogHandler):
    #adapter = MDMiAdapter(logger, {'encode': 'utf-8'})
    #logger = logging.getLogger(__name__)
    #debug_formatter = logging.Formatter('%(asctime)s %(name)s[%(process)d]: %(levelname)s %(filename)s[%(lineno)d] - %(message)s')
    #_formatter = logging.Formatter('%(name)s[%(process)d]: %(levelname)s %(filename)s[%(lineno)d] - %(message)s')

    # syslog handler
    _handler = _MDMiLogHandler('/dev/log', SysLogHandler.LOG_LOCAL6)
    #handler.qualname='MDMIntegration'
    #handler.propagate=1
    #_handler.setFormatter(_formatter)

    logger.addHandler(_handler)

    # get log level from configure file
    config = SafeConfigParser()
    try:
        config.read('/opt/mdmi/etc/mdmi.conf')
        level = 'DEBUG'
        format = '%(name)s[%(process)d]: %(levelname)s %(filename)s[%(lineno)d] - %(message)s'
        if config.has_section('logger'):
            if config.has_option('logger', 'level'):
                level = config.get('logger', 'level').upper()
            if config.has_option('logger', 'format'):
                format = config.get('logger', 'format')
    except Exception as e:
        logger.setLevel(logging.DEBUG)
        _formatter = logging.Formatter('%(name)s[%(process)d]: %(levelname)s %(filename)s[%(lineno)d] - %(message)s')
        _handler.setFormatter(_formatter)
    else:
        if level in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
            logger.setLevel(eval('.'.join(['logging', level])))
        else:
            logger.setLevel(logging.DEBUG)

        try:
            _formatter = logging.Formatter(format)
            _handler.setFormatter(_formatter)
        except Exception as e:
            _formatter = logging.Formatter('%(name)s[%(process)d]: %(levelname)s %(filename)s[%(lineno)d] - %(message)s')
            _handler.setFormatter(_formatter)

        # set additional log just for mdmi
        #if additional and os.access(additional, os.W_OK):
        #    # file debug handler
        #    debug_handler = TimedRotatingFileHandler(additional, 'D', 1, backupCount = 7)
        #    debug_handler.setFormatter(debug_formatter)
        #    logger.addHandler(debug_handler)
    finally:
        del config
