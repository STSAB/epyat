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
import EDevice
import EInterface
from EInterface import CommandError
from EInterface import TimeoutException


class  Test_EDeviceTestCase(unittest.TestCase):

    MANUFACTURER = "Telit"
    """ Needs to be set according to the modules manufacturer. """

    MODEL = "GM862-QUAD-PY"
    """ Needs to be set according the module type used. """

    SOFTWARE_REVISION = "07.02.502"
    """ Needs to be set according the revision of the software installed on the device. """


    def setUp(self):
        EInterface.init()


    def test_getImei(self):
        """
        Test if a correct IMEI is read.
        """

        imei = EDevice.getImei()

        self.assertTrue(len(imei) == 15, "Check lenght of IEMI")
        self.assertTrue(imei.isdigit(), "Check if IMEI is numeric")


    def test_getImsi(self):
        """
        Test if a correct IMSI is read.

        Since the IMSI is stored on the SIM, this test will be different when
        no SIM is inserted. Hence run the test again with the SIM removed
        (or if it was removed in the first run, with the SIM inserted).
        """

        # SIM inserted
        if (EInterface.sendCommand("AT#QSS?")[0].find(",1") != -1):
            imsi = EDevice.getImsi()

            self.assertTrue(6 <= len(imsi) <= 15, "Check lenght of IMSI")
            self.assertTrue(imsi.isdigit(), "Check if IMSI is numeric")

            print "Tested with SIM inserted. Repeat test with SIM removed."
        else:
            try:
                EDevice.getImsi()
                self.fail("No SIM inserted but no CommandError thrown")
            except CommandError, ce:
                self.assertEqual(ce.getErrorCode(), 10, "Check error code")
                print "Tested with SIM removed. Repeat test with SIM inserted."
            except:
                self.fail("Invalid exception thrown")


    def test_getManufacturer(self):
        """
        Test if a correct manufacturer is read.
        """

        self.assertEqual(EDevice.getManufacturer(), Test_EDeviceTestCase.MANUFACTURER, "Check manufacturer")


    def test_getModel(self):
        """
        Test if a correct model is read.
        """

        self.assertEqual(EDevice.getModel(), Test_EDeviceTestCase.MODEL, "Check model")


    def test_getSoftwareRevision(self):
        """
        Test if a correct software revision is read.
        """

        self.assertEqual(EDevice.getSoftwareRevision(), Test_EDeviceTestCase.SOFTWARE_REVISION, "Check model")

    # @unittest.skip("skipping reboot")
    # def test_reboot(self):
    #     """
    #     Tests the reboot function.
    #     """
    #
    #     EDevice.reboot()
    #     self.assertRaises(EInterface.TimeoutException, EInterface.sendCommand, command = "AT", timeout = 1)
    #
    #     # Wait until the module has rebooted
    #     time.sleep(5)
    #
    #     self.assertEqual(EInterface.sendCommand("AT")[0], "", "Check if module is ready")

    # @unittest.skip("skipping shutdown")
    # def test_shutdown(self):
    #     """
    #     Tests the shutdown function.
    #
    #     As this sends a shutdown command to the module, all following tests
    #     may fail since the module may keep turned off.
    #     """
    #
    #     time.sleep(1)
    #     EDevice.shutdown()
    #     time.sleep(2)
    #     self.assertRaises(TimeoutException, EInterface.sendCommand, command = "AT", timeout = 1)


def suite():
    suite1 = unittest.makeSuite(Test_EDeviceTestCase, 'test')
    return unittest.TestSuite((suite1,))



