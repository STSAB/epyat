from ESocket import ESocket
from logger import log


CHUNK_SIZE = 1024

SENDING = 1
RECEIVING = 2
CLOSED = 3

# HTTP status codes
SC_OK = 200
SC_ACCEPTED = 200
SC_NOT_MODIFIED = 304


class Session:
    def __init__(self):
        self._socket = None
        self._response = None
        pass

    def post(self, host, port, selector, payload_length, headers={}):
        #create socket from ..?
        self._socket = ESocket(1, host, port)
        self._response = Response(self._socket)

        # Assemble HTTP headers.
        headers['Content-length'] = payload_length
        headers['Host'] = "%s:%s" % (host, port)

        self._socket.send('POST %s HTTP/1.1\r\n' % quote(selector), 1)
        self._socket.send('\r\n'.join('%s: %s' % (key, value) for (key, value) in headers.iteritems()))
        self._socket.send('\r\n\r\n')
        return Payload(self, payload_length), self._response

    def get(self, host, port, selector, headers={}):
        #create socket from ..?
        socket = ESocket(1, host, port)
        self._response = Response(socket)

        # Assemble HTTP headers.
        headers['Host'] = "%s:%s" % (host, port)

        self._socket.send('GET %s HTTP/1.1\r\n' % quote(selector), 1)
        self._socket.send('\r\n'.join('%s: %s' % (key, value) for (key, value) in headers.iteritems()))
        self._socket.send('\r\n\r\n')
        return self._response


class Response:
    def __init__(self, socket):
        self._socket = socket
        self.headers = None
        self._headers = ""

        self.status_code = 0

        self.status = RECEIVING

        self._content = []
        self._content_length = 0

    def _create_header(self, res):
        log.debug("check if headers")
        if self.headers is not None:
            return res
        self._headers = self._headers + res
        res = ""
        log.debug("search for headers")
        if self._headers.find("\r\n\r\n") != -1:
            log.debug("Found header")
            self._headers, res = self._headers.split("\r\n\r\n", 2)

            self.headers = Headers(self._headers)
            del self._headers

            return res
        else:
            return ""


    def update(self):
        log.debug("update")
        if self.status == SENDING:
            return SENDING

        if self.status < CLOSED:
            #check if the buffer is empty instead
            res = self._socket.receive()
            if res == "" and self._socket.status() == 0:
                self.status = CLOSED
            log.debug(res)
            res = self._create_header(res)
            self._content.append(res)
            self._content_length = self._content_length + len(res)
            #check if we get all content
        log.debug("update check header")
        if self.headers is not None:
            cl = self.headers["Content-Length"]
            if cl is not None and cl <= self._content_length:
                self.status = 4
                self._socket.close()
        log.debug("leaving update")

        return self.status

    def getContent(self, size=1024):
        log.debug("getContent")
        #same as in Ebuffer, maybe make something better handling o it
        res = ""
        for i in range(len(self._content)):
            add = size - len(res)
            if add <= 0:
                break
            res = res + self._content[i][:add]
            self._content[i] = self._content[i][add:]

        #clear this up
        for i in range(len(self._content) - 1, -1, -1):
            if self._content[i] == "":
                del self._content[i]

        return res


class Payload:
    def __init__(self, parent, content_length):
        self.parent = parent
        self.content_length = content_length
        self.sent = 0

    def add(self, data):
        self.parent._socket.send(data)
        self.sent = self.sent + len(data)
        if self.sent >= self.content_length:
            self.parent.status = RECEIVING


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

















