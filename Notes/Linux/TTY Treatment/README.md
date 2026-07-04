# TTY Treatment

## ¿Qué es?

El tratamiento de la TTY consiste en convertir una reverse shell básica en una terminal completamente interactiva para trabajar de forma más cómoda.

---

## ¿Cuándo utilizarlo?

Siempre que se obtenga una reverse shell limitada.

---

## Metodología

1. Obtener una reverse shell.
2. Ejecutar una shell interactiva.
3. Suspender la sesión.
4. Configurar la terminal.
5. Recuperar la conexión.

---

## Comandos importantes

Crear una bash interactiva:

```bash
script /dev/null -c bash
```

Suspender la shell:

```bash
Ctrl + Z
```

Configurar la terminal:

```bash
stty raw -echo
fg
reset xterm
export TERM=xterm
export SHELL=bash
```

---

## Errores comunes

- Olvidar restaurar la terminal.
- No exportar la variable TERM.

---

## Buenas prácticas

- Realizar el tratamiento inmediatamente después de obtener la shell.
- Configurar correctamente TERM y SHELL.

---

## Laboratorios donde lo he utilizado

- Facultad (The Hacker Labs)
