from wtforms import Form
from wtforms import StringField, PasswordField, EmailField, IntegerField, TextAreaField, BooleanField, FormField, DecimalField, SelectField, DateTimeField
from wtforms import validators
from .set_network import Time_Local

class LoginForm(Form):
    username = StringField('Username', [
        validators.length(min=3,max=50)
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])

class RegUserForm(Form):
    username = StringField('Username', [
        validators.length(min=3,max=50)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.length(min=5),
        validators.EqualTo('confirm_password')
    ])
    confirm_password = PasswordField('Confirmar password')

class UserForm(Form):
    name = StringField('Nombre',[
        validators.length(max=50),
    ])
    phone = StringField('Telefono',[
        validators.length(max=10),
    ])
    email = EmailField('Correo',[
        validators.length(max=100),
        validators.Email()
    ])

class NetworkForm(Form):
    disabled = ''
    address = StringField('Direccion IP',[
        validators.DataRequired(),
        validators.IPAddress(),
    ], render_kw={disabled:''})
    netmask = StringField('Mascara de red',[
        validators.DataRequired(),
        validators.IPAddress(),
    ], render_kw={disabled:''})
    gateway = StringField('Puerta de enlace',[
        validators.DataRequired(),
        validators.IPAddress(),
    ], render_kw={disabled:''})
    dhcp = SelectField('Enrutamiento', choices=[('dhcp','dhcp'),('static','static')])
    dns1 = StringField('DNS 1')
    dns2 = StringField('DNS 2')
    ssid = StringField('SSID')
    password = StringField('Password-SSID')

class DatetimeForm(Form):
    ntp = SelectField('Obtener automaticamente', choices=[('yes','Si'),('no','No')])
    dt = DateTimeField('Fecha y hora')
    zn = SelectField('Zona horaria', choices=Time_Local.get_timezones())

class ApForm(Form):
    status = SelectField('Punto de acceso (Hotspot)', choices=[('active','Activado'),('inactive','Desactivado')])
    ssid = StringField('AP_SSID')
    password = StringField('AP_PASSWORD')