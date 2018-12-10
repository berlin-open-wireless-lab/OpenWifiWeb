from OpenWifiWeb.viewIncludes import *
from openwifi.authentication import get_node_by_request

@view_config(route_name="luci_proxy", permission='node_access')
def luci_proxy(request):
    device = get_node_by_request(request)
    uuid = request.matchdict['uuid']

    address = device.address

    path = "/"
    for sub_path in request.matchdict['req']:
        path += sub_path + "/"

    proxy = Proxy()
    request.upath_info = path

    request.server_port=80
    request.server_name=address

    res = request.get_response(proxy)

    # TODO: find a better way than this diry hack
    # to get rid of the hop-by-hop header stuff
    try:
        res.headers.pop("Keep-Alive")
    except:
        pass

    try:
        res.headers.pop("Connection")
    except:
        pass

    try:
        res.headers.pop("Transfer-Encoding")
    except:
        pass

    luci_url = 'cgi-bin/luci'
    proxied_url = "luci_proxy/"+uuid+"/cgi-bin/luci"

    escaped_luci_url = 'cgi-bin\/luci'
    escaped_proxied_url = "luci_proxy\/"+uuid+"\/cgi-bin\/luci"

    static_luci_url = 'luci-static/'
    static_proxied_url = "luci_proxy/"+uuid+"/luci-static/"

    escaped_static_luci_url = 'luci-static\/'
    escaped_static_proxied_url = "luci_proxy\/"+uuid+"\/luci-static\/"

    # TODO: do these things based on content-type
    try:
        res.text = res.text.replace(luci_url,proxied_url)
        res.text = res.text.replace(escaped_luci_url,escaped_proxied_url)
        res.text = res.text.replace(static_luci_url,static_proxied_url)
        res.text = res.text.replace(escaped_static_luci_url,escaped_static_proxied_url)
    except:
        pass

    if res.status_int == 302:
        device_location = 'http://'+address+':80'
        this_location = request.host_url
        res.headers['Location'] = res.headers['Location'].replace(device_location, this_location)
        res.headers['Location'] = res.headers['Location'].replace(luci_url, proxied_url)
        res.headers['Set-Cookie'] = res.headers['Set-Cookie'].replace(luci_url, proxied_url)

    return res
