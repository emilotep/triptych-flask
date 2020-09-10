
# Triptych automation portal
Why "Triptych" you ask? Well... I thought it sounded cool.

## Credit where credit is due

The Flask part is based on the Flask Template repo here: https://github.com/emieli/Flask-Template

## Versions:

Proxmox Virtual Environment 6.1-7
PHPIpam Dev version 1.5
FortiOS 6.2.5
Python 3.7

Relevant python modules:

	python3 -m pip freeze
	....
	Flask==1.1.2
	Jinja2==2.11.2
	netaddr==0.8.0
	requests==2.24.0
	urllib3==1.25.10
	virtualenv==20.0.31
	Werkzeug==1.0.1
	...

## What's it for?

Automating deployment of containers in Proxmox, assigning IP from PHPIpam, updating DNS records (PHPIpam PowerDns integration) and creating firewall objects in a Fortinet firewall.
PHEW!

Some defaults are hardcoded in the classes, read through and edit what you want. You can probably glean some info about my environment from the defaults but whatever...

## stuff you need to know about your environment:

* proxmox ip/user/password/node id
* firewall ip/api user token
* phpipam application id and api key + user/password
* phpipam subnet id that you want to use
* probably more shit.

## stuff about credentials

Create a credentials.json file like this somewhere and tell the script where to find it via the credsdir variable (hard coded, see below):

	{
		"ipamapikey":   "asdasdasdasdasdasdasdasdasdasdasd",
		"firewallip":   "10.0.0.1",
		"fwapitoken":   "asdasdqweqeqwedfghfghfghfgh",
		"ipamhost":     "ipam.example.com",
		"ipamuser":     "yourapiuser",
		"ipampasswd":   "yourapipassword",
		"pmhost":       "pm.example.com",
		"pmuser":       "root@pam"
	}


## Hardcoded stuff you need to think about

* the "credsdir" variable provides the absolute path to the credentials.json file and is hard coded in a few places in triptych-automate.py, change it to fit your environment. 
* dnsserver for containers is also hard coded in triptych-automate.py, change it to fit your env.
* the proxmox node id can be supplied to the __init__ of proxmoxapi but defaults to fit my env. Might consider changing that.
* self.net0string in class_proxmoxapi.py is hard coded to fit my env. might want to look at it.
* self.template in class_proxmoxapi.py can be provided with kwargs, but defaults to my default template. might want to change that to fit you.
* self.storage in class_proxmoxapi.py
* self.domain in class_proxmoxapi.py defaults to fit my env.
* self.dnsserver in class_proxmoxapi.py defaults to fit my env.
* object type in class_fortiapi.py is hard coded to ipmask, functionality can be extended here.
* devicetyp in class_phpipam.py has a hard coded parameter in the payload which is a custom field in my IPAM. remove this or create the field as a custom address field or it will break your balls.

Other than that it's probably not too bad, the templates in app/templates/ctdeploy have placeholders and defaults that you might want to change as well.

