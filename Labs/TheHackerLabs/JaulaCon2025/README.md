# JaulaCon2025 (The Hacker Labs)

## Sistema

Linux

---

## Objetivo del laboratorio

Practicar técnicas de enumeración web sobre un CMS, explotar vulnerabilidades conocidas en Bludit para obtener acceso inicial, extraer credenciales desde la aplicación web y realizar una escalada de privilegios mediante permisos sudo mal configurados.

---

## Tecnologías trabajadas

- HTTP
- SSH
- Bludit CMS
- Metasploit
- Hash Cracking
- Linux
- Sudo

---

## Metodología

- La enumeración inicial mostró únicamente los servicios SSH y HTTP, por lo que decidí centrar el análisis en la aplicación web.

- Tras acceder al sitio observé que utilizaba Bludit como gestor de contenidos. Como la enumeración manual y el código fuente no revelaban credenciales ni información sensible, el siguiente paso fue identificar la versión del CMS para comprobar si existían vulnerabilidades conocidas.

- Una vez localizado un bypass de autenticación para esa versión de Bludit, conseguí acceder al panel de administración. A partir de ese momento el objetivo pasó a ser obtener acceso al sistema operativo.

- Tras conseguir una sesión sobre el servidor web, inicié una búsqueda de credenciales dentro de la instalación de Bludit, obteniendo el hash de un usuario del sistema. Después de descifrar la contraseña pude acceder mediante SSH.

- Finalmente, una vez dentro del sistema, seguí la metodología habitual de post-explotación ejecutando `sudo -l`, descubriendo que el binario `busctl` podía ejecutarse como root sin contraseña, lo que permitió completar la escalada de privilegios utilizando GTFOBins.

---

## Explotación

### 1. Reconocimiento

Se realizó un escaneo completo con Nmap para identificar los servicios disponibles.

Servicios encontrados:

- SSH (22)
- HTTP (80)

---

### 2. Enumeración Web

Se analizó la aplicación web manualmente.

Como la página no cargaba correctamente, fue necesario añadir el dominio correspondiente al archivo `/etc/hosts`.

Durante la enumeración se identificó un directorio `/admin`, correspondiente al panel de administración de Bludit.

El sitio mostraba además el nombre **JaulaCon2025**, que posteriormente resultó ser un usuario válido.

---

### 3. Identificación de la vulnerabilidad

Se identificó la versión de Bludit instalada y se buscaron vulnerabilidades públicas.

Se localizó la vulnerabilidad **CVE-2019-17240**, que permite realizar un bypass de autenticación mediante fuerza bruta.

Para explotarla se adaptó un script público encontrado en GitHub, obteniendo la contraseña del usuario administrador.

---

### 4. Acceso inicial

Una vez autenticado en Bludit, se utilizó un módulo de Metasploit que aprovecha una vulnerabilidad de subida de archivos para obtener una sesión Meterpreter.

Desde dicha sesión se accedió al archivo:

```
/var/www/html/bl-content/databases/users.php
```

donde se localizaron el hash y el salt del usuario **JaulaCon2025**.

El hash fue descifrado utilizando CrackStation, obteniendo la contraseña en texto plano.

Con estas credenciales fue posible acceder al sistema mediante SSH.

---

### 5. Escalada de privilegios

Tras ejecutar `sudo -l` se comprobó que el usuario podía ejecutar el binario `busctl` con privilegios de root sin necesidad de contraseña.

Consultando GTFOBins se identificó una técnica que permitía ejecutar una shell privilegiada utilizando dicho binario, obteniendo finalmente acceso como root.

---

## Lecciones aprendidas

- Identificar la versión exacta de un CMS puede conducir directamente a vulnerabilidades conocidas.
- Los paneles de administración suelen ser un objetivo prioritario durante la enumeración web.
- Obtener acceso al CMS no siempre implica controlar el sistema operativo; en ocasiones es necesario buscar credenciales almacenadas por la propia aplicación.
- Los hashes almacenados por aplicaciones web pueden reutilizarse para acceder mediante otros servicios como SSH.
- Siempre es recomendable revisar los archivos de configuración y bases de datos de una aplicación comprometida en busca de credenciales.
- `sudo -l` continúa siendo uno de los primeros comandos que deben ejecutarse durante la enumeración local.
- GTFOBins resulta esencial para identificar técnicas de escalada de privilegios mediante binarios permitidos por sudo.

---

## Knowledge Map

### 🌐 Web-Pentesting

- File Upload Vulnerabilities

CVE

- CVE-2019-17240

---

### 📚 Notes

Networking

- HTTP
- SSH

Tools

- Gobuster
- Metasploit
- CrackStation

Linux
- GTFOBins

  Sudo
  - busctl
