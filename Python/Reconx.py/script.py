#!/usr/bin/env python3
"""
ReconX
======

Herramienta de enumeración para pentesting orientada a laboratorios tipo
TryHackMe, Hack The Box y preparación para la OSCP.

Script de fichero único: no requiere pip, venv ni dependencias externas.
Solo usa la librería estándar de Python 3 (subprocess, argparse, re, sys).

Instalación como comando global "reconx":
    chmod +x reconx.py
    sudo cp reconx.py /usr/local/bin/reconx

Uso:
    reconx <IP>

Ejemplo:
    reconx 10.10.10.10
"""

import argparse
import re
import subprocess
import sys

# --------------------------------------------------------------------------
# Colores ANSI (sin dependencias externas, funcionan en cualquier terminal
# Linux moderna, incluida Kali).
# --------------------------------------------------------------------------
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_banner():
    """Muestra el banner inicial de la herramienta."""
    print(CYAN + BOLD + "=================================" + RESET)
    print(CYAN + BOLD + "            ReconX" + RESET)
    print(CYAN + BOLD + "=================================" + RESET)


def print_success(message: str):
    """Imprime un mensaje de éxito en verde con prefijo [+]."""
    print(GREEN + f"[+] {message}" + RESET)


def print_error(message: str):
    """Imprime un mensaje de error en rojo con prefijo [-]."""
    print(RED + f"[-] {message}" + RESET)


def print_info(message: str):
    """Imprime un mensaje informativo en cian con prefijo [*]."""
    print(CYAN + f"[*] {message}" + RESET)


def print_warning(message: str):
    """Imprime un mensaje de advertencia en amarillo con prefijo [!]."""
    print(YELLOW + f"[!] {message}" + RESET)


# --------------------------------------------------------------------------
# FASE 1 - Funciones principales
# --------------------------------------------------------------------------

def check_connection(ip: str) -> bool:
    """
    Comprueba la conectividad con el host objetivo mediante ping.

    Ejecuta exactamente:
        ping -c 3 <ip>

    Args:
        ip: Dirección IP del objetivo.

    Returns:
        True si el host responde (returncode == 0), False en caso contrario.
    """
    print_info("Comprobando conectividad...")

    try:
        resultado = subprocess.run(
            ["ping", "-c", "3", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print_error("El comando 'ping' no se encuentra instalado en este sistema.")
        sys.exit(1)

    return resultado.returncode == 0


def run_initial_scan(ip: str) -> str:
    """
    Ejecuta un escaneo completo de puertos con nmap sobre el objetivo.

    Ejecuta exactamente:
        nmap -p- <ip>

    La salida NO se muestra por pantalla, se captura internamente para
    poder extraer los puertos abiertos.

    Args:
        ip: Dirección IP del objetivo.

    Returns:
        La salida completa (stdout) del comando nmap como cadena de texto.
    """
    print_info("Ejecutando reconocimiento de puertos (nmap -p-)...")
    print_info("Esto puede tardar unos minutos, por favor espera...")

    try:
        resultado = subprocess.run(
            ["nmap", "-p-", ip],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print_error("El comando 'nmap' no se encuentra instalado en este sistema.")
        sys.exit(1)

    if resultado.returncode != 0:
        print_error(f"nmap finalizó con un error:\n{resultado.stderr}")
        sys.exit(1)

    return resultado.stdout


def extract_ports(nmap_output: str) -> str:
    """
    Extrae todos los puertos que aparecen como "open" en la salida de nmap
    y los devuelve en formato separado por comas, listo para usarse en el
    siguiente escaneo (por ejemplo: "22,80,111,445").

    Args:
        nmap_output: Salida en texto plano generada por run_initial_scan().

    Returns:
        Cadena con los puertos abiertos separados por comas.
        Cadena vacía si no se detecta ningún puerto abierto.
    """
    # Las líneas de puertos abiertos en nmap tienen el formato:
    #   22/tcp   open  ssh
    #   80/tcp   open  http
    patron = re.compile(r"^(\d+)/(tcp|udp)\s+open\b", re.MULTILINE)
    puertos_encontrados = patron.findall(nmap_output)
    puertos = [numero for numero, _protocolo in puertos_encontrados]

    return ",".join(puertos)


def run_service_scan(ip: str, ports: str):
    """
    Ejecuta un escaneo de detección de servicios y versiones sobre los
    puertos indicados, mostrando la salida completa de nmap en tiempo real
    (igual que si el usuario lo ejecutara manualmente en su terminal).

    Ejecuta exactamente:
        nmap -sV -sC -p<ports> <ip>

    Args:
        ip: Dirección IP del objetivo.
        ports: Puertos separados por comas (ej: "22,80,111,445").
    """
    print_info("Ejecutando escaneo de servicios (nmap -sV -sC)...\n")

    comando = ["nmap", "-sV", "-sC", "-p", ports, ip]

    try:
        # No capturamos stdout/stderr: al heredar los del proceso padre,
        # la salida de nmap se muestra en la terminal en tiempo real,
        # línea a línea, exactamente igual que una ejecución manual.
        subprocess.run(comando)
    except FileNotFoundError:
        print_error("El comando 'nmap' no se encuentra instalado en este sistema.")
        sys.exit(1)


# --------------------------------------------------------------------------
# Punto de entrada
# --------------------------------------------------------------------------

def parse_arguments():
    """Configura y procesa los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        prog="reconx",
        description="ReconX - Herramienta de enumeración para pentesting (TryHackMe / HTB / OSCP).",
    )
    parser.add_argument("ip", help="Dirección IP del host objetivo (ej: 10.10.10.10)")
    return parser.parse_args()


def main():
    """
    Función principal: orquesta la FASE 1 completa de ReconX.

    Flujo:
        1. Comprobar conectividad (ping). Si no hay respuesta, se informa
           y se termina inmediatamente sin ejecutar nada más.
        2. Escaneo inicial de todos los puertos (nmap -p-), sin mostrar
           salida en pantalla.
        3. Extracción automática de los puertos abiertos.
        4. Escaneo de servicios/versiones (nmap -sV -sC) sobre esos puertos,
           mostrando la salida completa en tiempo real.
    """
    args = parse_arguments()
    ip = args.ip

    print_banner()

    # --- Paso 1: comprobación de conectividad ---
    if not check_connection(ip):
        print_error("IP desconectada")
        sys.exit(1)

    print_success("IP conectada")

    # --- Paso 2: escaneo inicial de puertos (silencioso) ---
    salida_inicial = run_initial_scan(ip)

    # --- Paso 3: extracción de puertos abiertos ---
    puertos = extract_ports(salida_inicial)

    if not puertos:
        print_error("No se han detectado puertos abiertos. Finalizando.")
        sys.exit(1)

    print_success("Puertos encontrados:")
    print(puertos)

    # --- Paso 4: escaneo de servicios y versiones (salida en tiempo real) ---
    run_service_scan(ip, puertos)


if __name__ == "__main__":
    main()
