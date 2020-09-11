from flask import Blueprint, render_template, url_for, request, abort, session, flash
import ipaddress
from scripts.triptych_automate import getnewip, getnextid, deploy_container, to_json, createfwobj, inventorize

ctdeploy = Blueprint("ctdeploy", __name__)

import json

@ctdeploy.route('/', methods=['GET', 'POST'])
def index():
    # THIS HAPPENS WHEN WE FIRST REQUEST THE PAGE.
    if request.method == "GET":

        title = "Deploy Container"   
        return render_template("ctdeploy/index.html", title = title)
    
    # THIS HAPPENS WHEN WE HIT "DEPLOY CONTAINER" IN THE FORM.
    if (request.method == "POST") and "deploy_container" in request.form:
        
        ct_hostname    = request.form["ct_name"].lower()
        ct_disksize    = request.form["disksize"]
        ct_cpus        = request.form["ct_cpus"]
        ct_memory      = request.form["ct_mem"]
        ct_vlan        = request.form["ct_vlan"]
        ct_sshkey      = request.form["ct_sshkey"]
        ct_password    = request.form["ct_passwrd"] 
        ct_template    = request.form["ct_template"] 
        
        if "Ubuntu" in ct_template:
            ct_type = "ubuntu-container"

        ct_ip = getnewip(ct_vlan, ct_hostname, ct_type)
        ct_id = getnextid()

        deploy_status = deploy_container(
            ct_id,
            ct_ip,
            ct_hostname,
            ct_sshkey,
            ct_password,
            ct_disksize,
            ct_cpus,
            ct_memory,
            ct_vlan,
            ct_template
        )

        # Reformatting ct_ip a little to fit firewall object syntax
        ct_ip = ct_ip.split("/")[0] + "/32"
        fwobj_status = createfwobj(ct_hostname, ct_ip)

        # Triggering update of ansible inventory
        inventorize()

        # Some checking of object creation and container deployment status:
        if fwobj_status["status"] == "success":
            if ("UPID" in deploy_status["data"]) and ("vzcreate:{}:".format(str(ct_id)) in deploy_status["data"]):
                title = "Hey ho!"
                return render_template(
                    "ctdeploy/deploy-success.html", 
                    title = title,
                    deploy_status = deploy_status,
                    fwobj_status = fwobj_status,
                    ct_id = ct_id,
                    ct_ip = ct_ip,
                    ct_hostname = ct_hostname,
                    ct_disksize = ct_disksize,
                    ct_cpus = ct_cpus,
                    ct_memory = ct_memory,
                    ct_vlan = ct_vlan,
                    ct_template = ct_template
                    )