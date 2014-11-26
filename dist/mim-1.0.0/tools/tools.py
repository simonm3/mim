""" miscellaneous tools """    

from logs import log
import os
from subprocess import call
import shlex
import zlib

devnull = open(os.devnull, 'w')
def su(cmd):
    """ sudo cmd with stdout=devnull """
    call(shlex.split("sudo %s"%cmd), stdout=devnull)

def setTitle(title):
    """ set title on linux terminal window """
    os.system('echo "\033]0;%s\007"'%title)

class zips(object):
    """ compress/decompress using zlib, gzip, deflate 
        e.g. zips("zlib").compress(text)
             zips("zlib").decompress(text)
    """
    methods = dict(deflate = -zlib.MAX_WBITS,
                   zlib = zlib.MAX_WBITS,
                   gzip = zlib.MAX_WBITS | 16)
    
    def __init__(self, method):
        self.method = method
        self.obj = zlib.compressobj(9, zlib.DEFLATED, self.methods[method]) 

    def compress(self, text):
        return self.obj.compress(text) + self.obj.flush()

    def decompress(self, text):
        return zlib.decompress(text, self.methods[self.method])