# Fruits (The Hacker Labs)

## Sistema
Linux

---

## Objetivo del laboratorio
Practicar técnicas de enumeración web, descubrir vulnerabilidades de tipo Local File Inclusion (LFI), obtener acceso inicial mediante fuerza bruta sobre SSH y realizar una escalada de privilegios aprovechando permisos sudo mal configurados.

---

## Tecnologías trabajadas
- HTTP
- SSH
- Local File Inclusion (LFI)
- Linux
- Sudo

---

## Metodología
- La enumeración inicial mostró únicamente los servicios SSH y HTTP, por lo que decidí centrar la atención en la aplicación web.
- Tras analizar la página principal observé que la búsqueda utilizaba un parámetro en la URL. Como no encontré información relevante ni en el código fuente ni mediante un primer escaneo de directorios con Gobuster, asumí que el punto de entrada podía estar relacionado con dicho parámetro.
- Mediante fuzzing conseguí identificar el nombre del parámetro y comprobé que era vulnerable a Local File Inclusion, lo que permitió acceder al archivo `/etc/passwd` para obtener usuarios válidos del sistema.
- Con un usuario identificado, el siguiente paso fue intentar obtener credenciales mediante un ataque de fuerza bruta sobre el servicio SSH.
- Una vez conseguí acceso al sistema, inicié la enumeración local ejecutando `sudo -l`, ya que siempre es uno de los primeros pasos para detectar posibles vías de escalada de privilegios. El resultado mostró que el usuario podía ejecutar `find` con permisos elevados sin necesidad de contraseña, lo que permitió obtener una shell como root utilizando GTFOBins.

---
## Explotación
### 1. Reconocimiento
Se realizó un escaneo completo con Nmap para identificar los servicios expuestos.
Se detectaron:
- Puerto 22 (SSH)
- Puerto 80 (HTTP)

---

### 2. Enumeración Web

Se analizó la aplicación web manualmente.

Durante la navegación se observó un parámetro en la URL que llamó la atención al devolver errores cuando se introducían distintos valores.

Posteriormente se realizaron dos escaneos con Gobuster:

- Descubrimiento de directorios.
- Descubrimiento de archivos con extensiones PHP, TXT, PY y SH.

Esto permitió localizar `fruits.php`.

---

### 3. Descubrimiento del parámetro vulnerable

Utilizando Wfuzz se identificó el parámetro `file`.

Al acceder a:

```
fruits.php?file=/etc/passwd
```

fue posible leer el archivo `/etc/passwd`, confirmando la existencia de una vulnerabilidad Local File Inclusion.

---

### 4. Acceso inicial

Del archivo `/etc/passwd` se obtuvo el usuario:

- bananaman

Con un usuario válido se realizó un ataque de fuerza bruta mediante Hydra sobre el servicio SSH, obteniendo las credenciales de acceso.

Finalmente se estableció una sesión SSH con dicho usuario y se obtuvo la primera flag.

---

### 5. Escalada de privilegios

Tras ejecutar `sudo -l` se comprobó que el usuario podía ejecutar el binario `find` como root sin introducir contraseña.

Consultando GTFOBins se identificó una técnica para obtener una shell privilegiada utilizando dicho binario, consiguiendo acceso como root y recuperando la flag final.

---

## Lecciones aprendidas

- No toda la enumeración web consiste únicamente en descubrir directorios; analizar los parámetros de una aplicación puede revelar el verdadero vector de entrada.
- Una vulnerabilidad Local File Inclusion puede utilizarse para obtener usuarios válidos mediante la lectura del archivo `/etc/passwd`.
- Cuando se obtiene acceso inicial a un sistema Linux, ejecutar `sudo -l` debe formar parte de la metodología básica de enumeración.
- GTFOBins es una referencia imprescindible para identificar posibles técnicas de escalada de privilegios utilizando binarios permitidos por sudo.
- Hydra resulta especialmente útil cuando ya se dispone de un usuario válido y únicamente es necesario descubrir la contraseña.
