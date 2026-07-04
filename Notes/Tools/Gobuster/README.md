# Gobuster

## ¿Qué es?

Gobuster es una herramienta utilizada para enumerar directorios, archivos y subdominios.

---

## ¿Cuándo utilizarlo?

Siempre que exista un servicio HTTP.

---

## Metodología

1. Enumerar directorios.
2. Buscar archivos.
3. Probar extensiones.

---

## Comandos importantes

Enumeración básica

```bash
gobuster dir -u http://IP -w WORDLIST
```

Con extensiones

```bash
gobuster dir -u http://IP -w WORDLIST -x php,txt,sh
```

---

## Errores comunes

No utilizar extensiones.

---

## Buenas prácticas

Realizar varios escaneos utilizando distintas extensiones.

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
- JaulaCon2025 (The Hacker Labs)
- Facultad (The Hacker Labs)
