import frappe
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
import json


class HepsiburadaConnection:
    def __init__(self):
        self._s = requests.Session()

    def connect(self, integration: str, servicemethod: str, service: str, params, servicedata):
        company = frappe.defaults.get_user_default("Company")
        if frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "enable") == 1:
            username = frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "username")
            password = frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "password")

            serviceurl = ""
            if integration == "listing":
                if frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "usetest") == 0:
                    serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "list_host")
                else:
                    serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "list_testhost")
            if integration == "order":
                if frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "usetest") == 0:
                    serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "order_host")
                else:
                    serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "order_testhost")

            url = serviceurl + service
            # her web servis çağrısının başlık (header) kısmına utsToken etiketiyle sistem token’ının değerini
            # eklemelidir
            headers = {
                'Accept': frappe.db.get_single_value("hepsiburadacom Integration Settings", "contenttype")
            }

            try:
                r = self._s.request(method=servicemethod, url=url, headers=headers, params=params, data=servicedata,
                                    auth=HTTPBasicAuth(username, password))
                # For successful API call, response code will be 200 (OK)
                with r:
                    # Loading the response data into a dict variable json.loads takes in only binary or string
                    # variables so using content to fetch binary content Loads (Load String) takes a Json file and
                    # converts into python data structure (dict or list, depending on JSON)
                    return json.loads(r.content)
            except HTTPError as e:
                return r.raise_for_status()
            finally:
                pass
