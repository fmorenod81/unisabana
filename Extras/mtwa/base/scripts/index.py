#!/usr/bin/python
import os
import cgi
import appsitefunctions
import Cookie
import string, random, socket

# Turn on debug mode.
import cgitb
cgitb.enable()

def id_generator(size=6, chars=string.ascii_uppercase):
 return ''.join(random.choice(chars) for _ in range(size))

if 'SETCOOKIE' in os.environ:
 #Check if any cookie exists
 if 'HTTP_COOKIE' not in os.environ:
  #Set cookie
  appsessionidvalue = socket.gethostname()+id_generator()
  c = Cookie.SimpleCookie()
  c['appSessionID'] = appsessionidvalue
  #c['appSessionID']['expires'] = 300
  print c.output()

#This will figure out what module to call based on the URL passed.  /index.py?module=viewdb for example
form = cgi.FieldStorage()
modulename = form.getvalue('module')
# print form, "<!-- (DEBUG) -->"

#This will call the fucntion to loab the base.html file for the site.  None is used because those variable for the printsite function are not used in the general page, they are used elsewhere.
appsitefunctions.printsite(modulename,None,None,None)
