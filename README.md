
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

## Whats it for?

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

Create a credentials.json file like this somewhere and tell the script where to find it via the credsdir variable (hard coded):

	{
		"ipamapikey":   "asdasdasdasdasdasdasdasdasdasdasd",
		"firewallip":   "10.0.0.1",
		"fwapitoken":   "asdasdqweqeqwedfghfghfghfgh",
		"ipamhost":     "ipam.example.com",
		"ipamuser":     "yourapiuser",
		"ipampasswd":   "yourapipassword",
		"pmhost":       "pm.example.com",
		"pmuser":       "root@pam",
		"pmpasswd":     "yourproxmoxpassword",
		"sshkey":       "ssh-rsa asdasdasdasdasdasd....asdasdasdasd something@somehost"
	}


	
    

