# Hammer

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una aplicación web explotando varias debilidades en el proceso de autenticación, incluyendo la exposición de información sensible, el bypass del restablecimiento de contraseña, el secuestro de sesión mediante **PHPSESSID** y la manipulación de un **JSON Web Token (JWT)** para obtener privilegios elevados.

---

## 🛠️ Tecnologías trabajadas

- FFUF
- Burp Suite
- JWT
- PHP Sessions
- OTP Brute Force
- Cookies
- HTTP Authentication
- Web Enumeration

---

## 🧠 Metodología

La enumeración inicial mostró únicamente dos servicios expuestos: **SSH** y una aplicación web accesible en un puerto no estándar. Al no existir otros vectores claros de entrada, toda la investigación se centró en la aplicación web.

El análisis del código fuente reveló un patrón utilizado para nombrar los directorios internos de la aplicación, lo que permitió optimizar el fuzzing y descubrir un directorio de **logs** expuesto. Estos registros contenían información suficiente para identificar un usuario válido.

A partir de ese usuario fue posible abusar del mecanismo de recuperación de contraseña mediante un ataque de fuerza bruta sobre un código OTP de cuatro dígitos. El proceso también permitió obtener una nueva sesión (`PHPSESSID`), utilizada para secuestrar la autenticación y modificar la contraseña del usuario.

Finalmente, el análisis del **JWT** empleado por la aplicación permitió alterar sus claims y generar un token con mayores privilegios, consiguiendo acceso a las funcionalidades restringidas y completando el laboratorio.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **ReconX**.

Los servicios identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 1337 | HTTP |

Aunque el servicio SSH estaba disponible, el único vector de ataque viable era la aplicación web.

---

### 2. Enumeración web

Accedí a la aplicación.

```text
http://10.130.148.47:1337
```

La página mostraba un panel de autenticación.

Inspeccionando el código fuente encontré un comentario del desarrollador.

```text
Directory naming convention must be hmr_DIRECTORY_NAME
```

Este detalle revelaba el patrón utilizado para nombrar los directorios internos de la aplicación.

---

### 3. Descubrimiento de directorios

Aprovechando la información obtenida lancé un fuzzing utilizando el prefijo descubierto.

```bash
ffuf -w /usr/share/wordlists/SecLists-master/Discovery/Web-Content/raft-medium-directories.txt -u http://10.130.148.47:1337/hmr_FUZZ -mc 200,301,302,403
```

Entre los resultados aparecieron:

```text
css
images
js
logs
```

El directorio más interesante fue:

```text
hmr_logs
```

---

### 4. Enumeración de usuarios

Accedí al directorio de logs y revisé los archivos disponibles.

Entre los registros encontré un inicio de sesión correspondiente al usuario:

```text
tester@hammer.thm
```

Este correo proporcionó un usuario válido para continuar con la explotación.

---

### 5. Bypass del proceso de recuperación

Volví al panel de autenticación y utilicé la opción:

```text
Forgot Password
```

Introduje el correo descubierto.

```text
tester@hammer.thm
```

La aplicación solicitó un código OTP de cuatro dígitos.

Mediante un script realicé un ataque de fuerza bruta sobre dicho código.

El resultado proporcionó dos elementos fundamentales:

- Código OTP válido.
- Nuevo valor de la cookie `PHPSESSID`.

---

### 6. Secuestro de sesión

Accedí nuevamente a la aplicación y modifiqué manualmente la cookie de sesión desde las herramientas de desarrollo del navegador.

```text
PHPSESSID
```

La sustituí por el valor obtenido durante la fuerza bruta.

La aplicación aceptó la nueva sesión y permitió modificar la contraseña del usuario.

Con la contraseña ya cambiada inicié sesión normalmente y obtuve acceso al panel de usuario.

---

### 7. Post-explotación

Una vez autenticado recuperé la primera flag.

Dentro del panel encontré una consola que permitía ejecutar comandos sobre el servidor.

Sin embargo, la sesión expiraba rápidamente.

Para evitar autenticaciones constantes utilicé **Burp Suite** enviando las peticiones al módulo **Repeater**, lo que facilitó repetir las solicitudes sin necesidad de volver a iniciar sesión.

Durante la enumeración comprobé que únicamente estaba permitido ejecutar:

```text
ls
```

El resto de comandos eran bloqueados por la aplicación.

---

### 8. Manipulación del JWT

Analicé el token JWT utilizado por la aplicación mediante **jwt.io**.

Observé que el token contenía la información necesaria para generar una nueva firma válida, permitiendo modificar sus claims.

Tras alterar el contenido del JWT y firmarlo correctamente, sustituí el token original por el modificado.

La aplicación aceptó el nuevo JWT y concedió acceso a funcionalidades reservadas para usuarios con mayores privilegios.

Con ello obtuve la última flag del laboratorio.

---

## 📚 Lecciones aprendidas

- Este laboratorio mostró cómo varias debilidades de autenticación aparentemente independientes pueden combinarse hasta comprometer completamente una aplicación web.
- Optimizar el fuzzing utilizando patrones descubiertos en el código fuente.
- Localizar usuarios válidos mediante archivos de logs expuestos.
- Comprender el funcionamiento de los procesos de recuperación de contraseña mediante OTP.
- Realizar ataques de fuerza bruta sobre códigos OTP de pequeño tamaño.
- Secuestrar sesiones reutilizando cookies `PHPSESSID`.
- Utilizar **Burp Suite Repeater** para mantener sesiones activas durante la explotación.
- Analizar y modificar **JSON Web Tokens (JWT)**.
- Comprender cómo una validación incorrecta de JWT puede permitir la escalada de privilegios.
