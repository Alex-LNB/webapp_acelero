import subprocess
import ipaddress
import datetime

class Network():
    def __init__(self,interface,hostname,address,netmask,gateway,dhcp,dns1,dns2,status,ssid,password):
        self.interface = interface
        self.hostname = hostname
        self.address = address
        self.netmask = netmask
        self.gateway = gateway
        self.dhcp = dhcp
        self.dns1 = dns1
        self.dns2 = dns2
        self.status = status
        self.ssid = ssid
        self.password = password

    @classmethod
    def get_net(cls, interface, wifi=False):
        sub0 = subprocess.run('/bin/hostname', shell=True, capture_output=True, text=True)
        hostname = sub0.stdout.strip()
        sub1 = subprocess.run(f'/sbin/ip addr show {interface} | /bin/grep inet', shell=True, capture_output=True, text=True)
        if len(sub1.stdout.strip())==0:
            net = Network(interface=interface,hostname=hostname,address='',netmask='',gateway='',dhcp='',dns1='',dns2='',status=False,ssid='',password='')
            return net
        buff = sub1.stdout.split()
        buff = ipaddress.ip_interface(buff[1].strip())
        buff = buff.with_netmask
        buff = buff.split('/')
        address = buff[0]
        netmask = buff[1]
        sub2 = subprocess.run(f'/sbin/ip route | /bin/grep default | /bin/grep {interface}', shell=True, capture_output=True, text=True)
        if len(sub2.stdout.strip())==0:
            gateway = ''
            dhcp = ''
        else:
            buff = sub2.stdout.strip().split()
            gateway = buff[2]
            dhcp = buff[6]
        sub3 = subprocess.run(f'/usr/bin/nmcli dev show {interface} | /bin/grep IP4.DNS', shell=True, capture_output=True, text=True)
        buff = sub3.stdout.strip().split('\n')
        if len(buff)==1 and len(buff[0].strip())>0:
            dns1, dns2 = buff[0].split()[1], ''
        elif len(buff)==2:
            dns1, dns2 = buff[0].split()[1], buff[1].split()[1]
        else:
            dns1, dns2 = '', ''
        if wifi:
            sub4 = subprocess.run(f'/bin/cat /etc/netplan/set-network-wifi.yaml | /bin/grep "\\""', shell=True, capture_output=True, text=True)
            buff = sub4.stdout.strip().split("\n")
            ssid, password = buff[0].strip(" :\""), buff[1].split()[1].strip("\"")
        else:
            ssid, password = '', ''
        net = Network(interface=interface,hostname=hostname,address=address,netmask=netmask,gateway=gateway,dhcp=dhcp,dns1=dns1,dns2=dns2,status=True,ssid=ssid,password=password)
        return net

    def is_dhcp(self):
        if self.dhcp=='dhcp':
            return True
        else:
            return False

    @classmethod
    def upnet_dhcp(cls, interface, wifi=False, ssid='', password=''):
        if wifi:
            origen = "/etc/netplan/set-network-wifi.yaml"
            doc = f'# Configuración de red wifi\nnetwork:\n  version: 2\n  wifis:\n    {interface}:\n      dhcp4: yes\n      access-points:\n        "{ssid}":\n          password: "{password}"'
        else:
            origen = "/etc/netplan/set-network-ethernet.yaml"
            doc = f'# Configuración de red ethernet\nnetwork:\n  version: 2\n  ethernets:\n    {interface}:\n      dhcp4: yes'
        try:
            archi=open(origen, mode='w+')
            archi.write(doc)
            archi.close()
            fin = 0
        except OSError as err:
            fin = f'Error {err.args}'
        print(fin)
        return fin

    @classmethod
    def upnet_static(cls, interface, address, netmask, gateway, dns1, dns2, wifi=False, ssid='', password=''):
        buff = ipaddress.ip_interface(f'{address}/{netmask}')
        buff = buff.with_prefixlen
        buff = buff.split('/')
        address, netmask = buff[0], buff[1]
        if wifi:
            origen = "/etc/netplan/set-network-wifi.yaml"
            doc = f'# Configuración de red wifi\nnetwork:\n  version: 2\n  wifis:\n    {interface}:\n      dhcp4: no\n      addresses: [{address}/{netmask}]\n      gateway4: {gateway}\n      nameservers:\n        addresses: [{dns1},{dns2}]\n      access-points:\n        "{ssid}":\n          password: "{password}"'
        else:
            origen = "/etc/netplan/set-network-ethernet.yaml"
            doc = f'# Configuración de red ethernet\nnetwork:\n  version: 2\n  ethernets:\n    {interface}:\n      dhcp4: no\n      addresses: [{address}/{netmask}]\n      gateway4: {gateway}\n      nameservers:\n        addresses: [{dns1},{dns2}]'
        try:
            archi=open(origen, mode='w+')
            archi.write(doc)
            archi.close()
            return 0
        except OSError as err:
            return f'Error {err.args}'

    @classmethod
    def apply_netplan(cls):
        sub1=subprocess.run(["/usr/sbin/netplan apply"], shell=True, capture_output=True, text=True)
        if sub1.returncode == 0:
            return f'Netplan ejecutado con exito. {sub1.stdout}', 0
        else:
            return f'Netplan fallo la ejecucion. {sub1.stderr}', 1

