import unittest
import MOD
import EHttp
import EGprs
import ESocket
from logger import log

EGprs.init()

CONTENT_TYPE = "application/x-stsolutions-protobuf-car"


class HttpServiceTest(unittest.TestCase):
    def setUp(self):
        pass



    def tearDown(self):
        pass


    #@unittest.skip("skip sending")
    def testReceivingConfiguration(self):
        log.debug("testReceivingConfiguration")
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
            log.debug("Get reading ..")
            s=requests.status()
            res=response.getContent()
            MOD.sleep(1)
            data_size=data_size+len(res)

            log.debug("Getting out: %s" % data_size)
        assert data_size == size




    #@unittest.skip("skip sending")
    def testSendConfiguration(self):
        log.debug("testSendConfiguration")

        CONTENT_TYPE="text/plain"

        host="krylboc.se"
        port=9000
        selector="/checkpost"
        requests=EHttp.Requests()

        chunk_size = 1000
        size = (10 * 1024) + 9

        data = (size / chunk_size) * [chunk_size * "a"]
        if size % chunk_size > 0:
            data.append(size % chunk_size * "a")

        requests.headers["Content-Type"] = CONTENT_TYPE
        self.assertEqual( requests.headers["Content-Type"], CONTENT_TYPE)

        requests.post(host,port,selector,size)


        for chunk in data:
            log.debug("sending chunk")
            requests.add_payload(chunk)




        while requests.status() < EHttp.FINISHED:
            log.debug("Post reading ..")
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
        assert size_of_post == size



def suite():
    suite1 = unittest.makeSuite(HttpServiceTest, 'test')
    return unittest.TestSuite((suite1,))



