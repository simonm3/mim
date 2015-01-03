""" converts https links to http but when followed proxies via SSL """

import logging as log

from urlparse import urlparse

# callbacks
from mim.tools.pydispatch2 import on
from mim.proxyserver import gotRequest
from mim.proxyclient import gotResponseTree, gotResponseText

# urls converted https to http
SSL = set()

@on(gotRequest)
def proxyViaSSL(sender):
    if isSSL(sender.uri):
        log.debug("%s Request sent by proxy via SSL %s"%(sender.id, sender.uri))
        sender.scheme = "https"

@on(gotResponseTree)
def strip(sender, tree):
    """ replace ssl links with http """
    # works with lxml.html
    tree.rewrite_links(removeHTTPS)
    
    # works with lxml.etree
    """for elem in tree.xpath("//a"):
        try:
            elem.attrib["href"] = removeHTTPS(elem.attrib["href"])
        except:
            pass
    """
@on(gotResponseText)
def stripText(sender):
    """ replace https not in links/style tags e.g. in script tags
        NOTE this may prevent some scripts from running correctly
    """
    # note do not change location header as causes redirect loops

    # remove from text
    text = sender.data
    startlink = text.find("https://", 0)
    while startlink >= 0:
        endlink = text.find(" ", startlink + 1)
        link = text[startlink : endlink]
        link = removeHTTPS(link)
        text = text[0:startlink] + link + text[endlink:]
        startlink = text.find("https://", endlink)
    sender.data = text

def isSSL(uri):
    """ test if link was SSL converted to http """
    for elem in SSL:
        if uri.startswith(elem):
            return True
    return False

def removeHTTPS(link):
    """ converts ssl link to http """

    # note links are case sensitive!
    try:
        parsed = urlparse(link)
    except:
        # sometimes no space at end of links in scripts
        # could parse with regex to avoid these errors
        return link
    if parsed.scheme.lower() == "https":
        link = "http://"+link[8:]
        SSL.add(link)
    return link