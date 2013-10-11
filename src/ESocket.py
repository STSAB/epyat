import EInterface
import MOD
import MDM
import EBuffer
from logger import log
import EGprs


#read this from ESettings
BUFFSIZE = 1500
NEWLINE = "\r\n"

# Socket status
SS_CLOSED = 0
SS_ACTIVE = 1
SS_SUSPENDED = 2
SS_SUSPENDED_PENDING_DATA = 3
SS_LISTENING = 4
SS_INCOMING_CONNECTION = 5

class SocketException:
    """
    The TimoutException is thrown when the timeout is reached while waiting
    for a "OK", "ERROR" or "+CME ERROR:" response from the module.
    """

    pass


class ESocket:
    def __init__(self, connId, host, port):
        self.connId = connId
        self.host = host
        self.port = port
        #if socket is open close it and discard ..
        self.close()

    def send(self, data, open_socket=0):

        #TODO error. Code: 559

        #if socket is closed open,check if context is active and open itAT
        if open_socket == 1:
            log.debug("Socket is closed, open it")
            context = EGprs.contexts.getbysocket(self.connId)
            if not context.active():
                context.activate()

                #create the socket, dial out using command mode
            res = EInterface.sendCommand('AT#SD=%s,0,%s,"%s",255,0,1' % (self.connId, self.port, self.host), 180)
        elif open_socket == 0 and self.status() == 0:
            log.debug("Socket has been, closed, try to restart")
            raise SocketException

        #send data in 1024 chunk's
        length = len(data) #TODO read this from the ESettings

        #TODO if would be nice if we could move this command out to the EInterface

        for step in range((length / BUFFSIZE) + 1):
            #calculate what to send
            start = step * BUFFSIZE
            stop = (step + 1) * BUFFSIZE
            if stop > length:
                stop = length

            datapart = data[start:stop] + chr(26)

            MDM.send("AT#SSEND=%s%s" % (self.connId, NEWLINE), 5)

            timeout = MOD.secCounter() + 20
            while MOD.secCounter() < timeout:

                res = EBuffer.receive(1)
                if ">" in res:
                    MDM.send(datapart, 5)
                    # res=EBuffer.receive(1)
                    # if res.rfind("%sOK%s" % (NEWLINE, NEWLINE)) == -1:
                    #     log.error("SEND error: %s" % repr(res))
                    #     raise EInterface.CommandError(0)
                    log.debug("Socket sent %i %s" % (len(datapart) - 1, res))
                    break


    def receive(self):
        #read all up from the buffer, will waste ongoing commands
        if self.status() == 0:
            log.debug("Socket is closed")

        res = EBuffer.receive(1)

        return EBuffer.getSring(1, BUFFSIZE)

    def status(self):
        try:
            return int(EInterface.sendCommand("AT#SS=%s" % self.connId)[0].split(",")[1])
        except:
            log.debug("Socket status error")
            return -1

    def close(self):
        EInterface.sendCommand("AT#SH=%i" % self.connId, 20)




