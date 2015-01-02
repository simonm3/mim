""" handles requests and fires signals for subscriber plugins

    usage:
        reactor.listenTCP(port, proxyserver.ProxyFactory())
"""
from tools.logs import log
import logging
from urlparse import urlparse
import os
import tldextract
from tools.tools import zips

from twisted.internet import reactor, ssl
from twisted.web import http
from proxyclient import ProxyClientFactory
from tools.pydispatch2 import Signal

gotRequest = Signal("gotRequest")

class Request(http.Request):
    """ proxy requests via HTTP 
        send signals that can be handled by subscriber plugins
    """
    
    # unique id to track each request in log and browser
    nextid = 1

    def __init__(self, channel, queued):
        http.Request.__init__(self, channel, queued)
        self.version ="HTTP/1.1"
        self.id = "R%s" % Request.nextid
        Request.nextid += 1

    def process(self):
        """ called when request completely received """

        # parse url
        parsed = urlparse(self.uri)
        self.scheme = parsed.scheme
        self.path = parsed.path
        self.query = parsed.query
        if self.query:
            self.pathquery = '%s?%s' % (self.path, self.query)
        else:
            self.pathquery = self.path
        self.host = self.getHeader("Host")

        # extract domain (e.g. used to identify sessions)
        try:
            ext = tldextract.extract(self.host)
            self.domain = ".{domain}.{suffix}".format(domain=ext.domain, suffix=ext.suffix)
        except:
            self.domain = ""
            log.exception("{id} Error in tldextract with {host}".format(id=self.id, host=self.host))

        self.content.seek(0,0)
        self.data = self.content.read()

        if log.getEffectiveLevel()==logging.DEBUG:
            self.setHeader("myid", self.id)

        #log.debug("%s RAW REQUEST:\n%s" % (self.id, self.getRequest()))
        
        gotRequest.send(sender=self)

        # callback may have finished the connection
        if self.finished:
            return

        # set supported compression methods
        try:
            oldcodes = self.getHeader('accept-encoding').split(',')
            newcodes = [code for code in oldcodes if code in zips.methods]
            self.requestHeaders.addRawHeader('Accept-Encoding', ','.join(newcodes))
        except:
            self.requestHeaders.addRawHeader('Accept-Encoding', '')

        log.debug("%s FINAL REQUEST:\n%s" % (self.id, self.getRequest()))

        # note ProxyClientFactory expects dict rather than headers type
        if self.scheme == "https":
            reactor.connectSSL(self.host, 443, \
                                ProxyClientFactory(self.method, self.pathquery, self.version, \
                                self.getAllHeaders(), self.data, self), \
                                ssl.ClientContextFactory())
        else:
            reactor.connectTCP(self.host, 80, \
                ProxyClientFactory(self.method, self.pathquery, self.version, \
                self.getAllHeaders(), self.data, self))

    def getRequest(self):
        """ returns request string """
        output = '\n'.join(["{k}: {v}".format(**locals()) for k, v in self.getAllHeaders().items()])
        return "{method} {pathquery} {version}\n{output}{data}"\
                .format(method=self.method, pathquery=self.pathquery, \
                        version=self.version,output=output, data=self.data)

    def getResponse(self):
        """ returns response string """
        output = "{clientproto} {code} {code_message}\r\n".format(clientproto=self.clientproto,
                    code=self.code, code_message=self.code_message)
        for name, values in self.responseHeaders.getAllRawHeaders():
            for value in values:
                output += "{name}: {value}\r\n".format(**locals())
        for cookie in self.cookies:
            output += 'Set-Cookie: {cookie}\r\n'.format(**locals())
        return output

class Proxy(http.HTTPChannel):
    """ http protocol """
    requestFactory = Request

class ProxyFactory(http.HTTPFactory):
    """ factory that creates a proxy for each request """
    protocol = Proxy

    def log(self, request):
        """ supress request logging """
        pass