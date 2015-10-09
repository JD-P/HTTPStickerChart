import sys
import os
os.environ["REMOTE_USER"] = "test"
from wsgiref import simple_server
cgipath = os.path.join(os.path.split(__file__)[0], "cgi/") 
sys.path.append(cgipath)
from chartboard import *

httpd = simple_server.make_server('localhost', 9001, application)

httpd.serve_forever()

