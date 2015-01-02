""" replace favicon with lock icon """
from tools.logs import log

import os
import lxml

# callbacks
from tools.pydispatch2 import on
from mim.proxyserver import gotRequest
from mim.proxyclient import gotResponseTree

# lockicon to use as favicon.
with open("%s/../data/lock.ico"%os.getcwd()) as f:
    lockicon = f.read()

@on(gotResponseTree)
def removeFavicon(sender, tree):
    """ replace link with standard name so this can be identified on request """

    # remove favicon
    elems = tree.xpath('//link[@rel="icon" or @rel="shortcut icon"]')
    for elem in elems:
        log.debug("%s Replacing favicon"%sender.father.id)
        p = elem.getparent()
        p.remove(elem)

    # insert replacement favicon
    try:
        head = tree.xpath("//head")[0]
    except:
        head = lxml.html.fromstring("<head></head>")
        tree.insert(0, head)
    elem = lxml.etree.fromstring('<link rel="icon" href="/favicon.ico"/>')
    head.append(elem)

@on(gotRequest)
def sendLockFavicon(sender):
    """ replace favicon with lock file on older browsers """
    if not sender.path.endswith("favicon.ico"):
        return
    log.debug("{id} Sending lock favicon for {host}".format(id=sender.id, host=sender.host))
    sender.setResponseCode(200, "OK")
    sender.setHeader("Content-Type", "image/x-icon")
    sender.write(lockicon)
    sender.finish()