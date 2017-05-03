from OpenWifiWeb.viewIncludes import *

@view_config(route_name='luci', renderer='templates/luci.jinja2', layout='base', permission='view')
def luci2(request):
    print(request)
    uuid = request.matchdict['uuid']
    device = DBSession.query(OpenWrt).get(uuid)
    return {"uuid" : uuid,
            "password" : device.password,
            "login" : device.login}

@view_config(route_name='ubus',renderer="json", permission='view')
def ubus(request):
    command = request.matchdict['command']
    print(command)
    if len(command)>0:
        command = command[0]
    else:
        command=False
    uuid = request.matchdict['uuid']
    #print(request)
    #print(request.environ)
    proxy = Proxy()
    address=DBSession.query(OpenWrt).get(uuid).address
    #address='192.168.50.124'
    #request.environ["PATH_INFO"]="ubus/"+request.environ["PATH_INFO"].split('/')[-1]
    #request.environ["SERVER_NAME"]='192.168.50.116'
    #request.environ["SERVER_PORT"]=80
    request.server_port=80
    request.server_name=address
    request.host_name=address
    if command:
        request.upath_info='/ubus/'+request.upath_info.split('/')[-1]
    else:
        request.upath_info='/ubus'
    #print(request.url)
    #print(request.application_url)
    #print(request.path)
    #print(request.upath_info)
    #print(request.environ)
    res=request.get_response(proxy)
    #print(res.app_iter)
    #print(res)
    #print(str(res))
    return json.loads(res.app_iter[0].decode('utf8'))
