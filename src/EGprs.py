import EInterface
from logger import log

CTX_ID = 1


def init():
    """
    Initialize GPRS functionality.

    Configures the GPRS module and contexts. This does not connect to the GPRS network.
    """
    # Add an ACCEPT rule for all addresses. It's not clear if this is a bug in the firmware or not, but it is
    # required in order to connect with the _socket module from Python 2.7. It does not seem to be required when
    # doing socket communication using AT commands.
    try:
        EInterface.sendCommand('AT#FRWL=1,"192.168.1.1","0.0.0.0"')
    except EInterface.CommandError, e:
        if e.getErrorCode() != 4:
            raise


def connect(apn):
    """
    Connect to GPRS network.

    @return:
        True if connection was successful, False otherwise.
    """
    EInterface.sendCommand('AT+CGDCONT={},"IP","{}"'.format(CTX_ID, apn))
    EInterface.sendCommand('AT#GPRS=1')


def disconnect():
    EInterface.sendCommand('AT#GPRS=0')


def is_connected():
    """
    Check if GPRS connection is established and that the device has an IP address.

    @return:
        True if device has an IP address, False otherwise.
    """
    ip = EInterface.sendCommand("AT#CGPADDR=%s" % CTX_ID)[0].split(",")[1].replace('"', "")
    return len(ip) and ip != '0.0.0.0'
