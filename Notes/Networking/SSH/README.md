# SSH

## ¿Qué es?

SSH (Secure Shell) es un protocolo utilizado para acceder de forma remota a un sistema.

---

## ¿Cuándo utilizarlo?

Cuando se detecta el puerto 22 abierto o cualquier otro servicio SSH.

---

## Metodología

- Enumerar versión.
- Buscar usuarios válidos.
- Probar credenciales.
- Acceder al sistema.

---

## Comandos importantes

### Conexión

```bash
ssh usuario@IP
```

### Banner

```bash
nmap -sV -p22 IP
```

### Fuerza bruta

Hydra.

---

## Ejemplos

Acceso inicial tras obtener credenciales.

---

## Errores comunes

Intentar fuerza bruta sin disponer de usuarios válidos.

---

## Buenas prácticas

Intentar obtener usuarios antes de lanzar Hydra.

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
