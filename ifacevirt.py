import subprocess

if __name__ == '__main__':
    sub0 = subprocess.run('/usr/sbin/iw dev wlan0 interface add ap0 type __ap', shell=True)
    if sub0.returncode==0:
        sub1 = subprocess.run('/usr/bin/systemctl start create_ap.service', shell=True)