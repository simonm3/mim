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

def fwreset():
    """ reset firewall settings """
    su("sysctl net.ipv4.ip_forward=0")

    # reset defaults for filter, nat and mangle
    su("iptables -P INPUT ACCEPT")
    su("iptables -P FORWARD ACCEPT")
    su("iptables -P OUTPUT ACCEPT")
    su("iptables -t nat -P PREROUTING ACCEPT")
    su("iptables -t nat -P POSTROUTING ACCEPT")
    su("iptables -t nat -P OUTPUT ACCEPT")
    su("iptables -t mangle -P PREROUTING ACCEPT")
    su("iptables -t mangle -P OUTPUT ACCEPT")

    # flush rules
    su("iptables -F")
    su("iptables -t nat -F")
    su("iptables -t mangle -F")

    # erase chains
    su("iptables -X")
    su("iptables -t nat -X")
    su("iptables -t mangle -X")

    # set new rules
    su("iptables -A INPUT -i lo -j ACCEPT")

    log.info("iptables has been reset")