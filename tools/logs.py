"""
    configures logger

    Usage:
        from tools.logs import log, logfile

        # log a message
        log.info("hello")

        # clear logfile
        with open(logfile, 'w'):
            pass
"""
import logging
import os
import sys

logfile = None

class LoggerWriter:
    """ redirects a stream such as stderr/stdout to log file """
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
 
    def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

def _getLog(name=None):
    """ returns a logger with defaults:
            format for log messages
            log directed to console and log file
            logfile is in current.request.folder OR in current directory
            default level is DEBUG
    """
    global logfile

    # configure format including line number to trace message
    if name in ("STDOUT", "STDERR"):
        formatter = logging.Formatter('[%(name)s:%(levelname)s]:%(message)s')
    else:
        formatter = logging.Formatter('[%(name)s:%(levelname)s]:%(message)s\n(%(pathname)s\%(lineno)s, time=%(asctime)s)\n','%H:%M')

    # configure streamhandler
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(formatter)

    # configure filehandler
    try:
        # for web2py application
        from gluon import current
        directory = current.request.folder
        if not name:
            name = current.request.application
    except:
        directory = os.getcwd()
    logfile = os.path.join(directory, "log.txt")
    filehandler=logging.FileHandler(logfile)
    filehandler.setFormatter(formatter)

    # configure logger
    log = logging.getLogger(name)
    log.propagate = 0
    log.handlers = []
    log.addHandler(streamhandler)
    log.addHandler(filehandler)
    log.setLevel(logging.DEBUG)

    return log

log = _getLog()

# configure std and err tools.logs
stdlog = _getLog("STDOUT")
errlog = _getLog("STDERR")
sys.stdout = LoggerWriter(stdlog, logging.INFO)
sys.stderr = LoggerWriter(errlog, logging.ERROR)