import unittest
import MOD

from ESocket import ESocket
import EGprs
import EInterface

from logger import log

#import string
#import random

EGprs.init()




class ESocketTest(unittest.TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass

    #@unittest.skip("skip testGet for now")
    def testShouldGetPageWithoutProblem(self):
        log.debug("testGETPAGE")
        size = 10

        header = "GET /%s HTTP/1.1\r\n\
                Host: krylboc.se:9000\r\n\
                User-Agent:st-solution\r\n\
                Connection: keep-alive\r\n\
                Accept: *  \r\n\r\n" % size

        socket = ESocket(1, "krylboc.se", "9000")
        socket.send(header)

        MOD.sleep(30)

        res = socket.receive()
        data = ""
        while socket.status() > 0 or res != "":
            log.debug(res)
            data = data + res
            res = socket.receive()

        if data.find("\r\n\r\n") != -1:
            content = data.split("\r\n\r\n", 2)[1]
        else:
            content=0
            log.debug("GET data %s"  % repr(data))

        socket.close()

        assert len(content) == size



    # #@unittest.skip("skip testGet for now")
    # def testShouldGetPageWithProblem(self):
    #     #deactivate the context
    #     EGprs.deactivate(1)
    #
    #
    #     size = 10
    #
    #     header = "GET /%s HTTP/1.1\r\n\
    #             Host: krylboc.se:9000\r\n\
    #             User-Agent:st-solution\r\n\
    #             Connection: keep-alive\r\n\
    #             Accept: *  \r\n\r\n" % size
    #
    #     socket = ESocket(1, "krylboc.se", "9000")
    #     socket.send(header)
    #
    #     MOD.sleep(30)
    #
    #     res = socket.receive()
    #     data = ""
    #     while socket.status() > 0 or res != "":
    #         log.debug(res)
    #         data = data + res
    #         res = socket.receive()
    #
    #     if data.find("\r\n\r\n") != -1:
    #         content = data.split("\r\n\r\n", 2)[1]
    #     else:
    #         content=0
    #         log.debug(repr(data))
    #
    #     socket.close()
    #
    #     self.assertEqual(len(content), size)



    #@unittest.skip("skip posting data for now")
    def testPost(self):
        log.debug("testPOST")
        chunk_size = 1000
        size = (10 * 1024) + 9

        data = (size / chunk_size) * [chunk_size * "a"]
        if size % chunk_size > 0:
            data.append(size % chunk_size * "a")

        header = "POST /checkpost HTTP/1.1\r\n"
        header = header + "Content-Length: %i\r\n" % size
        header = header + "Host: krylboc.se:9000\r\n"
        header = header + "User-Agent:st-solution\r\n"
        header = header + "Connection: keep-alive\r\n"
        header = header + "Content-Type: text/plain\r\n\r\n"

        socket = ESocket(1, "krylboc.se", "9000")

        socket.send(header)

        MOD.sleep(50)


        for chunk in data:
            log.debug("sending chunk")
            socket.send(chunk)


        #MOD.sleep(30)
        res = socket.receive()

        if res.find("\r\n\r\n") != -1:
            content = res.split("\r\n\r\n", 2)[1]
        else:
            content=0
            log.warning("warning %s" % res)

        socket.close()

        assert int(content) == size


def suite():
    suite1 = unittest.makeSuite(ESocketTest, 'test')
    return unittest.TestSuite((suite1,))

