globalWebViews = [['home','Home'],
                  ['settings_gui','Settings'],
                  ['openwrt_list','OpenWrt'],
                  ['confarchive','Archive'],
                  ['sshkeys','SSH Keys'],
                  ['file_upload','File Upload']]

def addPluginRoutes(config):
    config.add_static_view('static', 'OpenWifiWeb:static', cache_max_age=3600)

    config.add_static_view('upload', 'OpenWifiWeb:upload', cache_max_age=3600)

    addOpenWrtRoutes(config)
    addArchiveRoutes(config)
    addSshRoutes(config)
    addLuciRoutes(config)

    config.add_route('settings_gui','/settings_gui')
    config.add_route('file_upload', '/file_upload')
    config.add_route('file_upload_delete', '/file_upload_delete/{FILE}')
    config.add_route('loginForm', '/loginForm')

    config.add_route('administration','/administration')

    config.add_route('configGraph', '/configGraph/{ID}')

def addOpenWrtRoutes(config):
    config.add_route('openwrt_list', '/openwrt')
    config.add_route('openwrt_detail', '/openwrt/{uuid}', factory='openwifi.node_context')
    config.add_route('openwrt_action', '/openwrt/{uuid}/{action}', factory='openwifi.node_context')
    config.add_route('openwrt_add', '/openwrt_add')
    config.add_route('openwrt_edit', '/openwrt_edit/{uuid}', factory='openwifi.node_context')
    config.add_route('openwrt_edit_config', '/openwrt_edit_config/{uuid}', factory='openwifi.node_context')

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
    config.add_route('luci_proxy', '/luci_proxy/{uuid}*req', factory='openwifi.node_context')
