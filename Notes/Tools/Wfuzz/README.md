# Wfuzz

## ¿Qué es?

Herramienta de fuzzing utilizada para descubrir parámetros, recursos y vulnerabilidades.

---

## ¿Cuándo utilizarlo?

Cuando existe una aplicación web con parámetros desconocidos.

---

## Metodología

- Identificar parámetros.
- Buscar recursos ocultos.
- Detectar vulnerabilidades.

---

## Comandos importantes

```bash
wfuzz -w WORDLIST http://IP/FUZZ
```

---

## Errores comunes

Filtrar mal los resultados.

---

## Buenas prácticas

Utilizar filtros como:

```
--hl
--hc
```

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
