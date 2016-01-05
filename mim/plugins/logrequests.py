""" log all requests """
import logging as log

# callbacks
from mim.proxyserver import events as s_events
from mim.proxyclient import events as c_events

loaded = set()
visited = set()

def init(args):
    c_events.gotResponseTree += storeLoaded
    s_events.gotRequest += logRequest

def storeLoaded(sender, tree):
    """ store image and script links so they are not logged """
    for item in tree.xpath("//img|//script|iframe"):
        try:
            loaded.add(item.attrib["src"])
        except:
            pass
    for item in tree.xpath("//link"):
        try:
            loaded.add(item.attrib["href"])
        except:
            pass

def logRequest(sender):
    """ log requests """
    if sender.host in loaded or sender.domain in visited:
        return

    visited.add(sender.domain)
    excluded = ['jpg', 'jpeg', 'js', 'json', 'gif', 'png', 'css', 'ico', 'js', 'svg', 'ttf', 'woff']
    extension = sender.path.split(".")[-1].lower()
    if extension in excluded:
        return

    log.info("requested: %s %s"%(sender.id, sender.host))