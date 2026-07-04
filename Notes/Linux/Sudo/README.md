# Sudo

## ¿Qué es?

Permite ejecutar comandos con privilegios elevados según la configuración del sistema.

---

## ¿Cuándo utilizarlo?

Siempre después de obtener acceso a un sistema Linux.

---

## Metodología

El primer comando que ejecuto tras acceder al sistema es:

```bash
sudo -l
```

El objetivo es identificar binarios que puedan ejecutarse con permisos elevados.

---

## Comandos importantes

```bash
sudo -l
```

---

## Errores comunes

No ejecutar `sudo -l` durante la enumeración interna.

---

## Buenas prácticas

Comprobar siempre GTFOBins cuando un binario pueda ejecutarse mediante sudo.

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
- JaulaCon2025 (The Hacker Labs)
