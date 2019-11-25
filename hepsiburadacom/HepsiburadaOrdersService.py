import frappe
from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection
from hepsiburadacom.HepsiburadaAddress import HepsiburadaAddress


class HepsiburadaOrdersService:
    def __init__(self):
        self.hepsiburadaconnection = HepsiburadaConnection()
        self.servicepath = "/orders"
        self.integration = "order"
        self.company = frappe.defaults.get_user_default("Company")
        self.doctype = "hepsiburada Order Item"
        self.detail_doctype = "hepsiburada Order Detail"
        self.company_setting_doctype = "hepsiburadacom Integration Company Setting"

    # Ödemesi Tamamlanmış Siparişleri Listeleme (Get List of Orders [GET])
    # Bu metod ödemesi tamamlanmış yeni siparişleri (new orders) listeleyebilmenize olanak tanır.
    def get_list_of_orderitems(self, offset, limit):
        servicemethod = "GET"
        servicetemplate = "/merchantid"
        servicetemplateresource = "/" + frappe.db.get_value(self.company_setting_doctype, self.company, "merchantid")
        service = self.servicepath + servicetemplate + servicetemplateresource
        # Parametreler(Parameters)
        if offset is None or limit is None:
            parameters = None
        else:
            parameters = {
                "offset": offset,
                "limit": limit
            }

        return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, parameters,
                                                  servicedata=None)

    # Siparişe Ait Detay Bilgilerini Listeleme (Get List of Orders Details [GET])
    # Bu metod bir siparişe ait kalemlerin detaylarını listelemeize olanak tanır.
    def get_list_of_orders_details(self, ordernumber: int):
        servicemethod = "GET"
        servicetemplate = "/merchantid"
        # Merchantid (gerekli, guid, b2910839-83b9-4d45-adb6-86bad457edcb) Her satıcının unique bir tanımlayıcısıdır.
        # Ordernumber (gerekli, int, 004563585) Her siparişin unique bir tanımlayıcısıdır.
        servicetemplateresource = "/" + frappe.db.get_value(self.company_setting_doctype, self.company,
                                                            "merchantid") + "/ordernumber/" + ordernumber
        service = self.servicepath + servicetemplate + servicetemplateresource

        return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, parameters,
                                                  servicedata=None)


@frappe.whitelist()
def initiate_hepsiburada_orderitems():
    os = HepsiburadaOrdersService()
    orderitems = os.get_list_of_orderitems(None, None)
    totalcount = orderitems["totalCount"]
    meta = frappe.get_meta(os.doctype)
    for item in orderitems["items"]:
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": os.doctype,
            "id": item["id"]
        }):
            newdoc = frappe.new_doc(os.doctype)
            newdoc.id = item["id"]
            newdoc.insert()

        frdoc = frappe.get_doc(os.doctype, item["id"])
        customer_type = ""
        customer_tax_id = ""
        if item["lastStatusUpdateDate"] != frdoc.laststatusupdatedate:
            for itemkey in item.keys():
                if itemkey == "shippingAddress":
                    sa = HepsiburadaAddress(item[itemkey], "Shipping")
                    if sa.use_address():
                        for key in ["addressId", "alternatePhoneNumber", "name"]:
                            frdoc.db_set((itemkey + "_" + key).lower(), item[itemkey][key])
                elif itemkey == "totalPrice" or \
                        itemkey == "unitPrice" or \
                        itemkey == "commission" or \
                        itemkey == "cargoCompanyModel":
                    for ikey in item[itemkey].keys():
                        if meta.has_field((itemkey + "_" + ikey).lower()):
                            frdoc.db_set((itemkey + "_" + ikey).lower(), item[itemkey][ikey])
                elif itemkey == "hbDiscount":
                    for ikey in item[itemkey].keys():
                        if ikey == "totalPrice" or \
                                ikey == "unitPrice":
                            for skey in item[itemkey][ikey].keys():
                                if meta.has_field((itemkey + "_" + ikey + "_" + skey).lower()):
                                    frdoc.db_set(
                                        (itemkey + "_" + ikey + "_" + skey).lower(), item[itemkey][ikey][skey])
                elif itemkey == "invoice":
                    for ikey in item[itemkey].keys():
                        if ikey == "address":
                            sa = HepsiburadaAddress(item[itemkey][ikey], "Billing")
                            if sa.use_address():
                                for key in ["addressId", "alternatePhoneNumber", "name"]:
                                    frdoc.db_set((itemkey + "_" + ikey + "_" + key).lower(), item[itemkey][ikey][key])
                        else:
                            if meta.has_field((itemkey + "_" + ikey).lower()):
                                frdoc.db_set((itemkey + "_" + ikey).lower(), item[itemkey][ikey])
                        # post CRUD process inspection
                        if ikey == "turkishIdentityNumber":
                            if item[itemkey][ikey] != "" or item[itemkey][ikey] is not None:
                                customer_type = "Individual"
                                customer_tax_id = item[itemkey][ikey]
                        if ikey == "taxNumber":
                            if item[itemkey][ikey] != "" or item[itemkey][ikey] is not None:
                                customer_type = "Company"
                                customer_tax_id = item[itemkey][ikey]
                else:
                    if meta.has_field(itemkey.lower()):
                        frdoc.db_set(itemkey.lower(), item[itemkey])

            frdoc.save()

            for orderdetail in os.get_list_of_orders_details(item["orderNumber"]):
                for customerdetail in orderdetail["customer"]:
                    # check if record exists by filters
                    if not frappe.db.exists({
                        "doctype": "Customer",
                        "customer_name": customerdetail["name"]
                    }):
                        newdoc = frappe.new_doc("Customer")
                        # required fields
                        newdoc.customer_name = customerdetail["name"]
                        newdoc.customer_type = customer_type
                        newdoc.customer_group = frappe.db.get_value(os.company_setting_doctype, os.company,
                                                                    "customer_group")
                        newdoc.territory = frappe.db.get_value(os.company_setting_doctype, os.company, "territory")
                        # optional fields
                        newdoc.tax_id = customer_tax_id

                        newdoc.insert()
                    # insert customer data to hepsiburada doctype
                    pass
                customerdoc = frappe.get_doc("Customer", filters={"customer_name": orderdetail["customer"]["name"]})


    return frappe.db.count("hepsiburada Order Item",
                           filters={"merchantid": frappe.db.get_value(os.company_setting_doctype, os.company,
                                                                      "merchantid")}) == totalcount
