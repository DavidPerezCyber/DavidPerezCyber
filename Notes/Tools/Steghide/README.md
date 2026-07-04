# Steghide

## ¿Qué es?

Steghide es una herramienta utilizada para extraer información oculta dentro de archivos mediante técnicas de esteganografía.

---

## ¿Cuándo utilizarlo?

Cuando durante una auditoría se encuentren imágenes o archivos sospechosos que puedan contener información oculta.

---

## Metodología

1. Identificar archivos interesantes.
2. Intentar extraer información.
3. Analizar el contenido obtenido.
4. Buscar credenciales, mensajes o pistas.

---

## Comandos importantes

Extraer información:

```bash
steghide extract -sf imagen.jpg
```

Insertar información:

```bash
steghide embed -cf imagen.jpg -ef archivo.txt
```

Información del archivo:

```bash
steghide info imagen.jpg
```

---

## Errores comunes

- No comprobar si la imagen está protegida mediante contraseña.
- Pensar que todas las imágenes contienen información.

---

## Buenas prácticas

- Revisar siempre imágenes sospechosas.
- Utilizarla junto con otras técnicas de análisis de archivos.

---

## Laboratorios donde lo he utilizado

- Facultad (The Hacker Labs)