class Time_Local():
    def __init__(self, dt, zn, ntp):
        self.dt = dt
        self.zn = zn
        self.ntp = ntp

    @classmethod
    def get_timelocal(cls):
        dt = datetime.datetime.now()
        sub0 = subprocess.run('/usr/bin/timedatectl status | /bin/grep zone', shell=True, capture_output=True, text=True)
        buff = sub0.stdout.strip().split()
        zn = buff[2]
        sub1 = subprocess.run("/usr/bin/timedatectl status | /bin/grep 'timesyncd\|NTP'", shell=True, capture_output=True, text=True)
        buff = sub1.stdout.strip().split()
        ntp = buff[2]
        dtl = Time_Local(dt=dt, zn=zn, ntp=ntp)
        return dtl

    @classmethod
    def get_timezones(cls):
        sub0 = sub0 = subprocess.run('/usr/bin/timedatectl list-timezones', shell=True, capture_output=True, text=True)
        buff = sub0.stdout.strip().split()
        tup = []
        for zone in buff:
            tup.append((zone,zone))
        return tup

    @classmethod
    def set_timelocal(cls, ntp='yes', dt='', zn=''):
        if ntp=='yes':
            sub0 = subprocess.run('/usr/bin/timedatectl set-ntp yes', shell=True, capture_output=True, text=True)
            if sub0.returncode==0:
                return f'Hora y fecha actualizada.{sub0.stdout}'
            else:
                return f'Fallo la configuracion.{sub0.stderr}'
        else:
            sub0 = subprocess.run('/usr/bin/timedatectl set-ntp no', shell=True, capture_output=True, text=True)
            sub1 = subprocess.run(f"/usr/bin/timedatectl set-time '{dt}'", shell=True, capture_output=True, text=True)
            sub2 = subprocess.run(f"/usr/bin/timedatectl set-timezone '{zn}'", shell=True, capture_output=True, text=True)
            if sub0.returncode==0 and sub1.returncode==0 and sub2.returncode==0:
                return f'Hora y fecha actualizada.{sub0.stdout}.{sub1.stdout}.{sub2.stdout}'
            else:
                return f'Fallo la configuracion.{sub0.stderr}-{ntp}-.{sub1.stderr}-{dt}-.{sub2.stderr}-{zn}-'

class AccessPoint():
    def __init__(self, status, ssid, password):
        self.status = status
        self.ssid = ssid
        self.password = password

    @classmethod
    def get_ap(cls):
        sub0 = subprocess.run('/bin/systemctl status create_ap.service | /bin/grep Active', shell=True, capture_output=True, text=True)
        status = sub0.stdout.strip().split()[1]
        if status!='active':
            status = 'inactive'
        sub1 = subprocess.run('/bin/cat /etc/create_ap.conf | /bin/grep SSID', shell=True, capture_output=True, text=True)
        ssid = sub1.stdout.strip().split('=')[1]
        sub2 = subprocess.run('/bin/cat /etc/create_ap.conf | /bin/grep PASSPHRASE', shell=True, capture_output=True, text=True)
        password = sub2.stdout.strip().split('=')[1]
        ap = AccessPoint(status=status,ssid=ssid,password=password)
        return ap

    @classmethod
    def set_ap(cls, status):
        if status=='inactive':
            sub0 = subprocess.run('/bin/systemctl stop create_ap.service', shell=True, capture_output=True, text=True)
        else:
            sub0 = subprocess.run('/bin/systemctl start create_ap.service', shell=True, capture_output=True, text=True)
        if sub0.returncode==0:
            return ' AP actualizado '+sub0.stdout
        else:
            return ' AP actualizado '+sub0.stderr