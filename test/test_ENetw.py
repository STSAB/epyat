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
import ENetwork
import EInterface
from EInterface import CommandError

class  Test_ENetworkTestCase(unittest.TestCase):

    def setUp(self):
        EInterface.init()


    def test_getAvailableOperators(self):
        """
        Tests the returned operator.

        Since the returned operator is non-deterministic, only the returned
        data-types and ranges  are checked.

        Run test with different SIMs and entered PIN.
        """
        try:
            res = ENetwork.getAvailableOperators()

            self.assertEqual(type(res), tuple, "Check if tuple")

            for op in res:
                self.assertEqual(type(op), dict, "Check if tuple contains dictionaries")

                self.assertEqual(len(op), 3, "Check number of entries in dictionary")
                self.assertTrue("status" in op, "Check if key \"status\" exists")
                self.assertEqual(type(op["status"]), int, "Check if \"status\" is an integer")
                self.assertEqual(type(op["status"]), int, "Check if key \"status\" is an integer")
                self.assertTrue(ENetwork.OPERATOR_UNKNOWN <= op["status"] <= ENetwork.OPERATOR_FORBIDDEN, "Check range of \"status\"")
                self.assertTrue("name" in op, "Check if key \"name\" exists")
                self.assertTrue("code" in op, "Check if key \"code\" exists")
                self.assertEqual(type(op["code"]), int, "Check if \"code\" is an integer")
        except CommandError, ce:
            self.assertEqual(ce.getErrorCode(), 30, "Check error code")
            print "Device did not find any network. Check antenna and PIN and run test again"


    def test_getConnectedOperator(self):
        """
        Tests the returned operator the module is connected to.

        Since the returned operator is non-deterministic, only the returned
        data-types and ranges  are checked.

        Run test with different SIMs and entered PIN.
        """

        # Code
        resC = ENetwork.getConnectedOperator(True)
        resN = ENetwork.getConnectedOperator()

        self.assertEqual(type(resC), dict, "Check if dictionary")
        self.assertEqual(len(resC), 2, "Check number of entries in dictionary")
        self.assertTrue("mode" in resC, "Check if key \"mode\" exists")
        self.assertEqual(type(resC["mode"]), int, "Check if \"mode\" is an integer")
        self.assertTrue("operator" in resC, "Check if key \"operator\" exists")

        self.assertEqual(type(resN), dict, "Check if dictionary")
        self.assertEqual(len(resN), 2, "Check number of entries in dictionary")
        self.assertTrue("mode" in resN, "Check if key \"mode\" exists")
        self.assertEqual(type(resN["mode"]), int, "Check if \"mode\" is an integer")
        self.assertTrue("operator" in resN, "Check if key \"operator\" exists")

        # Not registered
        if (EInterface.sendCommand("AT+COPS?")[0].find(",") == -1):
            self.assertEqual(resC["operator"], None, "Check if \"operator\" is None")
            self.assertEqual(resN["operator"], None, "Check if \"operator\" is None")
        else:
            self.assertEqual(type(resC["operator"]), int, "Check if \"operator\" is an integer")
            self.assertEqual(type(resN["operator"]), str, "Check if \"operator\" is a string")


    def test_getNetworkStatus(self):
        """
        Tests the returned network status.

        Since the returned operator is non-deterministic, only the returned
        data-types and ranges are checked.

        Run test with different SIMs and entered PIN and removed SIM.
        """

        res = ENetwork.getNetworkStatus()

        self.assertEqual(type(res), dict, "Check if dictionary")
        self.assertEqual(len(res), 3, "Check number of entries in dictionary")
        self.assertTrue("status" in res, "Check if key \"status\" exists")
        self.assertEqual(type(res["status"]), int, "Check if key \"status\" is an integer")
        self.assertTrue(ENetwork.NETWORK_NOT_SEARCHING <= res["status"] <= ENetwork.NETWORK_REGISTERED_ROAMING, "Check range of \"status\"")
        self.assertTrue("area" in res, "Check if key \"area\" exists")
        self.assertTrue("cell" in res, "Check if key \"status\" exists")

        if (res["status"] == ENetwork.NETWORK_NOT_SEARCHING or
          res["status"] == ENetwork.NETWORK_SEARCHING or
          res["status"] == ENetwork.NETWORK_DENIED or
          res["status"] == ENetwork.NETWORK_UNKNOWN):
            self.assertEqual(res["area"], None, "Check if key \"area\" is set to None")
            self.assertEqual(res["cell"], None, "Check if key \"cell\" is set to None")
            print "Tested with an expired/deactivated or removed SIM (no network registration). Repeat with an active SIM."
        else:
            self.assertEqual(type(res["area"]), str, "Check if key \"area\" is a string")
            self.assertEqual(type(res["cell"]), str, "Check if key \"cell\" is a string")
            print "Tested with an active SIM (with network registration). Repeat with an expired/deactivated SIM."


    def test_getSignalQuality(self):
        """
        Tests the returned signale quality.

        Since the returned quality is non-deterministic, only the returned
        data-types and ranges are checked.

        Run test with different SIMs and entered PIN.
        """

        res = ENetwork.getSignalQuality()

        self.assertEqual(type(res), dict, "Check if dictionary")
        self.assertEqual(len(res), 2, "Check number of entries in dictionary")
        self.assertTrue("strength" in res, "Check if key \"strength\" exists")
        self.assertEqual(type(res["strength"]), int, "Check if key \"strength\" is an integer")
        self.assertTrue(0 <= res["strength"] <= 99, "Check range of \"strength\"")
        self.assertTrue("error" in res, "Check if key \"error\" exists")
        self.assertTrue(0 <= res["error"] <= 99, "Check range of \"error\"")
        self.assertEqual(type(res["error"]), int, "Check if key \"error\" is an integer")


def suite():
    suite1 = unittest.makeSuite(Test_ENetworkTestCase, 'test')
    return unittest.TestSuite((suite1,))
