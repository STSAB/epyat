import unittest
import EHttp
import ESocket
import ESettings
from logger import log


CONTENT_TYPE = "application/x-stsolutions-protobuf-car"


class EHttpTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip("skip receiving")
    def testReceivingConfiguration(self):
        log.debug("testReceivingConfiguration")

        host = "krylboc.se"
        port = 80
        selector = "/"

        #create a session
        session = EHttp.Session()

        #add your own fancy header
        headers = {
            'remember': 'i got milk?'
        }

        #so get the response
        response = session.get(host, port, selector, headers)

        #how much have we got, not anything yet
        read = 0

        "so get it"
        while response.update() < EHttp.CLOSED:
            res = response.get_content()
            while res != "":
                #save the size we got and compare it later
                read = read + len(res)
                res = response.get_content()

                #send or save the read(parts) and you get a big file

        res = response.get_content()
        while res != "":
            #save the size we got and compare it later
            read = read + len(res)
            res = response.get_content()

        #check the response header
        content_length = response.headers['Content-Length']

        #we got
        log.debug("read: %i content: %i" % (read, int(content_length)))
        assert read == int(content_length)


    #@unittest.skip("skip sending")
    def testSendConfiguration(self):
        log.debug("testSendConfiguration")

        CONTENT_TYPE = "text/plain"

        host = "krylboc.se"
        port = 9000
        selector = "/checkpost"

        #create a session
        session = EHttp.Session()

        #how much data to sent
        size_of_data = 20000
        chunk_size = 1024
        data = size_of_data / chunk_size * [chunk_size * "a"]
        if size_of_data % chunk_size > 0:
            data.append(size_of_data % chunk_size * "a")

        #send the post header
        payload, response = session.post(host, port, selector, size_of_data)

        #and then the payload
        for chunk in data:
            payload.add(chunk)

        #here will we add our response from the post
        content = ""

        "so get it"
        while response.update() < EHttp.CLOSED:
            MOD.sleep(20)
            #here just downloaded
            content = content + response.get_content()

        assert size_of_data == int(content)

    def testResponseContentLengthShouldCheckContentLengthHttpField(self):
        response = EHttp.Response(None)
        response._headers['Content-Length'] = '1234990'
        assert response.content_length() == 1234990

def suite():
    suite1 = unittest.makeSuite(EHttpTest, 'test')
    return unittest.TestSuite((suite1,))


# if __name__ == '__main__':
#     # For inclusion in scripts, wouldn't it be nice if the exit status of
#     # this script reflected the success or failure of the test run? This
#     # is how to do it:
#     import sys
#     if not unittest.TextTestRunner().run(suite()).wasSuccessful():
#         sys.exit(1)
