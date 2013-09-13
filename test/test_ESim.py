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
import ESim
import EInterface
from EInterface import CommandError
from EInterface import TimeoutException


class  Test_ESimTestCase(unittest.TestCase):

    PIN = 4221
    """ The PIN of the SIM that's inserted into the module. """


    def setUp(self):
        EInterface.init()

    def __reboot(self):
        """
        Reboots the device by sending a shutdown command.
        """

        EInterface.sendCommand("AT#SHDN")
        time.sleep(10)
        EInterface.sendCommand("ATE0")
        EInterface.sendCommand("ATV1")
        EInterface.init()


    def test_enterPin(self):
        """
        Tests if the PIN is send to the module successfully.

        This test checks if a SIM is inserted if the SIM requires a PIN.
        Depending on this status, the unit-tests will be different. Therefor,
        the test should be launched with no SIM inserted, a SIM inserted that
        does not require a PIN and a SIM inserted that requires a PIN.

        If the SIM requires a PIN, the test will enter an invalid PIN before
        it sends the correct PIN (from the PIN-constant) to the module.

        The test will also change the PIN two times: First to 1234 and than back
        to the value specified in the PIN-constant.

        The module will be rebooted before the test is started to make sure
        that the PIN is "forgotten".

        The test uses the command AT#SHDN to reboot the device, which requires
        a hardware design that automatically turns the module on again after it's
        powered of. AT#SHDN is used because AT#REBOOT will cause the module
        to remember the PIN, so the PIN is not required on the next boot.
        """

        print "test_enterPin..."
        self.__reboot()
        # Wait till SIM is initialized (AT#QSS will be "0,0" if we do not wait)

        # SIM inserted
        if (EInterface.sendCommand("AT#QSS?")[0].find(",1") != -1):

            # PIN required
            if (EInterface.sendCommand("AT+CPIN?")[0].find("SIM PIN") != -1):
                # Invalid PIN
                print "Enter invalid PIN"
                try:
                    ESim.enterPin(0)
                    self.fail("Accepted invalid PIN")
                except CommandError, ce:
                    self.assertEqual(ce.getErrorCode(), 16, "Check error code")
                except:
                    self.fail("Invalid exception thrown")

                self.assertTrue(EInterface.sendCommand("AT+CPIN?")[0].find("SIM PIN") != -1, "PIN still required")

                # Valid PIN
                print "Enter valid PIN"
                ESim.enterPin(Test_ESimTestCase.PIN)
                self.assertTrue(EInterface.sendCommand("AT+CPIN?")[0].find("READY") != -1, "PIN accepted")

                # Reboot and try to change the PIN
                self.__reboot()

                # Change PIN to new one
                print "Change PIN to 1234"
                ESim.enterPin(Test_ESimTestCase.PIN, 1234)
                self.assertTrue(EInterface.sendCommand("AT+CPIN?")[0].find("READY") != -1, "PIN accepted and changed")

                # Reboot and check if PIN has been changed successfully
                self.__reboot()

                print "Change PIN back to old PIN"
                ESim.enterPin(1234, Test_ESimTestCase.PIN)
                self.assertTrue(EInterface.sendCommand("AT+CPIN?")[0].find("READY") != -1, "PIN accepted and changed")

                print "Tested with SIM inserted and PIN required.",\
                "Repeat test with SIM removed and a SIM inserted that does not require a PIN."

            # PIN not required
            else:
                self.assertTrue(EInterface.sendCommand("AT+CPIN?")[0].find("READY") != -1, "No PIN required")
                print "Tested with SIM inserted and no PIN required.",\
                "Repeat test with SIM removed and a SIM inserted that does require a PIN."

        # SIM removed
        else:
            try:
                ESim.enterPin(0)
                self.fail("No SIM inserted but no CommandError thrown")
            except CommandError, ce:
                self.assertEqual(ce.getErrorCode(), 10, "Check error code")
                print "Tested with SIM removed. Repeat test with SIM inserted."
            except TimeoutException, te:
                self.fail("TimeoutException thrown")
            except:
                raise


    def test_getStatus(self):
        """
        Tests if the correct SIM status is returned.

        Run this test with SIM removed, a SIM inserted that requires a PIN and
        one that does not.
        """

        print "test_getStatus..."
        # SIM inserted
        if (EInterface.sendCommand("AT#QSS?")[0].find(",1") != -1):
            res = ESim.getStatus()
            self.assertTrue(EInterface.sendCommand("AT+CPIN?")[0].find(res) != -1, "Check SIM status")
            print "Tested with SIM inserted. Repeat test with SIM removed."

        # SIM removed
        else:
            try:
                ESim.getStatus()
                self.fail("No SIM inserted but no CommandError thrown")
            except CommandError, ce:
                self.assertEqual(ce.getErrorCode(), 10, "Check error code")
                print "Tested with SIM removed. Repeat test with SIM inserted."
            except:
                raise


    def test_isInserted(self):
        """
        Tests if the correct SIM insertion-status is read.
        """

        print "test_isInserted"

        # SIM inserted
        try:
            EInterface.sendCommand("AT+CPIN?")

            self.assertTrue(ESim.isInserted(), "Check if SIM is inserted")
            print "Tested with SIM inserted. Repeat test with SIM removed."

        # SIM removed
        except:
            self.assertFalse(ESim.isInserted(), "Check if SIM is removed")
            print "Tested with SIM removed. Repeat test with SIM inserted."


if __name__ == '__main__':
    unittest.main()
