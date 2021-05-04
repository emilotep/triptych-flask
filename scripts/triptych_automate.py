from scripts.class_proxmoxapi import pmapi
from scripts.class_phpipam import phpipamapi
from scripts.class_fortiapi import fortiapi
import urllib3
import json
# import argparse
import sys
import os

# Disabling SSL warnings
urllib3.disable_warnings()

# Location of credentials.json file


# Building credentials from file.
# try:
#     with open(credsdir+"credentials.json","r") as f1:
#         credentials = json.load(f1)

#     ipamapikey = credentials["ipamapikey"]
#     firewallip = credentials["firewallip"]
#     fwapitoken = credentials["fwapitoken"]
#     ipamhost   = credentials["ipamhost"]
#     ipamuser   = credentials["ipamuser"]
#     ipampasswd = credentials["ipampasswd"]
#     pmhost     = credentials["pmhost"]
#     pmuser     = credentials["pmuser"]
#     pmpasswd   = credentials["pmpasswd"]
    # If you don't use key based ssh (WHICH YOU SHOULD!!), just use password.
    # try:
    #     sshkey     = credentials["sshkey"]
    # except:
    #     print("No ssh public key found in credentials file, continuing without.")
    #     sshkey = ""
    # # Checking if there is a default container password in credentials.json
    # try:
    #     ctpassword = credentials["ctpassword"]
    # except Exception as e:
    #     ctpassword = False
    #     print("Found no container password in credentials file... attempting to move on. ", e)

# except FileNotFoundError as e:
#     print(e)
    # print("There is no credentials file in your scriptdir, or it is not readable.", e)
    # ipamapikey = input("Provide IPAM api key                         :")
    # firewallip = input("Provide firewall ip or hostname              :")
    # fwapitoken = input("Provide firewall api token                   :")
    # ipamhost   = input("Provide phpipam hostname or ip               :")
    # ipamuser   = input("Provide phpipam username                     :")
    # ipampasswd = input("Provide phpipam password                     :")
    # pmhost     = input("Provide proxmox ip or hostname               :")
    # pmuser     = input("Provide proxmox username@realm like root@pam :")
    # pmpasswd   = input("Provide proxmox password                     :")
    # sshkey     = input("Provide ssh key to container (blank if none) :")
    # ctpassword = input("Provide ssh password for container           :")

# Defining arguments
# argparser = argparse.ArgumentParser()

# argparser.add_argument(
#     "-n",
#     "--vmname",
#     dest="vmname",
#     action="store",
#     required=False,
#     help="What host name to use",
# )

# argparser.add_argument(
#     "-d",
#     "--domain",
#     dest="domain",
#     action="store",
#     required=False,
#     help="What domain name to use",
#     default="yllenet.com"
# )

# argparser.add_argument(
#     "-p",
#     "--privileged_ct",
#     dest="privileged_ct",
#     action="store_true",
#     required=False,
#     help="Create privileged container",
#     default=False
# )

# argparser.add_argument(
#     "-s",
#     "--password",
#     dest="password",
#     action="store",
#     required=False,
#     help="Password to use for container",
#     default=False,
# )

# options = argparser.parse_args()

# vmname        = options.vmname
# domain        = options.domain
# privileged_ct = options.privileged_ct
# If password provided at runtime, the default (stored in credentials.json) will be overridden.
# if options.password:
#     ctpassword = options.password
# elif not ctpassword:
#     raise Exception("No container password provided at runtime and none found in credentials.json!")
# else:
#     pass

# Setting firewall object name/hostname to use with phpipam.

# Silly helper function for pretty output
def to_json(input):
    return json.dumps(input, indent = 2, sort_keys=True)

# ############# IPAM STUFF ############# 
# For now we will have to log into PHPIpam to make the A-record for the host.
# Will be possible to automate with powerdnsapi
# To actually assign the address, use "POST" method instead of "GET"
# Needs a subnet ID in phpipam, which is hardcoded right now
# http://ipam.example.com/index.php?page=subnets&section=1&subnetId=10 <== subnet id is 10

def getnewip(vlan, hostname, cttype):
    credsdir = "/opt/scripts/"
    try:
        with open(credsdir+"credentials.json","r") as f1:
            credentials = json.load(f1)
            ipamapikey = credentials["ipamapikey"]
            ipamhost   = credentials["ipamhost"]
            ipamuser   = credentials["ipamuser"]
            ipampasswd = credentials["ipampasswd"]
    except FileNotFoundError as e:
        return(e)
    
    if vlan == "SERVER":
        subnetid = "10"
    elif vlan == "DMZ":
        subnetid = "10"
    else:
        subnetid = "10"
    # Getting a new IP from the subnet + the subnet mask and adding them to the ctip variable.
    ylleipam = phpipamapi(ipamhost, ipamapikey, ipamuser, ipampasswd)
    # Need to add functionality to add custom_device-type to request.
    result = ylleipam.requestaddress(subnetid, hostname.lower(), devicetype="ubuntu-container", method="POST")
    newip = result["data"]
    subnetinfo = ylleipam.getonesubnet(subnetid)
    netmask = subnetinfo["data"]["mask"]
    ctip = "{}/{}".format(newip, netmask)
    return ctip

