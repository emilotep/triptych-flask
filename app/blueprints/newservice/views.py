from flask import Blueprint, render_template, url_for, request, abort, session, flash
import ipaddress
import socket
import time
import os

from scripts.class_phpipam import *

newservice = Blueprint("newservice", __name__)

import json

# Silly helper function for pretty output
def to_json(input):
    return json.dumps(input, indent = 2, sort_keys=True)

@newservice.route('/', methods=['GET', 'POST'])
def index():
    # THIS HAPPENS WHEN WE FIRST REQUEST THE PAGE.
    if request.method == "GET":

        title = "Deploy New Network Service"
        return render_template("newservice/index.html", title = title)

    # THIS HAPPENS WHEN WE HIT "DEPLOY CONTAINER" IN THE FORM.

    if (request.method == "POST") and "deploy_service" in request.form:
        vlan_range = range(100,199)

        credsdir = "/opt/scripts/"
        try:
            with open(credsdir+"credentials.json","r") as f1:
                credentials = json.load(f1)
                ipamapikey = credentials["ipamapikey"]
                ipamhost   = credentials["ipamhost"]
                ipamuser   = credentials["ipamuser"]
                ipampasswd = credentials["ipampasswd"]
        except FileNotFoundError as e:
            print(e)

        myipam = phpipamapi(ipamhost, ipamapikey, ipamuser, ipampasswd)

        ipam_vlans = myipam.getvlans()["data"]
        ipam_vrfs = myipam.getvrfs()["data"]
        ipam_subnets = myipam.getsubnets()["data"]

        with open("/opt/scripts/debug/triptychdebug.json", "w") as f:
            f.write(to_json(ipam_vlans))
            f.write("\n")
            f.write(to_json(ipam_vrfs))
            f.write("\n")
            f.write(to_json(ipam_subnets))
            f.write("\n")
        # quit()
        vlanlist = []
        for vlan in ipam_vlans:
            vlanlist.append(vlan["number"])

        for i in vlan_range:
            if str(i) in vlanlist:
                continue
            else:
                vlan_number = str(i)
                break

        service_name = "{}_{}".format(request.form["zone"], vlan_number)

        result = myipam.createvlan(
            vlan_number = vlan_number,
            vlan_name = service_name,
            vlan_location = "DC1",
            vlan_tags = request.form["zone"]
        )



        vrfmap = {
            "WEB": "3",
            "APP": "1",
            "DB": "2"
        }

        """ this is the result when creating a vlan:
        {
        "code": 201,
        "id": "30",
        "message": "Vlan created",
        "success": true,
        "time": 0.008
        }
        """

        ipam_vlan_id = result["id"]

        ip_subnet = "10.100.{}.0".format(vlan_number)

        result = myipam.createsubnet(
            ip_subnet = ip_subnet,
            subnet_name = service_name,
            vlan_id = ipam_vlan_id,
            vrf_id = vrfmap[request.form["zone"].upper()]
        )

        with open("/opt/scripts/debug/triptychdebug.json", "w") as f:
            f.write(to_json(result))

        os.system("python3 /opt/scripts/ansible/avd_dc1/avd_sync.py")

        return render_template(
            "newservice/deploy-success.html",
            ip_subnet = ip_subnet,
            vlan_number = vlan_number,
            vlan_name = service_name,
            zone = request.form["zone"]
        )
