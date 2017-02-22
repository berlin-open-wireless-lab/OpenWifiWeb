from OpenWifiWeb.viewIncludes import *

openwrt_actions = ['delete', 'getConfig', 'saveConfToArchive'] 

@view_config(route_name='openwrt_list', renderer='templates/openwrt.jinja2', layout='base', permission='view')
def openwrt_list(request):
    openwrt = DBSession.query(OpenWrt)
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
    return {'idfield': 'uuid',
            'domain': 'openwrt',
            'devices': json.dumps(devices),
            'confdomain': 'openwrt_edit_config',
            'items': openwrt,
            'table_fields': ['name', 'distribution', 'version', 'address', 'uuid','configuration', 'configured'],
            'actions' : openwrt_actions }

@view_config(route_name='openwrt_detail', renderer='templates/openwrt_detail.jinja2', layout='base', permission='view')
def openwrt_detail(request):
    device = DBSession.query(OpenWrt).get(request.matchdict['uuid'])
    if not device:
        return exc.HTTPNotFound()

    return {'device': device,
            'fields': ['name', 'distribution', 'version', 'address', 'uuid', 'login', 'password', 'templates'],
            'actions': openwrt_actions }

@view_config(route_name='openwrt_add', renderer='templates/openwrt_add.jinja2', layout='base', permission='view')
def openwrt_add(request):
    form = OpenWrtEditForm(request.POST)
    if request.method == 'POST' and form.validate():
        ap = OpenWrt(form.name.data, form.address.data, form.distribution.data, form.version.data, form.uuid.data, form.login.data, form.password.data, False)
        DBSession.add(ap)
        return HTTPFound(location=request.route_url('openwrt_list'))

    save_url = request.route_url('openwrt_add')
    return {'save_url':save_url, 'form':form}

@view_config(route_name='openwrt_edit_config', renderer='templates/openwrt_edit_config.jinja2', layout='base', permission='view')
def openwrt_edit_config(request):
    device = DBSession.query(OpenWrt).get(request.matchdict['uuid'])
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
        jobtask.update_config.delay(request.matchdict['uuid'])
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
    if action == 'getConfig':
        jobtask.get_config.delay(device.uuid)
    if action == 'saveConfToArchive':
        confToBeArchived = ConfigArchive(datetime.now(),device.configuration,device.uuid,id_generator())
        DBSession.add(confToBeArchived)

def get_action_return(action, request):
    if action == 'delete':
        return HTTPFound(location=request.route_url('openwrt_list'))
    if action == 'getConfig':
        return HTTPFound(location=request.route_url('openwrt_list'))
    if action == 'saveConfToArchive':
        return HTTPFound(location=request.route_url('confarchive'))

@view_config(route_name='openwrt_action', renderer='templates/openwrt_add.jinja2', layout='base', permission='view')
def openwrt_action(request):
    action = request.matchdict['action']
    device = DBSession.query(OpenWrt).get(request.matchdict['uuid'])
    if not device:
        return exc.HTTPNotFound()
    do_action_with_device(action, device)
    return get_action_return(action, request)