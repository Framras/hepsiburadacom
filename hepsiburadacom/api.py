import frappe
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth


@frappe.whitelist()
def check_integration(system, username, password, merchantid):
    company = frappe.defaults.get_user_default("Company")
    if frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "usetest") == 0:
        url = frappe.db.get_single_value("hepsiburadacom Integration Settings", "listhost")
    else:
        url = frappe.db.get_single_value("hepsiburadacom Integration Settings", "listtesthost")

    offset = 0
    limit = 0
    servicemethod = 'GET'
    serviceprotocol = "https://"
    servicehost = "listing-external-sit.hepsiburada.com"
    serviceurl = serviceprotocol + servicehost
    serviceendpoint = "/listings/merchantid"

    headers = {
        'Accept': frappe.db.get_single_value("hepsiburadacom Integration Settings", "contenttype")
    }

    serviceresource = "/" + merchantid

    servicestatus = ''
    s = requests.Session()
    try:
        r = s.request(method=servicemethod, url=serviceurl + serviceendpoint + serviceresource, params=,
                      headers=headers, auth=HTTPBasicAuth(username, password))
        with r:
            servicestatus = r.status_code
    except HTTPError as e:
        return ('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
    finally:
        return (servicestatus + r.content)
