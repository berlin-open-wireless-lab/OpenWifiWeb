from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from OpenWifiWeb.forms import LoginForm
from openwifi.login_views import auth

@view_config(route_name='loginForm',
             renderer='templates/login.jinja2',
             layout='base')
@forbidden_view_config(renderer='templates/login.jinja2', layout='base')
def login(request):

    form = LoginForm(request.POST)
    save_url = request.route_url('loginForm')

    invalidCredentials = 'invalidCredentials' in request.GET

    if request.method == 'POST' and form.validate() and not invalidCredentials:
        data = {}
        login = form.login.data
        password = form.password.data
        
        resp = auth(request, login, password)

        if type(resp) == HTTPFound:
            return resp
        else:
            return HTTPFound(location=request.route_url('loginForm')+'?invalidCredentials', headers=resp.headers)

    return {'save_url':save_url, 'form':form, 'invalidCredentials':invalidCredentials}
