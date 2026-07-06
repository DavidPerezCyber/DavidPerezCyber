# Casa Paco

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una vulnerabilidad de **Command Injection** presente en una aplicación web, obtener acceso inicial mediante SSH y aprovechar una tarea automatizada ejecutada como **root** para escalar privilegios.

---

## 🛠️ Tecnologías trabajadas

- Command Injection
- Burp Suite
- Hydra
- SSH
- Cron Jobs
- Reverse Shell

---

## 🧠 Metodología

La enumeración inicial mostró únicamente los servicios de **SSH** y **HTTP**, por lo que la aplicación web se convirtió en el principal punto de entrada.

Tras explorar la página web no encontré información especialmente útil, pero sí un formulario que permitía realizar pedidos. En lugar de asumir que únicamente aceptaba texto, decidí comprobar si los datos introducidos eran procesados de forma insegura. Al ejecutar un comando sencillo confirmé que existía una **Command Injection**, lo que abrió la puerta a una enumeración mucho más amplia del sistema.

En lugar de intentar obtener una shell directamente, utilicé la vulnerabilidad para recopilar información sobre el servidor. A través de Burp Suite fui modificando las peticiones para descubrir nuevos recursos y finalmente conseguí leer archivos del sistema, obteniendo así un usuario válido para realizar un ataque de fuerza bruta sobre SSH.

Una vez dentro de la máquina, la enumeración clásica no permitió encontrar una vía directa de escalada. Sin embargo, analizando los archivos del usuario observé que existía un script relacionado con una tarea que se ejecutaba de forma periódica. En lugar de seguir buscando binarios vulnerables, decidí investigar ese mecanismo, descubriendo que podía modificar un script ejecutado automáticamente como **root**.

La estrategia final consistió en reemplazar el contenido del script por una **reverse shell**, esperar a que el cron la ejecutara y obtener una sesión privilegiada.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando la dirección IP de la máquina mediante `arp-scan` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido con `ping`.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 192.168.1.26
```

Se descubrieron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

---

### 2. Enumeración web

Para acceder correctamente al sitio web fue necesario añadir el dominio al archivo `/etc/hosts`.

La página principal no mostraba información relevante, aunque encontré dos recursos interesantes:

- `menu.php`
- `llevar.php`

Dentro de `llevar.php` existía un formulario para realizar pedidos.

Durante las pruebas comprobé que los datos enviados no eran filtrados correctamente. Introduciendo un comando sencillo como:

```bash
id
```

la aplicación devolvía el resultado del comando ejecutado en el servidor, confirmando una vulnerabilidad de **Command Injection**.

---

### 3. Enumeración mediante Command Injection

Para analizar con mayor precisión la petición utilicé **Burp Suite**.

Interceptando y modificando las solicitudes sustituí el comando inicial por:

```bash
dir
```

Esto permitió descubrir nuevos archivos del servidor, entre ellos:

```
llevar1.php
```

Sobre este nuevo recurso aproveché nuevamente la vulnerabilidad para leer archivos del sistema utilizando:

```bash
cat /etc/passwd
```

Gracias a ello identifiqué un usuario interesante:

```
pacogerente
```

---

### 4. Acceso inicial

Con el usuario obtenido lancé un ataque de fuerza bruta mediante Hydra contra el servicio SSH.

```bash
hydra -l pacogerente -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.26
```

El ataque devolvió las siguientes credenciales:

```
pacogerente:dipset1
```

Con ellas inicié sesión mediante SSH.

```bash
ssh pacogerente@192.168.1.26
```

Una vez dentro localicé la primera flag (`user.txt`) en el directorio personal del usuario.

---

### 5. Enumeración interna

El primer paso fue comprobar si existían permisos especiales mediante:

```bash
sudo -l
```

No fue posible utilizar sudo.

A continuación busqué binarios SUID.

```bash
find / -perm -4000 2>/dev/null
```

Ninguno de ellos permitía una escalada de privilegios.

Continuando con la enumeración encontré un archivo llamado:

```
log.txt
```

Su contenido se actualizaba constantemente, indicando que existía algún proceso automatizado ejecutándose de forma periódica.

Investigando los scripts presentes en el sistema encontré un archivo denominado:

```
fabada.sh
```

Este script era el responsable de generar el contenido del log y estaba siendo ejecutado automáticamente por una tarea programada.

---

### 6. Escalada de privilegios

Al comprobar que tenía permisos de escritura sobre `fabada.sh`, sustituí su contenido por una **reverse shell**.

Mientras tanto preparé una máquina atacante escuchando conexiones entrantes.

```bash
nc -lvnp 443
```

Cuando el cron ejecutó nuevamente el script, la reverse shell fue lanzada automáticamente y obtuve una conexión como **root**.

Finalmente accedí al directorio:

```text
/root
```

y recuperé la última flag almacenada en:

```
root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio reforzó varios conceptos relacionados con la explotación de aplicaciones web y la importancia de la enumeración interna tras obtener acceso inicial.
- Detectar y explotar vulnerabilidades de **Command Injection**.
- Utilizar **Burp Suite** para modificar peticiones HTTP y ampliar la enumeración.
- Aprovechar la lectura de archivos mediante comandos para obtener usuarios válidos del sistema.
- Combinar la información obtenida con ataques de fuerza bruta sobre SSH.
- Comprender el funcionamiento básico de las tareas programadas (**Cron Jobs**) en sistemas Linux.
- Identificar scripts ejecutados automáticamente como posibles vectores de escalada de privilegios.
- Utilizar una **reverse shell** para obtener acceso privilegiado cuando un script es ejecutado por **root**.
