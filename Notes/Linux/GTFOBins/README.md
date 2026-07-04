# GTFOBins

## ¿Qué es?

GTFOBins es un repositorio que documenta formas legítimas de utilizar binarios de Unix para obtener ejecución de comandos, leer archivos o escalar privilegios cuando esos binarios pueden ejecutarse con permisos elevados.
Acceso a través de https://gtfobins.org/.

---

## ¿Cuándo utilizarlo?

Después de ejecutar:

```bash
sudo -l
```

o cuando un binario tiene permisos especiales (SUID, capabilities, etc.).

---

## Metodología

1. Identificar el binario.
2. Buscarlo en GTFOBins.
3. Verificar si existe una técnica aplicable.
4. Ejecutarla y validar el resultado.

---

## Errores comunes

Suponer que todos los binarios permiten escalada de privilegios.

---

## Buenas prácticas

Comprobar siempre la versión y el contexto antes de aplicar una técnica de GTFOBins.

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
- JaulaCon2025 (The Hacker Labs)
