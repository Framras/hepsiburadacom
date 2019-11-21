import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth
import json


class HepsiburadaConnection:
    def __init__(self):
        self._s = requests.Session()

    def connect(self, servicemethod: str, service: str, params, servicedata):
        company = frappe.defaults.get_user_default("Company")
        if frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "enable") == 1:
            username = frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "username")
            password = frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "password")

            if frappe.db.get_value("hepsiburadacom Integration Company Settings", company, "usetest") == 0:
                serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "listhost")
            else:
                serviceurl = frappe.db.get_single_value("hepsiburadacom Integration Settings", "listtesthost")

            url = serviceurl + service
            # her web servis çağrısının başlık (header) kısmına utsToken etiketiyle sistem token’ının değerini eklemelidir
            headers = {
                'Accept': frappe.db.get_single_value("hepsiburadacom Integration Settings", "contenttype")
            }

            try:
                r = self._s.request(method=servicemethod, url=url, headers=headers, params=params, data=servicedata,
                                    auth=HTTPBasicAuth(username, password))
                with r:
                    print(r.text)
            except HTTPError as e:
                print('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
            finally:
                print(r.request.url)
                print(r.request.headers)

            # For successful API call, response code will be 200 (OK)
            if response.ok:
                # Loading the response data into a dict variable
                # json.loads takes in only binary or string variables so using content to fetch binary content
                # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
                return json.loads(response.content)
            else:
                # If response code is not ok (200), print the resulting http error code with description
                return response.raise_for_status()
