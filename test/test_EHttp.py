import unittest
import MOD
import EHttp
import EGprs
import ESocket
from logger import log



CONTENT_TYPE = "application/x-stsolutions-protobuf-car"


class HttpServiceTest(unittest.TestCase):
    def setUp(self):
        pass
        #EGprs.init()


    def tearDown(self):
        pass


    #@unittest.skip("skip sending")
    def testReceivingConfiguration(self):
        size=4000


        host="krylboc.se"
        port=9000
        selector=str(size)
        requests=EHttp.Requests()

        requests.get(host,port,selector)

        while requests.status() < EHttp.FINISHED:
            MOD.sleep(10)
            requests.status()
            if requests.response.headers is not None:
                break
            log.debug("Waiting for headers")

        response=requests.response

        content_length=int(response.headers["Content-Length"])
        self.assertEqual(content_length,size)

        data_size=0
        while data_size< content_length:
            s=requests.status()
            res=response.getContent()
            MOD.sleep(1)
            data_size=data_size+len(res)

            log.debug("Getting out: %s" % data_size)
        self.assertEqual(data_size,size)




    #@unittest.skip("skip sending")
    def testSendConfiguration(self):


        CONTENT_TYPE="text/plain"

        host="krylboc.se"
        port=9000
        selector="/checkpost"
        requests=EHttp.Requests()

        payload=1200 *"remember the milk"

        requests.headers["Content-Type"] = CONTENT_TYPE
        self.assertEqual( requests.headers["Content-Type"], CONTENT_TYPE)

        requests.post(host,port,selector,len(payload))

        requests.add_payload(payload)




        while requests.status() < EHttp.FINISHED:
            MOD.sleep(10)
            requests.status()
            if requests.response.headers is not None:
                break
            log.debug("Waiting for headers")

        response=requests.response

        content_length=int(response.headers["Content-Length"])

        data_size=0
        res=""
        while data_size< content_length:
            s=requests.status()
            res=res+response.getContent()
            MOD.sleep(1)
            data_size=data_size+len(res)

            log.debug("Getting out: %s" % data_size)
        log.debug("post res %s" % res)
        size_of_post=int(res)
        self.assertEqual(size_of_post,len(payload))







