# Hydra

## ¿Qué es?

Herramienta para realizar ataques de fuerza bruta contra distintos servicios.

---

## ¿Cuándo utilizarlo?

Cuando ya se dispone de un usuario válido o existe una lista de posibles usuarios.

---

## Metodología

1. Obtener usuarios.
2. Seleccionar diccionario.
3. Ejecutar el ataque.
4. Validar las credenciales.

---

## Comandos importantes

SSH

```bash
hydra -l usuario -P rockyou.txt ssh://IP
```

---

## Ejemplos

Obtención de acceso SSH en Fruits.

---

## Errores comunes

Lanzar Hydra sin conocer usuarios válidos.

---

## Buenas prácticas

Reducir el número de intentos y utilizar usuarios reales cuando sea posible.

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
