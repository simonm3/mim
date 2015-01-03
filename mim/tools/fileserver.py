#!/usr/bin/python

""" simple file server using twisted 

    run from command prompt on port 8000
    or reactor.listenTCP(FILEPORT, fileserver.Site(fileserver.Data()))
"""
import logging as log

from twisted.web.server import Site
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.python.filepath import FilePath
import mimetypes
from mim.tools.tools import zips, setTitle
import os

class Data(Resource):
    isLeaf = True

    def __init__(self, datafolder):
        self.data = FilePath(datafolder)

    def render_GET(self, request):
        # check directory traversal. replace child with preauthChild to allow subfolders
        try:
            path = self.data.child(request.path.lstrip("/"))
        except:
            log.warning("Directory traversal attempt %s"%request.path)
            request.setResponseCode(404)
            return "File not found %s"%request.path
    
        # get content
        try:
            with path.open('rb') as f:
                content = f.read()
        except:
            log.warning("File not found %s"%path)
            request.setResponseCode(404)
            return "File not found %s"%path
        
        # set headers
        request.setResponseCode(200)
        if "Accept-Encoding" in request.headers:
            # check codings that are both accepted and which we can apply
            oldcodes = request.headers["Accept-Encoding"].split(",") or []
            newcodes = [code for code in oldcodes if code in zips.methods]
            if len(newcodes) > 0:
                code = newcodes[0]
                request.setHeader('content-encoding', code)
                content=zips(code).compress(content)
        request.setHeader('Content-type', mimetypes.guess_type(path.path)[0])
        request.setHeader('Content-length', len(content))
        request.setHeader('Cache-Control',  'max-age=604800, public')

        return content

if __name__ == '__main__':
    setTitle(__file__)

    port=8000
    reactor.listenTCP(port, Site(Data(os.getcwd()+"/data")))
    log.info("Serving on %s."%port)
    reactor.run()