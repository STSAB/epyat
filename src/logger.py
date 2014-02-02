# a small python like logger
import sys
import time
import os

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4


class _Logging:

    def __init__(self):
        self.loglevel = DEBUG

    def setloglevel(self, loglevel):
        self.loglevel = loglevel

    #Logs a message with level DEBUG on this logger
    def debug(self, msg):
        self._writelog(msg, INFO)

    #Logs a message with level INFO on this logger
    def info(self, msg):
        self._writelog(msg, INFO)

    #Logs a message with level WARNING on this logger
    def warning(self, msg):
        self._writelog(msg, WARNING)

    #Logs a message with level ERROR on this logger
    def error(self, msg):
        self._writelog(msg, ERROR)

    #Logs a message with level CRITICAL on this logger
    def critical(self, msg):
        self._writelog(msg, CRITICAL)

    def _writelog(self, msg, loglevel):
        if loglevel >= self.loglevel:
            # Raise an exception to get to the current stack trace. This does not look legit but it is the same
            # way as Traceback does in its extract_stack function.
            f = sys._getframe().f_back.f_back
            co = f.f_code
            filename = '%s:%i' % (os.path.basename(co.co_filename), f.f_lineno)
            sys.stdout.write('%f %s %s\r\n' % (time.time(), filename, str(msg)))

log = _Logging()
    
    

    


