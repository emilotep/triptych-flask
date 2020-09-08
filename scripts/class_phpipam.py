import requests
import json


class phpipamapi():

    def __init__(self, host, apikey, **kwargs):

        self.baseurl="http://{}/api/apiadmin".format(host)
        self.authurl = self.baseurl+"/user"

        payload = {
            "Auhtorization": "Basic "+apikey
        }

        self.auth = ("api-user", "XJcoS7Ms7Q")
        result = requests.post(self.authurl, auth=self.auth, json=payload).json()
        # print(result)
        self.token = result["data"]["token"]
        self.authheader = {'token': self.token }
        return

    def getsubnets(self):
        url = self.baseurl+"/subnets"

        result = requests.get(url, headers=self.authheader).json()
        return result


    def getsubnetaddresses(self, subnetid):
        url = self.baseurl+"/subnets/{}/addresses/".format(subnetid)

        result = requests.get(url, headers=self.authheader).json()
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

        url = self.baseurl+"/addresses/first_free/{}/".format(subnetid)
        payload = {
            "hostname": hostname
        }

        if method == "POST":
            result = requests.post(url, data=payload, headers=self.authheader).json()
        else:
            result = requests.get(url, headers=self.authheader).json()
        return result

# /api/my_app/addresses/first_free/{subnetId}/