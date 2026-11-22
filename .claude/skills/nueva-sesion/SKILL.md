---
name: nueva-sesion
description: Propone una Escena no repetida y escribe el registro de una nueva Sesión con sus prompts y metadatos de YouTube.
disable-model-invocation: true
---

# Nueva Sesión

Crea `sessions/NNNN-slug.md` con todo lo que el usuario necesita para generar el material. Antes de empezar, lee [GLOSSARY.md](../../../GLOSSARY.md), [docs/sesiones.md](../../../docs/sesiones.md) y [docs/hilo-conductor.md](../../../docs/hilo-conductor.md): las reglas del registro, los ejes y cómo escribir cada prompt viven allí.

## 1. Elegir la Escena

Lee los ejes de todas las Sesiones de `sessions/` y la tabla de [IDEAS.md](../../../IDEAS.md). Si el usuario ya trae una Escena, compruébala contra el registro; si no, propón **tres** Ideas que no se repitan con ninguna Sesión existente (misma combinación de `lugar` + `clima` + `punto_de_vista`) y que varíen respecto a las dos últimas Sesiones en al menos dos ejes. Dale una frase a cada una y deja que el usuario elija o ajuste.

Hecho cuando: el usuario ha elegido una Escena y has confirmado que no repite ninguna Sesión.

## 2. Escribir el registro

Copia [`sessions/_plantilla.md`](../../../sessions/_plantilla.md) a `sessions/NNNN-slug.md` con el siguiente número libre y rellena:

- Frontmatter: número, slug, `creada` con la fecha de hoy, ejes, `duracion` y `pistas` (2h y 10 salvo que el usuario diga otra cosa).
- Bloque ```imagen, bloque ```bucle y de 3 a 5 bloques ```pista, siguiendo la guía de prompts del hilo conductor.
- Metadatos de YouTube: título, descripción (sin capítulos todavía), etiquetas e idea de miniatura.

Si la Escena venía de `IDEAS.md`, quita su fila de la tabla.

Hecho cuando: el archivo no tiene marcadores de la plantilla sin rellenar salvo `publicada`, `youtube`, la sección Banda sonora y las Notas.

## 3. Entregar y generar

Muestra al usuario los prompts listos para copiar y pregúntale cómo quiere generar cada parte: a mano en AI Studio o con `scripts/generar.py`.

Para el modo automático: lanza primero el script **sin** `--si` (`uv run scripts/generar.py <tipo> NNNN`). Sin terminal interactiva se detiene tras imprimir qué generaría y su coste. Enseña ese resumen al usuario y vuelve a lanzarlo con `--si` solo después de que apruebe esa ejecución concreta. Orden: `imagen` (con `--n 3` para elegir) → el usuario elige y la copias como `media/NNNN-slug/imagen.png` → `bucle` → `pistas`. Puedes mirar las candidatas de imagen leyendo los PNG para opinar, pero la elección es del usuario.

En modo manual, recuérdale la convención de rutas de `media/` de [docs/sesiones.md](../../../docs/sesiones.md).

Cuando el material esté completo, pon `estado: generada` y sugiere `/montaje`.
