import requests
import json
import logging
import netaddr

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class pmapi():

    def __init__(self, host, user, passwd, **kwargs):
        
        self.baseurl = "https://{}:8006/api2/json/".format(host)
        self.authurl = self.baseurl+"access/ticket"
        self.authdata = {
            "username": user,
            "password": passwd,
        }
        self.nodeid = "pve"

        # We "log on" and get the csrf token and the ticket
        result = requests.post(self.authurl, data=self.authdata, verify=False).json()
        self.csrftoken = result["data"]["CSRFPreventionToken"]
        self.ticket = result["data"]["ticket"]
        self.authcookie = {
            "PVEAuthCookie": self.ticket 
        }
        self.csrfheader = {
            "CSRFPreventionToken": self.csrftoken
        }
        return

    def getnextid(self):

        # This simply returns 
        url = self.baseurl+"cluster/nextid"
        result = requests.get(url,cookies=self.authcookie, verify=False).json()
        return result["data"]

    def getct(self, vmid):
        url = self.baseurl+"nodes/pve/lxc/{}".format(vmid)

        result = requests.get(url,cookies=self.authcookie, verify=False).json()
        return result

    def createct(self, vmid, ip, vmname, **kwargs):
        # IP and GW from ip
        if "/" not in ip:
            raise Exception("ip needs to be in CIDR notation, ex: 10.0.0.10/24")
        self.ctip = ip
        # Setting gateway ip from ip in a dirty way.
        # self.ctgw = ip.split(".")[0:3]
        # self.ctgw.append("1")
        # self.ctgw = ".".join(self.ctgw)
        network = netaddr.IPNetwork(ip)
        self.ctgw = str(network[1])
        self.net0string = "bridge=vmbr0,name=eth0,ip="+self.ctip+",gw="+self.ctgw
        # VMID
        self.vmid = int(vmid)
        # Checking kwargs for some stuff, setting some defaults
        # Template
        if "template" in kwargs:
            self.template = kwargs["template"]
        else:
            self.template = "local:vztmpl/ubuntu-18.04-standard_18.04.1-1_amd64.tar.gz"
        # Proxmox node
        if "node" in kwargs:
            self.node = kwargs["node"]
        else:
            self.node = "pve"
        # CT Password
        if "password" in kwargs:
            self.ctpasswd = kwargs["password"]
        else:
            self.ctpasswd = "password123"
        # SSH Keys
        if "sshkey" in kwargs:
            self.sshkey = kwargs["sshkey"]
        else:
            self.sshkey = "" 
        # Storage
        if "storage" in kwargs:
            self.storage = kwargs["storage"]
        else:
            self.storage = "local-lvm"
        # Disk
        if "disk" in kwargs:
            self.ctdisk = str(kwargs["disk"])
        else:
            self.ctdisk = "10"
        # CPUs
        if "cpus" in kwargs:
            self.ctcpus = int(kwargs["cpus"])
        else:
            self.ctcpus = 1
        # Mem
        if "mem" in kwargs:
            self.ctmem = int(kwargs["mem"])
        else:
            self.ctmem = 512 # 512 is the default for proxmox.
        # VLAN
        if "vlan" in kwargs:
            self.ctvlan = kwargs["vlan"]
        else:
            self.ctvlan = ""
        # DNS domain
        if "domain" in kwargs:
            self.domain = kwargs["domain"]
        else:
            self.domain = "yllenet.com"
        # DNS server
        if "dnsserver" in kwargs:
            self.dnsserver = kwargs["dnsserver"]
        else:
            self.dnsserver = "10.20.20.13"

        url = self.baseurl+"nodes/{}/lxc".format(self.node)

        self.payload = {
            "cores": self.ctcpus,
            "hostname": vmname,
            "memory": self.ctmem,
            "nameserver": self.dnsserver,
            "net0": self.net0string,
            # "node": self.node, # Probably not needed.
            "ostemplate": self.template,
            # "pool": "", # Probably not needed.
            "rootfs": "{}:{}".format(self.storage,self.ctdisk),
            # "rootfs": "volume={} size={}".format(self.storage, self.ctdisk),
            "searchdomain": self.domain,
            "swap": 512, # 512 is the default for proxmox.
            "unprivileged": 0,
            "start": 1,
            "onboot": 1,
            "password": self.ctpasswd,
            "ssh-public-keys": self.sshkey,
            "vmid": self.vmid,
        }
        # quit(self.payload)
        result = requests.post(url,cookies=self.authcookie, verify=False, data=self.payload, headers=self.csrfheader).json()
        return result