# Formato:  *9900<comando>
# Comando:      *9900XY     Lectura de posicion y temperatura
# Respuesta:    $ x.x, y.y, t.t, SN

sim_example = '$-00.920,-00.210,030.045,N1212'
xdr_example = '$YXXDR,A,-00.920,D,N,A,-00.210,D,E,C,030.045,C,T-N1212*57'
ash_example = '$PASH,XDR,A,-00.920,D,N,A,-00.210,D,E,C,030.045,C,T-N1212'
tcm_example = '$P-00.905R002.190*19'

class LecturaAcelero():
    def __init__(self,x,y,u,t,sn):
        self.valX = x
        self.valY = y
        self.units = u
        self.temp = t
        self.sn = sn

    @classmethod
    def lee_sim(cls, cad):
        if len(cad)==0:
            return LecturaAcelero('0.0','0.0','-','0.0','-')
        buff = cad.strip(' $').split(',')
        data = LecturaAcelero(buff[0].strip(),buff[1].strip(),'Grados',buff[2].strip(),buff[3].strip())
        return data
    
    @classmethod
    def lee_xdr(cls, cad):
        buff = cad.strip(' $0123456789').rstrip('*').split(',')
        if buff[3]=='D' and buff[7]=='D': unit = 'Grados'
        elif buff[3]=='M' and buff[7]=='M': unit = 'MicroRadianes'
        else: unit = 'none'
        sn = buff[12].split('-')[1]
        data = LecturaAcelero(buff[6],buff[2],unit,buff[10],sn)
        return data

    @classmethod
    def lee_ash(cls, cad):
        buff = cad.strip(' $').split(',')
        if buff[4]=='D' and buff[8]=='D': unit = 'Grados'
        elif buff[4]=='M' and buff[8]=='M': unit = 'MicroRadianes'
        else: unit = 'none'
        sn = buff[13].split('-')[1]
        data = LecturaAcelero(buff[7],buff[3],unit,buff[11],sn)
        return data

    @classmethod
    def lee_tcm(cls, cad):
        buff = cad.strip(' $0123456789').rstrip('*').lstrip('P').split('R')
        unit = 'Grados'        
        sn = 'none'
        t = 'none'
        data = LecturaAcelero(buff[1],buff[0],unit,t,sn)
        return data

import serial, threading, time
from os import getcwd

puerto = '/dev/ttyUSB0'
baudios = 230400
buffer = []
t_muestra = 0.1

def leePuerto(ciclos:int):
    global buffer
    try:
        ser_lee = serial.Serial(puerto, baudrate = baudios, timeout=1.0)
        for i in range(ciclos):
            lec, com = ser_lee.readline(), ser_lee.readline()
            buffer.append([lec.decode('UTF-8'),time.strftime('%X')])
    except serial.SerialException as err:
        print('Error del puerto:\n',err)
        buffer.append(['',''])
    except BaseException as err:
        print('Error al leer el puerto:\n',err)
        ser_lee.close()
    else:
        ser_lee.close()

def muestreoRapido(ruta:str,t:int):
    global buffer
    buffer = []
    ciclos = int(t/t_muestra)
    nombre = time.strftime('%Y%m%d')+'_rapido.txt'
    try:
        leer = threading.Thread(target=leePuerto, args=(ciclos,))
        ser_cmd = serial.Serial(puerto, baudrate = baudios)
        leer.start()
        for i in range(ciclos):
            ser_cmd.write(b'*9900XY\n')
            time.sleep(t_muestra)
        leer.join()
    except serial.SerialException as err:
        print('Error del puerto:\n',err)
        return f'Error del puerto:\n{err}'
    except BaseException as err:
        print('Error al obtener la muestra:\n',err)
        ser_cmd.close()
        return f'Error al obtener la muestra:\n{err}'
    else:
        ser_cmd.close()
    try:
        archi = open(ruta+nombre,mode='a+')
        for buff in buffer:
            lec = LecturaAcelero.lee_sim(buff[0])
            archi.write(f"{lec.valX},{lec.valY},{buff[1]}\n")
    except BaseException as err:
        print('Error al escribir la muestra:\n',err)
        archi.close()
        return f'Error al escribir la muestra:\n{err}'
    else:
        archi.close()
        return 'Muestreo rapido exitoso. Archivo: '+nombre

def muestreoSimple(ruta:str):
    global buffer
    buffer = []
    ciclos = int(1/t_muestra)
    nombre = time.strftime('%Y%m%d')+'_simple.txt'
    try:
        leer = threading.Thread(target=leePuerto, args=(ciclos,))
        ser_cmd = serial.Serial(puerto, baudrate = baudios)
        leer.start()
        for i in range(ciclos):
            ser_cmd.write(b'*9900XY\n')
            time.sleep(t_muestra)
        leer.join()
    except serial.SerialException as err:
        print('Error del puerto:\n',err)
        return f'Error del puerto:\n{err}'
    except BaseException as err:
        print('Error al obtener la muestra:\n')
        ser_cmd.close()
        return f'Error al obtener la muestra:\n{err}'
    else:
        ser_cmd.close()
    x, y, z= 0.0, 0.0, 0
    for buff in buffer:
        lec = LecturaAcelero.lee_sim(buff[0])
        x += float(lec.valX.strip())
        y += float(lec.valY.strip())
        z += 1
    try:
        archi = open(ruta+nombre,mode='a+')
        archi.write(f"{round(x/z,4)},{round(y/z,4)},{time.strftime('%X')}\n")
    except BaseException as err:
        print('Error al escribir la muestra:\n',err)
        archi.close()
        return f'Error al escribir la muestra:\n{err}'
    else:
        archi.close()
        return 'Muestreo simple exitoso. Archivo: '+nombre

if __name__ == '__main__':
    print(muestreoRapido(getcwd()+'/',2))
    print(muestreoRapido(getcwd()+'/',5))
    print(muestreoRapido(getcwd()+'/',10))
    print(muestreoSimple(getcwd()+'/'))
    print(muestreoSimple(getcwd()+'/'))
    print(muestreoSimple(getcwd()+'/'))