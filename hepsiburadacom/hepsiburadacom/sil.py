from urllib.request import Request, urlopen, HTTPBasicAuthHandler, build_opener, install_opener
from urllib.error import URLError, HTTPError
import base64

servicemethod = 'GET'
serviceprotocol = "https://"
servicehost = "listing-external-sit.hepsiburada.com"
serviceurl = serviceprotocol + servicehost
serviceendpoint = "/listings/merchantid"

servicecontenttype = "application/json"

merchantid = "509778cf-7104-4c7f-850f-e14fdf5beb70"
serviceresource = "/" + merchantid

username = 'framras_dev'
password = 'Fr12345!'

servicedata = ""

req = Request(serviceurl + serviceendpoint + serviceresource)
req.add_header("Content-Type", servicecontenttype)
req.add_header("Host", servicehost)
userAndPass = base64.b64encode(username + ":" + password).decode("utf-8")
req.add_header("Authorization", userAndPass)
req.method = servicemethod

# Create an OpenerDirector with support for Basic HTTP Authentication...
# auth_handler = HTTPBasicAuthHandler()
# auth_handler.add_password(realm=None,
#                           uri=serviceurl,
#                           user=username,
#                           passwd=password)
# opener = build_opener(auth_handler)
# # ...and install it globally so it can be used with urlopen.
# install_opener(opener)

print(req.headers)
print(req.full_url)
try:
    response = urlopen(req)
    with response as f:
        print(f.read().decode('utf-8'))
except HTTPError as e:
    print('The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code))
except URLError as e:
    print('We failed to reach a server. ' + 'Reason: ' + e.reason)
