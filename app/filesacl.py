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

buffer = []
t_muestra = 0.2

def leePuerto(ciclos:int):
    global buffer
    print("crea puerto que lee")
    ser_lee = serial.Serial('/dev/ttyUSB0', baudrate = 230400, timeout=1.0) #---
    try:
        for i in range(ciclos):
            time.sleep(0.2)
            #lec, com = b'$ -1.4500, -0.9283,28.40,N9805', b'*9900XY'
            lec, com = ser_lee.readline(), ser_lee.readline()
            buffer.append([lec.decode('UTF-8'),time.strftime('%X')])
    except serial.SerialException as err:
        print('Error del puerto o tiempo de espera',err)
        buffer.append(['',''])
    except BaseException as err:
        print('Error al leer el puerto',err)
        print('cierra puerto que lee')
        ser_lee.close() #---
    else:
        print('cierra puerto que lee')
        ser_lee.close() #---

def muestreoRapido(ruta:str,t:int):
    global buffer
    buffer = []
    ciclos = int(t/t_muestra)
    nombre = time.strftime('%Y%m%d')+'_rapido.txt'
    leer = threading.Thread(target=leePuerto, args=(ciclos,))
    print("crea puerto que escribe")
    ser_cmd = serial.Serial('/dev/ttyUSB0', baudrate = 230400) #---
    leer.start()
    for i in range(ciclos):
        ser_cmd.write(b'*9900XY\n') #---
        time.sleep(t_muestra)
    leer.join()
    print('cierra puerto que escribe')
    ser_cmd.close() #---
    try:
        archi = open(ruta+nombre,mode='a+')
        for buff in buffer:
            lec = LecturaAcelero.lee_sim(buff[0])
            archi.write(f"{lec.valX},{lec.valY},{buff[1]}\n")
    except BaseException as err:
        print('Error',err)
        archi.close()
        return 'Error al obtener la muestra\n'+err
    else:
        archi.close()
        return 'Muestreo rapido exitoso. Archivo: '+nombre

def muestreoSimple(ruta:str):
    ciclos = int(1/t_muestra)
    nombre = time.strftime('%Y%m%d')+'_simple.txt'
    leer = threading.Thread(target=leePuerto, args=(ciclos,))
    print("crea puerto que escribe")
    ser_cmd = serial.Serial('/dev/ttyUSB0', baudrate = 230400) #---
    leer.start()
    for i in range(ciclos):
        ser_cmd.write(b'*9900XY\n') #---
        time.sleep(t_muestra)
    leer.join()
    print('cierra puerto que escribe')
    ser_cmd.close() #---
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
        print('Error',err)
        archi.close()
        return 'Error al obtener la muestra\n'+err
    else:
        archi.close()
        return 'Muestreo simple exitoso. Archivo: '+nombre


if __name__ == '__main__':
    pass
    #muestreoRapido(1)
    #muestreoRapido(10)