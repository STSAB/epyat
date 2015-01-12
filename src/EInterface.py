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
The EInterface is used for the communication between the API and the module
over its AT interface.

All functions in this module may throw an EInterface.CommandError or an
EInterface.TimeoutException, if a command used by this function couldn't be
executed properly. However, this should only happen in these functions, where
the exception is documented.

@author: Patrick Strobel
@version: $Revision$
"""

import MDM
import ETimer

NEWLINE = "\r\n"
""" Line seperator used by the module. """

OK = "%sOK%s" % (NEWLINE, NEWLINE)
""" OK reply. """

ERROR = "%sERROR%s" % (NEWLINE, NEWLINE)
""" Error reply. """

CME_ERROR = "%s+CME ERROR:" % NEWLINE
""" Extended error reply. """

PROMPT = "> "
""" Prompt reply. """

class EInterfaceError(Exception):
    pass


class TimeoutException(EInterfaceError):
    """
    The TimoutException is thrown when the timeout is reached while waiting
    for a "OK", "ERROR" or "+CME ERROR:" response from the module.
    """
    pass


class CommandError(EInterfaceError):
    """
    The CommandError is thrown when the module returned no "OK" message for
    a specific AT-command.
    """
    def __init__(self, errorCode):
        EInterfaceError.__init__(self, "Module responded with an error. Code: %d" % errorCode)
        self.__errorCode = errorCode

    def getErrorCode(self):
        """
        Gets the error code.

        See "AT Commands Reference Guide" for their meaning

        @return:
            The error code or "0", if the command returned "ERROR" only
        """
        return self.__errorCode


def init():
    """
    Initializes the module.

    This should be called before other functions of this API are used, since it
    sends commands to the module required for the API to work properly.
    """

    sendCommand("AT+CMEE=1")
    sendCommand("AT#SELINT=2")


def sendCommand(command, timeout=5, debug=False):
    """
    Sends a command to the module's AT-interface and waits for the response.

    The response is read until the string "OK", "ERROR" or "+CME ERROR:"
    (with leading newline) is found or if the timeout is reached.

    @param command:
        Command that will be send to the module. Has to be in uppercases.
    @type command:
        string
    @param timeout:
        Maximum time the function will try to read from the module.
    @param debug:
        Print the command to stdout before sending it.
    @type timeout:
        int

    @return:
        The module's response. Each line returned by the module is stored in
        a element of the returned tuple.
    @rtype:
        tuple

    @raise TimeoutException:
        Thrown, if timeout has been reached without reading "OK", "ERROR" or
        "+CME ERROR:".
    @raise CommandError:
        Thrown, if the module returned "ERROR" or "+CME ERROR:".
    """

    if debug:
        print command

    MDM.send(command, 5)
    MDM.send(NEWLINE, 5)

    timeout = ETimer.time() + timeout
    res = ""
    while ETimer.time() < timeout:
        res = res + MDM.read()

        if ERROR in res:
            raise CommandError(0)

        if CME_ERROR in res:
            start = res.rfind(CME_ERROR) + 14
            code = res[start:].strip()
            try:
                raise CommandError(int(code))
            except ValueError:
                raise EInterfaceError()

        # Read until a string is read that indicates the response end
        if PROMPT in res or OK in res:
            end = res.rfind("%sOK%s" % (NEWLINE, NEWLINE))
            return __responseToTuple(res[:end].strip(), command);

    raise TimeoutException #("Timeout reached while reading from the AT interface")


def __responseToTuple(res, command):
    """
    Removes leading repetition of the AT-command from the response-lines if
    they exist and returns the response as a tuple.

    @return:
        The module's response. Each line returned by the module is stored in
        a element of the returned tuple.
    @rtype:
        tuple
    """

    chunks = []
    for line in res.split(NEWLINE):
        end = line.find(":")
        # AT-command is repeated in the response line and is equivalent to the command
        if end != -1 and command.find(line[:end]) != -1:
            chunks.append(line[end + 2:])
        else:
            return res.split(NEWLINE)

    return tuple(chunks)
