import requests
import json


class fortiapi():

    def __init__(self, host, apitoken, **kwargs):
        self.baseurl="https://{}/api/v2/cmdb/".format(host)
        self.apitoken = apitoken

        return
    
    def sendget(self, endpoint, **kwargs):
        
        accessurl = self.baseurl+"{}?access_token={}".format(endpoint, self.apitoken)

        # If we have any filters (list of fields to include in response) we append them to the accessurl
        # &format=name|comment is an example.
        if "filters" in kwargs:
            filterstring = "&format="
            for item in kwargs["filters"]:
                filterstring += item+"|"
            filterstring = filterstring[0:-1]
            accessurl += filterstring

        # print(accessurl)
        # verify = False ignores SSL errors.
        result = requests.get(accessurl, verify=False).json()
        return result

    def createaddress(self, **kwargs):

        accessurl = self.baseurl+"firewall/address?access_token={}".format(self.apitoken)
        print()

        if "name" not in kwargs:
            raise Exception("You need to provide a name in the **kwargs")
        elif "subnet" not in kwargs:
            raise Exception("You need to provide a subnet in the **kwargs")

        self.payload = {
            "name": kwargs["name"],
            "subnet": kwargs["subnet"],
            "type": "ipmask",
            "comment": kwargs["comment"],
            "visibility": "enable"
            }

        result = requests.post(accessurl, json=self.payload, verify=False).json()


    def updateaddress(self, **kwargs):

        if "name" not in kwargs:
            raise Exception("You need to provide a name in the **kwargs")
        elif "subnet" not in kwargs:
            raise Exception("You need to provide a subnet in the **kwargs")

        accessurl = self.baseurl+"firewall/address/{}?access_token={}".format(kwargs["name"], self.apitoken)

        self.payload = {
            "name": kwargs["name"],
            "subnet": kwargs["subnet"],
            "type": "ipmask",
            "comment": kwargs["comment"],
            "visibility": "enable"
            }

        result = requests.put(accessurl, json=self.payload, verify=False).json()
    # def sendpost(self, endpoint, **kwargs)