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

import unittest
import time
import EInterface


class  EInterfaceTestCase(unittest.TestCase):

    def setUp(self):
        EInterface.init()


    def test_init(self):
        """
        Test if module is initialized properly (all init commands send correctly).
        """

        # Reboot to reset all settings that might have been set by other tests
        EInterface.sendCommand("AT#REBOOT")

        # Wait until the module has rebooted
        time.sleep(5)

        EInterface.init()

        self.assertEqual(EInterface.sendCommand("AT+CMEE?")[0], "1", "Check error result mode")
        self.assertEqual(EInterface.sendCommand("AT#SELINT?")[0], "2", "Check interface mode")


    def test_sendCommand(self):
        """
        Test if the sendCommand behaves correctly on valid and invalid commands.
        """

        self.assertTrue(len(EInterface.sendCommand("AT#LSCRIPT", 10)) > 0, "Check LSCRIPT response")

        # All leading command repetition and "OK" removed?
        for res in EInterface.sendCommand("AT#LSCRIPT", 10):
            self.assertTrue(res.find("LSCRIPT:") == -1, "Check if command is not repeated in result")
            self.assertTrue((len(res) != 2 or res.find("OK") != -1), "Check if \"OK\" is not in result")

        # Invalid/unknown command
        self.assertRaises(EInterface.CommandError, EInterface.sendCommand, command="AT+INVALID")

        # Invalid parameter
        self.assertRaises(EInterface.CommandError, EInterface.sendCommand, command="AT+CMEE=7")

        # Timeout
        self.assertRaises(EInterface.TimeoutException, EInterface.sendCommand, command="AT#LSCRIPT", timeout=0)


def suite():
    suite1 = unittest.makeSuite(EInterfaceTestCase, 'test')
    return unittest.TestSuite((suite1,))
