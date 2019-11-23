import frappe
from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection


class OrdersService:
    def __init__(self):
        self.hepsiburadaconnection = HepsiburadaConnection()
        self.servicepath = "/orders"
        self.integration = "order"

    # Satıcıya Ait Listing Bilgilerini Listeleme (Get List of Listings [GET])
    # Bu metod satıcıya ait listing bilgilerine ulaşmanıza olanak tanır.

    def get_list_of_orderitems(self, offset, limit):
        company = frappe.defaults.get_user_default("Company")
        servicemethod = "GET"
        servicetemplate = "/merchantid"
        servicetemplateresource = "/" + frappe.db.get_value("hepsiburadacom Integration Company Settings",
                                                            company, "merchantid")
        service = self.servicepath + servicetemplate + servicetemplateresource
        if offset is None or limit is None:
            params = None
        else:
            params = {
                'offset': offset,
                'limit': limit
            }

        return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, params, servicedata=None)


@frappe.whitelist()
def initiate_hepsiburada_orderitems():
    os = OrdersService()
    orderitems = os.get_list_of_orderitems(None, None)
    meta = frappe.get_meta("hepsiburada Order Items")
    for orderitem in orderitems["items"]:
        # check if record exists by filters
        if not frappe.db.exists({
            'doctype': 'hepsiburada Order Items',
            'id': str(orderitem["id"])
        }):
            newdoc = frappe.new_doc("hepsiburada Order Items")
            newdoc.id = str(orderitem["id"])
            newdoc.insert()

        frdoc = frappe.get_doc('hepsiburada Order Items', str(orderitem["id"]))
        for itemkey in orderitem.keys():
            if itemkey == "totalPrice" or \
                    itemkey == "unitPrice" or \
                    itemkey == "shippingAddress" or \
                    itemkey == "commission" or \
                    itemkey == "cargoCompanyModel":
                for ikey in orderitem[itemkey].keys():
                    if meta.has_field((itemkey + "_" + ikey).lower()):
                        frdoc.db_set((itemkey + "_" + ikey).lower(), orderitem[itemkey][ikey])
            elif itemkey == "hbDiscount":
                for ikey in orderitem[itemkey].keys():
                    if ikey == "totalPrice" or \
                            ikey == "unitPrice":
                        for skey in orderitem[itemkey][ikey].keys():
                            if meta.has_field((itemkey + "_" + ikey + "_" + skey).lower()):
                                frdoc.db_set(
                                    (itemkey + "_" + ikey + "_" + skey).lower(), orderitem[itemkey][ikey][skey])
            elif itemkey == "invoice":
                for ikey in orderitem[itemkey].keys():
                    if ikey == "address":
                        for skey in orderitem[itemkey][ikey].keys():
                            if meta.has_field((itemkey + "_" + ikey + "_" + skey).lower()):
                                frdoc.db_set(
                                    (itemkey + "_" + ikey + "_" + skey).lower(), orderitem[itemkey][ikey][skey])
                    else:
                        if meta.has_field((itemkey + "_" + ikey).lower()):
                            frdoc.db_set((itemkey + "_" + ikey).lower(), orderitem[itemkey][ikey])
            else:
                if meta.has_field(itemkey.lower()):
                    frdoc.db_set(itemkey.lower(), orderitem[itemkey])

        frdoc.save()

    return "success"
