---
name: montaje
description: Comprueba el material de una Sesión y genera montaje.mp4, los capítulos y la descripción final para YouTube.
disable-model-invocation: true
---

# Montaje

Une el Bucle y las Pistas de una Sesión en su Montaje. Términos en [GLOSSARY.md](../../../GLOSSARY.md); rutas en [docs/sesiones.md](../../../docs/sesiones.md).

## 1. Comprobar

Ejecuta `python3 scripts/montaje.py NNNN --solo-comprobar` y abre `media/NNNN-slug/union-bucle.png` (a la izquierda el último fotograma que suena, a la derecha el primero). El Bucle está listo cuando el script dice "Unión del Bucle OK" **y** en la imagen no ves diferencias de luz, posición o color entre las dos mitades. Si hay `AVISO` o diferencias visibles, díselo al usuario con lo que ves y propón regenerar el Bucle (ajustando el bloque ```bucle si el problema viene del prompt) antes de montar.

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
