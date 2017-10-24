from OpenWifiWeb.viewIncludes import *
from openwifi.utils import id_generator
from openwifi.authentication import get_node_by_request

openwrt_actions = ['delete', 'get config', 'save config to archive', 'parse config'] 

@view_config(route_name='openwrt_list', renderer='templates/openwrt.jinja2', layout='base', permission='view')
def openwrt_list(request):
    from openwifi.authentication import get_nodes
    openwrt = get_nodes(request)
    devices = []
    if request.POST:
        openwrts = []
        action = ""
        for name,value in request.POST.dict_of_lists().items():
            if name=='submitted':
                pass
            elif name=='action':
                action=value[0]
            elif value[0]=='on':
                openwrts.append(DBSession.query(OpenWrt).get(name))
        do_multi_openwrt_action(openwrts, action)
        return get_action_return(action, request)

    for device in openwrt:
        devices.append(str(device.uuid))


    table_fields = ['name', 'distribution', 'version', 'address', 'uuid','configuration', 'configured', 'master config']

    if 'group:admin' in request.effective_principals:
        table_fields.append('users')

    return {'idfield': 'uuid',
            'domain': 'openwrt',
            'devices': json.dumps(devices),
            'confdomain': 'openwrt_edit_config',
            'items': openwrt,
            'table_fields': table_fields,
            'actions' : openwrt_actions }

@view_config(route_name='openwrt_detail', renderer='templates/openwrt_detail.jinja2', layout='base', permission='node_access')
def openwrt_detail(request):
    device = get_node_by_request(request)
    if not device:
        return exc.HTTPNotFound()

    return {'device': device,
            'fields': ['name', 'distribution', 'version', 'address', 'uuid', 'login', 'password', 'templates', 'capabilities', 'communication_protocol', 'data'],
            'actions': openwrt_actions }

@view_config(route_name='openwrt_add', renderer='templates/openwrt_add.jinja2', layout='base', permission='node_add')
def openwrt_add(request):
    form = OpenWrtEditForm(request.POST)
    if request.method == 'POST' and form.validate():
        ap = OpenWrt(form.name.data, form.address.data, form.distribution.data, form.version.data, form.uuid.data, form.login.data, form.password.data, False)
        ap.setData('capabilities', form.capabilities.data)
        ap.setData('data', form.data.data)
        ap.setData('communication_protocol', form.communication_protocol.data)
        DBSession.add(ap)
        return HTTPFound(location=request.route_url('openwrt_list'))

    save_url = request.route_url('openwrt_add')
    return {'save_url':save_url, 'form':form}

@view_config(route_name='openwrt_edit', renderer='templates/openwrt_add.jinja2', layout='base', permission='node_access')
def openwrt_edit(request):
    device = get_node_by_request(request)
    if (not device):
        return exc.HTTPNotFound()
    form = OpenWrtEditForm(request.POST)
    if request.method == 'POST' and form.validate():
        device.set(form.name.data, form.address.data, form.distribution.data, form.version.data, form.uuid.data, form.login.data, form.password.data, device.configured)
        device.setData('capabilities', form.capabilities.data)
        device.setData('data', form.data.data)
        device.setData('communication_protocol', form.communication_protocol.data)
        return HTTPFound(location=request.route_url('openwrt_list'))
    else:
        form.name.data = device.name
        form.address.data = device.address
        form.distribution.data = device.distribution
        form.version.data = device.version
        form.uuid.data = device.uuid
        form.login.data = device.login
        form.password.data = device.password
        form.capabilities.data = device.capabilities
        form.communication_protocol.data = device.communication_protocol
        form.data.data = device.data

    save_url = request.route_url('openwrt_edit', uuid=device.uuid)
    return {'save_url':save_url, 'form':form}

@view_config(route_name='openwrt_edit_config', renderer='templates/openwrt_edit_config.jinja2', layout='base', permission='node_access')
def openwrt_edit_config(request):
    device = get_node_by_request(request)
    if not device:
        return exc.HTTPNotFound()
    conf = Uci()
    conf.load_tree(device.configuration);
    if request.POST:
        configsToBeUpdated=[]
        newConfig = {}
        for key, val in request.POST.dict_of_lists().items():
            if key != "submitted":
                val[0] = val[0].replace("'", '"') # for better json recognition
                packagename, configname, optionname = key.split()
                if not (packagename in newConfig.keys()):
                    newConfig[packagename] = {}
                    newConfig[packagename]['values'] = {}
                if not (configname in newConfig[packagename]['values'].keys()):
                    newConfig[packagename]['values'][configname] = {}
                try:
                    savevalue = json.loads(val[0])
                except ValueError:
                    savevalue = val[0]
                newConfig[packagename]['values'][configname][optionname] = savevalue
        newUci = Uci()
        newUci.load_tree(json.dumps(newConfig));
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(conf.diff(newUci));
        device.configuration = newUci.export_json()
        transaction.commit()
        return HTTPFound(location=request.route_url('openwrt_list'))
    return{ 'hiddenOptions' : ['.index','.type','.name','.anonymous'],
            'config'        : conf,
           'devicename'     : device.name}

def do_multi_openwrt_action(openwrts, action):
    for openwrt in openwrts:
        do_action_with_device(action, openwrt)

def do_action_with_device(action, device):
    if action == 'delete':
        DBSession.delete(device)
    if action == 'get config':
        jobtask.get_config.delay(device.uuid)
    if action == 'save config to archive':
        jobtask.archive_config(device.uuid)
    if action == 'parse config':
        from openwifi.dbHelper import parseToDBModel
        parseToDBModel(device)

def get_action_return(action, request):
    if action == 'delete' or \
       action == 'get config' or \
       action == 'parse config':
        return HTTPFound(location=request.route_url('openwrt_list'))
    if action == 'save config to archive':
        return HTTPFound(location=request.route_url('confarchive'))

@view_config(route_name='openwrt_action', renderer='templates/openwrt_add.jinja2', layout='base', permission='node_access')
def openwrt_action(request):
    action = request.matchdict['action']
    device = get_node_by_request(request)
    if not device:
        return exc.HTTPNotFound()
    do_action_with_device(action, device)
    return get_action_return(action, request)
