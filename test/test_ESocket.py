import unittest
import MOD

from ESocket import ESocket
import EGprs
import EInterface

from logger import log

#import string
#import random

EInterface.init()
EGprs.init()




class ESocketTest(unittest.TestCase):
    def setUp(self):




        #self.socket=ESocket(1,"www.dn.se",80)
        self.socket = ESocket(2, "krylboc.se", 9000)


    def tearDown(self):
        pass
        self.socket.close()

    @unittest.skip("skip testGet for now")
    def test_ShouldGetPageWithoutProblem(self):
        log.debug("testGETPAGE")

        host="sl.se"
        port=80
        selector="/"

        header = "GET %s HTTP/1.1\r\nUser-Agent: testing\r\nHost: %s:%i\r\nAccept: */*\r\nConnection:Keep-Alive\r\n\r\n" % (selector,host,port)


        # size="/"
        #
        # header = "GET %s HTTP/1.0\r\n\
        #         Host: www.dn.se\r\n\
        #         User-Agent:st-solution\r\n\
        #         Connection:Keep-Alive\r\n\
        #         Accept: */*  \r\n\r\n" % size




        self.socket.send(header,1)


        #wait 30 seconds for the reponse

        MOD.sleep(300)

        # data = ""
        # res = self.socket.receive()
        # data = data + res
        #
        # while self.socket.status() > 0 or res != "":
        #     log.debug("Socket status %i" % self.socket.status())
        #     log.debug("reading %i" % len(res))
        #
        #     res = self.socket.receive()
        #     data = data + res
        #
        # MOD.sleep(30)


        size=0

        data = self.socket.receive()
        #data = data + res

        splitter=data.find("\r\n\r\n")
        log.debug("split at %i" % splitter)

        if data.find("\r\n\r\n") != -1:
            log.debug(data[:splitter])
            header,content = data.split("\r\n\r\n", 1)
            log.debug("header: " + header)
            size=int(header[header.rfind(":") +1:])
        else:
            content=""
            log.debug("GET data %s"  % repr(data))
        log.debug("Content: %i , Size: %i" % (len(content) , size))
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
        # chunk_size = 1000
        # size = (10 * 1024) + 9
        #
        # data = (size / chunk_size) * [chunk_size * "a"]
        # if size % chunk_size > 0:
        #     data.append(size % chunk_size * "a")


        size=200

        header = "POST /checkpost HTTP/1.1\r\n"
        header = header + "Content-Length: %i\r\n" % size
        header = header + "Host: krylboc.se:9000\r\n"
        header = header + "User-Agent:st-solution\r\n"
        header = header + "Connection: keep-alive\r\n"
        header = header + "Content-Type: text/plain\r\n\r\n"



        log.debug("send header")
        self.socket.send(header,open_socket=1)

        log.debug("send data")
        chunk_size=1024
        data=size/chunk_size *[chunk_size *"a"]
        if size % chunk_size > 0:
            data.append(size % chunk_size * "a")


        for chunk in data:
            self.socket.send(chunk)


        res = self.socket.receive()

        if res.find("\r\n\r\n") != -1:
            content = res.split("\r\n\r\n", 2)[1]
        else:
            content=0
            log.warning("warning %s" % res)



        assert int(content) == size


def suite():
    suite1 = unittest.makeSuite(ESocketTest, 'test')
    return unittest.TestSuite((suite1,))

