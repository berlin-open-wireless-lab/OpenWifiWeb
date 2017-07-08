from OpenWifiWeb.viewIncludes import *
from openwifi.utils import id_generator

@view_config(route_name='confarchive', renderer='templates/archive_list.jinja2', layout='base', permission='view')
def confarchive(request):
    configs = DBSession.query(ConfigArchive)
    return {'idfield': 'id',
            'domain': 'confarchive',
            'items': configs,
            'table_fields': ['date', 'id', 'router_uuid', 'configuration'],
            'actions' : {'show config':'archive_edit_config',
                         'apply config':'archive_apply_config'}
            }

@view_config(route_name='archive_edit_config', renderer='templates/archive_edit_config.jinja2', layout='base', permission='view')
def archive_edit_config(request):
    archiveConfig = DBSession.query(ConfigArchive).get(request.matchdict['id'])
    if not archiveConfig:
        return exc.HTTPNotFound()
    device = DBSession.query(OpenWrt).get(archiveConfig.router_uuid)
    if not device:
        return exc.HTTPNotFound()
    conf = Uci()
    conf.load_tree(archiveConfig.configuration);
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
        confToBeArchivedNew = ConfigArchive(datetime.now(),
                                            json.dumps(newConfig),
                                            archiveConfig.router_uuid,
                                            id_generator())
        DBSession.add(confToBeArchivedNew)
        return HTTPFound(location=request.route_url('confarchive'))
    return{ 'hiddenOptions' : ['.index','.type','.name','.anonymous'],
            'config'        : conf,
            'routerName'    : device.name,
            'date'          : archiveConfig.date}

@view_config(route_name='archive_apply_config', renderer='templates/archive_apply_config.jinja2', layout='base', permission='view')
def archiveapplyconfig(request):
    config = DBSession.query(ConfigArchive).get(request.matchdict['id'])
    if not config:
        return exc.HTTPNotFound()

    from openwifi.authentication import get_nodes
    openwrt = get_nodes(request)

    devices = {}
    if request.POST:
        for name,value in request.POST.dict_of_lists().items():
            if name!='submitted' and value: # if item is not the submit button and it's checkd
                deviceToBeUpdated = DBSession.query(openwrt).get(name)
                deviceToBeUpdated.configuration = config.configuration
                transaction.commit()
                jobtask.update_config.delay(str(deviceToBeUpdated.uuid))
            return HTTPFound(location = request.route_url('confarchive'))
    for device in openwrt:
        name = str(device.name)
        while name in devices.keys():
            name += '_'
        devices[name] = str(device.uuid)
    return { 'devices' : devices,
             'checked' : [] }
