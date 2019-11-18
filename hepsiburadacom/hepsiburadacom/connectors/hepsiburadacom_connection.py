import frappe
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth


@frappe.whitelist()
def check_integration(username, password, merchantid):
    servicemethod = 'GET'
    serviceprotocol = "https://"
    servicehost = "listing-external-sit.hepsiburada.com"
    serviceurl = serviceprotocol + servicehost
    serviceendpoint = "/listings/merchantid"

    servicecontenttype = "application/json"

    merchantid = "509778cf-7104-4c7f-850f-e14fdf5beb70"
    serviceresource = "/" + merchantid

    username = 'framras_dev'
    password = 'Fr12345!'

    servicedata = ""
    try:
        r = requests.get(serviceurl + serviceendpoint + serviceresource, auth=HTTPBasicAuth(username, password))
        with r:
            print(r.text)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
    finally:
        print(r.request.url)
        print(r.request.headers)
