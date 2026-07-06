# Facultad (The Hacker Labs)

## Sistema

Linux

---

## Objetivo del laboratorio

Practicar técnicas de enumeración sobre un entorno WordPress, obtener acceso inicial mediante una vulnerabilidad de subida de archivos, realizar movimientos entre usuarios locales y completar una escalada de privilegios aprovechando permisos sudo y un script mal configurado.

---

## Tecnologías trabajadas

- HTTP
- SSH
- WordPress
- WPScan
- File Upload
- PHP
- Linux
- Sudo

---

## Metodología

- La enumeración inicial mostró únicamente los servicios SSH y HTTP, por lo que decidí centrar el análisis en la aplicación web para obtener credenciales o algún punto de entrada.

- Tras revisar la página principal sin encontrar información relevante, continué con la enumeración de directorios mediante Gobuster. Esto permitió descubrir una instalación de WordPress, por lo que el siguiente paso fue identificar usuarios y comprobar si existían credenciales débiles utilizando herramientas específicas para este CMS.

- Una vez obtenido acceso al panel de administración, el objetivo pasó a ser conseguir ejecución de código en el servidor mediante la subida de un archivo PHP malicioso.

- Con acceso al sistema como `www-data`, inicié la enumeración local para identificar otros usuarios y posibles vías de escalada de privilegios. El análisis de los permisos sudo permitió comprometer un segundo usuario, desde el que fue posible obtener nuevas credenciales para acceder mediante SSH.

- Finalmente, tras acceder por SSH, una nueva revisión de los permisos sudo reveló un script ejecutable como root. Analizando su funcionamiento fue posible modificarlo para obtener una shell con privilegios elevados.

---

## Explotación

### 1. Reconocimiento

Se realizó un escaneo completo con Nmap para identificar los servicios disponibles.

Servicios encontrados:

- SSH (22)
- HTTP (80)

---

### 2. Enumeración Web

Se analizó la página principal sin encontrar información relevante.

Mediante Gobuster se descubrieron nuevos directorios, entre ellos una instalación de WordPress accesible desde `/education`.

También se analizó una imagen mediante técnicas de esteganografía para comprobar si contenía información oculta.

---

### 3. Enumeración de WordPress

Se utilizó WPScan para identificar usuarios registrados y comprobar la existencia de credenciales débiles.

Tras enumerar el usuario `facultad`, se realizó un ataque de diccionario que permitió obtener acceso al panel de administración.

---

### 4. Acceso inicial

Con acceso al panel de WordPress se aprovechó el plugin **WP File Manager** para subir un archivo PHP con una reverse shell.

Tras ejecutar el archivo desde el navegador se obtuvo una conexión como el usuario `www-data`.

Posteriormente se realizó un tratamiento de la TTY para trabajar de forma más cómoda durante la enumeración.

---

### 5. Enumeración interna

Se identificaron los usuarios locales del sistema y se revisaron los permisos sudo.

El usuario `www-data` podía ejecutar el binario `php` como el usuario `gabri`, lo que permitió cambiar de usuario mediante una técnica documentada en GTFOBins.

Durante la enumeración del usuario `gabri` se localizaron unas credenciales almacenadas en el directorio de correo, que tras ser descifradas permitieron acceder mediante SSH como `vivian`.

---

### 6. Escalada de privilegios

Una vez conectado mediante SSH se ejecutó `sudo -l`, comprobando que el usuario podía ejecutar un script ubicado en `/opt/vivian/script.sh` con privilegios de root.

Tras analizar su funcionamiento se modificó el contenido del script para ejecutar una shell Bash. Al volver a ejecutarlo mediante sudo se obtuvo acceso como root y se completó el laboratorio.

---

## Lecciones aprendidas

- Identificar un CMS durante la enumeración permite utilizar herramientas especializadas como WPScan para agilizar el proceso de reconocimiento.
- La enumeración de usuarios y credenciales débiles en WordPress puede proporcionar acceso al panel de administración sin necesidad de explotar vulnerabilidades complejas.
- Un plugin de gestión de archivos puede convertirse en un punto de entrada si permite subir archivos ejecutables al servidor.
- Siempre es recomendable realizar un tratamiento de la TTY tras obtener una reverse shell para facilitar la post-explotación.
- La enumeración de permisos sudo puede permitir movimientos laterales entre usuarios antes de conseguir privilegios de root.
- Los directorios de correo (`/var/mail`) pueden contener credenciales o información sensible útil durante una auditoría.
- Antes de intentar técnicas complejas de escalada, es importante analizar cuidadosamente los scripts que pueden ejecutarse mediante sudo, ya que una mala configuración puede proporcionar acceso directo como root.
