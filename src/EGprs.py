import EInterface
from logger import log


class Context:
    def __init__(self, cid):
        self.cid = cid
        self.apn = ''

    def configure(self, apn, pdp_addr="0.0.0.0", d_comp=0, h_comp=0):
        EInterface.sendCommand('AT+CGDCONT=%i,"IP",%s,%s,%i,%i' % (self.cid, apn, pdp_addr, d_comp, h_comp), 20)

    def configured(self):
        return str(self.cid) in EInterface.sendCommand("AT#CGPADDR=?", 20)[0][1:-1].split(",")

    def reset(self):
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
            EInterface.sendCommand("AT#SGACT=%s,0" % self.cid)

    def ip(self):
        if not self.configured():
            return ""
        return EInterface.sendCommand("AT#CGPADDR=%s" % self.cid)[0].split(",")[1].replace('"', "")

_context = Context(1)


def init(apn):
    """
    Initialize GPRS functionality.

    Configures the GPRS module and contexts. This does not connect to the GPRS network.

    @param apn: Access Point Name to use for connecting.
    """
    # Add an ACCEPT rule for all addresses. It's not clear if this is a bug in the firmware or not, but it is
    # required in order to connect with the _socket module from Python 2.7. It does not seem to be required when
    # doing socket communication using AT commands.
    try:
        EInterface.sendCommand('AT#FRWL=1,"192.168.1.1","0.0.0.0"')
    except EInterface.CommandError, e:
        if e.getErrorCode() != 4:
            raise

    # Configure contexts
    _context.apn = apn


def connect():
    """
    Connect to GPRS network.

    @return:
        True if connection was successful, False otherwise.
    """
    try:
        log.info('Activating context %i' % _context.cid)
        EInterface.sendCommand('AT+CGDCONT={},"IP","{}"'.format(_context.cid, _context.apn))
        log.info('Enabling GPRS')
        EInterface.sendCommand('AT#GPRS=1')
    except EInterface.EInterfaceError, e:
        log.error('Error, ' + str(e))
        return False

    return is_connected()


def disconnect():
    try:
        log.info('Disabling GPRS')
        EInterface.sendCommand('AT#GPRS=0')
    except EInterface.EInterfaceError, e:
        log.error('Error, ' + str(e))


def is_connected():
    """
    Check if GPRS connection is established and that the device has an IP address.

    @return:
        True if device has an IP address, False otherwise.
    """
    ip = _context.ip()
    return len(ip) and ip != '0.0.0.0'
