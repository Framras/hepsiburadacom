import frappe


class HepsiburadaAddress:
    def __init__(self, address: dict, address_type: str):
        self.address = address
        self.address_type = address_type
        self.doctype = "Address"
        self.default_address_type = "Shipping"

    def use_address(self):
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": self.doctype,
            'address_title': self.address["addressId"]
        }):
            newdoc = frappe.new_doc(self.doctype)
            newdoc.address_title = self.address["addressId"]
            newdoc.address_type = self.default_address_type
            newdoc.address_line1 = self.address["address"]
            newdoc.city = self.address["city"]
            newdoc.country = frappe.get_value("Country", filters={'code': self.address["countryCode"].lower()},
                                              fieldname="country_name")
            newdoc.insert()

        frdoc = frappe.get_doc(self.doctype, self.address["addressId"] + "-" + self.default_address_type)
        if frdoc.address_type == self.default_address_type:
            frdoc.db_set("address_type", self.default_address_type)
            frdoc.db_set("is_shipping_address", 1)
        elif self.address_type == "Billing":
            if frdoc.address_type != self.default_address_type:
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
