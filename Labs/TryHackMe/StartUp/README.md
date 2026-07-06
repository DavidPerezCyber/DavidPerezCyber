# Startup

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux aprovechando un servidor **FTP con Anonymous Login**, obtener una **reverse shell** mediante una subida de archivos, recuperar credenciales analizando una captura de red con **Wireshark** y escalar privilegios hasta obtener acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- FTP
- Anonymous Login
- PHP Reverse Shell
- Wireshark
- PCAP Analysis
- SSH
- Python
- Cron Jobs

---

## 🧠 Metodología

La enumeración inicial reveló tres servicios interesantes: **FTP**, **SSH** y **HTTP**. El hecho de que el servidor FTP permitiera autenticación anónima lo convirtió inmediatamente en el principal punto de entrada, ya que ofrecía la posibilidad de escribir archivos directamente en el servidor.

Aunque inicialmente los archivos presentes en el FTP no aportaban información relevante, la enumeración de la aplicación web mostró un directorio desde el que era posible acceder a los archivos almacenados en dicho servidor. Esto permitió utilizar el FTP como mecanismo para subir una **reverse shell** y ejecutarla desde el navegador.

Una vez comprometido el sistema, la enumeración interna permitió localizar un directorio con una captura de tráfico de red (`.pcapng`). En lugar de continuar buscando vulnerabilidades locales, decidí analizar esa evidencia, ya que podía contener credenciales o información sensible.

El análisis del tráfico reveló la contraseña de un usuario del sistema, permitiendo pivotar hacia una cuenta con mayores privilegios. La escalada final se basaba en la modificación de un script ejecutado automáticamente por **root**, una técnica muy habitual en laboratorios relacionados con tareas programadas.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé comprobando la conectividad con la máquina mediante `ping` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 10.10.241.120
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP (Anonymous Login permitido) |
| 22 | SSH |
| 80 | HTTP |

---

### 2. Enumeración de servicios

El primer servicio analizado fue el servidor FTP.

Accedí utilizando el usuario:

```text
anonymous
```

y descargué los archivos disponibles.

Aunque inicialmente no contenían información útil, confirmé que tenía permisos para subir nuevos archivos al servidor.

Posteriormente revisé la aplicación web y realicé una enumeración de directorios.

Entre los recursos descubiertos apareció:

```
/files
```

Este directorio correspondía al contenido almacenado en el servidor FTP.

---

### 3. Obtención del acceso inicial

Aprovechando que el contenido del FTP era accesible desde la web, preparé una **reverse shell** en PHP basada en el script de PentestMonkey.

Posteriormente la subí al servidor mediante FTP.

```bash
send shell.php
```

Preparé un listener con Netcat.

```bash
nc -lvnp 443
```

Finalmente accedí al archivo desde el navegador.

```
http://10.10.241.120/files/shell.php
```

La reverse shell se ejecutó correctamente y obtuve acceso al sistema.

---

### 4. Acceso inicial

La shell obtenida pertenecía al usuario:

```
www-data
```

Para trabajar con mayor comodidad realicé el tratamiento habitual de la TTY.

```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```

Durante la exploración encontré un archivo llamado:

```
recipe.txt
```

que respondía a una de las preguntas del laboratorio.

---

### 5. Enumeración interna

Comencé revisando los usuarios existentes.

```bash
cat /etc/passwd
```

Entre ellos aparecían:

- root
- lennie
- vagrant
- ftpsecure

Posteriormente encontré un directorio especialmente interesante:

```
/incidents
```

Dentro de él aparecía una captura de red:

```
suspicious.pcapng
```

Descargué el archivo y lo analicé utilizando **Wireshark**.

Durante el análisis seguí uno de los flujos TCP, donde apareció el historial completo de una sesión interactiva.

En dicha conversación se observaba la contraseña utilizada por otro usuario durante un intento de autenticación.

Gracias a esta información pude acceder al usuario:

```
lennie
```

y recuperar la primera flag:

```
user.txt
```

---

### 6. Escalada de privilegios

La escalada de privilegios se basaba en un **script ejecutado automáticamente por root**.

El objetivo consistía en modificar dicho script para ejecutar una **reverse shell** cuando la tarea programada volviera a ejecutarse.

Aunque durante la resolución original conseguí identificar correctamente el vector de escalada, no logré completar esta última fase por mis propios medios.

Posteriormente consulté la solución oficial del laboratorio para comprender el funcionamiento completo y verificar la obtención de la flag de **root**.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar técnicas muy diferentes a las utilizadas habitualmente en otros CTF, especialmente el análisis de tráfico de red como parte del proceso de post-explotación.
- Aprovechar servidores FTP configurados con **Anonymous Login**.
- Relacionar recursos compartidos entre FTP y servidores web.
- Subir y ejecutar una **reverse shell** mediante un servidor FTP.
- Estabilizar una shell interactiva utilizando Python.
- Analizar capturas de tráfico con **Wireshark**.
- Seguir flujos TCP para recuperar credenciales utilizadas durante sesiones anteriores.
- Comprender cómo los **cron jobs** pueden convertirse en vectores de escalada de privilegios.

### Reflexión

Este laboratorio destacó especialmente por introducir el análisis forense de red dentro de una cadena de pentesting. Hasta ese momento la mayoría de laboratorios se resolvían mediante enumeración directa del sistema, mientras que en esta ocasión fue necesario interpretar una captura de tráfico para recuperar credenciales válidas. La escalada de privilegios también permitió comprender cómo un **cron job** mal configurado puede convertirse en un vector de ejecución de código con privilegios elevados. Aunque no conseguí completar esa última fase de forma autónoma, el laboratorio resultó muy útil para identificar un punto de mejora claro: profundizar en el funcionamiento de las tareas programadas y los mecanismos habituales de escalada relacionados con ellas.
