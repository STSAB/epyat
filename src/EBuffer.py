import MDM


#TODO get this from ESettings
NEWLINE = "\r\n"


#create the buffer fpr srings
_buffer = 6 * [[]]

_no_carrier = 0

#buffer funktions

def _addSRING(cid, data):
    log.debug("add cid %i, data %i" % (cid, len(data)))
    _buffer[cid - 1].append(data)


def clearSRING():
    for i in range(len(_buffer)):
        _buffer[i] = []


#check for unread NO CARRIER
def no_carrier():
    res = _no_carrier
    _no_carrier = 0
    return res


def getSring(cid, maxlen):
    item = _buffer[cid - 1]

    res = ""
    for i in range(len(item)):
        add = maxlen - len(res)
        if add <= 0:
            break
        res = res + item[i][:add]
        item[i] = item[i][add:]

    #clear this up
    for i in range(len(item) - 1, -1, -1):
        if item[i] == "":
            del item[i]

    #_buffer[cid-1]=_buffer[cid-1][maxlen:]
    return res


def check_Sring(cid):
    #returns true if we have something in buffer
    return _buffer != []


def receive(timeoutTenthOfSec):
    #check telit
    res = MDM.receive(1)
    if len(res) == 0:
        return res
        #log.debug(res)
    #check for unsoiltced messgage
    #SRING
    res = _get_SRING(res)
    #NO CARRIER
    res = _stripNO_CARRIER(res)

    return res


def _stripNO_CARRIER(res):
    # if "NO CARRIER" in res:
    #     _no_carrier=1
    #     res=res.replace("NO CARRIER\r\n", "")
    return res


def _get_SRING(res):
    #we want to find cid (1), lengt of data (102) and get out the data
    #SRING: 1,102, lorem ipsum ...\r\n
    #print repr(res[:30])

    while 1:
        start = res.find("SRING")
        if start == -1:
            break



        #find the starting points

        #cid is between start and the next ,
        s1 = start + 7
        s2 = res.find(",", s1)
        cid = int(res[s1:s2])

        #length is between one step further from s2 and next ,
        s2 = s2 + 1
        s3 = res.find(",", s2)
        length = int(res[s2:s3])

        #data is one step further from s3 and the lenght of lenght
        s3 = s3 + 1
        data = res[s3:s3 + length]

        #add the sring to the buffer
        _addSRING(cid, data)


        #cut out the whole SRING... + \r\n
        #SRING starts on start and ends on start of data + length of data + newline
        s4 = s3 + length + len(NEWLINE)
        res = res[:start] + res[s4:]

    return res

                        
                                                                                
                                                                                
                                                                              
   

    
    
