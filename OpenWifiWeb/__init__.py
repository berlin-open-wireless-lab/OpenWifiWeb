globalWebViews = [['home','Home'],
                  ['settings','Settings'],
                  ['openwrt_list','OpenWrt'],
                  ['confarchive','Archive'],
                  ['templates','Templates'],
                  ['sshkeys','SSH Keys'],
                  ['file_upload','File Upload']]

def addPluginRoutes(config):
    config.add_static_view('static', 'OpenWifiWeb:static', cache_max_age=3600)

    config.add_static_view('upload', 'OpenWifiWeb:upload', cache_max_age=3600)

    addOpenWrtRoutes(config)
    addTemplatesRoutes(config)
    addArchiveRoutes(config)
    addSshRoutes(config)
    addLuciRoutes(config)

    config.add_route('home', '/')
    config.add_route('settings','/settings')
    config.add_route('file_upload', '/file_upload')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('configGraph', '/configGraph/{ID}')

def addOpenWrtRoutes(config):
    config.add_route('openwrt_list', '/openwrt')
    config.add_route('openwrt_detail', '/openwrt/{uuid}')
    config.add_route('openwrt_action', '/openwrt/{uuid}/{action}')
    config.add_route('openwrt_add', '/openwrt_add')
    config.add_route('openwrt_edit', '/openwrt_edit/{uuid}')
    config.add_route('openwrt_edit_config', '/openwrt_edit_config/{uuid}')

def addTemplatesRoutes(config):
    config.add_route('templates', '/templates')
    config.add_route('templates_add', '/templates_add')
    config.add_route('templates_assign', '/templates_assign/{id}')
    config.add_route('templates_edit', '/templates_edit/{id}')
    config.add_route('templates_delete', '/templates_delete/{id}')
    config.add_route('templates_action', '/templates/{id}/{action}')

def addArchiveRoutes(config):
    config.add_route('confarchive', '/confarchive')
    config.add_route('archive_edit_config', '/archive_edit_config/{id}')
    config.add_route('archive_apply_config', '/archive_apply_config/{id}')

def addSshRoutes(config):
    config.add_route('sshkeys', '/sshkeys')
    config.add_route('sshkeys_add', '/sshkeys_add')
    config.add_route('sshkeys_assign', '/sshkeys_assign/{id}')
    config.add_route('sshkeys_action', '/sshkeys/{id}/{action}')

def addLuciRoutes(config):
    config.add_route('luci', '/luci/{uuid}')
    config.add_route('ubus', '/ubus/{uuid}*command')
