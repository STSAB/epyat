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
The ESms module gives access to the module's SMS functionalities. Through this
module, SMS-messages can be sent and receivec messages can be read.

All functions in this module may throw an EInterface.CommandError or an
EInterface.TimeoutException, if a command used by this function couldn't be
executed properly. However, this should only happen in these functions, where
the exception is documented.

@author: Patrick Strobel
@version: $Revision$
"""

import EInterface

STATUS_UNREAD = "REC UNREAD"
STATUS_READ = "REC READ"
STATUS_UNSENT = "STO UNSENT"
STATUS_SENT = "STO SENT"


class SmsMessage(object):
    def __init__(self, number, text, status=STATUS_UNSENT, arrival=None):
        """
        Creates a new instance that represents a SMS message.

        @param number:
            The number the message will be sent to when C{sendMessage(int)} is called.
            The string might start with a "+" character indicating a number in international
            format.
        @type number:
            string
        @param text:
            The message's text.
            If the text is longer than 160 characters, the module will send more than
            one SMS-message and distribute the text among these. However, the number
            of messages is limited to 10, so the maximum text-length is 1520 characters.
        @type text:
            string
        @param status:
            The status that will be assigned to the message when it is stored. Must
            be on of the C{STATUS_...} constants.
        @type status:
            string
        @param arrival:
            The date and time the message arrived at the SMS service center.
        @type arrival:
            string
        """
        self.__number = number
        self.__text = text
        self.__status = status
        self.__arrival = arrival
        self._index = -1

    def getIndex(self):
        """
        The index where the message is sotred in the module's memory

        @return:
            The index
        @rtype:
            int
        """

        return self._index

    def getNumber(self):
        """
        The number the message is sent to (if this message has been stored
        to be sent later on) or the number from which the message has been sent
        (if it's a message that has been received).

        @return:
            The number
        @rtype:
            string
        """

        return self.__number


    def getNumberType(self):
        """
        The type in which the phone number is given.

        @return:
            The type as internal numeric value (as used by the AT-commands).
        @rtype:
            int
        """

        if (self.__number.find("+") == -1):
            return 129
        else:
            return 145


    def getText(self):
        """
        The message's text

        @return:
            The text
        @rtype:
            string
        """

        return self.__text


    def getStatus(self):
        """
        The message status.

        @return:
            The status. On of the C{STATUS_...} constants.
        @rtype:
            string
        """

        return self.__status

    def getArrival(self):
        """
        The date and time when the message arrived at the service center.

        @return:
            The data and time
        @rtype:
            string
        """

        return self.__arrival


class SmsStatusReport(object):
    def __init__(self, status, reference, arrival, delivery):
        """
        Creates a new instance that represents a SMS status report.

        @param status:
            The status that will be assigned to the message when it is stored. Must
            be on of the C{STATUS_...} constants.
        @type status:
            string
        @param arrival:
            The date and time the message arrived at the SMS service center.
        @type arrival:
            string
        @param delivery:
            The date and time the message has been deliverd to the destination
            phone number.
        @type delivery:
            string
        """

        self.__status = status
        self.__reference = reference
        self.__arrival = arrival
        self.__delivery = delivery


    def getStatus(self):
        """
        The message status.

        @return:
            The status. On of the C{STATUS_...} constants.
        @rtype:
            string
        """

        return self.__status

    def getReference(self):
        """
        The internal reference nubmer of the message used by the service center.

        @return:
            The reference number
        @rtype:
            int
        """

        return self.__reference


    def getArrival(self):
        """
        The date and time when the message arrived at the service center.

        @return:
            The data and time
        @rtype:
            string
        """

        return self.__arrival


    def getDelivery(self):
        """
        The date and time when the message has been delivered to the destination
        phone number.

        @return:
            The data and time
        @rtype:
            string
        """

        return self.__delivery


def init():
    """
    Initializes the module.

    This should be called before other functions in this module are used, since it
    sends commands to the module required for the SMS-functions to work properly.

    Commands: AT#SMSMODE, AT+CMGF, AT+CNMI
    """

    EInterface.sendCommand("AT#SMSMODE=1")
    EInterface.sendCommand("AT+CMGF=1")
    EInterface.sendCommand("AT+CNMI=2,1,0,0,0")
    #EInterface.sendCommand("AT+CSDH=1")


def deleteMessage(message):
    """
    Deletes a received or stored (through C{storeMessage()}) message from the
    modules memory.

    Command: AT+CMGD

    @param index:
        The message the should be removed from the storage block.
        Might be given as an index (int) or as an instance of C{SmsMessage}
        that represents a stored/received message.
    @type index:
        SmsMessage/int

    @raise EInterface.CommandError:
        Thrown, if the message cannot be removed (invalid nubmer or storage
        block is already empty).
    """

    if (type(message) == SmsMessage):
        index = message.getIndex()
    else:
        index = message

    EInterface.sendCommand("AT+CMGD=%d" % index)


def getStorageStatus():
    """
    Gets the status of the SIM's message storage.

    Command: AT+CPMPS

    @return:
        The storage status as a dictionary contatins three keys: C{free}, C{used} and
        C{total}.
        The key C{free} contains the number of free storage blocks, C{used}
        the number of used blocks and C{total} the total number of storage blocks
        supported by the SIM.
    @rtype:
        {"free": int, "used": int, "total": int}
    """

    res = EInterface.sendCommand("AT+CPMS?")[0].split(",")
    used = int(res[1])
    total = int(res[2])
    return {"free": total - used, "used": used, "total": total}


def readMessage(index):
    """
    Reads a message from a message storage block.

    The read message might be a massage that has been received, stored
    (through C{storeMessage()}) or it might be a message status report.

    If a received message is read, it's status will change to C{STATUS_READ}

    Command: AT+CMGR

    @param index:
        The index of the storage block the message should be read from.
    @type index:
        int
    @return:
        The read message (as instance of C{SmsMessage}) or status report (as
        instance of C{SmsStatusReport})
    @rtype:
        SmsMessage/SmsStatusReport

    @raise EInterface.CommandError:
        Thrown, if the message cannot be read (invalid nubmer or storage
        block is empty).
    """

    res = EInterface.sendCommand("AT+CMGR=%d" % index)

    header = res[0].split(",")

    # Erase AT command which gets echoed back.
    header[0] = header[0].replace('+CMGR: ', '')

    status = header[0]

    if (len(res) == 2):
        # Received or stored message

        # Extract data from header. Arrival might be None if a stored message is read.
        number = header[1]

        if (len(header[2]) == 0):
            # Received message
            arrival = header[3]
        else:
            # Stored message
            arrival = None

        text = res[1]

        return SmsMessage(number, text, status, arrival)
    else:
        # Status report message
        reference = header[2]
        arrival = header[5]
        delivery = header[6]

        return SmsStatusReport(status, reference, arrival, delivery)


def readMessages(status="ALL"):
    """
    Reads all message with a given status from the modules storage.

    @param status:
        Messages with this status are read from the memory. If not set, all
        messages will be read. Must be on of the C{STATUS_...} constants.
    @type status:
        string
    @return:
        All messages that have been read.
    @rtype:
        tuple
    """

    res = EInterface.sendCommand("AT+CMGL=\"%s\"" % status)

    inHeader = True
    header = None
    list = []

    for line in res:
        if (inHeader):
            # Read header
            header = line.split(",")

            # Erase AT command which gets echoed back.
            header[0] = header[0].replace('+CMGL: ', '')

            inHeader = False
        else:
            # Read data from header
            index = int(header[0])
            status = header[1]
            number = header[2]

            # Create message
            message = SmsMessage(number, line, status)
            message._index = index

            list.append(message)
            inHeader = True

    return list


def sendMessage(message):
    """
    Sends a message to a given number.

    Commands: AT+CMGS

    @param message:
        The message that will be send to the number stored in the message.
    @type destinationOrStorage:
        SmsMessage
    @return:
        The message reference number returned by the network.
    @rtype:
        int

    @raise EInterface.CommandError:
        Thrown, if the message cannot be sent (module is not attached
        to a network, the destination number is invalid etc.).
    """

    res = EInterface.sendCommand(
        "AT+CMGS=\"%s\",%d\r%s%s" % (message.getNumber(), message.getNumberType(), message.getText(), chr(0x1A)))

    return int(res[0])


def sendStoredMessage(index):
    """
    Sends a message that has been stored in the module's memory.

    Commands: AT+CMSS

    @param messageOrStorage:
        The index that indicates the storage block of the stored message that should
        be sent.
    @type destinationOrStorage:
        int
    @return:
        The message reference number returned by the network.
    @rtype:
        int

    @raise EInterface.CommandError:
        Thrown, if the message cannot be sent (module is not attached
        to a network, the destination number is invalid, no message is stored
        at the given index etc.).
    """

    res = EInterface.sendCommand("AT+CMSS=%d" % index)

    return int(res[0])


def storeMessage(message):
    """
    Writes a new message into the SIM's message storage.

    Stored message can be send to the given destination later on.

    Command: AT+CMGW

    @return:
        The index of the storage block the message has been written to.
    @rtype:
        int

    @raise EInterface.CommandError:
        Thrown, if message could not be written to the storage (no free storage
        blocks available)
    """

    # The character 0x1A terminates the input and causes the module to stored the message
    res = EInterface.sendCommand("AT+CMGW=\"%s\",%d,\"%s\"\r%s%s" % (
    message.getNumber(), message.getNumberType(), message.getStatus(), message.getText(), chr(0x1A)))
    message._index = int(res[0])
    return int(res[0])
