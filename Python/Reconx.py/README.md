# ReconX

## Descripción

ReconX es una herramienta de enumeración automatizada para pentesting, escrita en Python 3 puro (sin dependencias externas). Automatiza el flujo inicial de reconocimiento de red que normalmente se ejecuta a mano en labs de TryHackMe y Hack The Box: comprueba si el objetivo está vivo, escanea todos los puertos, extrae automáticamente los que están abiertos y lanza sobre ellos un escaneo de detección de servicios y versiones, mostrando la salida de Nmap en tiempo real.

## Objetivo

El objetivo de ReconX es eliminar los pasos manuales y repetitivos del reconocimiento inicial en máquinas de laboratorio, sirviendo además como proyecto personal de aprendizaje y práctica de cara a la preparación de la certificación **OSCP**. Está pensado para crecer progresivamente: la FASE 1 (conectividad + escaneo de puertos + detección de servicios) es la base sobre la que se irán añadiendo nuevas fases de enumeración (web, SMB, fuerza bruta, generación de informes, etc.).

## Características

- Desarrollado en **Python 3**, usando únicamente librerías estándar (`subprocess`, `argparse`, `re`, `sys`) — sin `pip install`, sin `venv`, sin dependencias externas.
- Comprobación de conectividad con el objetivo mediante `ping -c 3`.
- Escaneo completo de puertos (`nmap -p-`) de forma silenciosa, capturando la salida internamente.
- Extracción automática de los puertos abiertos y conversión al formato `22,80,111,445` sin intervención manual.
- Escaneo de servicios y versiones (`nmap -sV -sC`) sobre los puertos detectados, mostrando la salida completa de Nmap **en tiempo real**, igual que una ejecución manual.
- Salida por terminal clara y con colores (verde para éxito, rojo para error, cian para información).
- Gestión de errores: detecta si `ping` o `nmap` no están instalados y detiene la ejecución con un mensaje claro.
- Código dividido en funciones (`check_connection`, `run_initial_scan`, `extract_ports`, `run_service_scan`, `main`), documentado con comentarios, listo para ampliarse con nuevas fases (WhatWeb, Gobuster, Nikto, Enum4linux, SMBMap, RPCClient, Hydra, FFUF, Nuclei, generación de informes...).

## Uso

```bash
reconx <IP>
```

Ejemplo:

```bash
reconx 10.10.10.10
```

Flujo de ejecución:

1. Comprueba la conectividad con el objetivo (`ping -c 3 <IP>`). Si no responde, muestra `[-] IP desconectada` y termina inmediatamente.
2. Si el host está activo, ejecuta `nmap -p- <IP>` de forma silenciosa.
3. Extrae automáticamente los puertos abiertos detectados.
4. Ejecuta `nmap -sV -sC -p<puertos> <IP>` mostrando la salida completa en tiempo real.

### Ejemplo de salida

```
=================================
            ReconX
=================================
[*] Comprobando conectividad...
[+] IP conectada
[*] Ejecutando reconocimiento de puertos (nmap -p-)...
[+] Puertos encontrados:
22,80,111
[*] Ejecutando escaneo de servicios (nmap -sV -sC)...

(aquí aparece la salida completa de nmap en tiempo real)
```

## Instalación

### Requisitos previos

- Linux (probado en Kali)
- Python 3
- `nmap`

### Instalación como comando global (recomendado)

```bash
chmod +x reconx.py
sudo cp reconx.py /usr/local/bin/reconx
```

A partir de aquí, el comando `reconx` queda disponible desde cualquier carpeta y cualquier terminal nueva, sin necesidad de entornos virtuales ni de activar nada:

```bash
reconx 10.10.10.10
```

### Ejecución directa sin instalar

Si prefieres no copiarlo a `/usr/local/bin`, también puedes ejecutarlo directamente desde la carpeta donde lo tengas:

```bash
chmod +x reconx.py
./reconx.py 10.10.10.10
```
