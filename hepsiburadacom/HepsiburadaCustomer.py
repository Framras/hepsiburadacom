import frappe


class HepsiburadaCustomer:
    def __init__(self, customer: dict, customer_type: str, customer_tax_id: str):
        self.customer = customer
        self.customer_type = customer_type
        self.customer_tax_id = customer_tax_id
        self.doctype = "Customer"
        self.company = frappe.defaults.get_user_default("Company")
        self.company_setting_doctype = "hepsiburadacom Integration Company Setting"

    def use_customer(self):
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": self.doctype,
            "customer_name": self.customer["name"]
        }):
            new_customer_doc = frappe.new_doc(self.doctype)
            # required fields
            new_customer_doc.customer_name = self.customer["name"]
            new_customer_doc.customer_type = self.customer_type
            new_customer_doc.customer_group = frappe.db.get_value(self.company_setting_doctype,
                                                                  self.company, "customer_group")
            new_customer_doc.territory = frappe.db.get_value(self.company_setting_doctype, self.company,
                                                             "territory")
            # optional fields
            new_customer_doc.tax_id = self.customer_tax_id

            new_customer_doc.insert()
        return frappe.db.exists({
            "doctype": self.doctype,
            "customer_name": self.customer["name"]
        })
