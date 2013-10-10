def format_exception(etype, value, tb):
    return "etype:%s\r\n value:%s\r\ntb:%s\r\n" % (str(etype), str(value), tb.tb_lineno)


