import string
from ESocket import ESocket
from logger import log


CHUNK_SIZE = 1024


SENDING = 1
RECEIVING = 2
FINISHED = 3


CLOSED=0

class Headers:
    """a case insensitive dict"""

    def __init__(self, str_headers=None):
        self._head="" #this is the header head ex "GET /test HTTP/1.0"

        if str_headers is None:
            self._headers = {'user-agent': 'st-solution',
                            'accept': '*/*',
                            'connection': 'keep-alive'}
        else:
            self._headers = {}
            self._headers_from_string(str_headers)

    def _headers_from_string(self,str_headers):
        self._rawheader=str_headers
        for line in str_headers.split("\r\n"):
            if line.find(":") != -1:
                key, value = line.split(":", 1)
                self._headers[key.lower()] = str(value).lower()

    def __setitem__(self, key, value):
        self._headers[key.lower()] = str(value).lower()


    def __delitem__(self, key):
        del self._headers[key.lower()]


    def __getitem__(self, key):
        if self._headers.has_key(key.lower()):
            return self._headers[key.lower()]


    def __str__(self):
        header =self._head
        for key in self._headers.keys():
            header = header + '%s: %s\r\n' % (key, self._headers[key])
        return self._head + "\r\n" + header + "\r\n"



class Response:
    def __init__(self, socket, parent):

        self.socket = socket
        self.headers = None
        self.content = ""
        self.content_length=0
        self._status = 0

        self.buffer = ""

        self._parent=parent



    def _update(self):
        log.debug("is this a error  %s" % self._parent._status)
        if self._parent._status == FINISHED:
            return FINISHED

        log.debug("reading from socket")
        resp = self.socket.receive()

        log.debug(resp)



        if self.headers is None:
            log.debug("getting header")
            self.buffer = self.buffer + resp;
            if self.buffer.find("\r\n\r\n") != -1:
                headers,resp=self.buffer.split("\r\n\r\n",1)
                #create the header
                self.headers=Headers(headers)

            else:
                resp=""
        else:
            log.debug("we have header")

        self.content_length=self.content_length+len(resp)
        self.content=self.content+resp



        if  (self.headers is not None):
            log.debug("checking header")
            log.debug("contemtlength %s" % self.headers["content-length"])
            if self.headers["content-length"] is not None  and  int(self.headers["content-length"]) == self.content_length:
                self._parent._status = FINISHED


        log.debug("klar med uppdateringen")


    def getContent(self):
        log.debug("content: %s " % len(self.content))
        resp,self.content=self.content[:CHUNK_SIZE],self.content[CHUNK_SIZE:]
        return resp

class Requests:
    def __init__(self):
        #init  default headers
        self.headers = Headers()
        self.response = None
        self.payload = None
        self.socket=None
        self._payload_sent=0
        self._status=0


    def get(self, host, port, selector):
        #cretate socket
        self.socket = ESocket(1, host, port)

        self.headers._head='GET %s HTTP/1.0\n' % quote(selector)
        self.headers['Host'] = host

        self.socket.send(str(self.headers))

        self.response=Response(self.socket, self)


    def post(self, host, port, selector="/", content_length=0):
        #cretate socket
        self.socket = ESocket(1, host, port)

        self.headers._head='POST %s HTTP/1.0\n' % quote(selector)
        self.headers['Host'] = host
        self.headers['Content-length'] = content_length


        self.socket.send(str(self.headers))

        self.payload=[]

    def add_payload(self,chunk):
        self.socket.send(chunk)
        self._payload_sent=self._payload_sent + len(chunk)
        if self._payload_sent >=  int(self.headers['Content-length']):
            self.response=Response(self.socket, self)
            self._status=RECEIVING

    def status(self):
        #try:
        if self._status < FINISHED:
            log.debug("status update")
            self.response._update()
        return  self._status
        #except:
        #    log.debug("status error")
        #    return FINISHED


    def restart(self):
        pass



#from python 1.5.2 urllib.py (without permission)
letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
digits = '0123456789'
always_safe = letters + digits + '_,.-'


def quote(s, safe='/'):
    safe = always_safe + safe
    res = []
    for c in s:
        if c in safe:
            res.append(c)
        else:
            res.append('%%%02x' % ord(c))
    return "".join(res)







