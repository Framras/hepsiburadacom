import frappe
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from hepsiburadacom.HepsiburadaListingsService import HepsiburadaListingsService
from hepsiburadacom.HepsiburadaOrdersService import HepsiburadaOrdersService


@frappe.whitelist()
def check_integration(system, username, password, merchantid):
    integration_setting = "hepsiburadacom Integration Setting"
    service_method = 'GET'

    service_url = ""
    if system == "live":
        service_url = frappe.db.get_single_value(integration_setting, "list_host")
    elif system == "test":
        service_url = frappe.db.get_single_value(integration_setting, "list_testhost")
    service_endpoint = "/listings/merchantid"
    service_resource = "/" + merchantid

    headers = {
        'Accept': frappe.db.get_single_value(integration_setting, "contenttype")
    }
    params = {
        "offset": 0,
        "limit": 1
    }

    service_status = ""
    s = requests.Session()
    try:
        r = s.request(method=service_method, url=service_url + service_endpoint + service_resource, params=params,
                      headers=headers, auth=HTTPBasicAuth(username, password))
        with r:
            service_status = r.status_code
    except HTTPError as e:
        return 'The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code)
    finally:
        if service_status == 200:
            return "success"
        else:
            return "failure"


@frappe.whitelist()
def initiate_hepsiburada_listings():
    ls = HepsiburadaListingsService()
    return ls.process_listings()


@frappe.whitelist()
def initiate_hepsiburada_orderitems():
    os = HepsiburadaOrdersService()
    return os.process_order_items()
