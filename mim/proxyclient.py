""" handles response from server and fires signals for subscriber plugins
"""

import logging as log

from twisted.web import proxy, http
from twisted.protocols.policies import TimeoutMixin
from lxml.html import fromstring, tostring, HTMLParser
from mim.tools.tools import zips

from mim.tools.pydispatch2 import Signal

gotResponseTree = Signal("gotResponseTree")
gotResponseText = Signal("gotResponseText")
gotResponseImage = Signal("gotResponseImage")

class ProxyClient(proxy.ProxyClient, TimeoutMixin):
    """ sends request to server and processes response """ 
    
    def __init__(self, command, rest, version, headers, data, father):
        proxy.ProxyClient.__init__(self, command, rest, version, headers, data, father)
        
        # response header info
        self.contentlength = None
        self.isHTML = False
        self.imagetype = None

        self.finished = False
        self.setTimeout(30)
        d = father.notifyFinish()
        d.addBoth(self.onRequestFinished)

    def connectionMade(self):
        # sometimes request disconnects BEFORE notifyFinish() has been trapped
        # could not find a way to detect this without referring to _disconnected
        if self.father._disconnected:
            log.debug("{id} Request disconnected before proxy client initialised" \
                                .format(id=self.father.id))
            self.finish()
            return

        # send request to web server
        proxy.ProxyClient.connectionMade(self)

    def onRequestFinished(self, message=None):
        """ callback from request.notifyFinish() """
        if message:
            log.debug("{id} Request finished with error\n{message}"\
                            .format(id=self.father.id, message=message))
        self.finish()

    def timeoutConnection(self):
        log.debug("%s Timed out"%self.father.id)
        TimeoutMixin.timeoutConnection(self)
    
    def finish(self):
        """ close server and client. can be called multiple times """
        if not self.father.finished and not self.father._disconnected:
            self.father.finish()

        if not self.finished:
            self.transport.loseConnection()
            self.setTimeout(None)
            self.finished = True

    ################ response ##############################################

    def handleHeader(self, key, value):
        """ manipulate and/or save response headers """
        if key.lower() == 'content-length':
            self.contentlength = value
        elif key.lower() in ("content-security-policy", "x-frame-options", \
                            "x-content-type-options", "strict-transport-security"):
            return
        elif key.lower() == 'set-cookie':
            # remove secure and httponly flags
            # NOTE have to parse cookies manually as Cookie library does not parse secure bit
            elems = value.split(";")
            value = ";".join([elem for elem in elems \
                             if elem.lstrip().rstrip().lower() \
                             not in ("secure", "httponly")])
        elif key.lower() == 'content-type':
            if value.find('image/') >= 0:
                self.imagetype = value.split("image/")[-1]
            elif value.find('html') >= 0:
                self.isHTML = True

        proxy.ProxyClient.handleHeader(self, key, value)
    
    def handleEndHeaders(self):
        # default waits for response forever e.g. on cached images
        if self.father.code in http.NO_BODY_CODES:
            self.finish()

    def handleResponsePart(self, content):
        if self.isHTML or self.imagetype:
            # buffer for processing in handleResponse
            http.HTTPClient.handleResponsePart(self, content)
        else:
            # write immediately
            proxy.ProxyClient.handleResponsePart(self, content)

    def handleResponseEnd(self):
        # call HTTPClient version which calls handleResponse
        # note ProxyClient assumes all written to client and closes the connection
        http.HTTPClient.handleResponseEnd(self)
    
    def handleResponse(self, content):
        try:
            # log response after handleHeader but before other changes
            log.debug("{id} RESPONSE {pathquery}\n{response}" \
                .format(id=self.father.id, pathquery=self.father.pathquery, \
                                    response=self.father.getResponse()))

            # make member variable to allow subscribers to change
            self.data = content

            # response with no body or already written in handleResponsePart e.g. js, css
            if not self.data:
                self.finish()
                return

            # process images
            if self.imagetype:
                gotResponseImage.send(sender=self)

            # process HTML from successful requests. Ignore HTML from 404 not found etc..
            elif self.isHTML and self.father.code == 200:
                self.processHTML()

            # if response used contentlength then update for new length
            # if no length header then twisted will use chunking
            if self.contentlength:
                self.father.setHeader('Content-Length', len(self.data))
            self.father.write(self.data)
            self.finish()
        except:
            log.exception("{id} Unhandled error in handleResponse\nuri={uri}\n".format \
                                (id=self.father.id, uri=self.father.uri))
    
    ########################################################################################################################

    def processHTML(self):
        """ decodes data; calls callbacks; recodes data """
        zipencoding = None
        try:
            zipencoding = self.father.responseHeaders.getRawHeaders("Content-Encoding")[-1]
            self.data = zips(zipencoding).decompress(self.data)
        except:
            zipencoding = None

        if len(self.data) > 1 \
            and not self.data == "<!-- default response -->":
            # use encoding header if available. default is meta tag but not always present.
            # assumes unicode. could enforce with unicodedammit but very slow and never found necessary
            try:
                encoding = self.father.responseHeaders.getRawHeaders \
                                ("content-type")[-1].split('charset=')[1].split(";")[0]
            except:
                encoding = "ISO-8859-1"
            try:
                tree = fromstring(self.data, parser=HTMLParser(encoding=encoding))
                gotResponseTree.send(sender=self, tree=tree)
                self.data = tostring(tree, encoding=encoding)
            except:
                log.exception("{id} Content not parseable len={len} enc={enc}\n{data}"\
                    .format(id=self.father.id, len=len(self.data), enc=encoding, data=self.data[:100]))
         
        # gotResponseTree used by most plugins but but sometimes may want to see raw text
        gotResponseText.send(sender=self)

        if zipencoding:
            self.data = zips(zipencoding).compress(self.data)

class ProxyClientFactory(proxy.ProxyClientFactory):
    protocol = ProxyClient