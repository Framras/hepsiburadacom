import frappe


class HepsiburadaSalesOrderItem:
    def __init__(self, salesorderitem: dict):
        self.salesorderitem = salesorderitem
        self.doctype = "Sales Order Item"

    def use_salesorder(self):
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": self.doctype,
            'address_title': self.address["addressId"]
        }):
            newdoc = frappe.new_doc(self.doctype)
            newdoc.address_title = self.address["addressId"]
            newdoc.address_type = self.default_addresstype
            newdoc.address_line1 = self.address["address"]
            newdoc.city = self.address["city"]
            newdoc.country = frappe.get_value("Country", filters={'code': self.address["countryCode"].lower()},
                                              fieldname="country_name")
            newdoc.insert()

        frdoc = frappe.get_doc(self.doctype, self.address["addressId"] + "-" + self.default_addresstype)
        if self.address_type == self.default_addresstype:
            frdoc.db_set("address_type", "Shipping")
            frdoc.db_set("is_shipping_address", 1)
        elif self.address_type == "Billing":
            if frdoc.address_type != self.default_addresstype:
                frdoc.db_set("address_type", "Billing")
                frdoc.db_set("is_primary_address", 1)
        frdoc.db_set("address_line1", self.address["address"])
        frdoc.db_set("address_line2", self.address["district"] + "/" + self.address["town"])
        frdoc.db_set("country", frappe.get_value("Country", filters={'code': self.address["countryCode"]},
                                                 fieldname="country_name"))
        frdoc.db_set("phone", self.address["phoneNumber"])
        frdoc.db_set("city", self.address["city"])
        frdoc.db_set("email_id", self.address["email"])

        frdoc.save()

        return frappe.db.exists({
            "doctype": self.doctype,
            'address_title': self.address["addressId"]
        })
