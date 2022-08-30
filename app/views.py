from os import getcwd, scandir
from flask import Blueprint
from flask import render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import current_user, login_required, login_user, logout_user

from . import login_manager
from .forms import LoginForm, RegUserForm, UserForm, ApForm, DatetimeForm, NetworkForm
from .models import User
from .set_network import AccessPoint, Network, Time_Local
from .consts import interface
from .filesacl import muestreoRapido, muestreoSimple

page = Blueprint('page',__name__)
folder = '/files_acl/'
folder_route = getcwd()+folder

@page.before_app_first_request
def before_req():
    User.set_admin()

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(id)

@page.route('/', methods=['GET','POST'])
@page.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.get_by_username(form.username.data)
        if user and user.verify_password(form.password.data):
            login_user(user)
            flash(f'Iniciaste sesion {user.username}')
            return redirect(url_for('.index'))
        else: 
            flash('Usuario y/o contraseña invalidos', 'error')
            return redirect(url_for('.login'))
    return render_template('auth/login.html', title='Login', form=form)

@page.route('/logout')
def logout():
    logout_user()
    flash('Cerraste session')
    return redirect(url_for('.login'))

@page.route('/register', methods=['GET','POST'])
@login_required
def register():
    form = RegUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.create_element(form.username.data, form.password.data)
        flash(f'Usuario {user.username} creado')
        return redirect(url_for('.index'))
    return render_template('auth/register.html', title='Register', form=form)

@page.route('/user/<int:user_id>')
@login_required
def show_user(user_id):
    user = User.get_by_id(user_id)
    return render_template('auth/show_user.html', title='User', user=user)    

@page.route('/user/edit/<int:user_id>', methods=['GET','POST'])
@login_required
def edit_user(user_id):
    user = User.get_by_id(user_id)
    if not (current_user.id == user.id or current_user.is_admin):
        flash('No tiene permiso para editar este usuario')
        return redirect(url_for('.index'))
    form = UserForm(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        user = User.update_element(user.id,form.name.data,form.phone.data,form.email.data)
        if user:
            flash(f'Usuario {user.username} actualizado')
    return render_template('auth/user_edit.html', title='Edit User', form=form, user=user)

@page.route('/index')
@login_required
def index():
    dic = sorted(scandir(folder_route), key=lambda e: e.name)
    return render_template('index.html', title='Index', dic=dic, fold=folder)

@page.get('/index/<string:name_file>')
@login_required
def get_file(name_file):
    print(name_file)
    return send_from_directory(folder_route,path=name_file,as_attachment=False)

@page.get('/index/download/<string:name_file>')
@login_required
def download_file(name_file):
    print(name_file)
    return send_from_directory(folder_route,path=name_file,as_attachment=True)

@page.get('/index/muestreo/rapido')
@login_required
def get_muestreo_rapido():
    msj = muestreoRapido(folder_route,10)
    flash(msj)
    return redirect(url_for('.index'))

@page.get('/index/muestreo/simple')
@login_required
def get_muestreo_simple():
    msj = muestreoSimple(folder_route)
    flash(msj)
    return redirect(url_for('.index'))

@page.route('/setdate', methods=['GET','POST'])
@login_required
def setdate():
    if not current_user.is_admin:
        flash('No tiene permisos de administrador')
        redirect(url_for('.index'))
    dtl = Time_Local.get_timelocal()
    form = DatetimeForm(request.form, obj=dtl)
    if request.method == 'POST' and form.validate():
        msj = Time_Local.set_timelocal(form.ntp.data,form.dt.data,form.zn.data)
        flash(f'{msj}')
        return redirect(url_for('.index'))
    return render_template('config/setdate.html', title='Datetime', form=form, dtl=dtl)

@page.route('/setnet', methods=['GET','POST'])
@login_required
def setnet():
    if not current_user.is_admin:
        flash('No tiene permisos de administrador')
        redirect(url_for('.index'))
    ap = AccessPoint.get_ap()
    form = ApForm(request.form, obj=ap)
    ethe = Network.get_net(interface=interface['ether'])
    wifi = Network.get_net(interface=interface['wifi'], wifi=True)
    if request.method == 'POST':
        buff = AccessPoint.set_ap(form.status.data)
        y, z= Network.apply_netplan()
        flash(f'{buff} - {y}')
        return redirect(url_for('.index'))
    return render_template('config/setnet.html', title='Network', form=form, ethe=ethe, wifi=wifi)

@page.route('/setnet/ethernet', methods=['GET','POST'])
@login_required
def setethe():
    if not current_user.is_admin:
        flash('No tiene permisos de administrador')
        redirect(url_for('.index'))
    net = Network.get_net(interface=interface['ether'])
    form = NetworkForm(request.form, obj=net)
    if request.method == 'POST' and form.validate():
        if form.dhcp.data == 'dhcp':
            x = Network.upnet_dhcp(interface=interface['ether'])
        elif form.dhcp.data == 'static':
            x = Network.upnet_static(interface=interface['ether'], address=form.address.data, netmask=form.netmask.data, gateway=form.gateway.data, dns1=form.dns1.data, dns2=form.dns2.data)
        if x == 0:
            y, z= Network.apply_netplan()
            flash(f'Configuracion de red actualizada - {y}')
            return redirect(url_for('.index'))
        else:
            flash(f'Fallo la configuracion de red - {x}','error')
            return redirect(url_for('.index'))
    return render_template('config/setethe.html', title='Ethernet', net=net, form=form)

@page.route('/setnet/wifi', methods=['GET','POST'])
@login_required
def setwifi():
    if not current_user.is_admin:
        flash('No tiene permisos de administrador')
        redirect(url_for('.index'))
    net = Network.get_net(interface=interface['wifi'],wifi=True)
    form = NetworkForm(request.form, obj=net)
    if request.method == 'POST' and form.validate():
        if form.dhcp.data == 'dhcp':
            x = Network.upnet_dhcp(interface=interface['wifi'], wifi=True, ssid=form.ssid.data, password=form.password.data)
        elif form.dhcp.data == 'static':
            x = Network.upnet_static(interface=interface['wifi'], address=form.address.data, netmask=form.netmask.data, gateway=form.gateway.data, dns1=form.dns1.data, dns2=form.dns2.data, wifi=True, ssid=form.ssid.data, password=form.password.data)
        if x == 0:
            y, z= Network.apply_netplan()
            flash(f'Configuracion de red actualizada - {y}')
            return redirect(url_for('.index'))
        else:
            flash(f'Fallo la configuracion de red - {x}','error')
            return redirect(url_for('.index'))
    return render_template('config/setwifi.html', title='Wifi', net=net, form=form)
