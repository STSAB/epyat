# a small python like logger
import sys
DEBUG=0
INFO=1
WARNING=2
ERROR=3
CRITICAL=4


class _Logging:

    def __init__(self):
        self.loglevel = DEBUG
    def setloglevel(self,loglevel):
        self.loglevel=loglevel
    #Logs a message with level DEBUG on this logger
    def debug(self,msg):
        self._writelog(msg,INFO)    

    #Logs a message with level INFO on this logger
    def info(self,msg):
        self._writelog(msg,INFO)
    
    #Logs a message with level WARNING on this logger
    def warning(self,msg):
        self._writelog(msg,WARNING)
    
    #Logs a message with level ERROR on this logger
    def error(self,msg):
        self._writelog(msg,ERROR)
    
    
    #Logs a message with level CRITICAL on this logger
    def critical(self,msg):
        self._writelog(msg,CRITICAL)
        
    def _writelog(self,msg,loglevel):
        if loglevel >= self.loglevel:
            sys.stdout.write(str(msg) + "\r\n")
            #print msg + "\r\n"
            

            
log=_Logging() 
log.debug("LOG DEBUG")
        
    
    

    


