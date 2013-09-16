#from ENetwork import getNetworkStatus,getSignalQuality
from EInterface import sendCommand, init
from logger import log
import Config

import EInterface




#move this out
EInterface.init()


config=Config.Config()

config.apn="internet.telenor.se"
config.defaultTimeout=5

timeout=config.defaultTimeout=5




#TELIT AT#COMMAND reference page 176

#GPRS settings

#get and set the GRPS mode
#GRPS only "B", GPRS/GSM "CG" and GSM only "CC"
def getCGCLASS():
    res=EInterface.sendCommand("AT+CGCLASS?")
    return res[0]


def setCGCLass(grpsclass="B"):
    res=EInterface.sendCommand("AT+CGCLASS=%s" % grpsclass)


#attach or deattach the gprs service
def getGprsService():
    res=EInterface.sendCommand("AT+CGATT?")
    return int(res[0])

def setGprsService(attach=1):
    res=EInterface.sendCommand("AT+CGATT=%i" % attach)


# AT+CGEREP? 0,0




#CGDCONT functions for retrieving and settings the PDP context

def create_context(cid,apn=config.apn,pdp_addr="0.0.0.0",d_comp=0,h_comp=0):
    res=sendCommand('AT+CGDCONT=%i, "IP" ,%s, %s, %i, %i' % (cid,apn,pdp_addr,d_comp,h_comp))

#do we need this, if do it better
def get_context(cid):
    #TODO add example
    res=EInterface.sendCommand("AT+CGDCONT?")
    for item in res:
        if cid == int(item[0]):
            return {'cid':int(item[0]),'apn': item[2]}


def configured(cid):

    #res like [''] or ('(2)',) or ('(1,2)',)
    # remove "(" ")" and split on ","
    res=EInterface.sendCommand("AT#CGPADDR=?")[0][1:-1].split(",")

    if res == "":
        res=[]

    return str(cid) in res


def reset_context(cid):
    deactivate(cid)
    res=EInterface.sendCommand('AT+CGDCONT=%i' % cid)

def reset_all():
    for cid in available(1):
        if configured(cid):
            reset_context(cid)

def available(all=0):

    #res like '(1-5),"IP",,,(0-1),(0-1)', we want 1-5
    res=EInterface.sendCommand("AT+CGDCONT=?")[0].split(",")[0][1:-1].split("-")

    start,stop=int(res[0]),int(res[1])

    avail=range(start,stop+1)
    if not all:
        #available is available - configured cid's
        avail=filter(lambda cid:configured(cid),avail)

    return avail




#activate and deactivate context AT#SGACT
def activate(cid):
    if configured(cid) and not active(cid):
        res=EInterface.sendCommand("AT#SGACT=%s, 1"  % cid)

def deactivate(cid):
    if configured(cid) and active(cid):
        res=EInterface.sendCommand("AT#SGACT=%s, 0"  % cid)


def active(cid):
    #res like [''],('2,0',),('1,0', '2,0')

    res=EInterface.sendCommand("AT#SGACT?")
    if res == "":
        return None
    for c in res:
        id,status=c.split(",")

        if int(id) == cid:
            return int(status) == 1


def ip(cid):
    # res like ('1,"79.102.92.247"',) or ('2,""',)
    if configured(cid):
        res=EInterface.sendCommand("AT#CGPADDR=%s" % cid)[0]
        return res.split(",")[1].replace('"','')
        #return res.split(",")[1].strip('"')









#socket config


def activate_ctx(connid):
    # AT#SCFG?
    res=EInterface.sendCommand("AT#SCFG?")[connid-1].split(",")
    activate(int(res[1]))


def is_active_ctx(connid):
    res=EInterface.sendCommand("AT#SCFG?")[connid-1].split(",")
    #log.debug(res)
    return active(int(res[1]))







def init():
    #setCGCLass()

    for cid in range(1,7):
        res=EInterface.sendCommand("AT#SH=%i" % cid)



    reset_all()

    #set default config

    create_context(1)
    create_context(2)








#init()













# connections=[]
#
#
# class Connection:
#     def __init__(self, cid):
#         self.cid=cid
#         self.socket=None
#
#     def status(self):
#         res=EInterface.sendCommand("AT#CGPADDR=%s" % self.ctxid)
#
#
#
#     def activate(self):
#         pass
#
# def init():
#     #deactive active conections
#
#
#
#     try:
#         res=sendCommand("AT#SGACT?")
#         if len(res)>1:
#             #strip out the two first
#             for item in res[2:]:
#                 cid,status=item.split(":")[1].split(",")
#                 log.debug( "CID",cid,status)
#                 if int(status) == 1:
#                     #deactivate it
#                     res=sendCommand("AT#SGACT=%s,0" % (status))
#
#     except:
#         log.error("SGACT? error")
#
#     for i in range(1,4):
#         try:
#             sendCommand('AT+CGDCONT=%s'  % (i) )
#
#         except:
#             log.error("GCDCONT clear error on PDB %s" % (i))
#
#         try:
#             sendCommand('AT+CGDCONT=%s,"IP","internet.telenor.se","0.0.0.0",0,0'  % (i))
#         except:
#             log.error( "GCDCONT activate error on PDB %s" % (i))
#
#     res=sendCommand('AT+CGDCONT?')
#     sendCommand('AT+CGACT=1')
#
#
#     res=sendCommand('AT+CGACT?')
#
#
#
#
#
#
#
#
# def status():
#     print getSignalQuality()













