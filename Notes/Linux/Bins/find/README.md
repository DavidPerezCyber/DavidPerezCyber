# find

## ¿Qué es?

`find` es una utilidad de Linux utilizada para buscar archivos y directorios dentro del sistema de archivos aplicando diferentes criterios como nombre, propietario, permisos, tamaño o fecha de modificación.

Además de su función principal, `find` puede ejecutar comandos sobre los resultados obtenidos mediante la opción `-exec`, lo que lo convierte en un binario interesante desde el punto de vista de la escalada de privilegios cuando puede ejecutarse con permisos elevados.

---

## ¿Cuándo utilizarlo?

Durante una auditoría puede utilizarse para:

- Buscar archivos concretos.
- Localizar archivos con permisos especiales.
- Enumerar directorios.
- Ejecutar comandos sobre archivos encontrados.
- Escalar privilegios si puede ejecutarse mediante `sudo` o posee permisos SUID.

---

## Metodología

Cuando `sudo -l` indica que el usuario puede ejecutar `find` como otro usuario (especialmente root), el siguiente paso consiste en comprobar si es posible ejecutar comandos mediante la opción `-exec`.

En ese caso, se consulta GTFOBins para verificar si existe una técnica de escalada aplicable.

---

## Comandos importantes

### Buscar un archivo

```bash
find / -name archivo.txt 2>/dev/null
```

---

### Buscar archivos SUID

```bash
find / -perm -4000 2>/dev/null
```

---

### Buscar archivos pertenecientes a un usuario

```bash
find / -user root 2>/dev/null
```

---

### Ejecutar un comando sobre los resultados

```bash
find . -exec comando {} \;
```

---

### Escalada de privilegios mediante sudo

```bash
sudo find . -exec /bin/bash \; -quit
```

> La sintaxis exacta puede variar según el contexto y la técnica documentada en GTFOBins.

---

## Errores comunes

- Pensar que cualquier uso de `find` implica una escalada de privilegios.
- No revisar si realmente puede ejecutarse mediante `sudo`.
- Olvidar consultar GTFOBins antes de intentar una explotación.

---

## Buenas prácticas

- Revisar siempre la salida de `sudo -l`.
- Consultar GTFOBins para conocer las técnicas disponibles.
- Utilizar `find` como herramienta de enumeración incluso cuando no sea vulnerable.

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
