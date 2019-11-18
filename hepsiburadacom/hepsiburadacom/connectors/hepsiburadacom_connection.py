import frappe
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth


@frappe.whitelist()
def test_listintegration(username, password, authenticationtype):
    servicemethod = 'GET'
    serviceurl = "https://listing-external-sit.hepsiburada.com"
    serviceendpoint = "/listings/merchantid"

    servicecontenttype = "application/json"

    merchantid = "509778cf-7104-4c7f-850f-e14fdf5beb70"
    serviceresource = "/" + merchantid

    servicedata = ""

    req = Request(serviceurl + serviceendpoint + serviceresource, authenticationtype=)
    req.add_header("Content-Type", servicecontenttype)
    req.method = servicemethod

    # Create an OpenerDirector with support for Basic HTTP Authentication...
    auth_handler = HTTPBasicAuthHandler()
    auth_handler.add_password(user='framras_dev',
                              passwd='Fr12345!')
    opener = build_opener(auth_handler)
    # ...and install it globally so it can be used with urlopen.
    install_opener(opener)

    try:
        response = urlopen(req)
        with response as f:
            return f.read().decode('utf-8')
    except HTTPError as e:
        return 'The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code)
    except URLError as e:
        return 'We failed to reach a server. ' + 'Reason: ' + e.reason
