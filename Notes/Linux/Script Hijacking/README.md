# Script Hijacking

## ¿Qué es?

Script Hijacking consiste en modificar un script legítimo que se ejecuta con privilegios elevados para conseguir la ejecución de comandos como otro usuario o como root.

---

## ¿Cuándo utilizarlo?

Cuando un usuario puede modificar un script que posteriormente será ejecutado con privilegios elevados.

---

## Metodología

1. Identificar scripts ejecutados mediante sudo o tareas programadas.
2. Analizar su funcionamiento.
3. Comprobar permisos de escritura.
4. Modificar el contenido para ejecutar una shell.
5. Esperar o ejecutar el script.

---

## Comandos importantes

Buscar scripts:

```bash
find / -name "*.sh" 2>/dev/null
```

Editar un script:

```bash
nano script.sh
```

Dar permisos:

```bash
chmod +x script.sh
```

---

## Errores comunes

- No comprobar si el script realmente se ejecuta.
- Modificar el script sin hacer una copia previa.
- No revisar los permisos del archivo.

---

## Buenas prácticas

- Analizar completamente el funcionamiento del script antes de modificarlo.
- Comprobar si existen tareas programadas relacionadas.
- Revisar siempre los permisos de escritura.

---

## Laboratorios donde lo he utilizado

- Facultad (The Hacker Labs)
