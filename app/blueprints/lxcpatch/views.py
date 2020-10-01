from flask import Blueprint, render_template, url_for, request, abort, session, flash
import ipaddress
import os
import socket
import time
import subprocess

lxcpatch = Blueprint("lxcpatch", __name__)

import json

@lxcpatch.route('/', methods=['GET', 'POST'])
def index():
    # THIS HAPPENS WHEN WE FIRST REQUEST THE PAGE.
    if request.method == "GET":

        title = "Patch your stuff!"   
        return render_template("lxcpatch/index.html", title = title)
    
    # THIS HAPPENS WHEN WE HIT "DEPLOY CONTAINER" IN THE FORM.

    if (request.method == "POST") and "configure_lxc" in request.form:
        cmd = ["ansible-playbook", "/opt/scripts/ansible/ansible-linux/do-updates/PLAY-lxc-containers.yml"]

        try:
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            output = e.output
        
        output = output.decode("utf-8")
        output = output.split("\n")
        statuses = {}
        recapseen = False
        for item in output:
            if "PLAY RECAP" not in item and recapseen == False:
                continue
            if "PLAY RECAP" in item:
                recapseen = True
            if (recapseen == True) and (item != "") and ("ok" in item):
                item = item.split(":")
                host = item[0].strip()
                returncodes = item[1].strip().split()
                statuses[host] = {
                    "ok":           returncodes[0].strip().split("=")[1],
                    "changed":      returncodes[1].strip().split("=")[1],
                    "unreachable":  returncodes[2].strip().split("=")[1],
                    "failed":       returncodes[3].strip().split("=")[1],
                    "skipped":      returncodes[4].strip().split("=")[1],
                    "rescued":      returncodes[5].strip().split("=")[1],
                    "ignored":      returncodes[6].strip().split("=")[1],
                    }
                
        return render_template("lxcpatch/patch-status.html", statuses = statuses)