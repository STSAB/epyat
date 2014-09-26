from logger import log
import _socket as socket

CHUNK_SIZE = 1024

SENDING = 1
RECEIVING = 2
CLOSED = 3

# HTTP status codes
SC_OK = 200
SC_ACCEPTED = 202
SC_NOT_MODIFIED = 304
SC_BAD_REQUEST = 400
SC_FORBIDDEN = 403
SC_NOT_FOUND = 404
SC_INTERNAL_SERVER_ERROR = 500


class EHttpError(Exception):
    """
    Base EHttp error.
    """


class ConnectionError(EHttpError):
    """
    Error raised on connection failure. This includes DNS resolution failures, connection refusal and unavailable hosts.
    """
    pass


class TimeoutError(EHttpError):
    """
    Operation timeout.
    """
    pass


class ResponseError(EHttpError):
    """
    HTTP response error.
    """
    def __init__(self, code, message):
        self.status_code, self.message = code, message


class Session:
    def __init__(self):
        self._response = None

    def post(self, host, port, selector, payload_length, headers=None, parameters=None, timeout=None):
        if not headers:
            headers = {}

        try:
            sock = _connect(host, port, timeout=timeout)
            self._response = Response(sock)

            # Assemble HTTP headers.
            headers['Content-length'] = payload_length
            headers['Host'] = "%s:%s" % (host, port)

            sock.sendall('POST %s HTTP/1.1\r\n' % _get_request(selector, parameters))
            sock.sendall('\r\n'.join('%s: %s' % (key, value) for (key, value) in headers.iteritems()))
            sock.sendall('\r\n\r\n')
            return Payload(self, sock, payload_length), self._response
        except socket.gaierror, e:
            raise ConnectionError(e.strerror)
        except socket.timeout, e:
            raise TimeoutError(e.message)
        except socket.error, e:
            raise EHttpError(e)

    def get(self, host, port, selector, headers=None, parameters=None, timeout=None):
        if not headers:
            headers = {}

        try:
            sock = _connect(host, port, timeout=timeout)
            self._response = Response(sock)

            # Assemble HTTP headers.
            headers['Host'] = "%s:%s" % (host, port)

            sock.sendall('GET %s HTTP/1.1\r\n' % _get_request(selector, parameters))
            sock.sendall('\r\n'.join('%s: %s' % (k, v) for (k, v) in headers.iteritems()))
            sock.sendall('\r\n\r\n')
            # Request complete. No further writing will be done.
            # sock.shutdown(socket.SHUT_WR)
        except socket.gaierror, e:
            raise ConnectionError(e.strerror)
        except socket.timeout, e:
            raise TimeoutError(e.message)
        except socket.error, e:
            raise EHttpError(e)

        return self._response


def _get_request(selector, parameters):
    """
    Concatenate a resource based on a selector and its parameters. Both the selector and the parameters are escaped
    to comply with URL requirements.

    _get_request('/user_info', {'firstname': 'John', 'lastname': 'Doe'})
    returns the following request string: /user_info?firstname=John&lastname=Doe.

    This function only supports strings.

    @param selector: Root selector to use for request.
    @param parameters: Dictionary of string:string pairs which will be embedded into the request.
    @return: selector and parameters merged into a URL compatible request.
    """
    request = quote(selector)

    if parameters:
        request = '%s?%s' % (request, '&'.join('%s=%s' % (quote(k), quote(v)) for (k, v) in parameters.iteritems()))
    return request


