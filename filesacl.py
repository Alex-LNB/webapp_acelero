# Formato: *9900<comando>
# Comandos:
#   XY      Lectura de posicion y temperatura
#   SO-xxx  Configura formato de salida XY
#           SIM(simple default)
#           ASH(Ashtech NMEA), XDR(NMEA XDR), TCM(Trimble format)
#   XYCx    Envia lecturas continuas
#           x-> 0(8-10/s), 1(4/s), 2(1/s default)
#           3(1/10s), 4(1/60s), 5(1/h), 6(1/12h), 7(1/24h)
#           0A(promedio de 8-10/s), 1A(promedio de 4/s), A|2A(promedio de 1/s)
#   XYC-OFF     Apaga el comando XYCx

# Comunicacion con puerto serial
# https://unix.stackexchange.com/questions/117037/how-to-send-data-to-a-serial-port-and-see-any-answer

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
        buff = cad.strip(' $').split(',')
        data = LecturaAcelero(buff[0],buff[1],'Grados',buff[2],buff[3])
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

if __name__ == '__main__':
    lsim = LecturaAcelero.lee_sim(cad=sim_example)
    print(lsim.valX,lsim.valY,lsim.units,lsim.temp,lsim.sn)
    lxdr = LecturaAcelero.lee_xdr(cad=xdr_example)
    print(lxdr.valX,lxdr.valY,lxdr.units,lxdr.temp,lxdr.sn)
    lash = LecturaAcelero.lee_ash(cad=ash_example)
    print(lash.valX,lash.valY,lash.units,lash.temp,lash.sn)
    ltcm = LecturaAcelero.lee_tcm(cad=tcm_example)
    print(ltcm.valX,ltcm.valY,ltcm.units,ltcm.temp,ltcm.sn)
