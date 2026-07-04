# HTTP

## ¿Qué es?

HTTP (HyperText Transfer Protocol) es el protocolo utilizado para la comunicación entre clientes y servidores web.

Durante un pentest suele ser uno de los primeros servicios que se analizan, ya que muchas vulnerabilidades se encuentran en aplicaciones web.

---

## ¿Cuándo utilizarlo?

Siempre que un escaneo detecte un servicio web (puertos 80, 8080, 8000, etc.).

---

## Metodología

Cuando encuentro un servicio HTTP normalmente sigo este proceso:

1. Acceder a la aplicación desde el navegador.
2. Revisar el código fuente.
3. Identificar tecnologías utilizadas.
4. Buscar parámetros GET y POST.
5. Enumerar directorios y archivos.
6. Buscar vulnerabilidades.

---

## Comandos importantes

### Curl

```bash
curl http://IP
```

Realizar peticiones HTTP desde la terminal.

### Gobuster

```bash
gobuster dir -u http://IP -w WORDLIST
```

Enumeración de directorios.

### Wfuzz

```bash
wfuzz -w WORDLIST http://IP/FUZZ
```

Fuzzing de parámetros o recursos.

---

## Ejemplos

- Enumeración de directorios.
- Identificación de parámetros.
- Detección de vulnerabilidades web.

---

## Errores comunes

- No revisar el código fuente.
- No analizar los parámetros de la URL.
- Limitarse únicamente a Gobuster.

---

## Buenas prácticas

Combinar navegación manual con herramientas automáticas.

---

## Laboratorios donde lo he utilizado

- Fruits (The Hacker Labs)
