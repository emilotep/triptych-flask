from class_proxmoxapi import pmapi
from class_phpipam import phpipamapi
from class_fortiapi import fortiapi
import urllib3
import json
import argparse
import sys

# Disabling SSL warnings
urllib3.disable_warnings()

# Location of credentials.json file
credsdir = "/opt/scripts/"

# Building credentials from file.
try:
    with open(credsdir+"credentials.json","r") as f1:
        credentials = json.load(f1)

    ipamapikey = credentials["ipamapikey"]
    firewallip = credentials["firewallip"]
    fwapitoken = credentials["fwapitoken"]
    ipamhost   = credentials["ipamhost"]
    ipamuser   = credentials["ipamuser"]
    ipampasswd = credentials["ipampasswd"]
    pmhost     = credentials["pmhost"]
    pmuser     = credentials["pmuser"]
    pmpasswd   = credentials["pmpasswd"]
    # If you don't use key based ssh (WHICH YOU SHOULD!!), just use password.
    try:
        sshkey     = credentials["sshkey"]
    except:
        print("No ssh public key found in credentials file, continuing without.")
        sshkey = ""
    # Checking if there is a default container password in credentials.json
    try:
        ctpassword = credentials["ctpassword"]
    except Exception as e:
        ctpassword = False
        print("Found no container password in credentials file... attempting to move on. ", e)

except FileNotFoundError as e:
    print("There is no credentials file in your scriptdir, or it is not readable.", e)
    ipamapikey = input("Provide IPAM api key                         :")
    firewallip = input("Provide firewall ip or hostname              :")
    fwapitoken = input("Provide firewall api token                   :")
    ipamhost   = input("Provide phpipam hostname or ip               :")
    ipamuser   = input("Provide phpipam username                     :")
    ipampasswd = input("Provide phpipam password                     :")
    pmhost     = input("Provide proxmox ip or hostname               :")
    pmuser     = input("Provide proxmox username@realm like root@pam :")
    pmpasswd   = input("Provide proxmox password                     :")
    sshkey     = input("Provide ssh key to container (blank if none) :")
    ctpassword = input("Provide ssh password for container           :")

# Defining arguments
argparser = argparse.ArgumentParser()

argparser.add_argument(
    "-n",
    "--vmname",
    dest="vmname",
    action="store",
    required=False,
    help="What host name to use",
)

argparser.add_argument(
    "-d",
    "--domain",
    dest="domain",
    action="store",
    required=False,
    help="What domain name to use",
    default="yllenet.com"
)

argparser.add_argument(
    "-p",
    "--privileged_ct",
    dest="privileged_ct",
    action="store_true",
    required=False,
    help="Create privileged container",
    default=False
)

argparser.add_argument(
    "-s",
    "--password",
    dest="password",
    action="store",
    required=False,
    help="Password to use for container",
    default=False,
)

options = argparser.parse_args()

vmname        = options.vmname
domain        = options.domain
privileged_ct = options.privileged_ct
# If password provided at runtime, the default (stored in credentials.json) will be overridden.
if options.password:
    ctpassword = options.password
elif not ctpassword:
    raise Exception("No container password provided at runtime and none found in credentials.json!")
else:
    pass

# Setting firewall object name/hostname to use with phpipam.
objname      = "{}.{}".format(vmname, domain)

# Silly helper function for pretty output
def to_json(input):
    return json.dumps(input, indent = 2, sort_keys=True)

# ############# IPAM STUFF ############# 
# For now we will have to log into PHPIpam to make the A-record for the host.
# Will be possible to automate with powerdnsapi
# To actually assign the address, use "POST" method instead of "GET"
# Needs a subnet ID in phpipam, which is hardcoded right now
# http://ipam.yllenet.com/index.php?page=subnets&section=1&subnetId=10 <== subnet id is 10
 
ylleipam = phpipamapi(ipamhost, ipamapikey)
result = ylleipam.requestaddress("10", objname, method="GET")
newip = result["data"]
print(newip)

# ############# PROXMOX STUFF #############
# Request next ctid from proxmox
proxmox = pmapi(pmhost, pmuser, pmpasswd)
ctid = proxmox.getnextid()
quit(ctid)

proxmox.createct(
    ctid,
    newip,
    "apitest01",
    password=ctpassword,
    sshkey=sshkey,
    
    )

# ############# FIREWALL STUFF #############
# Will have to add functionality to check if the object exists.
firewall = fortiapi(firewallip, fwapitoken)

# Determine if we need to create a new object or update it.
fwaddexists = firewall.sendget("firewall/address/"+objname)
if fwaddexists["http_status"] == 404:
    fwaddexists = False
elif fwaddexists["http_status"] == 200:
    fwaddexists = True
else:
    raise Exception("Couldn't handle response from firewall, was http status other than 404 or 200? Response was :\n"+to_json(fwaddexists))

if fwaddexists == False:
    firewall.createaddress(
        name=objname,
        subnet=newip+"/32",
        comment="Autocreated by Triptych",
        )
else:
    firewall.updateaddress(
        name=objname,
        subnet=newip+"/32",
        comment="Autocreated by Triptych",
        )

# print(to_json(result))

