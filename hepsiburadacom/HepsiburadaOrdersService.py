import frappe
from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection
from hepsiburadacom.HepsiburadaAddress import HepsiburadaAddress
from hepsiburadacom.HepsiburadaListingsService import HepsiburadaListingsService
from hepsiburadacom.HepsiburadaCustomer import HepsiburadaCustomer


class HepsiburadaOrdersService:
    def __init__(self):
        self.hepsiburada_connection = HepsiburadaConnection()
        self.service_path = "/orders"
        self.integration = "order"
        self.company = frappe.defaults.get_user_default("Company")
        self.doctype = "hepsiburada Order Item"
        self.customer_doctype = "Customer"
        self.detail_doctype = "hepsiburada Order Detail"
        self.item_doctype = "Item"
        self.listing_doctype = "hepsiburada Listing"
        self.company_setting_doctype = "hepsiburadacom Integration Company Setting"
        self.customer_type = ''
        self.customer_tax_id = ''

    # Ödemesi Tamamlanmış Siparişleri Listeleme (Get List of Orders [GET])
    # Bu metod ödemesi tamamlanmış yeni siparişleri (new orders) listeleyebilmenize olanak tanır.
    def get_list_of_order_items(self, offset, limit):
        service_method = "GET"
        service_template = "/merchantid"
        service_template_resource = "/" + frappe.db.get_value(self.company_setting_doctype, self.company, "merchantid")
        service = self.service_path + service_template + service_template_resource
        # Parametreler(Parameters)
        if offset is None or limit is None:
            parameters = None
        else:
            parameters = {
                "offset": offset,
                "limit": limit
            }

        return self.hepsiburada_connection.connect(self.integration, service_method, service, parameters,
                                                   servicedata=None)

    # Siparişe Ait Detay Bilgilerini Listeleme (Get List of Orders Details [GET])
    # Bu metod bir siparişe ait kalemlerin detaylarını listelemeize olanak tanır.
    def get_list_of_orders_details(self, ordernumber: int):
        service_method = "GET"
        service_template = "/merchantid"
        # Merchantid (gerekli, guid, b2910839-83b9-4d45-adb6-86bad457edcb) Her satıcının unique bir tanımlayıcısıdır.
        # Ordernumber (gerekli, int, 004563585) Her siparişin unique bir tanımlayıcısıdır.
        service_template_resource = "/" + frappe.db.get_value(self.company_setting_doctype, self.company,
                                                              "merchantid") + "/ordernumber/" + ordernumber
        service = self.service_path + service_template + service_template_resource

        return self.hepsiburada_connection.connect(self.integration, service_method, service, params=None,
                                                   servicedata=None)

    def process_order_items(self):
        hb_order_items = self.get_list_of_order_items(None, None)
        total_count = hb_order_items["totalCount"]
        meta = frappe.get_meta(self.doctype)
        for hb_order_item in hb_order_items["items"]:
            if self.check_order_item_doctype(hb_order_item["id"]):
                hb_order_item_doc = frappe.get_doc(self.doctype, hb_order_item["id"])
            else:
                # should be error
                pass
            if hb_order_item["lastStatusUpdateDate"] != hb_order_item_doc.laststatusupdatedate:
                for hb_order_item_key in hb_order_item.keys():
                    if hb_order_item_key == "shippingAddress":
                        sa = HepsiburadaAddress(hb_order_item[hb_order_item_key], "Shipping")
                        if sa.use_address():
                            for key in ["addressId", "alternatePhoneNumber", "name"]:
                                hb_order_item_doc.db_set((hb_order_item_key + "_" + key).lower(),
                                                         hb_order_item[hb_order_item_key][key])
                    elif hb_order_item_key == "totalPrice" or \
                            hb_order_item_key == "unitPrice" or \
                            hb_order_item_key == "commission" or \
                            hb_order_item_key == "cargoCompanyModel":
                        for ikey in hb_order_item[hb_order_item_key].keys():
                            if meta.has_field((hb_order_item_key + "_" + ikey).lower()):
                                hb_order_item_doc.db_set((hb_order_item_key + "_" + ikey).lower(),
                                                         hb_order_item[hb_order_item_key][ikey])
                    elif hb_order_item_key == "hbDiscount":
                        for ikey in hb_order_item[hb_order_item_key].keys():
                            if ikey == "totalPrice" or \
                                    ikey == "unitPrice":
                                for skey in hb_order_item[hb_order_item_key][ikey].keys():
                                    if meta.has_field((hb_order_item_key + "_" + ikey + "_" + skey).lower()):
                                        hb_order_item_doc.db_set(
                                            (hb_order_item_key + "_" + ikey + "_" + skey).lower(),
                                            hb_order_item[hb_order_item_key][ikey][skey])
                    elif hb_order_item_key == "invoice":
                        for ikey in hb_order_item[hb_order_item_key].keys():
                            if ikey == "address":
                                sa = HepsiburadaAddress(hb_order_item[hb_order_item_key][ikey], "Billing")
                                if sa.use_address():
                                    for key in ["addressId", "alternatePhoneNumber", "name"]:
                                        hb_order_item_doc.db_set(
                                            (hb_order_item_key + "_" + ikey + "_" + key).lower(),
                                            hb_order_item[hb_order_item_key][ikey][key])
                            else:
                                if meta.has_field((hb_order_item_key + "_" + ikey).lower()):
                                    hb_order_item_doc.db_set((hb_order_item_key + "_" + ikey).lower(),
                                                             hb_order_item[hb_order_item_key][ikey])
                            # post CRUD process inspection
                            if ikey == "turkishIdentityNumber":
                                if hb_order_item[hb_order_item_key][ikey] != "" or \
                                        hb_order_item[hb_order_item_key][ikey] is not None:
                                    self.customer_type = "Individual"
                                    self.customer_tax_id = hb_order_item[hb_order_item_key][ikey]
                            if ikey == "taxNumber":
                                if hb_order_item[hb_order_item_key][ikey] != "" or \
                                        hb_order_item[hb_order_item_key][ikey] is not None:
                                    self.customer_type = "Company"
                                    self.customer_tax_id = hb_order_item[hb_order_item_key][ikey]
                    else:
                        if meta.has_field(hb_order_item_key.lower()):
                            hb_order_item_doc.db_set(hb_order_item_key.lower(), hb_order_item[hb_order_item_key])

            hb_order_item_doc.save()
            # check if sku exists among hepsiburada listings
            if not frappe.db.exists({
                "doctype": self.listing_doctype,
                "hepsiburadasku": hb_order_item["sku"]
            }):
                ls = HepsiburadaListingsService()
            # if sku does not exist, process all listings
            if ls.process_listings():
                hb_listing_doc = frappe.get_doc(doctype=self.listing_doctype,
                                                filters={"hepsiburadasku": hb_order_item["sku"]})
                item_doc = frappe.get_doc(doctype=self.item_doctype, filters={"item_code": hb_listing_doc.merchantsku})
            else:
                # should be error
                pass

            # check if order detail exists
            if self.check_orders_detail_doctype(hb_order_item["orderNumber"]):
                self.process_orders_details(hb_order_item["orderNumber"])
            else:
                # should be error
                pass

        return frappe.db.count(self.doctype, filters={
            "merchantid": frappe.db.get_value(self.company_setting_doctype, self.company, "merchantid")}) == total_count

    def process_orders_details(self, order_number):
        hb_orders_detail = self.get_list_of_orders_details(order_number)
        meta = frappe.get_meta(self.detail_doctype)
        if self.check_orders_detail_doctype(order_number):
            hb_order_detail_doc = frappe.get_doc(self.detail_doctype, order_number)
        else:
            # should be error
            pass
        for hb_order_detail_key in hb_orders_detail.keys():
            if hb_order_detail_key == "customer":
                hbc = HepsiburadaCustomer(hb_orders_detail[hb_order_detail_key], self.customer_type,
                                          self.customer_tax_id)
                if hbc.use_customer():
                    for key in hb_orders_detail[hb_order_detail_key]:
                        if meta.has_field((hb_order_detail_key + "_" + key).lower()):
                            hb_order_detail_doc.db_set((hb_order_detail_key + "_" + key).lower(),
                                                       hb_orders_detail[hb_order_detail_key][key])
                customer_doc = frappe.get_doc(doctype=self.customer_doctype, filters={
                    "customer_name": hb_orders_detail[hb_order_detail_key]["name"]})
            if hb_order_detail_key == "invoice":
                for key in hb_orders_detail[hb_order_detail_key]:
                    if meta.has_field((hb_order_detail_key + "_" + key).lower()):
                        hb_order_detail_doc.db_set((hb_order_detail_key + "_" + key).lower(),
                                                   hb_orders_detail[hb_order_detail_key][key])
            if hb_order_detail_key == "deliveryAddress":
                for key in hb_orders_detail[hb_order_detail_key]:
                    if meta.has_field((hb_order_detail_key + "_" + key).lower()):
                        hb_order_detail_doc.db_set((hb_order_detail_key + "_" + key).lower(),
                                                   hb_orders_detail[hb_order_detail_key][key])

    def check_order_item_doctype(self, filter_id):
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": self.doctype,
            "id": filter_id
        }):
            new_hb_order_item_doc = frappe.new_doc(self.doctype)
            new_hb_order_item_doc.id = filter_id
            new_hb_order_item_doc.insert()
        return frappe.db.exists({
            "doctype": self.doctype,
            "id": filter_id
        })

    def check_orders_detail_doctype(self, filter_id):
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": self.detail_doctype,
            "ordernumber": filter_id
        }):
            new_hb_order_item_doc = frappe.new_doc(self.detail_doctype)
            new_hb_order_item_doc.ordernumber = filter_id
            new_hb_order_item_doc.insert()
        return frappe.db.exists({
            "doctype": self.detail_doctype,
            "ordernumber": filter_id
        })
