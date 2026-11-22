# Lamplight

Taller del canal de YouTube **Lamplight**: vídeos largos para estudiar y concentrarse, con una Escena realista y nocturna en bucle y música lofi, todo generado con IA.

El repo guarda las ideas, los prompts y el registro de cada Sesión; el material (imágenes, vídeo, audio) se queda fuera de git en `media/`.

## Flujo de cada Sesión

1. **`/nueva-sesion`**: Claude propone Escenas que no repiten ninguna anterior, escribe `sessions/NNNN-slug.md` con los prompts y los metadatos de YouTube.
2. **Generar el material**, a mano en AI Studio o con el script:
   - Imagen con Nano Banana → `media/NNNN-slug/imagen.png`
   - Bucle con Gemini Omni (la imagen como primer y último fotograma) → `bucle.mp4`
   - Pistas con Lyria → `pistas/01.mp3`, `02.mp3`…
3. **`/montaje`**: Claude comprueba que el Bucle cierra, une todo en `montaje.mp4` y saca los capítulos.
4. Ver, subir a YouTube (marcando contenido sintético) y pasarle el enlace a Claude.

## Puesta en marcha

- `ffmpeg` instalado (`brew install ffmpeg`).
- Para la generación automática: `brew install uv`, y copiar `.env.example` a `.env` con una clave de la API de Gemini de pago.

```bash
uv run scripts/generar.py pistas 0001   # muestra coste estimado y pide confirmación
```

```bash
python3 scripts/montaje.py 0001 --solo-comprobar
```

## Dónde está cada cosa

- [GLOSSARY.md](GLOSSARY.md): vocabulario (Sesión, Escena, Bucle, Pista…)
- [IDEAS.md](IDEAS.md): Escenas candidatas
- [docs/hilo-conductor.md](docs/hilo-conductor.md): identidad visual y guía de prompts
- [docs/sesiones.md](docs/sesiones.md): registro, estados y estructura de `media/`
