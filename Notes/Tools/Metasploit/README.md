# Metasploit

## ¿Qué es?

Metasploit Framework es una plataforma utilizada para desarrollar, probar y ejecutar exploits contra sistemas vulnerables.

---

## ¿Cuándo utilizarlo?

Cuando existe una vulnerabilidad conocida para la que Metasploit dispone de un módulo compatible.

---

## Metodología

1. Buscar el módulo adecuado.
2. Configurar sus parámetros.
3. Ejecutar el exploit.
4. Validar el acceso obtenido.

---

## Comandos importantes

Buscar módulos:

```bash
search 
```

Mostrar parámetros:

```bash
show options
```

Configurar un parámetro:

```bash
set RHOSTS IP
```

Ejecutar el módulo:

```bash
run
```

Obtener una shell:

```bash
shell
```

---

## Errores comunes

- Utilizar un módulo sin comprobar la versión del objetivo.
- No revisar correctamente los parámetros antes de ejecutar el exploit.

---

## Buenas prácticas

Validar siempre que el módulo corresponde con la versión del software objetivo.

---

## Laboratorios donde lo he utilizado

- JaulaCon2025 (The Hacker Labs)
