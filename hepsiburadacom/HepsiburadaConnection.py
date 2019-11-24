import frappe
import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
import json


class HepsiburadaConnection:
    def __init__(self):
        self._s = requests.Session()
        self.integration_setting_doctype = "hepsiburadacom Integration Setting"
        self.company_setting_doctype = "hepsiburadacom Integration Company Setting"
        # Başlık(Header)
        self.headers = {
            'Accept': frappe.db.get_single_value(self.integration_setting_doctype, "contenttype")
        }

    def connect(self, integration: str, servicemethod: str, service: str, params, servicedata):
        company = frappe.defaults.get_user_default("Company")
        if frappe.db.get_value(self.company_setting_doctype, company, "enable") == 1:
            username = frappe.db.get_value(self.company_setting_doctype, company, "username")
            password = frappe.db.get_value(self.company_setting_doctype, company, "password")

            serviceurl = ""
            if integration == "listing":
                if frappe.db.get_value(self.company_setting_doctype, company, "usetest") == 0:
                    serviceurl = frappe.db.get_single_value(self.integration_setting_doctype, "list_host")
                else:
                    serviceurl = frappe.db.get_single_value(self.integration_setting_doctype, "list_testhost")
            if integration == "order":
                if frappe.db.get_value(self.company_setting_doctype, company, "usetest") == 0:
                    serviceurl = frappe.db.get_single_value(self.integration_setting_doctype, "order_host")
                else:
                    serviceurl = frappe.db.get_single_value(self.integration_setting_doctype, "order_testhost")

            url = serviceurl + service

            try:
                r = self._s.request(method=servicemethod, url=url, headers=self.headers, params=params,
                                    data=servicedata, auth=HTTPBasicAuth(username, password))
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