# ############# PROXMOX STUFF #############
# Request next ctid from proxmox

def getnextid():
    credsdir = "/opt/scripts/"
    try:
        with open(credsdir+"credentials.json","r") as f1:
            credentials = json.load(f1)
            pmhost     = credentials["pmhost"]
            pmuser     = credentials["pmuser"]
            pmpasswd   = credentials["pmpasswd"]
    except FileNotFoundError as e:
        return(e)
    
    proxmox = pmapi(pmhost, pmuser, pmpasswd)
    ctid = proxmox.getnextid()
    return ctid

def deploy_container(ctid, ctip, hostname, sshkey, ctpassword, disk, cpus, mem, vlan, template, **kwargs):
    credsdir = "/opt/scripts/"
    try:
        with open(credsdir+"credentials.json","r") as f1:
            credentials = json.load(f1)
            pmhost     = credentials["pmhost"]
            pmuser     = credentials["pmuser"]
            pmpasswd   = credentials["pmpasswd"]
    except FileNotFoundError as e:
        return(e)
    
    # I have only one template at present, here you can customize a bit.
    if template == "Ubuntu_18_04":
        template = "local:vztmpl/ubuntu-18.04-standard_18.04.1-1_amd64.tar.gz"
    

    ctname = hostname.split(".")[0].upper()
    domain = hostname.split(".")[1:]
    domain = ".".join(domain)
    # return ctname, domain, template

    if vlan == "DMZ":
        vlan = "50"
    else:
        vlan = ""

    proxmox = pmapi(pmhost, pmuser, pmpasswd)
    result = proxmox.createct(
        ctid,
        ctip,
        ctname,
        password=ctpassword,
        sshkey=sshkey,
        template=template,
        # node="pve" # Using default value in class
        # storage="local-lvm" # Using default storage in class
        disk=disk,
        cpus=cpus, # Default #CPUs in class = 1
        mem=mem, # Default mem amount in class = 512
        vlan=vlan, 
        domain=domain, # From arguments
        dnsserver="10.20.20.13", # This is default but providing it anyway.
        )
    print(to_json(result))
    return result

# ############# FIREWALL STUFF #############
def createfwobj(hostname, ctip):
    credsdir = "/opt/scripts/"
    try:
        with open(credsdir+"credentials.json","r") as f1:
            credentials = json.load(f1)
            firewallip = credentials["firewallip"]
            fwapitoken = credentials["fwapitoken"]
    except FileNotFoundError as e:
        return(e)
    
    firewall = fortiapi(firewallip, fwapitoken)

    # Determine if we need to create a new object or update it.
    fwaddexists = firewall.sendget("firewall/address/"+hostname)
    if fwaddexists["http_status"] == 404:
        fwaddexists = False
    elif fwaddexists["http_status"] == 200:
        fwaddexists = True
    else:
        raise Exception("Couldn't handle response from firewall, was http status other than 404 or 200? Response was :\n"+to_json(fwaddexists))

    # Create
    if fwaddexists == False:
        result = firewall.createaddress(
            name=hostname,
            subnet=ctip+"/32",
            comment="Autocreated by Triptych",
            )
    # Update
    else:
        result = firewall.updateaddress(
            name=hostname,
            subnet=ctip+"/32",
            comment="Autocreated by Triptych",
            )
    
    return result

# ########### POWERDNS STUFF #############
# I couldn't get my class for powerdns API to work so i did it the reaaaaaally ugly fucked-up way.

def pdnsupdate(hostname, ip, zone):

    credsdir = "/opt/scripts/"
    try:
        with open(credsdir+"credentials.json","r") as f1:
            credentials = json.load(f1)

        pdnshost = credentials["pdnshost"]
        pdnsapikey = credentials["pdnsapikey"]

    except FileNotFoundError as e:
        print(e)

    if zone[-1] != ".":
        zone = zone+"."
    
    if hostname[-1] != ".":
        if zone[0::-1] not in hostname:
            hostname = hostname + "." + zone
        else:
            hostname = hostname + "."
    
    commandstring = "curl -X PATCH --data '{\"rrsets\": [ {\"name\": \""+hostname+"\", \"type\": \"A\", \"ttl\": 900, \"changetype\": \"REPLACE\", \"records\": [ {\"content\": \""+ip+"\", \"disabled\": false } ] } ] }' -H 'X-API-Key: "+pdnsapikey+"' http://"+pdnshost+":8081/api/v1/servers/localhost/zones/"+zone
    os.system(commandstring)

# Calling my ansible inventory script.
# Sorry for doing it this way but it was the laziest solution.
def inventorize():
    os.system("python3 /opt/scripts/inventory-scripts/inventorize.py")
