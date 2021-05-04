import requests
import json


class phpipamapi():

    def __init__(self, host, apikey, username, password, **kwargs):

        self.apiapp = "apiadmin"
        self.baseurl="http://{}/api/{}".format(host, self.apiapp)
        self.authurl = self.baseurl+"/user"

        payload = {
            "Auhtorization": "Basic "+apikey
        }

        self.auth = (username, password)
        result = requests.post(self.authurl, auth=self.auth, json=payload).json()
        # print(result)
        self.token = result["data"]["token"]
        self.authheader = {'token': self.token }
        return

    def getsubnets(self):
        url = self.baseurl+"/subnets"
        result = requests.get(url, headers=self.authheader).json()
        return result

    def getonesubnet(self, subnetid):
        url = self.baseurl+"/subnets/{}".format(subnetid)
        result = requests.get(url, headers=self.authheader).json()
        return result

    def getsubnetaddresses(self, subnetid):
        url = self.baseurl+"/subnets/{}/addresses/".format(subnetid)
        result = requests.get(url, headers=self.authheader).json()
        return result

    def getvrfs(self):
        url = self.baseurl+"/vrf"
        result = requests.get(url, headers=self.authheader).json()
        return result

    def getonevrf(self, vrfid, **kwargs):
        url = self.baseurl+"/vrf/{}".format(vrfid)
        if "getsubnets" in kwargs and kwargs["getsubnets"] == True:
            url += "/subnets"
        result = requests.get(url, headers=self.authheader).json()
        return result

    def getvlans(self):
        url = self.baseurl+"/vlan/"
        result = requests.get(url, headers=self.authheader).json()
        return result

    def getsections(self):
        url = self.baseurl+"/sections"
        result = requests.get(url, headers=self.authheader).json()
        return result

    def getdevices(self):
        url = self.baseurl+"/devices/"
        result = requests.get(url, headers=self.authheader).json()
        return result

    def createvlan(self, vlan_number, vlan_name, vlan_location, vlan_tags, customer_id = "1", vlan_domain = "1"):
        url = self.baseurl+"/vlan/"
        payload = {
            "number": vlan_number,
            "name": vlan_name,
            "custom_Location": vlan_location,
            "custom_tags": vlan_tags,
            "customer_id": customer_id,
            "domainId": vlan_domain,
            "description": "Created by Triptych Automation Portal"
        }
        result = requests.post(url, data=payload, headers=self.authheader).json()
        return result

    def createsubnet(self, ip_subnet, subnet_name, vlan_id, vrf_id, custom_SVI_style = "access", customer_id = "1", sectionId = "4"):
        url = self.baseurl+"/subnets/"
        location = {
            "address": "Gamlestadstorget 16",
            "description": "Lab DC1",
            "id": "1",
            "lat": None,
            "long": None,
            "name": "DC1"
        }
        payload = {
            "location": "1",
            "mask": "24",
            "customer_id": customer_id,
            "vlanId": vlan_id,
            "description": subnet_name,
            "custom_SVI_style": custom_SVI_style,
            "custom_FWObjects": "no",
            "subnet": ip_subnet,
            "sectionId": sectionId,
            "vrfId": vrf_id,
            "custom_ansible_inventory": "0"
        }
        result = requests.post(url, data=payload, headers=self.authheader).json()
        return result

    def requestaddress(self, subnetid, hostname, **kwargs):
        if "method" in kwargs:
            if kwargs["method"].upper() == "POST":
                method = kwargs["method"].upper()
            elif kwargs["method"].upper() == "GET":
                method = kwargs["method"].upper()
            else:
                raise Exception("This method may only use http GET and POST methods")
        else:
            method = "GET"

        if "devicetype" in kwargs:
            self.devicetype = kwargs["devicetype"]
        else:
            self.devicetype = "unspecified"

        url = self.baseurl+"/addresses/first_free/{}/".format(subnetid)
        payload = {
            "hostname": hostname,
            "custom_deviceType": self.devicetype,
        }

        if method == "POST":
            result = requests.post(url, data=payload, headers=self.authheader).json()
        else:
            result = requests.get(url, headers=self.authheader).json()
        return result