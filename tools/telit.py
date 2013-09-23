from glob import glob
import os
from stat import ST_MTIME, ST_SIZE
import time
import sys

import MDM
import EInterface

EInterface.init()

EInterface.sendCommand("AT#ENHRST=1,0")

time.sleep(5)

EInterface.init()

time.sleep(5)

from filelogger import getfilelogger
from logger import log

class File():
    def __init__(self,filepath):
        directory,filename=os.path.split(filepath)
        fileName,extension=filename.split(".")
        if len(fileName + '.pyo') > 16:
            print "warning too long filename"
        self.dir=directory
        self.filename=filename
        self.path=filepath
        st=os.stat(self.path)
        self.mtime=st[ST_MTIME]
        self.length=st[ST_SIZE]
        self.logfiles=getfilelogger(directory)


    @property
    def lastupdate(self):
        return self.logfiles[self.filename]

    @lastupdate.setter
    def lastupdate(self, value):
        self.logfiles[self.filename]=value

    @property
    def updated(self):
        if self.lastupdate is None:
            return False
        else:
            return self.lastupdate >= self.mtime
    def update(self):
        #delete file(s)
        #print "Deleting files if exist", self.filename
        #if self.filename + "o" in telitfiles:
        #    print "try to delete", self.filename +"o"
        deletefile(self.filename + "o")
        #if self.filename in telitfiles:
        #print "try to delete", self.filename
        deletefile(self.filename)

        #write files
        print "writing file",self.filename
        res=MDM.receive(1)
        MDM.send("AT#WSCRIPT=%s,%i\r\n" % (self.filename,self.length),50)

        res=MDM.receive(50)
        print "write resp", res
        if not ">>>" in res:
            print "missing \r\n>>>",res," we try anyway "


        with open(self.path,"rb") as f:
            i=0
            for chunk in readfile(self.path):
                i+=len(chunk)
                MDM.send(chunk,5)
                print "\tsending line %i of %i"  % (i, self.length)
                time.sleep(1)

        res=MDM.receive(1)
        if "OK\r\n"  in res:
            print "ok writing ", self.filename
            #if success,update log, don't save fractions(milliseconds)
            self.logfiles[self.filename]=int(time.time())
            #self.lastupdate = int(time.time())






def readfile(filepath):
    with open(filepath, "rb") as file_obj:
          while True:
                data = file_obj.read(1024)
                if not data:
                    break
                yield data






def telitFiles():
    res=EInterface.sendCommand("AT#LSCRIPT",50)
    print res
    #do not return the last row free  bytes
    return [x.split(",")[0].strip().strip('"') for x in res[:-1]]

def deleteall():
    for f in telitFiles():
        deletefile(f)

def deletefile(filename):
    try:
        cmd='AT#DSCRIPT="%s"' % (filename)
        res=EInterface.sendCommand(cmd)
        print "Deleted", filename
    except EInterface.TimeoutException:
        print "TimeoutException on delete %s" % filename

def writefile(filename,filepath):
    pass
def escript(filename):
    cmd='AT#ESCRIPT="%s"' % filename
    res=EInterface.sendCommand(cmd)
    if res[0] == "OK":
        print "Changed upstart script to %s" % filename

def reboot():

    cmd='AT#REBOOT'
    res=EInterface.sendCommand(cmd)
    if res[0] == "OK":
        print "REBOOT"

def run(filename=None):
    if filename is not None:
        escript(filename)
    res=EInterface.sendCommand("AT#EXECSCR")
    if res[0] == "OK":
        print "Starting active script"



files=[]
telitfiles=telitFiles()

def load(directory, pattern):
    loadfiles=glob(os.path.join(os.path.abspath(directory),pattern))
    for f in loadfiles:
        files.append(File(f))




def sync():
    for f in files:
        if not f.updated:
            f.update()






















