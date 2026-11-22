---
name: montaje
description: Comprueba el material de una Sesión y genera montaje.mp4, los capítulos y la descripción final para YouTube.
disable-model-invocation: true
---

# Montaje

Une el Bucle y las Pistas de una Sesión en su Montaje. Términos en [GLOSSARY.md](../../../GLOSSARY.md); rutas en [docs/sesiones.md](../../../docs/sesiones.md).

## 1. Comprobar

Ejecuta `python3 scripts/montaje.py NNNN --solo-comprobar` y abre `media/NNNN-slug/union-bucle.png` (a la izquierda el último fotograma que suena, a la derecha el primero). Si la unión no cierra (`AVISO`), el script la cierra con un fundido de 1,5 s; no hace falta regenerar por eso. Lo que sí obliga a regenerar es la **vibración**: objetos que deberían estar quietos (marco de la ventana, muebles) desplazándose. Para detectarla, compara fotogramas consecutivos en una zona estática recortada (SSIM con `ffmpeg`; caídas por debajo de ~0,95 son saltos) y mira una hoja de contactos. Genera `--vista-previa` y pide al usuario que la vea antes de montar.

Revisa también la lista de Pistas: duraciones parecidas y ninguna anormalmente corta (un fallo de generación). Las Pistas suenan en orden de nombre de archivo.

## 2. Montar

Pide al usuario los títulos de las Pistas o propón unos en inglés acordes con la Escena (cortos y evocadores, como "Neon Puddles", "Last Train Home"). Escríbelos como lista numerada en la sección `## Banda sonora` del registro, en el orden de los archivos: el script los usa para los capítulos.

Ejecuta `python3 scripts/montaje.py NNNN` en segundo plano (una Sesión de 2 h tarda unos minutos). La duración sale del frontmatter (`duracion`).

## 3. Cerrar

Hecho cuando todo esto es cierto:

- `montaje.mp4` existe con la duración esperada (la imprime el script).
- La descripción de YouTube del registro incluye el contenido de `capitulos.txt`.
- En Notas queda constancia de lo aprendido (qué prompt funcionó, cuántas candidatas hizo falta descartar).
- `estado: montada`.

Recuérdale al usuario que lo vea y escuche antes de subirlo (tú no puedes reproducirlo), que marque el contenido como alterado o sintético al subirlo, y que después te pase el enlace para poner `estado: publicada` y rellenar `youtube` y `publicada`.
