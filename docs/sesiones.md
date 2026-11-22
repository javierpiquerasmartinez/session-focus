# Sesiones: registro y material

Cómo se guarda cada Sesión en el repo y dónde vive su material. Términos en [GLOSSARY.md](../GLOSSARY.md).

## Registro

Cada Sesión es un archivo `sessions/NNNN-slug.md`, numerado desde `0001` en orden de creación, copiado de [`sessions/_plantilla.md`](../sessions/_plantilla.md). El archivo es la única fuente de verdad de la Sesión: ejes, prompts, metadatos de YouTube y notas. El slug va en inglés, en minúsculas y con guiones (`tokyo-rain-30th-floor`).

### Estado

El campo `estado` del frontmatter avanza en este orden:

| Estado | Significa |
|---|---|
| `prompts-listos` | Prompts escritos, falta generar el material |
| `generada` | Imagen, Bucle y Pistas están en `media/` |
| `montada` | Existe `montaje.mp4` y los capítulos |
| `publicada` | Subida a YouTube; `youtube` tiene el enlace |

### Ejes de la Escena

Cinco ejes en el frontmatter, con valores cortos en español para poder compararlos entre Sesiones:

- `lugar`: ciudad, bosque, costa, montaña, interior… y el sitio concreto en `lugar_detalle`
- `hora`: atardecer, hora azul, noche, madrugada, amanecer
- `clima`: despejado, lluvia, tormenta, niebla, nieve
- `estacion`: primavera, verano, otoño, invierno
- `punto_de_vista`: ventana, exterior, altura, vehículo

Dos Sesiones **se repiten** si coinciden en `lugar`, `clima` y `punto_de_vista` a la vez. Las Ideas pendientes viven en [`IDEAS.md`](../IDEAS.md).

## Material (`media/`)

`media/` no se versiona. Cada Sesión tiene `media/NNNN-slug/`, con el mismo nombre que su archivo de registro:

```
media/0001-tokyo-rain-30th-floor/
├── imagen.png          ← la imagen elegida, PNG o JPG (primer y último fotograma del Bucle)
├── bucle.mp4           ← el Bucle elegido
├── pistas/01.mp3 …     ← las Pistas, en el orden en que sonarán
├── candidatas/         ← variantes generadas y descartadas
├── montaje.mp4         ← salida de /montaje
├── capitulos.txt       ← salida de /montaje
└── miniatura-a/b/c.jpg ← salida de scripts/miniatura.swift (texto grande, discreto, sin texto)
```

Da igual si el material lo genera el usuario a mano en AI Studio o `scripts/generar.py`: acaba en las mismas rutas.

### Limpieza tras publicar

Una vez `publicada`, se borra lo que se puede regenerar o ya no sirve: `montaje.mp4`, `vista-previa-bucle.mp4`, `union-bucle.png`, `capitulos.txt` (ya está en la descripción del registro) y `candidatas/`. Se conservan `imagen`, `bucle.mp4` y `pistas/` (con ellos `/montaje` rehace el vídeo en minutos) y las miniaturas (para "Probar y comparar"). Los originales que el usuario descargó y ya están copiados aquí van a la Papelera tras comprobar que son idénticos.
