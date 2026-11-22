# Hilo conductor y guía de prompts

La identidad visual y sonora del canal **Lamplight**, y cómo escribir los prompts de cada Sesión.

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

La misma `imagen.png` va como primer y último fotograma, así que el prompt solo describe **movimiento ambiental sutil y cíclico**:

- Lista qué se mueve y cómo ("raindrops slowly running down the glass, distant car lights flowing far below, steam gently rising from the mug").
- Cierra siempre con: "Static locked-off camera, no camera movement. Subtle, slow, calm motion only. The scene returns exactly to its initial state. No people. No dialogue, no music, no sound effects."
- Evita cambios de luz globales: el inicio y el final han de coincidir.

El audio que genere Omni se descarta en el Montaje.

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
