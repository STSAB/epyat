import unittest
import MOD

from ESocket import ESocket
import EInterface

from logger import log

#import string
#import random


class ESocketTest(unittest.TestCase):
    def setUp(self):
        pass



    def tearDown(self):
        pass

    #@unittest.skip("skip testGet for now")
    def testGet(self):
        size=1024

        header="GET /%s HTTP/1.1\r\n\
                Host: krylboc.se:9000\r\n\
                User-Agent:st-solution\r\n\
                Connection: keep-alive\r\n\
                Accept: *  \r\n\r\n" % size



        socket=ESocket(1,"krylboc.se","9000")
        socket.send(header)

        MOD.sleep(30)

        res=socket.receive()
        data=""
        while socket.status() > 0 or  res != "":
            data=data + res
            res=socket.receive()



        content=data.split("\r\n\r\n",2)[1]

        socket.close()

        self.assertEqual(len(content),size)


    #@unittest.skip("skip posting data for now")
    def testPost(self):
        chunk_size=1000
        size=(10 * 1024) +9

        data=(size/chunk_size)*[chunk_size*"a"]
        if size%chunk_size > 0:
            data.append(size%chunk_size*"a")


        header="POST /checkpost HTTP/1.1\r\n"
        header+="Content-Length: %i\r\n" % size
        header+="Host: krylboc.se:9000\r\n"
        header+="User-Agent:st-solution\r\n"
        header+="Connection: keep-alive\r\n"
        header+="Content-Type: text/plain\r\n\r\n"

        socket=ESocket(1,"krylboc.se","9000")

        socket.send(header)


        MOD.sleep(50)


        for chunk in data:
            socket.send(chunk)


        #MOD.sleep(30)
        res=socket.receive()
        log.debug("res POST: " + res)
        data=res.split("\r\n\r\n",2)[1]

        socket.close()

        self.assertEqual(int(data), size)




