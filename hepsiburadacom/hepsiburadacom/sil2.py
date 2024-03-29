import json
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth

username = ''
password = ''
merchantid = ''
ordernumber = '041241372'

servicemethod = 'GET'
serviceprotocol = "https://"
servicehost = "listing-external-sit.hepsiburada.com"
servicehost2 = "oms-external-sit.hepsiburada.com"
serviceendpoint = "/listings"
serviceendpoint2 = "/orders"
serviceresource = "/merchantid/" + merchantid
servicetemplate3 = "/ordernumber/" + ordernumber
serviceurl = serviceprotocol + servicehost + serviceendpoint + serviceresource
serviceurl2 = serviceprotocol + servicehost2 + serviceendpoint2 + serviceresource
serviceurl3 = serviceprotocol + servicehost2 + serviceendpoint2 + serviceresource + servicetemplate3

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
            print(l)
            print("order detail" + str(l["hepsiburadaSku"] + "-------------"))
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
        response = json.loads(r.content)
        print(json.dumps(response))
        for l in response["items"]:
            print(l)
            print("order number" + str(l["orderNumber"]) + "-------------")
            for p in l.keys():
                print(str(p).lower() + " " + str(l[p]))
except HTTPError as e:
    print('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
finally:
    print(r.content)
    print("this is the end")

try:
    r = s.request(method=servicemethod, url=serviceurl3, headers=headers, params=params, data=servicedata,
                  auth=HTTPBasicAuth(username, password))
    with r:
        response = json.loads(r.content)
        print(json.dumps(response))
        for l in response["items"]:
            print(l)
            print("order" + str(l["orderNumber"]) + "-------------")
            for p in l.keys():
                print(str(p).lower() + " " + str(l[p]))
except HTTPError as e:
    print('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
finally:
    print(r.content)
    print("this is the end")
