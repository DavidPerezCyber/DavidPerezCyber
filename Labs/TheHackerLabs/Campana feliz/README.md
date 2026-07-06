# Campana Feliz

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux obteniendo credenciales a través de un panel web vulnerable, acceder al panel de administración **Webmin** y aprovechar sus funcionalidades para obtener acceso como **root**, recuperando las flags del sistema.

---

## 🛠️ Tecnologías trabajadas

- Webmin
- Hydra
- HTTP POST Brute Force
- Base64
- Gobuster
- Command Shell

---

## 🧠 Metodología

La enumeración inicial mostró tres servicios expuestos: **SSH**, un servidor **HTTP** en un puerto no estándar y **Webmin**. Aunque Webmin podía parecer el objetivo más interesante, decidí no intentar explotarlo directamente sin disponer de credenciales válidas.

Durante la exploración de la aplicación web observé que la página principal estaba prácticamente vacía, pero el código fuente contenía información codificada en Base64. En lugar de ignorarla, decidí decodificar su contenido para comprobar si escondía pistas útiles. Aunque no proporcionó credenciales completas, sí orientó la investigación hacia posibles usuarios del sistema.

Después de una enumeración más profunda con Gobuster apareció un panel de autenticación oculto. Al comprobar que no existía ninguna vulnerabilidad evidente, opté por realizar un ataque de fuerza bruta específicamente sobre el formulario web utilizando Hydra, en lugar de atacar directamente el servicio SSH.

Una vez obtenido acceso al panel, aproveché la posibilidad de ejecutar comandos para continuar enumerando el sistema. Esta enumeración permitió descubrir un archivo con credenciales pertenecientes al panel de Webmin.

Con dichas credenciales fue posible acceder a Webmin, donde la propia herramienta proporcionaba una consola de comandos ejecutándose con privilegios elevados. Esto permitió obtener acceso completo al sistema sin necesidad de realizar una escalada de privilegios tradicional.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando la dirección IP de la máquina mediante `arp-scan` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido con `ping`.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 192.168.1.28
```

Se descubrieron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 8088 | HTTP |
| 10000 | Webmin |

---

### 2. Enumeración web

Accedí al servicio web disponible en el puerto **8088**.

La página principal estaba prácticamente vacía, aunque revisando el código fuente encontré dos cadenas codificadas en **Base64**.

Tras decodificarlas aparecieron varias pistas relacionadas con posibles usuarios y credenciales.

Posteriormente realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://192.168.1.28:8088 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -x php,py,txt,sh
```

La enumeración permitió descubrir el recurso:

```
/shell.php
```

Al acceder apareció un formulario de autenticación.

Las credenciales obtenidas anteriormente no funcionaban, por lo que fue necesario buscar otra vía de acceso.

---

### 3. Ataque de fuerza bruta sobre el formulario web

En lugar de atacar el servicio SSH, decidí realizar un ataque de fuerza bruta directamente contra el formulario de autenticación utilizando el módulo **http-post-form** de Hydra.

```bash
hydra -l campana -P /usr/share/wordlists/rockyou.txt 192.168.1.28 -s 8088 http-post-form "/shell.php:username=^USER^&password=^PASS^:Username or password invalid"
```

El ataque devolvió las siguientes credenciales:

```
campana:lovely
```

Con ellas inicié sesión correctamente en el panel.

---

### 4. Enumeración desde el panel web

Una vez autenticado apareció una consola desde la que era posible ejecutar comandos directamente sobre el sistema.

Aproveché esta funcionalidad para continuar la enumeración.

```bash
ls -la /opt
```

Durante la exploración encontré un archivo relacionado con el servicio Webmin.

Al revisar su contenido aparecieron las credenciales necesarias para acceder al panel disponible en el puerto **10000**.

---

### 5. Acceso como administrador

Accedí al panel de **Webmin** utilizando las credenciales descubiertas durante la enumeración.

Una vez autenticado navegué hasta:

```
Tools → Command Shell
```

Esta funcionalidad permitía ejecutar comandos directamente como **root**.

Desde esta consola localicé las dos flags del laboratorio:

- `user.txt`
- `root.txt`

Sin necesidad de realizar una escalada de privilegios adicional.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió profundizar en la enumeración de aplicaciones web y comprender la importancia de analizar toda la información disponible antes de intentar explotar un servicio.
- Analizar información oculta en el código fuente mediante **Base64**.
- Enumerar aplicaciones web alojadas en puertos no estándar.
- Utilizar **Hydra** para realizar ataques de fuerza bruta sobre formularios HTTP mediante el módulo `http-post-form`.
- Diferenciar entre un ataque de fuerza bruta sobre SSH y un ataque contra un formulario web.
- Aprovechar una consola web para realizar enumeración del sistema.
- Comprender el funcionamiento básico de **Webmin** y sus herramientas administrativas.
- Utilizar la funcionalidad **Command Shell** de Webmin para ejecutar comandos con privilegios elevados.
