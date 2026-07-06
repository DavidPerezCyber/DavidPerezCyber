# Vulnversity

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una vulnerabilidad de **File Upload** para obtener una **Remote Code Execution (RCE)** y escalar privilegios aprovechando un binario **SUID** mal configurado hasta conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- File Upload
- Burp Suite
- Gobuster
- PHP Reverse Shell
- Netcat
- SUID
- GTFOBins
- systemctl

---

## 🧠 Metodología

La enumeración inicial mostró varios servicios expuestos, pero el puerto **3333** destacaba por alojar una aplicación web poco habitual. En lugar de centrarme en el servicio Squid, decidí investigar primero la aplicación, ya que las aplicaciones web suelen ofrecer una superficie de ataque mayor.

Tras realizar una enumeración de directorios apareció una funcionalidad de subida de archivos. Este tipo de funcionalidades siempre merece un análisis detallado, ya que una validación incorrecta puede permitir la ejecución de código en el servidor.

Aunque el servidor bloqueaba las extensiones PHP más comunes, asumí que el filtrado probablemente se realizaba únicamente por extensión. En lugar de abandonar la vía de ataque, utilicé Burp Suite para realizar un fuzzing de extensiones alternativas compatibles con PHP hasta encontrar una que el servidor aceptaba.

Una vez conseguida la ejecución remota de código, la fase de post-explotación consistió en buscar mecanismos clásicos de escalada de privilegios. La enumeración de binarios SUID reveló un binario poco habitual (`systemctl`) que, combinado con las técnicas documentadas en GTFOBins, permitió obtener acceso como **root**.

Este laboratorio refuerza la importancia de combinar una buena enumeración web con una correcta enumeración local tras obtener acceso inicial.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo de puertos mediante Nmap.

```bash
nmap -p- 10.129.187.136
```

Los servicios más relevantes identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 3128 | Squid Proxy |
| 3333 | HTTP |

Posteriormente profundicé sobre el servicio Squid.

```bash
nmap -sC -sV -p 3128 10.129.187.136
```

La enumeración confirmó:

- Squid Proxy 4.10
- Sistema operativo Ubuntu

Sin embargo, el servicio que presentaba una mayor superficie de ataque seguía siendo la aplicación web del puerto **3333**.

---

### 2. Enumeración web

Accedí a la aplicación disponible en:

```text
http://10.129.187.136:3333
```

No aparecían funcionalidades especialmente interesantes a simple vista, por lo que decidí realizar una enumeración de directorios.

```bash
gobuster dir -u http://10.129.187.136:3333 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```

La enumeración descubrió un recurso importante:

```
/internal
```

Dentro de este directorio encontré un formulario para subir archivos.

La existencia de una funcionalidad de subida de archivos hacía muy probable la posibilidad de obtener ejecución remota de código.

---

### 3. Explotación del File Upload

El primer intento consistió en subir una reverse shell en PHP.

Sin embargo, el servidor bloqueaba las extensiones habituales como:

```
.php
```

Para identificar una extensión aceptada utilicé **Burp Suite Intruder**, realizando un pequeño fuzzing de extensiones compatibles con PHP.

Tras varias pruebas encontré una extensión válida:

```
.phtml
```

Renombré la reverse shell utilizando dicha extensión y la subí correctamente al servidor.

Preparé un listener con Netcat.

```bash
nc -lvnp 1234
```

Posteriormente ejecuté el archivo accediendo a:

```text
http://10.129.187.136:3333/internal/uploads/php-reverse-shell.phtml
```

La conexión se estableció correctamente y obtuve una shell sobre la máquina víctima.

---

### 4. Acceso inicial

La shell obtenida pertenecía al usuario:

```
bill
```

Durante la exploración recuperé la primera flag del laboratorio.

```
user.txt
```

---

### 5. Enumeración interna

Una vez comprometido el sistema inicié la búsqueda de posibles mecanismos de escalada.

Comencé enumerando los binarios SUID.

```bash
find / -perm -u=s -type f 2>/dev/null
```

Entre ellos apareció un binario especialmente interesante:

```
/bin/systemctl
```

---

### 6. Escalada de privilegios

Consultando **GTFOBins** comprobé que `systemctl` puede utilizarse para ejecutar servicios personalizados con privilegios elevados cuando dispone del bit SUID.

Siguiendo la técnica documentada fue posible ejecutar un servicio malicioso y obtener una shell como **root**.

Finalmente recuperé la última flag almacenada en:

```
/root/root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió reforzar varios conceptos fundamentales relacionados con la explotación de aplicaciones web y la escalada de privilegios en Linux.
- Identificar funcionalidades vulnerables de **File Upload**.
- Utilizar **Gobuster** para descubrir recursos ocultos.
- Emplear **Burp Suite Intruder** para realizar fuzzing de extensiones de archivos.
- Comprender que muchos filtros únicamente validan la extensión del archivo y no su contenido.
- Ejecutar una **reverse shell** mediante extensiones alternativas como `.phtml`.
- Enumerar binarios **SUID** tras obtener acceso inicial.
- Aprovechar el binario `systemctl` para obtener privilegios elevados mediante técnicas documentadas en GTFOBins.

### Reflexión

La principal enseñanza de este laboratorio fue comprobar que los filtros de subida de archivos rara vez son suficientes cuando únicamente validan la extensión del fichero. Mediante un sencillo fuzzing fue posible encontrar una extensión alternativa aceptada por el servidor y conseguir ejecución remota de código. Además, reforzó la importancia de revisar siempre los binarios SUID tras obtener acceso inicial, ya que incluso binarios poco habituales como **systemctl** pueden convertirse en un vector de escalada si están configurados de forma insegura. También puso de manifiesto que **GTFOBins** debe utilizarse no solo como una colección de comandos, sino como una referencia para comprender por qué un binario puede utilizarse para elevar privilegios.
