# a small python like logger
import sys
import ETimer

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
COLORS = {
    WARNING: YELLOW,
    INFO: WHITE,
    DEBUG: BLUE,
    CRITICAL: YELLOW,
    ERROR: RED
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"

class _Logging:

    def __init__(self):
        self.loglevel = DEBUG
        self.use_colors = False

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
            col_start = COLOR_SEQ % (30 + COLORS[loglevel]) if self.use_colors else ''
            col_end = RESET_SEQ if self.use_colors else ''

            # Raise an exception to get to the current stack trace. This does not look legit but it is the same
            # way as Traceback does in its extract_stack function.
            f = sys._getframe().f_back.f_back
            co = f.f_code
            filename = '{}:{}'.format(co.co_filename[co.co_filename.rfind('/') + 1:], f.f_lineno)
            sys.stdout.write('{0}{1} {2} {3}{4}\r\n'.format(col_start, ETimer.time(), filename, str(msg), col_end))

log = _Logging()
    
    

    


