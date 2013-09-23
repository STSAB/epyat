import os


class log():
    def __init__(self,path):
        #print "create filelogger"
        self.logfile=os.path.join(path,"log.txt")
        try:
            with open(self.logfile,"r") as f:
                self.files = dict(line.split() for line in f)
        except:
            self.files={}
    def __getitem__(self, item):
        if self.files.has_key(item):
            return int(self.files[item])
    def __setitem__(self, key, value):
        self.files[key]=value
        self.save()

    def __delitem__(self, key):
        if key in self.files:
            del self.files[key]
            self.save()


    def __del__(self):
        self.save()

    def save(self):
       #print "save to log"
       with open(self.logfile,"w") as f:
                for key,value in self.files.items():
                    f.write(key + "\t" + str(value) + "\n")

_filelogger={}

def getfilelogger(path):
    path=os.path.abspath(path)
    if not _filelogger.has_key(path):
        _filelogger[path]=log(path)

    return _filelogger[path]
