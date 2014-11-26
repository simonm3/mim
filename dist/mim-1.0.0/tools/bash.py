""" wrapper for bash commands that parses their output into vars
    e.g. route() => {'iface': 'wlan0', 'router': '192.168.0.1'}
"""
from subprocess import call, check_output, STDOUT
import shlex
import socket

class bash(object):
    """ abstract base for each command """
    
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

class ifconfig(bash):
    def startparse(self):
        self.localhost = None
        self.wlanip = None
        self.wlanmac = None

    def parse(self, line):
        if line and not line.startswith(" "):
            self._iface = line.split()[0]
        
        if self._iface == "lo":
            if line.strip().startswith("inet addr"):
                self.localhost = line.split()[1].split(":")[1]
        
        elif self._iface.startswith("wlan"):
            if line.startswith("wlan"):
                self.wlanmac = line.split()[4]
            if line.strip().startswith("inet addr"):
                self.wlanip = line.split()[1].split(":")[1]

class iwconfig(bash):
    def startparse(self):
        # interface is key to dict with attributes essid, monitor
        self.interfaces = dict()

    def parse(self, line):
        if len(line) == 0:
            return
        if line[0] != ' ':
            self._iface = line[:line.find(' ')]
            self.interfaces[self._iface] = dict()
            if 'IEEE 802.11' in line:
                if "ESSID:\"" in line:
                    self.interfaces[self._iface]["essid"] = line.split(":")[-1]
            return
        if 'Mode:Monitor' in line:
            self.interfaces[self._iface]["monitor"]=True
 
class route(bash):
    def startparse(self):
        self.iface = None
        self.router = None

    def parse(self, line):
        line = line.split()
        if line[0] == 'default' or line[0] == "0.0.0.0":
            self.iface = line[-1]
            self.router = line[1]

class arp(bash):
    def startparse(self):
        # ip is key
        self.mac = dict()

    def parse(self, line):
        line=line.split()
        self.mac[line[0]]= line[2]

class nmap(bash):
    def startparse(self):
        # ip is key
        self.mac = dict()
        self.hw = dict()
        self.ip = set()
    
    def parse(self, line):
        if line.startswith('Nmap'):
            self._ip = line.split()[-1]
            try:
                socket.inet_aton(self._ip)
                self.ip.add(self._ip)
            except socket.error:
                pass
        if line.startswith('MAC'):
            line = line.split()
            self.mac[self._ip] = line[2]
            self.hw[self._ip] = line[3].replace("(","").replace(")","")

class nbtscan(bash):
    def startparse(self):
        # dict with ip = windows netbios name
        self.netbios = dict()
    
    def parse(self, line):
        line = line.split()
        try:
            # test if valid ip address
            socket.inet_aton(line[0])
            self.netbios[line[0]] = line[1]
        except (socket.error, IndexError):
            pass
