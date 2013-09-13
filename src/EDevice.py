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
The EDevice module gives access to general information about the GPRS-module and
to general control functionallity.

All functions in this module may throw an EInterface.CommandError or an
EInterface.TimeoutException, if a command used by this function couldn't be
executed properly. However, this should only happen in these functions, where
the exception is documented.

@author: Patrick Strobel
@version: $Revision$
"""

import EInterface

def getImei():
    """
    Gets the International Mobile Equipment Identity (IMEI), the module's serial number.

    Command: AT+CGSN

    @return:
        The serial number
    @rtype:
        string
    """

    return EInterface.sendCommand("AT+CGSN")[0]


def getImsi():
    """
    Gets the International Mobile Subscriber Identity (IMSI).

    Command: AT+CIMI

    @return:
        The IMSI.
    @rtype:
        string

    @raise EInterface.CommandError:
        Thrown, if the IMSI couldn't be read because no SIM is inserted.
    """

    return EInterface.sendCommand("AT+CIMI")[0]


def getManufacturer():
    """
    Gets the manufacturer of the module.

    Command: AT+CGMI

    @return:
        The manufacturer.
    @rtype:
        string
    """

    return EInterface.sendCommand("AT+CGMI")[0]


def getModel():
    """
    Gets the model of the module.

    Command: AT+CGMM

    @return:
        The module's name.
    @rtype:
        string
    """

    return EInterface.sendCommand("AT+CGMM")[0]


def getSoftwareRevision():
    """
    Gets the revision of the software running on the module.

    Command: AT+CGMR

    @return:
        The software revision.
    @rtype:
        string
    """

    return EInterface.sendCommand("AT+CGMR")[0]


def reboot():
    """
    Reboots the module.

    Command: AT#REBOOT
    """

    return EInterface.sendCommand("AT#REBOOT")[0]


def shutdown():
    """
    Turns the module off.

    Command: AT#SHDN
    """

    return EInterface.sendCommand("AT#SHDN")[0]