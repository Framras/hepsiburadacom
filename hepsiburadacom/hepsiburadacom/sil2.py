import json
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth

username = 'framras_dev'
password = 'Fr12345!'
merchantid = '509778cf-7104-4c7f-850f-e14fdf5beb70'

servicemethod = 'GET'
serviceprotocol = "https://"
servicehost = "listing-external-sit.hepsiburada.com"
servicehost2 = "oms-external-sit.hepsiburada.com"
serviceendpoint = "/listings"
serviceendpoint2 = "/orders"
serviceresource = "/merchantid/" + merchantid
serviceurl = serviceprotocol + servicehost + serviceendpoint + serviceresource
serviceurl2 = serviceprotocol + servicehost2 + serviceendpoint2 + serviceresource

servicecontenttype = "application/json; charset=utf-8"
headers = {
    'Accept': servicecontenttype
}

servicedata = None
params = None

s = requests.Session()
try:
    r = s.request(method=servicemethod, url=serviceurl, headers=headers, params=params, data=servicedata,
                  auth=HTTPBasicAuth(username, password))
    with r:
        response = json.loads(r.content)
        print(json.dumps(response))
        for l in response["listings"]:
            print("1-------------" + str(l["hepsiburadaSku"]))
            for p in l.keys():
                print(str(p).lower() + " " + str(l[p]))
except HTTPError as e:
    print('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
finally:
    print(r.content)
    print("this is the end")

try:
    r = s.request(method=servicemethod, url=serviceurl2, headers=headers, params=params, data=servicedata,
                  auth=HTTPBasicAuth(username, password))
    with r:
        print(r.content)
        response = json.loads(r.content)
        print(json.dumps(response))
        for l in response["items"]:
            print(str(l["orderNumber"]) + "-------------" + str(l))
            for p in l.keys():
                print(str(p).lower() + " " + str(l[p]))
except HTTPError as e:
    print('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
finally:
    print(r.content)
    print("this is the end")
