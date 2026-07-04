# WPScan

## ¿Qué es?

WPScan es una herramienta especializada en la enumeración y auditoría de instalaciones WordPress.

Permite identificar usuarios, versiones, plugins, temas y vulnerabilidades conocidas.

---

## ¿Cuándo utilizarlo?

Cuando durante la enumeración se detecta un sitio WordPress.

---

## Metodología

1. Confirmar que el sitio utiliza WordPress.
2. Identificar la versión.
3. Enumerar usuarios.
4. Buscar plugins vulnerables.
5. Buscar temas vulnerables.
6. Comprobar credenciales débiles.

---

## Comandos importantes

Información general:

```bash
wpscan --url http://IP
```

Enumerar usuarios:

```bash
wpscan --url http://IP --enumerate u
```

Enumerar plugins vulnerables:

```bash
wpscan --url http://IP --enumerate vp
```

Ataque de diccionario:

```bash
wpscan --url http://IP --usernames usuario --passwords rockyou.txt
```

---

## Errores comunes

- No identificar correctamente la URL del WordPress.
- No comprobar plugins y temas.
- Lanzar ataques de fuerza bruta sin conocer usuarios.

---

## Buenas prácticas

- Enumerar primero usuarios.
- Revisar la versión antes de buscar vulnerabilidades.
- Analizar plugins y temas instalados.

---

## Laboratorios donde lo he utilizado

- Facultad (The Hacker Labs)
