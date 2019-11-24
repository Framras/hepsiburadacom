import frappe
from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection
from hepsiburadacom.HepsiburadaAddress import HepsiburadaAddress


class OrdersService:
    def __init__(self):
        self.hepsiburadaconnection = HepsiburadaConnection()
        self.servicepath = "/orders"
        self.integration = "order"
        self.company = frappe.defaults.get_user_default("Company")

    # Satıcıya Ait Listing Bilgilerini Listeleme (Get List of Listings [GET])
    # Bu metod satıcıya ait listing bilgilerine ulaşmanıza olanak tanır.

    def get_list_of_orderitems(self, offset, limit):

        servicemethod = "GET"
        servicetemplate = "/merchantid"
        servicetemplateresource = "/" + frappe.db.get_value("hepsiburadacom Integration Company Setting",
                                                            self.company, "merchantid")
        service = self.servicepath + servicetemplate + servicetemplateresource
        if offset is None or limit is None:
            params = None
        else:
            params = {
                "offset": offset,
                "limit": limit
            }

        return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, params, servicedata=None)

    def get_list_of_orders_details(self, offset, limit):

        servicemethod = "GET"
        servicetemplate = "/merchantid"
        servicetemplateresource = "/" + frappe.db.get_value("hepsiburadacom Integration Company Setting",
                                                            self.company, "merchantid")
        service = self.servicepath + servicetemplate + servicetemplateresource
        if offset is None or limit is None:
            params = None
        else:
            params = {
                "offset": offset,
                "limit": limit
            }

        return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, params, servicedata=None)


@frappe.whitelist()
def initiate_hepsiburada_orderitems():
    os = OrdersService()
    orderitems = os.get_list_of_orderitems(None, None)
    totalcount = orderitems["totalCount"]
    meta = frappe.get_meta("hepsiburada Order Item")
    for item in orderitems["items"]:
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": 'hepsiburada Order Item',
            "id": item["id"]
        }):
            newdoc = frappe.new_doc("hepsiburada Order Item")
            newdoc.id = item["id"]
            newdoc.company = os.company
            newdoc.insert()

        frdoc = frappe.get_doc('hepsiburada Order Item', item["id"])
        for itemkey in item.keys():
            if itemkey == "shippingAddress":
                sa = HepsiburadaAddress(item[itemkey], "Shipping")
                if sa.use_address() and meta.has_field((itemkey + "_" + "addressId").lower()):
                    frdoc.db_set((itemkey + "_" + "addressId").lower(), item[itemkey]["addressId"])
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
                        if sa.use_address() and meta.has_field((itemkey + "_" + ikey + "_" + "addressId").lower()):
                            frdoc.db_set((itemkey + "_" + ikey + "_" + "addressId").lower(),
                                         item[itemkey][ikey]["addressId"])
                    else:
                        if meta.has_field((itemkey + "_" + ikey).lower()):
                            frdoc.db_set((itemkey + "_" + ikey).lower(), item[itemkey][ikey])
            else:
                if meta.has_field(itemkey.lower()):
                    frdoc.db_set(itemkey.lower(), item[itemkey])

        frdoc.save()

    return frappe.db.count("hepsiburada Order Item",
                           filters={"merchantid": frappe.db.get_value("hepsiburadacom Integration Company Setting",
                                                                      os.company, "merchantid")}) == totalcount
