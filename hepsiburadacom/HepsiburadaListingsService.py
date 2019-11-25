import frappe
from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection


class HepsiburadaListingsService:
    def __init__(self):
        self.hepsiburada_connection = HepsiburadaConnection()
        self.service_path = "/listings"
        self.integration = "listing"
        self.company = frappe.defaults.get_user_default("Company")
        self.doctype = "hepsiburada Listing"
        self.company_setting_doctype = "hepsiburadacom Integration Company Setting"

    # Satıcıya Ait Listing Bilgilerini Listeleme (Get List of Listings [GET])
    # Bu metod satıcıya ait listing bilgilerine ulaşmanıza olanak tanır.
    def get_list_of_listings(self, offset, limit):
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

    def process_listings(self):
        listings = self.get_list_of_listings(None, None)
        total_count = listings["totalCount"]
        meta = frappe.get_meta(self.doctype)
        for listing in listings["listings"]:
            # check if record exists by filters
            if not frappe.db.exists({
                "doctype": self.doctype,
                "hepsiburadasku": listing["hepsiburadaSku"],
                "company": self.company
            }):
                newdoc = frappe.new_doc(self.doctype)
                newdoc.hepsiburadasku = listing["hepsiburadaSku"]
                newdoc.company = self.company
                newdoc.insert()

            frdoc = frappe.get_doc(self.doctype, listing["hepsiburadaSku"])
            for p in listing.keys():
                if meta.has_field(p.lower()):
                    frdoc.db_set(p.lower(), listing[p])

            frdoc.save()

            # check if record exists by filters
            if not frappe.db.exists({
                "doctype": "Item",
                "item_code": listing["merchantSku"]
            }):
                new_item = frappe.new_doc("Item")
                # required fields
                new_item.item_code = listing["merchantSku"]
                new_item.item_group = frappe.db.get_value(self.company_setting_doctype, self.company, "item_group")
                new_item.stock_uom = frappe.db.get_value(self.company_setting_doctype, self.company, "stock_uom")
                # optional fields
                new_item.is_sales_item = 1
                new_item.include_item_in_manufacturing = 0
                new_item.is_stock_item = 1

                new_item.insert()

        return frappe.db.count(self.doctype, filters={"company": self.company}) == total_count
