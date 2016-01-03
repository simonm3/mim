""" replace favicon with lock icon """
import logging as log
import os
import lxml

# callbacks
from mim.proxyserver import events as s_events
from mim.proxyclient import events as c_events

# lockicon to use as favicon.
datafolder = os.path.join(os.path.dirname(__file__), "data")
with open(os.path.join(datafolder, "lock.ico")) as f:
    lockicon = f.read()

def init(args):
    c_events.gotResponseTree += removeFavicon
    s_events.gotRequest += sendLockFavicon

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

def sendLockFavicon(sender):
    """ replace favicon with lock file on older browsers """
    if not sender.path.endswith("favicon.ico"):
        return
    log.debug("{id} Sending lock favicon for {host}".format(id=sender.id, host=sender.host))
    sender.setResponseCode(200, "OK")
    sender.setHeader("Content-Type", "image/x-icon")
    sender.write(lockicon)
    sender.finish()