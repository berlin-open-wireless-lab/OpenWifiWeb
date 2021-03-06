from OpenWifiWeb.viewIncludes import *
from pyramid.httpexceptions import HTTPForbidden
from openwifi.utils import id_generator
from openwifi.authentication import auth_used

@view_config(route_name='home', renderer='templates/home.jinja2', layout='base', permission='view')
def home(request):
    return {}

@view_config(route_name="configGraph", renderer='templates/configGraph.jinja2', layout='base', permission='view')
def drawConfigGraph(request):
    return {"confID" : request.matchdict["ID"]}

@view_config(route_name='settings_gui', renderer='templates/settings.jinja2', layout='base', permission='view')
def settingsView(request):
    form = SettingsForm(request.POST)

    if request.method == 'POST' and form.validate():
        for key, value in form.data.items():
            alreadySavedSetting = DBSession.query(OpenWifiSettings).get(key)
            if alreadySavedSetting:
                alreadySavedSetting.value = value
            else:
                setting = OpenWifiSettings(key, value)
                DBSession.add(setting)
        return HTTPFound(location=request.route_url('home'))
    else:
        # Fill data from DB into form
        for field in form:
            setting = DBSession.query(OpenWifiSettings).get(field.name)
            if setting:
                field.data = setting.value

    save_url = request.route_url('settings_gui')
    return {'save_url':save_url, 'form':form}


@view_config(route_name='file_upload', renderer='templates/file_upload.jinja2', layout='base', request_method="GET", permission='view')
def file_upload_get(request):
    basepath = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(basepath, 'upload')
    user_id = None

    if auth_used(request) and request.user:
        file_path = os.path.join(basepath, 'upload', request.user.id)
        user_id = request.user.id
        if not os.path.exists(file_path):
            os.makedirs(file_path)

    files = os.listdir(file_path)

    # don't display gitkeep file
    try:
        files.pop(files.index('.gitkeep'))
    except ValueError:
        pass

    return {"files":files, 'user_id':user_id}

@view_config(route_name='file_upload', renderer='templates/file_upload.jinja2', layout='base', request_method="POST", permission='view')
def file_upload_post(request):
    filename = request.POST['file'].filename #TODO: check filename if it can be trusted!
    input_file = request.POST['file'].file

    basepath = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(basepath, 'upload', filename)

    if auth_used(request) and request.user:
        file_path = os.path.join(basepath, 'upload', request.user.id)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_path = os.path.join(basepath, 'upload', request.user.id, filename)

    temp_file_path = file_path + '~'

    input_file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    os.rename(temp_file_path, file_path)

    return HTTPFound(location=request.route_url('file_upload'))

@view_config(route_name='file_upload_delete', renderer='templates/file_upload.jinja2', layout='base', permission='view')
def file_upload_delete(request):
    filename = request.matchdict['FILE']

    basepath = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(basepath, 'upload', filename)

    if auth_used(request) and request.user:
        file_path = os.path.join(basepath, 'upload', request.user.id, filename)

    os.remove(file_path)
    return HTTPFound(location=request.route_url('file_upload'))

@view_config(route_name='administration', renderer='templates/administration.jinja2', layout='base', permission='modUsers')
def admin_route(request):
    return {}
