""" log all requests """
from tools.logs import log

# callbacks
from tools.pydispatch2 import on
from mim.proxyserver import gotRequest
from mim.proxyclient import gotResponseTree

loaded = set()
visited = set()

log.info("loaded logreqiesstsf")

@on(gotResponseTree)
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

@on(gotRequest)
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