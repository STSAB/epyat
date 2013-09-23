
import MOD
import MDM
from logger import log
#log.setloglevel(2)
import unittest
import EInterface
import EGprs

MDM.send("AT+CMEE=1\r\n",10)
MDM.send("AT#SELINT=2\r\n",10)

EGprs.init()




def suite():
    alltests = unittest.TestSuite()
    testfiles=[]

    res=EInterface.sendCommand("AT#LSCRIPT",30)

    for item in res:
        if item.find(".pyo") != -1:
            continue
        if item.find("test_EH") != -1:
            filename=item.split(",")[0].strip().replace('"',"")
            #remove extension
            filename=filename.split(".")[0]
            if not filename in testfiles:
                testfiles.append(filename)
                log.debug("added %s for test" % filename)
        else:
            log.debug("skipping %s" % item)



    for module in map(__import__,testfiles):
        alltests.addTest(module.suite())



    return alltests








log.debug("#########################################################################################")
log.debug("#                                                                                       #")
log.debug("#          START TEST                                                                   #")
log.debug("#                                                                                       #")
log.debug("#########################################################################################")

unittest.TextTestRunner().run(suite())


log.debug("#########################################################################################")
log.debug("#                                                                                       #")
log.debug("#          STOP TEST                                                                   #")
log.debug("#                                                                                       #")
log.debug("#########################################################################################")

#sys.stdout.write( "go telit\n")
#while 1:

#
#    log.debug( "hello telit\n")
#    MOD.sleep(100)

