# Bocata de Calamares

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una vulnerabilidad de **SQL Injection** para obtener acceso a funcionalidades ocultas de la aplicación web, conseguir credenciales válidas para acceder mediante SSH y escalar privilegios hasta obtener acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- SQL Injection
- Base64
- Gobuster
- Hydra
- SSH
- GTFOBins
- find

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **SSH** y **HTTP**, por lo que la aplicación web se convirtió en el punto de entrada principal.

Durante la navegación por la web aparecieron varias pistas que indicaban el camino a seguir. Una de ellas hacía referencia a las inyecciones SQL, lo que sugería que el formulario de autenticación podía ser vulnerable. En lugar de seguir enumerando directorios sin contexto, decidí comprobar esa posibilidad.

Tras conseguir acceder al panel de administración mediante una **SQL Injection**, continué explorando la aplicación hasta encontrar una referencia a un texto que debía codificarse en Base64. En lugar de interpretarlo como un simple mensaje, entendí que probablemente estaba relacionado con algún recurso oculto de la aplicación.

El acceso a esa nueva funcionalidad permitió leer archivos del sistema, por lo que el siguiente objetivo fue obtener usuarios válidos desde `/etc/passwd` y utilizarlos para realizar ataques de fuerza bruta contra SSH.

Una vez conseguido el acceso inicial, la propia máquina proporcionaba una pista sobre la escalada de privilegios. Tras confirmar los permisos disponibles mediante `sudo -l`, únicamente fue necesario buscar la técnica correspondiente en GTFOBins para obtener acceso como **root**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando la dirección IP de la máquina mediante `arp-scan` y confirmé que se trataba de un sistema Linux gracias al TTL obtenido con `ping`.

Posteriormente realicé un escaneo completo utilizando Nmap.

```bash
nmap -p- --open -sS -sC -sV --min-rate 5000 -n -Pn 192.168.1.25
```

Se descubrieron los siguientes servicios:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

---

### 2. Enumeración web

Al acceder a la página principal no encontré información técnica relevante, aunque sí aparecían varias pistas importantes.

Entre ellas destacaban:

- Un correo electrónico que sugería la existencia del usuario **administrador**.
- Una advertencia sobre posibles vulnerabilidades de **SQL Injection**.

Realicé una enumeración de directorios con Gobuster.

```bash
gobuster dir -u http://192.168.1.25 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

Los resultados no mostraban nada útil, por lo que repetí la búsqueda incluyendo extensiones comunes.

```bash
gobuster dir -u http://192.168.1.25 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -x txt,php,py,sh
```

Esta vez apareció el recurso:

```
/login.php
```

---

### 3. Explotación de la aplicación web

Siguiendo la pista encontrada anteriormente, probé distintas cargas de SQL Injection sobre el formulario de autenticación.

Tras varios intentos conseguí acceder utilizando la siguiente carga:

```sql
admin' OR '1'='1
```

Una vez autenticado apareció una nueva sección denominada:

```
todo-list.php
```

En ella encontré la palabra:

```
lee_archivos
```

Decidí codificar ese texto en Base64.

```bash
echo "lee_archivos" | base64
```

El resultado permitió acceder a un nuevo recurso oculto de la aplicación.

```
http://192.168.1.25/bGVlX2FyY2hpdm9zCg==.php
```

Este recurso disponía de una funcionalidad para leer archivos del sistema.

---

### 4. Enumeración del sistema

La primera comprobación fue acceder al archivo:

```
/etc/passwd
```

Gracias a ello identifiqué tres usuarios:

- root
- tyuiop
- superadministrator

Con esta información lancé ataques de fuerza bruta mediante Hydra contra el servicio SSH.

El usuario **tyuiop** no devolvió resultados.

Sin embargo, para el usuario **superadministrator** obtuve las siguientes credenciales:

```
superadministrator:princesa
```

---

### 5. Acceso inicial

Con las credenciales obtenidas inicié sesión mediante SSH.

```bash
ssh superadministrator@192.168.1.25
```

Una vez dentro localicé la primera flag (`user.txt`) en el directorio personal del usuario.

---

### 6. Enumeración interna

Durante la revisión de los archivos encontré un documento llamado:

```
recordatorio.txt
```

Su contenido indicaba claramente que la escalada de privilegios estaba relacionada con **sudo**.

Comprobé los permisos disponibles.

```bash
sudo -l
```

El resultado mostró que el usuario podía ejecutar el binario:

```
/usr/bin/find
```

como **root** sin necesidad de introducir contraseña.

---

### 7. Escalada de privilegios

Consulté **GTFOBins** para buscar técnicas de explotación del binario `find`.

La técnica recomendada consistía en ejecutar:

```bash
sudo find . -exec /bin/sh \; -quit
```

Tras ejecutar el comando obtuve una shell con privilegios de **root**.

Finalmente accedí al directorio:

```text
/root
```

y recuperé la flag almacenada en:

```
root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio me permitió reforzar la importancia de interpretar correctamente las pistas que proporciona una aplicación web durante una auditoría.
- Detectar oportunidades de **SQL Injection** a partir de la información mostrada por la propia aplicación.
- Aprovechar una autenticación vulnerable para acceder a funcionalidades ocultas.
- Utilizar **Base64** como mecanismo para descubrir nuevos recursos dentro de una aplicación.
- Aprovechar una funcionalidad de lectura de archivos para enumerar usuarios mediante `/etc/passwd`.
- Combinar la información obtenida durante la enumeración con ataques de fuerza bruta mediante Hydra.
- Identificar pistas dentro del propio sistema que facilitan la escalada de privilegios.
- Utilizar **GTFOBins** para explotar el binario `find` cuando está permitido mediante `sudo`.
