# Copyright 2012 Patrick Strobel.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The ESim module is used to query the SIM status and to set or change the SIM's PIN.

All functions in this module may throw an EInterface.CommandError or an
EInterface.TimeoutException, if a command used by this function couldn't be
executed properly. However, this should only happen in these functions, where
the exception is documented.

@author: Patrick Strobel
@version: $Revision$
"""

import MOD
import EInterface
from EInterface import CommandError
from EInterface import TimeoutException


def getCcid():
    """
    Gets the Integrated Circuit Card Identification (CCID) of the SIM card.

    Command: AT#CCID

    @return:
        The SIM card's CCID if available
    @rtype:
        string
    """

    return EInterface.sendCommand("AT#CCID")[0]

def enterPin(pin, newPin=None):
    """
    Sends the SIM's PIN or PUK to the module, if a PIN or PUK has to be entered.

    Please keep in mind that you will have to enter the PUK if a invalid PIN has
    been entered for three times. Also, the SIM might be locked if a invalid PUK
    is entered to often.

    Use getStatus() to see if a PIN is required.

    Command: AT+CPIN

    @param pin:
        The PIN that will be send to the device. This can be either a PIN
        (4 digits) or a PUK, if this is requested (typically if a invalid PIN has
        been entered three times).
    @type pin:
        int
    @param newPin:
        Sets the PIN to a new value. This is required if the first parameter is
        a PUK and optional if the first parameter is a 4-digit-PIN.
    @type newPin:
        int

    @raise EInterface.CommandError:
        Thrown, if the PIN/PUK couldn't be set because no SIM is inserted, the
        PIN/PUK is invalid or has been entered to often.
    """

    if (newPin is None):
        EInterface.sendCommand("AT+CPIN=%d" % pin)[0]
    else:
        EInterface.sendCommand("AT+CPIN=%d,%d" % (pin, newPin))[0]


def getStatus():
    """
    Gets the SIM's status.

    Command: AT+CPIN

    @return:
        The status. On of the strings READY, SIM PIN, SIM PUK, PH-SIM PIN,
        PH-FSIM PIN, PH-FSIM PUK, SIM PIN2, SIM PUK2, PH-NET PIN, PH-NET PUK,
        PH-NETSUB PIN, PH-NETSUB PUK, PH-SP PIN, PH-SP PUK, PH-CORP PIN, PH-CORP PUK
        or PH-MCL PIN. See the AT Commands Reference Guide for detailed information.
    @rtype:
        string

    @raise EInterface.CommandError:
        Thrown, if the status couldn't be read because no SIM is inserted.
    """

    return EInterface.sendCommand("AT+CPIN?")[0]


def isInserted():
    """
    Checks if the SIM is inserted into the module.

    Command: AT#QSS

    @return:
        True, if SIM is inserted.
    @rtype:
        boolean
    """

    res = EInterface.sendCommand("AT#QSS?")[0].split(",")

    return (len(res) == 2 and res[1] == "1")


def isReady():
    """
    Checks if the SIM is ready.

    Shortly after the module has booted, the module copies the entries of the SIM's
    phone-book into the RAM. While this data is copied, the SIM cannot be
    accessed.

    Command: AT+CPBS

    @return:
        True, if the SIM is ready. That is, all data has been copied into the RAM.
    @rtype:
        boolean
    """

    try:
        EInterface.sendCommand("AT+CPBS?")[0]
        return True
    except CommandError:
        return False


def waitTillReady(timeout=10):
    """
    Waits till the SIM becomes ready.

    This function will wait until all phone-book entries have been copied into
    the RAM (see isReady()).

    Command: AT+CPBS

    @param maxTimeout:
        Maxiumum time in seconds to wait for the SIM to become ready.
    @type:
        int

    @raise EInterface.TimeoutException:
        Thrown, if SIM is not ready after maxTimeout seconds.
    """

    timeout = MOD.secCounter() + timeout

    while (MOD.secCounter() < timeout):
        if (isReady()):
            return
        MOD.sleep(2)

    raise TimeoutException("Timeout reached while waiting for the SIM to become ready")