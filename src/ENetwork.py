# Copyright 2012 Patrick Strobel.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The ENetwork module gives information about the network the module is connected to
and its connection status (like signal strength and quality). This module allows
to configure the module's network settings, too.

All functions in this module may throw an EInterface.CommandError or an
EInterface.TimeoutException, if a command used by this function couldn't be
executed properly. However, this should only happen in these functions, where
the exception is documented.

@author: Patrick Strobel
@version: $Revision$
"""

import EInterface

MODE_AUTOMATIC = 0
""" The operator is selected automatically. """

MODE_MANUAL = 1
""" The operator is selected manually. """

MODE_DEREGISTER = 2
""" The module deregisters itself from the network. """

MODE_AUTOSWITCH = 4
""" The operator is selected manually but module will switch to automatic mode if manual
selection fails. """

NETWORK_NOT_SEARCHING = 0
""" The module is not registered to a network and is not searching for one. """

NETWORK_REGISTERED_HOME = 1
""" The module is registered to the home network, roaming is disabled. """

NETWORK_SEARCHING = 2
""" The module is not registered to a network but is searching for one. """

NETWORK_DENIED = 3
""" The network registration has been denied. """

NETWORK_UNKNOWN = 4
""" The modules network status is unknown. """

NETWORK_REGISTERED_ROAMING = 5
""" The module is registered to a foreign network and roaming is enabled. """

OPERATOR_UNKNOWN = 0
""" The operator is unknown. """

OPERATOR_AVAILABLE = 1
""" The operator is available. """

OPERATOR_CURRENT = 2
""" The module is currently registered to this operator. """

OPERATOR_FORBIDDEN = 3
""" The module cannot connect to this operator. """


def getAvailableOperators():
    """
    Gets all available cellular networks.

    May take up to 1 minute.

    Command: AT+COPS

    @return:
        Available networks as tuple. Each entry in the returned tuple is a
        dictionary that represents a single network operator. The dictionary has
        three keys: C{status}, C{name} and C{code}.
        The key C{status} contains the status of the operator and is equivalent
        to on of the C{OPERATOR_...} constants. The key C{name} stores the
        operator's name and C{code} stores the operator's code (country code [3]
        + network code [2 or 3]).
    @rtype:
        ({"status": int, "name": string, "code": int}, ...)

    @raise EInterface.CommandError:
        Thrown, if the module cannot register to a network (bad connection etc.).
    """

    # Remove list of supported modes and formats
    res = EInterface.sendCommand("AT+COPS=?", 60)[0].split(",,(")[0]

    # Remove first an last brackets
    res = res[1:-1]

    list = []
    # Split and iterate over all returned operators
    for operator in res.split("),("):
        operator = operator.split(",")
        dict = {"status": int(operator[0]), "name": operator[1][1:-1], "code": int(operator[3][1:-1])}
        list.append(dict)

    return tuple(list)


def getConnectedOperator(code=0):
    """
    Gets the network operator the device is currently connected to.

    Command: AT+COPS

    @param code:
        If set to true, the returned operator-field will contain the operator's
        code. Otherwise, it contains the operator's name.
    @return:
        Information about the connection as dictionary with the keys C{mode} and
        C{operator}. C{mode} contains the connection mode and is equivalent to
        one of the C{MODE_...} constants. C{operator} stores the operator
        the module is connected to or C{None} if the module is not registered
        to a network.
    @rtype:
        {"mode": int, "operator": int/string}
    """

    if code:
        EInterface.sendCommand("AT+COPS=3,2")
    else:
        EInterface.sendCommand("AT+COPS=3,0")

    res = EInterface.sendCommand("AT+COPS?")[0].split(",")

    if len(res) <= 1:
        return {"mode": int(res[0]), "operator": None}
    else:
        if code:
            return {"mode": int(res[0]), "operator": int(res[2][1:-1])}
        else:
            return {"mode": int(res[0]), "operator": res[2][1:-1]}


def getNetworkStatus():
    """
    Gets the the status of the device's network connection/registration.

    Command: AT+CREG

    @return:
        The returned dictionary contatins three keys: C{status}, C{area} and
        C{cell}.
        The key C{status} contains the network registration status. Its value
        is equivalent to on of the C{NETWORK_...} constants. The key C{area}
        contains the cell's area code the module is registered to and C{cell}
        contains this cell's ID. C{area} and C{cell} are set to C{None} if the
        module is not registered to any network.
    @rtype:
        {"status": int, "area": string, "cell": string}
    """

    EInterface.sendCommand("AT+CREG=2")

    res = EInterface.sendCommand("AT+CREG?")[0].split(",")
    status = int(res[1])

    if status == NETWORK_REGISTERED_HOME or status == NETWORK_REGISTERED_ROAMING:
        return {"status": status, "area": res[2], "cell": res[3]}
    else:
        return {"status": status, "area": None, "cell": None}


def getSignalQuality():
    """
    Gets the signal strength and error rate.

    Command: AT+CSQ

    @return:
        The returned dictionary contains two keys: C{strength} and C{error}.
        The key C{strength} containts the singal strength having a value set
        to 99 if the module is not connected or the strength is unknown or a
        value between 0 and 31 for strength between -113 dBm and -51 dBm.
        The key C{error} contains the the error rate having a value set to
        99 if the module is not connected or the error rate is unknown or a
        value between 0 and 7 for rates between 0.2 % and 12.8 %.
    @rtype:
        {"strength": int, "error": int}
    """

    res = EInterface.sendCommand("AT+CSQ")[0].split(",")

    return {"strength": int(res[0]), "error": int(res[1])}


def setOperator(mode, operator=None):
    """
    Sets the network operator and registration mode.

    Command: AT+COPS

    @param mode:
        The connection/registration mode. Must be on of the C{MODE_...}
        constants.
    @type mode:
        int
    @param operator:
        The operator the module should connect to. Only used when
        mode is set to C{MODE_MANUAL} or C{MODE_AUTOSWITCH}. Operator can
        be set as code (integer) or as operator name (string).
    @type operator:
        int/string
    """
    if operator is not None:
        if (type(operator) == int):
            EInterface.sendCommand("AT+COPS=%d,2,%d" % (mode, operator))
        else:
            EInterface.sendCommand("AT+COPS=%d,0,\"%s\"" % (mode, operator))
    else:
        EInterface.sendCommand("AT+COPS=%d" % mode)
