import EInterface
from logger import log


class Context:
    def __init__(self, cid):
        self.cid = cid

    def configure(self, apn, pdp_addr="0.0.0.0", d_comp=0, h_comp=0):
        res = EInterface.sendCommand('AT+CGDCONT=%i,"IP",%s,%s,%i,%i' % (self.cid, apn, pdp_addr, d_comp, h_comp), 20)

    def configured(self):
        #res is like [''] or ('(1)',) or ('(1,2)',)
        # remove "(" ")" and split on ","
        #res like [''] or ('(2)',) or ('(1,2)',)
        return str(self.cid) in EInterface.sendCommand("AT#CGPADDR=?", 20)[0][1:-1].split(",")

    def reset(self):
        self.deactivate()
        EInterface.sendCommand('AT+CGDCONT=%i' % self.cid)

    def active(self):
        #if we have a ip, it's active
        return self.ip() != ""

    def activate(self):
        if self.configured() and not self.active():
            EInterface.sendCommand("AT#SGACT=%s,1" % self.cid, 200)
            if not self.active():
                log.warning("Activation failed")

    def deactivate(self):
        if self.configured() and self.active():
            for socket in self.get_sockets():
                EInterface.sendCommand("AT#SH=%s" % socket)
            EInterface.sendCommand("AT#SGACT=%s,0" % self.cid)

    def ip(self):
        if not self.configured():
            return ""
        return EInterface.sendCommand("AT#CGPADDR=%s" % self.cid)[0].split(",")[1].replace('"', "")

    def get_sockets(self):
        sockets = []
        res = EInterface.sendCommand("AT#SCFG?")
        for row in res:
            row = row.split(",")
            if int(row[1]) == self.cid:
                sockets.append(int(row[0]))
        return sockets


class Contexts:
    def __init__(self):
        self._contexts = []
        for i in range(2):
            self._contexts.append(Context(i + 1))

    def __getitem__(self, index):
        return self._contexts[index]

    def items(self):
        return self._contexts

    def getbysocket(self, socket_id):
        res = EInterface.sendCommand("AT#SCFG?")[socket_id - 1].split(",")[1]
        return self._contexts[int(res) - 1]

    def reset_all(self):
        for c in self.items():
            c.reset()

contexts = Contexts()


def init(apn):
    # Add an ACCEPT rule for all addresses. It's not clear if this is a bug in the firmware or not, but it is
    # required in order to connect with the _socket module from Python 2.7. It does not seem to be required when
    # doing socket communication using AT commands.
    try:
        EInterface.sendCommand('AT#FRWL=1,"192.168.1.1","0.0.0.0"')
    except EInterface.CommandError, e:
        if e.getErrorCode() != 4:
            raise

    # Activate contexts
    for context in contexts:
        log.debug('Activating context %i' % context.cid)
        try:
            EInterface.sendCommand('AT+CGDCONT={},"IP","{}"'.format(context.cid, apn))
            log.debug('Context {} IP: {}'.format(context.cid, context.ip()))
        except EInterface.CommandError, e:
            raise

    # Enable GPRS
    EInterface.sendCommand('AT#GPRS=1')
