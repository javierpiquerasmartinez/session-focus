# Hilo conductor y guía de prompts

La identidad visual y sonora del canal **Lamplight Sessions**, y cómo escribir los prompts de cada Sesión.

## Constantes (todas las Escenas)

- **Fotorrealismo**: aspecto de fotografía o fotograma de cine; nunca ilustración, anime ni 3D estilizado.
- **Cámara fija**: ni paneo, ni zoom, ni dolly. Lo único que se mueve es el entorno.
- **Sin personas**: ni siluetas ni manos. Como mucho, tráfico o barcos lejanos sin detalle humano.
- **Contraste cálido/frío**: una fuente de luz cálida cercana (lámpara, ventana iluminada, farol, hoguera) frente a un exterior frío o azulado.
- **Franja horaria**: del atardecer a la noche por defecto. Amanecer con niebla o día de tormenta solo como excepción ocasional.
- **Calma**: nada que llame la atención de golpe (relámpagos, destellos, coches rápidos en primer plano).

Lo que varía entre Sesiones son los ejes de la Escena (ver [sesiones.md](sesiones.md)).

## Prompt de imagen (Nano Banana)

En inglés, como una descripción de fotografía:

1. Encuadre y punto de vista ("view from a 30th-floor apartment window…").
2. Sujeto y lugar con detalles concretos (materiales, objetos del primer plano, fondo).
3. Luz: la fuente cálida y el exterior frío, nombrados explícitamente.
4. Clima y atmósfera.
5. Estilo fotográfico: "photorealistic, shot on a full-frame camera, 35mm lens, shallow depth of field, cinematic color grading".
6. Restricciones: "no people, no text, no logos, no watermark".

Formato 16:9. Deja zonas que puedan moverse con naturalidad en el Bucle: lluvia sobre un cristal, vapor de una taza, llama, luces de tráfico lejano, niebla, hojas.

## Prompt de vídeo (Gemini Omni, Bucle)

Vídeo a partir de `imagen` (en AI Studio, adjuntándola una vez), **siempre en 720p**: el 1080p de Omni es un reescalado que hace vibrar la cámara a mitad del clip (comprobado en la Sesión 0001). El Montaje reescala a 1080p o más. El cierre del Bucle no depende del modelo: si el último fotograma no vuelve al primero, el Montaje lo cierra con un fundido de 1,5 s. El prompt solo describe **movimiento ambiental sutil**:

- Abre con la estabilidad, que es el fallo más habitual (vibración de cámara): "The camera is mounted on a heavy tripod and stays completely motionless for the entire video: no shake, no jitter, no drift, no zoom, no parallax." y nombra los objetos que deben quedarse quietos ("The window frame, the desk, the lamp… remain perfectly still and pixel-stable").
- Lista qué se mueve y cómo ("raindrops slowly running down the glass, distant car lights flowing far below, steam gently rising from the mug").
- Pide brillo constante en las fuentes de luz y cierra con: "Calm, peaceful motion only. No people. Silent video: no dialogue, no music, no sound effects."

El audio que genere Omni se descarta en el Montaje. Antes de dar un Bucle por bueno, `python3 scripts/montaje.py NNNN --vista-previa` genera `vista-previa-bucle.mp4` con tres repeticiones para verlo.

## Prompts de Pistas (Lyria)

En inglés. Cada Banda sonora tiene una paleta común y varias variaciones que se reparten entre las Pistas:

- **Base común**: "Instrumental only, no vocals. Lo-fi, warm, mellow, slow tempo (70–85 BPM), soft vinyl crackle, gentle tape saturation. Calm and unobtrusive, suited for studying. Around 3 minutes, with a soft intro and a gentle fade-out ending."
- **Ambiente de la Escena** dentro de la Pista ("soft rain ambience in the background", "faint distant city hum", "crackling fireplace").
- **Variaciones** de instrumento líder y tonalidad para que las Pistas no suenen iguales: Rhodes, piano con fieltro (felt piano), guitarra jazz, contrabajo, saxo suave, vibráfono… Mantén una tonalidad o modo cercano entre Pistas para que los fundidos encajen.

## Metadatos de YouTube

En inglés.

- **Título**: `<Escena evocadora> | <duración> lofi for study & focus | Lamplight Sessions` (p. ej. "Rainy Night in Tokyo from the 30th Floor | 2 Hours lofi for Study & Focus | Lamplight Sessions"). Máximo unos 90 caracteres.
- **Descripción**: dos o tres frases que sitúen la Escena, la lista de capítulos (salida de `/montaje`), una línea de que imagen y música están generadas con IA, y unos 3 hashtags.
- **Etiquetas**: 10–15, mezcla de genéricas (lofi, study music, focus music) y de la Escena (tokyo rain, night city).
- **Miniatura**: un fotograma de `imagen.png` con 2–4 palabras grandes ("RAINY TOKYO NIGHT"). Al subir, marca el contenido como alterado o sintético.
