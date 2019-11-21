import hepsiburadacom.connectors.HepsiburadaConnection as HepsiburadaConnection


class ListingsService:
    def __index__(self):
        self._hepsiburadaconnection = HepsiburadaConnection()
        self._servicepath = "/listings"

    # Satıcıya Ait Listing Bilgilerini Listeleme (Get List of Listings [GET])
    # Bu metod satıcıya ait listing bilgilerine ulaşmanıza olanak tanır.
    def get_list_of_listings(self, offset, limit):
        company = frappe.defaults.get_user_default("Company")
        servicemethod = "GET"
        servicetemplate = "/merchantid"
        servicetemplateresource = "/" + frappe.db.get_value("hepsiburadacom Integration Company Settings",
                                                            company, "merchantid")
        service = self._servicepath + servicetemplate + servicetemplateresource
        if offset is None and limit is None:
            params = None
        else:
            params = {
                'offset': offset,
                'limit': limit
            }

        return self._hepsiburadaconnection.connect(servicemethod, service, params)
