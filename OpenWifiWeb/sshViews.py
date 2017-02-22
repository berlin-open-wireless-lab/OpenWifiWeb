from OpenWifiWeb.viewIncludes import *

@view_config(route_name='sshkeys', renderer='templates/sshkeys.jinja2', layout='base', permission='view')
def sshkeys(request):
    sshkeys = DBSession.query(SshKey)
    openwrts = {}
    for sshkey in sshkeys:
        openwrts[sshkey.id] = []
        for openwrt in sshkey.openwrt:
            openwrts[sshkey.id].append({ 'uuid' : openwrt.uuid, \
                                           'name' : openwrt.name})
    return { 'items' : sshkeys,
	     'openwrts' : openwrts,
             'table_fields' : ['id', 'key', 'comment', 'openwrt' ,'actions'],
             'actions' : ['delete']}

@view_config(route_name='sshkeys_add', renderer='templates/sshkeys_add.jinja2', layout='base', permission='view')
def sshkeys_add(request):
    form = SshKeyForm(request.POST)
    if request.method == 'POST' and form.validate():
        query = DBSession.query(sql_func.max(SshKey.id)) 
        try: 
            max = int(query[0][0])
        except:
            max = 0
        sshkey = SshKey(form.key.data, form.comment.data, max+1)
        DBSession.add(sshkey)
        return HTTPFound(location=request.route_url('sshkeys'))
    save_url = request.route_url('sshkeys_add')
    return {'save_url':save_url, 'form':form}


@view_config(route_name='sshkeys_assign', renderer='templates/archive_apply_config.jinja2', layout='base', permission='view')
def sshkeys_assign(request):
    sshkey = DBSession.query(SshKey).get(request.matchdict['id'])
    if not sshkey:
        return exc.HTTPNotFound()
    openwrt = DBSession.query(OpenWrt)
    devices = {}
    if request.POST:
        devices_to_be_updated = []
        for ow in openwrt:
            try:
                ow.ssh_keys.remove(sshkey)
                devices_to_be_updated.append(ow.uuid)
            except ValueError: # if the template is not assoc - do nothing
                pass
        for name,value in request.POST.dict_of_lists().items():
            if name!='submitted':
                device = DBSession.query(OpenWrt).get(name)
                if  value: # if item is not the submit button and it's checkd
                    device.ssh_keys.append(sshkey)
                    devices_to_be_updated.append(device.uuid)
        transaction.commit()
        for update_device in set(devices_to_be_updated):
            jobtask.update_openwrt_sshkeys.delay(update_device)
        return HTTPFound(location = request.route_url('sshkeys'))
    for device in openwrt:
        name = str(device.name)
        while name in devices.keys():
            name += '_'
        devices[name] = str(device.uuid)
    checked = []
    for device in sshkey.openwrt:
        checked.append(str(device.uuid))
    return { 'devices' : devices,
             'checked' : checked}

@view_config(route_name='sshkeys_action', renderer='templates/sshkeys.jinja2', layout='base', permission='view')
def sshkeys_action(request):
    action = request.matchdict['action']
    id = request.matchdict['id']
    sshkey = DBSession.query(SshKey).get(id)
    if not sshkey:
        return exc.HTTPNotFound()
    if action == 'delete':
        DBSession.delete(sshkey)
        return HTTPFound(location=request.route_url('sshkeys'))
    return { 'keys' : sshkeys }
