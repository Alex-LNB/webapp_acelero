# Webapp

## Inclinómetro Digital

Aplicativo web para la toma de lecturas del inclinómetro digital, almacenar las muestras en archivos de texto, para poder ser visualizados y/o descargados, además, tendrá su sección para configurar la red y la hora/fecha del dispositivo.

## Dependencias

- Sistema Operativo
  - Raspberry Pi (Raspbian, basado en Debian), sistema operativo para la Raspberry Pi 3
- Interprete Python
  - Python >= 3.7
    - Flask
	- Bootstrap4.0
	- SQLAlchemy
	- Gunicorn
    - PySerial 3.5
- Base de datos
  - MySQL
- Utilidades de Linux
  - Nginx
  - Netplan
  - Ufw
- Extra
  - Proyecto [Linux Wifi Hotspot](https://github.com/lakinduakash/linux-wifi-hotspot) (Para la creacion del AP / Hotspot)