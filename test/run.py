import sys

sys.path.append("../tools")
sys.path.append("../src")

import telit


telit.load("../src", "*.py")
telit.load("../test","test*.py")
telit.load("../test/include","*.py")





telit.load("../test","main.py")
telit.sync()



telit.run("main.py")

