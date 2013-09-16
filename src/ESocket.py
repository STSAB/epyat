import EInterface
import MOD
import MDM
import EBuffer
from logger import log
import EGprs

BUFFSIZE = 1024
NEWLINE="\r\n"

class ESocket:
    def __init__(self, connId, host, port):
        self.connId = connId
        self.host = host
        self.port = port
        log.debug("Create ESocket:%s:%s,%s" % (self.host, self.port, self.connId))
        self.close()



    def connected(self):
        res=EInterface.sendCommand("AT#CGPADDR=%s" % self.connId)
        return res

    def send(self, data):
        #TODO everything
        #move out the command logic and handel that in the EInterface instead of here
        #if socket is closed open it and try to activate
        if not self.status():
            log.debug("Socket is closed, start over and try to open")
            i=0
            while 1:
                try:

                    if not EGprs.is_active_ctx(self.connId):
                        EGprs.activate_ctx(self.connId)

                    #create the socket, dial out using command mode
                    res = EInterface.sendCommand('AT#SD=%s,0,%s,"%s",0,0,1' % (self.connId, self.port, self.host))
                    break
                except EInterface.TimeoutException:
                    i=i+1
                    log.debug("Socket start send: timeout exception")
                    #if we have done this for a while raise and error instead
                    raise  EInterface.TimeoutException("Timeout reached while reading from the AT interface")
                    
        #send data in 1024 chunk's
        length = len(data)


        #log.debug(EInterface.sendCommand("AT#SI"))
        log.debug("Sending %s bytes" % length)
        for step in range((length / BUFFSIZE) + 1):
            start = step * BUFFSIZE
            stop = (step + 1) * BUFFSIZE
            if stop > length:
                stop = length
            datapart = data[start:stop] + chr(26)

            MDM.send("AT#SSEND=%s%s" % (self.connId,NEWLINE),5)

            timeout = MOD.secCounter() + 20
            while MOD.secCounter() < timeout:

                res=EBuffer.receive(1)
                if ">" in res:
                    MDM.send(datapart,5)
                    res=EBuffer.receive(1)
                    log.debug("SSEND terminated with" + str(res))
                    break
                else:
                    log.debug("SSEND terminated with" + str(res))
                    self.close()
            else:
                self.close()









    def receive(self):
        #read all up from the buffer, will waste ongoing commands
        res=EBuffer.receive(1)
        res=EBuffer.getSring(1,BUFFSIZE)

        return res

    def status(self):
        #TODO examples, add info from AT# AT#SLASTCLOUSURE
        res = EInterface.sendCommand("AT#SS=%s" % (self.connId))
        log.debug("SS:" + str(res))
        try:
            return int(res[0].split(",")[1])
        except:
            return 0

    def close(self):
        res=EInterface.sendCommand("AT#SH=%i" % self.connId,20)
        log.debug("Socket:close:%s" % res)



