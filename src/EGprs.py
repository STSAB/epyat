#from ENetwork import getNetworkStatus,getSignalQuality
from EInterface import sendCommand, init
from logger import log
import Config

import EInterface

config=Config.Config()

config.apn="internet.telenor.se"

class Context:
    def __init__(self, cid):
        self.cid=cid

    def configure(self, apn=config.apn,pdp_addr="0.0.0.0",d_comp=0,h_comp=0):
        res=sendCommand('AT+CGDCONT=%i, "IP" ,%s, %s, %i, %i' % (self.cid,apn,pdp_addr,d_comp,h_comp),20)
        if not res == "OK":
            log.warning("Creating context failed")

    def configured(self):
        #res is like [''] or ('(1)',) or ('(1,2)',)
        # remove "(" ")" and split on ","
        #res like [''] or ('(2)',) or ('(1,2)',)
        return str(self.cid) in EInterface.sendCommand("AT#CGPADDR=?",20)[0][1:-1].split(",")

    def reset(self):
        self.deactivate()
        sendCommand('AT+CGDCONT=%i' % self.cid)

    def active(self):
        #if we have a ip, it's active
        return self.ip() != ""
    def activate(self):
        if self.configured() and not self.active():
            sendCommand("AT#SGACT=%s,1" % self.cid,200)
            if not self.active():
                log.warning("Activation failed")

    def deactivate(self):
        if self.configured() and self.active():
            for socket in self.get_sockets():
                sendCommand("AT#SH=%s" % socket)
            sendCommand("AT#SGACT=%s,0" % self.cid)

    def ip(self):
        if not self.configured():
            return ""
        return sendCommand("AT#CGPADDR=%s" % self.cid)[0].split(",")[1].replace('"',"")

    def get_sockets(self):
        sockets=[]
        res=EInterface.sendCommand("AT#SCFG?")
        for row in res:
            row=row.split(",")
            if int(row[1]) == self.cid:
                sockets.append(int(row[0]))
        return sockets





class Contexts:

    def __init__(self):
        self._contexts=[]
        for i in range(5):
            self._contexts.append(Context(i+1))

    def __getitem__(self, index):
        return self._contexts[index]


    def items(self):
        return self._contexts


    def getbysocket(self,socket_id):
        res=EInterface.sendCommand("AT#SCFG?")[socket_id-1].split(",")[1]
        return self._contexts[int(res)-1]

    def reset_all(self):
        for c in self.items():
            c.reset()




contexts=Contexts()














#move this out
#EInterface.init()



def init():

    contexts[0].reset()
    contexts[1].reset()


    #set default config
    res=EInterface.sendCommand("AT#SCFG=1,1,1500,90,600,50")
    res=EInterface.sendCommand("AT#SCFGEXT=1,2,0,10,0,0")
    res=EInterface.sendCommand("AT#SCFG=2,1,1500,90,600,50")
    res=EInterface.sendCommand("AT#SCFGEXT=2,2,0,10,0,0")


    contexts[0].configure()
    contexts[1].configure()

















