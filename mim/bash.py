""" wrapper for bash commands that parses their output into vars
    e.g. route() => {'iface': 'wlan0', 'router': '192.168.0.1'}
"""
import logging as log

from subprocess import check_output, STDOUT
import shlex
import socket

import types
def dump(obj, depth=4, l=""):
    #fall back to repr
    if depth<0: return repr(obj)
    #expand/recurse dict
    if isinstance(obj, dict):
        name = ""
        objdict = obj
    else:
        #if basic type, or list thereof, just print
        canprint=lambda o:isinstance(o, (int, float, str, unicode, bool, types.NoneType, types.LambdaType))
        try:
            if canprint(obj) or sum(not canprint(o) for o in obj) == 0: return repr(obj)
        except TypeError as e:
            pass
        #try to iterate as if obj were a list
        try:
            return "[\n" + "\n".join(l + dump(k, depth=depth-1, l=l+"  ") + "," for k in obj) + "\n" + l + "]"
        except TypeError as e:
            #else, expand/recurse object attribs
            name = (hasattr(obj, '__class__') and obj.__class__.__name__ or type(obj).__name__)
            objdict = {}
            for a in dir(obj):
                if a[:2] != "__" and (not hasattr(obj, a) or not hasattr(getattr(obj, a), '__call__')):
                    try: objdict[a] = getattr(obj, a)
                    except Exception as e: objdict[a] = str(e)
    if name.startswith("_"):
        return ""
    return name + "{\n" + "\n".join(l + repr(k) + ": " + dump(v, depth=depth-1, l=l+"  ") + "," for k, v in objdict.iteritems()) + "\n" + l + "}"

class bash(object):
    """ abstract base for commands that return mulitple lines for parsing """
    
    def __init__(self, *args):
        """ calls bash command and feeds each output line to parse method """
        
        # initialise
        self.startparse()

        # if just one arg then split string into a list
        if len(args) == 1:
            args = shlex.split(args[0])
        
        # execute and parse lines
        cmd = ["sudo", type(self).__name__]+list(args)
        #log.debug("bash=>%s"%' '.join(cmd))
        self._data = check_output(cmd, stderr=STDOUT)
        for line in self._data.splitlines():
            self.parse(line.decode())
      
    def __repr__(self):
        """ shows variables returned """
        out = {var : getattr(self,var) for var in vars(self) if not var.startswith("_")}
        return str(out)
  
    def startparse(self):
        """ initialise output variables """
        pass

    def parse(self, line):
        """ parse each line of output """
        pass
#####################################################
class iface(object):
    name = None
    ip = None
    mac = None
    router = None
    
    # wireless
    essid = None
    monitor = None

class ifconfig(bash):
    def startparse(self):
        self.ifaces = []

    def parse(self, line):
        if line and not line.startswith(" "):
            self._iface = iface()
            self._iface.name = line.split()[0]
            self.ifaces.append(self._iface)
       
        if line.strip().startswith("inet addr"):        
            self._iface.ip = line.split()[1].split(":")[1]

        if line.startswith(self._iface.name):
            self._iface.mac = line.split()[-1]
      
class iwconfig(bash):
    def startparse(self):
        self.ifaces = []

    def parse(self, line):
        if len(line) == 0:
            return
        if line[0] != ' ':
            self._iface = iface()
            self.ifaces.append(self._iface)
            iface.name = line[:line.find(' ')]
            if 'IEEE 802.11' in line:
                if "ESSID:\"" in line:
                    self._iface.essid = line.split(":")[-1]
            return
        if 'Mode:Monitor' in line:
            self._iface.monitor = True
 
class route(bash):
    def startparse(self):
        self.ifaces = []

    def parse(self, line):
        line = line.split()
        if line[0] == 'default' or line[0] == "0.0.0.0":
            self._iface = iface()
            self.ifaces.append(self._iface)
            self._iface.name = line[-1]
            self._iface.ip = line[1]

###################################################

class host(object):
    ip = None
    mac = None
    hw = None
    netbios = None

class arp(bash):
    def startparse(self):
        self.hosts = []

    def parse(self, line):
        self.host = host()
        self.hosts.append(self.host)
        line=line.split()
        self.host.ip = line[0]
        self.host.mac = line[2]

class nmap(bash):
    def startparse(self):
        self.hosts = []
        
    def parse(self, line):
        if line.startswith('Nmap scan report'):
            self.host = host()
            self.hosts.append(self.host)
            self.host.ip = line.split()[-1]

        if line.startswith('MAC'):
            line = line.split()
            self.host.mac = line[2]
            self.host.hw = line[3].replace("(","").replace(")","")

class nbtscan(bash):
    def startparse(self):
        self.hosts = []
    
    def parse(self, line):
        line = line.split()
        try:
            # test if valid ip address
            socket.inet_aton(line[0])
            self.host = host()
            self.hosts.append(self.host)
            self.host.ip = line[0]
            self.host.netbios = line[1]
        except (socket.error, IndexError):
            pass
##############################################