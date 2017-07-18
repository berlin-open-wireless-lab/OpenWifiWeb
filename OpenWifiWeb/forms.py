from wtforms import Form, TextField, IntegerField, PasswordField, StringField
from wtforms import widgets

class PasswordFieldNonHide(StringField):
    """
    A StringField, except renders an ``<input type="password">``.
    Also, whatever value is accepted by this field is not rendered back
    to the browser like normal fields.
    """
    widget = widgets.PasswordInput(hide_value=False)

class AccessPointAddForm(Form):
    name = TextField('name')
    hardware = TextField('hardware')
    address = TextField('address')
    radios_2g = IntegerField('2ghz Radios')
    radios_5g = IntegerField('5ghz Radios')

class AccessPointEditForm(Form):
    name = TextField('name')
    hardware = TextField('hardware')
    address = TextField('address')
    sshkey = TextField('sshkey') # private key to access this ap
    sshhostkey = TextField('sshhostkey') # remote host key

class OpenWrtEditForm(Form):
    name = TextField('name')
    address = TextField('address')
    distribution = TextField('distrubtion')
    version = TextField('version') # private key to access this ap
    uuid = TextField('uuid') # remote host key
    configured = TextField('configured')
    login = TextField('login')
    password = PasswordFieldNonHide('password')
    configuration = TextField('configuration')
    capabilities = TextField('capabilities')
    communication_protocol = TextField('communication_protocol')

class LoginForm(Form):
    login = TextField('login')
    password = PasswordField('password')

class SshKeyForm(Form):
    key = TextField('key')
    comment = TextField('comment')

class SettingsForm(Form):
    baseImageUrl = TextField('Base Image URL')
    baseImageChecksumUrl = TextField('Base Image Checksum file URL')
