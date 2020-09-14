
import requests
import json


def to_json(input):
    return json.dumps(input, indent = 2, sort_keys=True)

class pdnsapi():

    def __init__(self, host, apikey, **kwargs):

        # Defaults to powerdns standard port 8081
        if "port" in kwargs:
            self.port = kwargs["port"]
        else:
            self.port = "8081"
        
        self.host = host
        self.apikey = apikey

        self.authheader = {
            "X-API-Key": self.apikey,
        }

        self.baseurl = "http://{}:{}/api/v1/servers/localhost/".format(self.host, self.port)
        return
    
    def createArecord(self, zone, hostname, ip):
        # Add . to zone name
        if zone[-1] != ".":
            self.zone = zone+"."
        else:
            self.zone = zone

        url = self.baseurl+"zones/{}".format(self.zone)

        # Trying to check if the zone is already provided in the hostname. Else we add it.
        if hostname[-1] != ".":     # like dudeface or dudeface.yllenet.com
            if zone[0::-1] not in hostname:             # like dudeface
                self.hostname = hostname + "." + self.zone    # results: dudeface.yllenet.com.
            else:                                       # like dudeface.yllenet.com
                self.hostname = hostname + "."          # results dudeface.yllenet.com.
        else:
            self.hostname = hostname                    # if you finish with a . we assume you have provided the full fqdn.

        self.ip = ip

        self.payload = {
            "rrsets": [ 
                {"name": "plebbork.yllenet.com.", 
                "type": "A", 
                "ttl": 86400, 
                "changetype": "REPLACE", 
                "records": [ {"content": "10.10.10.10", "disabled": False } ] } 
                ] }
        
        result = requests.patch(url, data=self.payload, headers=self.authheader)
        result = result.json()
        return result


"""
curl -X PATCH --data '{"rrsets": [ {"name": "pleb.yllenet.com.", "type": "A", "ttl": 86400, "changetype": "REPLACE", "records": [ {"content": "10.10.10.10", "disabled": false } ] } ] }' -H 'X-API-Key: someapikey' http://10.20.20.5:8081/api/v1/servers/localhost/zones/yllenet.com. | jq .
"""