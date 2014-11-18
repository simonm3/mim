""" log all requests """
from logs import log

# callbacks
from tools.pydispatch2 import on
from mim.proxyserver import gotRequest
from mim.proxyclient import gotResponseTree

loaded = set()
visited = set()

@on(gotResponseTree)
def storeLoaded(sender, tree):
    """ store image and script links so they are not logged """
    for item in tree.xpath("//img|//script"):
        try:
            loaded.add(item.attrib["src"])
        except:
            pass

@on(gotRequest)
def logRequest(sender):
    """ log requests """
    if sender.uri in loaded or sender.uri in visited:
        return

    visited.add(sender.uri)
    excluded = ['jpg', 'jpeg', 'js', 'json', 'gif', 'png', 'css', 'ico', 'js', 'svg', 'woff']
    extension = sender.uri.split(".")[-1].lower()
    if extension in excluded:
        return

    log.info("requested: %s %s"%(sender.id, sender.uri))