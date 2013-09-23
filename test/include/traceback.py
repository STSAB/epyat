import sys
def format_exception(etype,value,tb):
    return "etype:%s\r\n value:%s\r\ntb:%s\r\n" % (str(etype),str(value),str(tb))
