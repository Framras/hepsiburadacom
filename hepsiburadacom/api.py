import frappe
import json
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth


@frappe.whitelist()
def check_integration(system, username, password, merchantid):
    company = frappe.defaults.get_user_default("Company")
    servicemethod = 'GET'

    serviceurl = ""
    if system == "live":
        serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "list_host")
    elif system == "test":
        serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "list_testhost")
    serviceendpoint = "/listings/merchantid"
    serviceresource = "/" + merchantid

    headers = {
        'Accept': frappe.db.get_single_value("hepsiburadacom Integration Settings", "contenttype")
    }
    params = {
        'offset': 0,
        'limit': 1
    }

    servicestatus = ''
    s = requests.Session()
    try:
        r = s.request(method=servicemethod, url=serviceurl + serviceendpoint + serviceresource, params=params,
                      headers=headers, auth=HTTPBasicAuth(username, password))
        with r:
            servicestatus = r.status_code
            response = json.loads(r.content)
            print(json.dumps(response))
    except HTTPError as e:
        return ('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
    finally:
        return (servicestatus)
