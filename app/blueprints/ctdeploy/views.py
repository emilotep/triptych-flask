from flask import Blueprint, render_template, url_for, request, abort, session, flash
import ipaddress
from scripts.triptych_automate import getnewip, getnextid, deploy_container, to_json, createfwobj

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
        
        ct_hostname    = request.form["ct_name"]
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

        # return ct_hostname, ct_disksize, ct_cpus, ct_memory, ct_vlan, ct_sshkey, ct_password, ct_template
        title = "Hey ho!"
        return render_template(
            "ctdeploy/stuff.html", 
            title = title,
            ct_ip = ct_ip,
            ct_id = ct_id,
            # ct_hostname = ct_hostname,
            # ct_disksize = ct_disksize,
            # ct_cpus = ct_cpus,
            # ct_memory = ct_memory,
            # ct_vlan = ct_vlan,
            # ct_sshkey = ct_sshkey,
            # ct_password = ct_password,
            # ct_template = ct_template
            )