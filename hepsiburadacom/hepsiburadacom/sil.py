from hepsiburadacom.HepsiburadaConnection import HepsiburadaConnection
from hepsiburadacom.HepsiburadaAddress import HepsiburadaAddress

username = 'framras_dev'
password = 'Fr12345!'
merchantid = '509778cf-7104-4c7f-850f-e14fdf5beb70'
ordernumber = '041241372'

hepsiburadaconnection = HepsiburadaConnection()
servicepath = "/orders"
integration = "order"


# Satıcıya Ait Listing Bilgilerini Listeleme (Get List of Listings [GET])
# Bu metod satıcıya ait listing bilgilerine ulaşmanıza olanak tanır.

def get_list_of_orderitems(self, offset, limit):
    servicemethod = "GET"
    servicetemplate = "/merchantid"
    servicetemplateresource = "/" + merchantid
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
    servicetemplateresource = "/" + merchantid
    service = self.servicepath + servicetemplate + servicetemplateresource
    if offset is None or limit is None:
        params = None
    else:
        params = {
            "offset": offset,
            "limit": limit
        }

    return self.hepsiburadaconnection.connect(self.integration, servicemethod, service, params, servicedata=None)


def initiate_hepsiburada_orderitems():
    orderitems = get_list_of_orderitems(None, None)
    meta = frappe.get_meta("hepsiburada Order Item")
    for orderitem in orderitems["items"]:
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": 'hepsiburada Order Item',
            "id": orderitem["id"]
        }):
            newdoc = frappe.new_doc("hepsiburada Order Item")
            newdoc.id = orderitem["id"]
            newdoc.insert()

        frdoc = frappe.get_doc('hepsiburada Order Item', orderitem["id"])
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


@frappe.whitelist()
def initiate_hepsiburada_orders():
    os = OrdersService()
    orderitems = os.get_list_of_orders_details(None, None)
    meta = frappe.get_meta("hepsiburada Order")
    for orderitem in orderitems["items"]:
        # check if record exists by filters
        if not frappe.db.exists({
            "doctype": 'hepsiburada Order',
            "id": str(orderitem["id"])
        }):
            newdoc = frappe.new_doc("hepsiburada Order")
            newdoc.id = str(orderitem["id"])
            newdoc.insert()

        frdoc = frappe.get_doc('hepsiburada Order Item', str(orderitem["id"]))
        for itemkey in orderitem.keys():
            if itemkey == "shippingAddress":
                sa = HepsiburadaAddress(orderitem[itemkey], "shipping")
                sareturn = sa.use_address()
            elif itemkey == "totalPrice" or \
                    itemkey == "unitPrice" or \
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
                        sa = HepsiburadaAddress(orderitem[itemkey][ikey], "billing")
                        sareturn = sa.use_address()
                    else:
                        if meta.has_field((itemkey + "_" + ikey).lower()):
                            frdoc.db_set((itemkey + "_" + ikey).lower(), orderitem[itemkey][ikey])
            else:
                if meta.has_field(itemkey.lower()):
                    frdoc.db_set(itemkey.lower(), orderitem[itemkey])

        frdoc.save()

    return sareturn
