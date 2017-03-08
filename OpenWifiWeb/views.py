from OpenWifiWeb.viewIncludes import *

from pyramid_ldap3 import (
    get_ldap_connector,
    groupfinder)

@view_config(route_name='home', renderer='templates/home.jinja2', layout='base', permission='view')
def home(request):
    return {}


@view_config(route_name='login',
             renderer='templates/login.jinja2',
         layout='base')
@forbidden_view_config(renderer='templates/login.jinja2', layout='base')
def login(request):
    form = LoginForm(request.POST)
    save_url = request.route_url('login')

    if request.method == 'POST' and form.validate():
        login = form.login.data
        password = form.password.data
        print("login " + login + " password " + password); 
        connector = get_ldap_connector(request)
        data = connector.authenticate(login, password)
        if data is not None:
            print("data found!!")
            dn = data[0]
            headers = remember(request, dn)
            return HTTPFound(location=request.route_url('home'), headers=headers)
        else:
            print("wrong credentials")
            error = 'Invalid credentials'

    return {'save_url':save_url, 'form':form}

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return Response('Logged out', headers=headers)

@view_config(route_name="configGraph", renderer='templates/configGraph.jinja2', layout='base', permission='view')
def drawConfigGraph(request):
    return {"confID" : request.matchdict["ID"]}

@view_config(route_name='settings', renderer='templates/settings.jinja2', layout='base', permission='view')
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

    save_url = request.route_url('settings')
    return {'save_url':save_url, 'form':form}


@view_config(route_name='file_upload', renderer='templates/file_upload.jinja2', layout='base', request_method="GET", permission='view')
def file_upload_get(request):
    return {}

@view_config(route_name='file_upload', renderer='templates/file_upload.jinja2', layout='base', request_method="POST", permission='view')
def file_upload_post(request):
    filename = request.POST['file'].filename #TODO: check filename if it can be trusted!
    input_file = request.POST['file'].file

    basepath = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(basepath, 'upload', filename)

    temp_file_path = file_path + '~'

    input_file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    os.rename(temp_file_path, file_path)

    return HTTPFound(location=request.route_url('home'))

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