class Response:
    def __init__(self, sock):
        self._socket = sock
        self.headers = None
        self._headers = ""
        self.status_code = 0
        self.status = RECEIVING
        self._content = []
        self._content_length = 0

    def __repr__(self):
        return '<Response [%s]>' % (self.status_code)

    def _create_header(self, res):
        if self.headers is not None:
            return res
        self._headers = self._headers + res
        if '\r\n\r\n' not in self._headers:
            # Headers+content not received yet.
            return ''

        # Split the data into headers+content
        self._headers, res = self._headers.split("\r\n\r\n", 2)

        # Parse response
        try:
            version, self.status_code, self._headers = self._headers.split(' ', 2)
            self.status_code = int(self.status_code)
        except ValueError, e:
            log.error("Error reading status: %s" % e)
            return ''

        # Parse header section to convert each header to a dictionary entry.
        headers = {}
        for row in self._headers.split('\r\n'):
            # Skip header rows we cannot split into key/value pairs.
            if ': ' not in row:
                continue
            key, value = row.split(': ')
            headers[key] = value

        self.headers = headers
        del self._headers
        return res

    def update(self):
        if self.status == SENDING:
            return SENDING

        if self.status < CLOSED:
            # check if the buffer is empty instead
            res = self._socket.recv(1024)
            if len(res) == 0:
                self.status = CLOSED

            res = self._create_header(res)
            self._content.append(res)
            self._content_length += len(res)
            # check if we get all content

        # Consider the transmission complete if the we have received as much data as Content-Length specifies.
        if (self.status != CLOSED
            and self.headers
            and 'Content-Length' in self.headers
            and self._content_length >= int(self.headers['Content-Length'])
        ):
            self.status = CLOSED
            # No further reading to be done.
            # self._socket.shutdown(socket.SHUT_RD)
            # self._socket.settimeout(None)
            log.debug('Closing socket')
            self._socket.close()
        return self.status

    def content_length(self):
        """
        Returns the length of the response's content if available. This checks the 'Content-Length' header, so in
        order for this call to work a successful call to update() must preceed it.

        @return: Length of payload in HTTP request if any.
        """
        if not self.headers:
            return 0
        return int(self.headers.get('Content-Length', 0))

    def get_content(self, size=CHUNK_SIZE):
        # same as in Ebuffer, maybe make something better handling o it
        res = ""
        for i in range(len(self._content)):
            add = size - len(res)
            if add <= 0:
                break
            res = res + self._content[i][:add]
            self._content[i] = self._content[i][add:]

        # clear this up
        for i in range(len(self._content) - 1, -1, -1):
            if self._content[i] == "":
                del self._content[i]

        return res

    def raise_for_status(self):
        """
        Raise an exception if stored status code contains an error.
        """
        msg = ''
        if 400 <= self.status_code < 500:
            msg = 'Client error'
        elif 500 <= self.status_code < 600:
            msg = 'Server error'

        if msg:
            raise ResponseError(self.status_code, '{} {}'.format(self.status_code, msg))


class Payload:
    def __init__(self, parent, sock, content_length):
        self.parent = parent
        self.socket = sock
        self.content_length = content_length
        self.sent = 0

    def remaining(self):
        return self.content_length - self.sent

    def add(self, data):
        self.socket.sendall(data)
        self.sent += len(data)
        if self.sent >= self.content_length:
            self.parent.status = RECEIVING


def quote(s, safe='/'):
    safe = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_,.-' + safe
    res = []
    for c in s:
        if c in safe:
            res.append(c)
        else:
            res.append('%%%02x' % ord(c))
    return ''.join(res)


def _connect(host, port, timeout=None):
    # Resolve socket parameters.
    af, socktype, proto, canonname, sa = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)[0]

    # Create socket.
    log.debug("Creating socket")
    sock = socket.socket(af, socktype, proto)

    try:
        # Bind socket to context ID. This uses a non-standard socket option which will fail when executed
        # outside of the Telit environment.
        log.debug("Setting socket options")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_CONTEXTID, 1)
    except AttributeError:
        # Error binding socket to context. This only applies to Telit platforms and should not happen.
        import sys

        if 'Telit' in sys.platform:
            raise

    # Set timeout if specified
    # if timeout:
    # sock.settimeout(timeout)
    # Disable TCP delay
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    # Connect
    sock.connect((host, port))

    return sock
