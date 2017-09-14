from OpenWifiWeb.viewIncludes import *
from openwifi.authentication import get_node_by_request

@view_config(route_name='luci', renderer='templates/luci.jinja2', layout='base', permission='node_access')
def luci2(request):
    device = get_node_by_request(request)
    return {"uuid" : device.uuid,
            "password" : device.password,
            "login" : device.login}

@view_config(route_name='ubus',renderer="json", permission='node_access')
def ubus(request):
    command = request.matchdict['command']

    if len(command)>0:
        command = command[0]
    else:
        command=False

    proxy = Proxy()
    address = get_node_by_request(request).address

    request.server_port=80
    request.server_name=address
    request.host_name=address
    if command:
        request.upath_info='/ubus/'+request.upath_info.split('/')[-1]
    else:
        request.upath_info='/ubus'

    res = request.get_response(proxy)

    return json.loads(res.app_iter[0].decode('utf8'))
