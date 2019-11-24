import frappe


class HepsiburadaAddress:
    def __init__(self, address: dict, address_type: str):
        self.address = address
        self.address_type = address_type
        self.doctype = "Address"
        self.default_addresstype = "Shipping"

    def use_address(self):
        # check if record exists by filters
        if not frappe.db.exists({
            'doctype': self.doctype,
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

        frdoc = frappe.get_doc(self.doctype, self.address["addressId"])
        if self.address_type == "shipping":
            frdoc.frdoc.db_set("address_type", "Shipping")
            frdoc.frdoc.db_set("is_shipping_address", 1)
        elif self.address_type == "billing":
            if frdoc.address_type != self.default_addresstype:
                frdoc.frdoc.db_set("address_type", "Billing")
            frdoc.frdoc.db_set("is_primary_address", 1)
        frdoc.frdoc.db_set("address_line1", self.address["address"])
        frdoc.frdoc.db_set("address_line2", self.address["district"] + "/" + self.address["town"])
        frdoc.frdoc.db_set("country", frappe.get_value("Country", filters={'code': self.address["countryCode"]},
                                                       fieldname="country_name"))
        frdoc.frdoc.db_set("phone", self.address["phoneNumber"])
        frdoc.frdoc.db_set("city", self.address["city"])
        frdoc.frdoc.db_set("email_id", self.address["email"])

        meta = frappe.get_meta(self.doctype)
        for addresskey in ["alternatePhoneNumber", "name"]:
            if meta.has_field("hepsiburada_" + addresskey.lower()):
                frdoc.db_set("hepsiburada_" + addresskey.lower(), self.doctype[addresskey])
        frdoc.save()
        return True
