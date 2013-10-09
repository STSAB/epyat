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

import EDevice
import EInterface
import ENetwork
import ESim

EInterface.init()
print "Manufacturer: " + EDevice.getManufacturer()
print "Model: " + EDevice.getModel()
print "IMEI: " + EDevice.getImei()
print "IMSI: " + EDevice.getImsi()
print "Software rev.: " + EDevice.getSoftwareRevision()

print "Sim status: " + ESim.getStatus()
print "Operators available:", ENetwork.getAvailableOperators()
print "Network status:", ENetwork.getNetworkStatus()
print "Signal quality:", ENetwork.getSignalQuality()
