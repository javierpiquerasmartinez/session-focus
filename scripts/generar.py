# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai"]
# ///
"""Generación automática del material de una Sesión con la API de Gemini.

Uso (siempre con uv, que instala la dependencia aislada):
    uv run scripts/generar.py imagen 0001 --n 3   # candidatas en candidatas/imagen-NN.png
    uv run scripts/generar.py bucle 0001          # candidata en candidatas/bucle-NN.mp4
    uv run scripts/generar.py pistas 0001         # completa pistas/NN.mp3 hasta `pistas:`

Lee los prompts de los bloques ```imagen, ```bucle y ```pista del archivo
sessions/NNNN-slug.md. Antes de llamar a la API muestra qué va a generar y el
coste estimado, y pide confirmación. --si salta la pregunta: úsalo solo cuando
el usuario ya haya aprobado esa ejecución concreta.

La clave se lee de GEMINI_API_KEY (entorno o archivo .env en la raíz del repo).
"""

import argparse
import base64
import os
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Modelos y precios estimados (USD). Revisa https://ai.google.dev/gemini-api/docs/pricing
# si Google cambia algo: este bloque es lo único que hay que tocar.
MODELO_IMAGEN = "gemini-nano-banana-2.1"
PRECIO_IMAGEN = 0.0504  # por imagen 2K
MODELO_VIDEO = "gemini-omni-1.2-flash"
PRECIO_VIDEO_SEGUNDO = 0.07  # por segundo a 720p (el 1080p de Omni vibra; ver docs/hilo-conductor.md)
MODELO_MUSICA = "lyria-3.5"
PRECIO_PISTA = 0.08  # por Pista

LIMITE_POR_DEFECTO = 5.0


def fallar(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def cargar_clave() -> str:
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*([A-Z_]+)\s*=\s*(.*?)\s*$", linea)
            if m and m.group(2) and m.group(1) not in os.environ:
                os.environ[m.group(1)] = m.group(2).strip("'\"")
    clave = os.environ.get("GEMINI_API_KEY")
    if not clave:
        fallar("falta GEMINI_API_KEY (copia .env.example a .env y rellénalo)")
    return clave


def resolver_sesion(ident: str):
    numero = ident.split("-")[0]
    registros = sorted((RAIZ / "sessions").glob(f"{numero}-*.md"))
    if not registros:
        fallar(f"no existe sessions/{numero}-*.md")
    registro = registros[0]
    carpeta = RAIZ / "media" / registro.stem
    return registro, carpeta


def bloques(texto: str, tipo: str) -> list:
    encontrados = re.findall(rf"^```{tipo}[ \t]*\n(.*?)^```", texto, re.MULTILINE | re.DOTALL)
    return [b.strip() for b in encontrados if b.strip()]


def frontmatter_int(texto: str, campo: str):
    m = re.search(rf"^{campo}:\s*(\d+)", texto, re.MULTILINE)
    return int(m.group(1)) if m else None


def siguiente_ruta(carpeta: Path, prefijo: str, ext: str) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    n = 1
    while (carpeta / f"{prefijo}{n:02d}{ext}").exists():
        n += 1
    return carpeta / f"{prefijo}{n:02d}{ext}"


def confirmar(resumen: list, coste: float, limite: float, si: bool) -> None:
    print("Se va a generar:")
    for linea in resumen:
        print(f"  - {linea}")
    print(f"Coste estimado: {coste:.2f} $ (límite por ejecución: {limite:.2f} $)")
    if coste > limite:
        fallar(f"el coste estimado supera el límite; sube --limite a propósito si de verdad lo quieres")
    if si:
        return
    if not sys.stdin.isatty():
        fallar("sin terminal interactiva: confirma la ejecución y vuelve a lanzarla con --si")
    if input("¿Continuar? [s/N] ").strip().lower() not in {"s", "si", "sí", "y", "yes"}:
        fallar("cancelado")


def b64(ruta: Path) -> str:
    return base64.b64encode(ruta.read_bytes()).decode()


def guardar_salida(cliente, salida, destino: Path) -> None:
    """Guarda una salida de interactions (inline en base64 o como URI del Files API)."""
    if salida is None:
        fallar("la respuesta no trae salida; revisa el prompt o el modelo")
    datos = getattr(salida, "data", None)
    if datos:
        destino.write_bytes(base64.b64decode(datos))
        return
    uri = getattr(salida, "uri", None)
    if not uri:
        fallar("la salida no trae ni datos ni URI")
    nombre = uri.rstrip("/").split("/")[-1]
    for _ in range(120):
        info = cliente.files.get(name=f"files/{nombre}")
        estado = info.state.name if info.state else ""
        if estado == "ACTIVE":
            break
        if estado == "FAILED":
            fallar("el archivo generado quedó en estado FAILED")
        time.sleep(5)
    contenido = cliente.files.download(file=uri)
    if isinstance(contenido, (bytes, bytearray)):
        destino.write_bytes(contenido)
    elif not destino.exists():
        fallar("no se pudo descargar el archivo generado")


def generar_imagen(cliente, prompt: str, destino: Path) -> None:
    respuesta = cliente.interactions.create(
        model=MODELO_IMAGEN,
        input=prompt,
        response_format={"type": "image", "aspect_ratio": "16:9", "image_size": "2K", "mime_type": "image/png"},
    )
    guardar_salida(cliente, respuesta.output_image, destino)


def generar_bucle(cliente, imagen: Path, prompt: str, segundos: int, destino: Path) -> None:
    mime = "image/png" if imagen.suffix.lower() == ".png" else "image/jpeg"
    fotograma = {"type": "image", "data": b64(imagen), "mime_type": mime}
    respuesta = cliente.interactions.create(
        model=MODELO_VIDEO,
        # Misma imagen como primer y último fotograma → el clip cierra en bucle.
        input=[fotograma, fotograma, {"type": "text", "text": prompt}],
        response_format={"type": "video", "aspect_ratio": "16:9", "resolution": "720p", "duration": f"{segundos}s"},
    )
    guardar_salida(cliente, respuesta.output_video, destino)


def generar_pista(cliente, prompt: str, destino: Path) -> None:
    respuesta = cliente.interactions.create(model=MODELO_MUSICA, input=prompt)
    guardar_salida(cliente, respuesta.output_audio, destino)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tipo", choices=["imagen", "bucle", "pistas"])
    ap.add_argument("sesion", help="número de la Sesión (0001) o NNNN-slug")
    ap.add_argument("--n", type=int, default=1, help="candidatas a generar (imagen y bucle)")
    ap.add_argument("--segundos", type=int, default=8, help="duración del Bucle, 3–10 s (8)")
    ap.add_argument("--cantidad", type=int, help="Pistas a generar (por defecto, las que faltan hasta `pistas:`)")
    ap.add_argument("--limite", type=float, default=LIMITE_POR_DEFECTO, help="coste máximo por ejecución en $")
    ap.add_argument("--si", action="store_true", help="no preguntar (solo con aprobación previa del usuario)")
    args = ap.parse_args()

    registro, carpeta = resolver_sesion(args.sesion)
    texto = registro.read_text(encoding="utf-8")
    trabajos = []  # (descripción, función sin argumentos)

    if args.tipo == "imagen":
        prompts = bloques(texto, "imagen")
        if not prompts:
            fallar(f"{registro.name} no tiene bloque ```imagen")
        for _ in range(args.n):
            destino = siguiente_ruta(carpeta / "candidatas", "imagen-", ".png")
            destino.touch()  # reserva el nombre para la siguiente candidata
            trabajos.append((destino, lambda d=destino: generar_imagen(cliente, prompts[0], d)))
        coste = args.n * PRECIO_IMAGEN
        resumen = [f"{args.n} imagen(es) 16:9 2K con {MODELO_IMAGEN}"]

    elif args.tipo == "bucle":
        prompts = bloques(texto, "bucle")
        if not prompts:
            fallar(f"{registro.name} no tiene bloque ```bucle")
        imagenes = [carpeta / f"imagen{ext}" for ext in (".png", ".jpg", ".jpeg")]
        imagen = next((p for p in imagenes if p.exists()), None)
        if imagen is None:
            fallar(f"falta media/{carpeta.name}/imagen.png (o .jpg): elige primero la imagen")
        if not 3 <= args.segundos <= 10:
            fallar("con primer y último fotograma, Omni admite de 3 a 10 s")
        for _ in range(args.n):
            destino = siguiente_ruta(carpeta / "candidatas", "bucle-", ".mp4")
            destino.touch()
            trabajos.append((destino, lambda d=destino: generar_bucle(cliente, imagen, prompts[0], args.segundos, d)))
        coste = args.n * args.segundos * PRECIO_VIDEO_SEGUNDO
        resumen = [f"{args.n} Bucle(s) de {args.segundos} s a 720p con {MODELO_VIDEO}, a partir de {imagen.name}"]

    else:
        prompts = bloques(texto, "pista")
        if not prompts:
            fallar(f"{registro.name} no tiene bloques ```pista")
        carpeta_pistas = carpeta / "pistas"
        existentes = len(list(carpeta_pistas.glob("*.mp3"))) if carpeta_pistas.exists() else 0
        objetivo = frontmatter_int(texto, "pistas") or 10
        cantidad = args.cantidad if args.cantidad is not None else max(objetivo - existentes, 0)
        if cantidad == 0:
            print(f"Ya hay {existentes} Pistas (objetivo {objetivo}); nada que generar.")
            return
        for k in range(cantidad):
            prompt = prompts[(existentes + k) % len(prompts)]
            destino = siguiente_ruta(carpeta_pistas, "", ".mp3")
            destino.touch()
            trabajos.append((destino, lambda d=destino, p=prompt: generar_pista(cliente, p, d)))
        coste = cantidad * PRECIO_PISTA
        resumen = [f"{cantidad} Pista(s) con {MODELO_MUSICA}, rotando {len(prompts)} prompt(s)"]

    try:
        confirmar(resumen, coste, args.limite, args.si)
    except SystemExit:
        for destino, _ in trabajos:
            if destino.exists() and destino.stat().st_size == 0:
                destino.unlink()
        raise

    from google import genai  # importación tardía: --help y la confirmación no necesitan el SDK

    cliente = genai.Client(api_key=cargar_clave())
    fallos = 0
    for destino, trabajo in trabajos:
        print(f"→ {destino.relative_to(RAIZ)}…", flush=True)
        try:
            trabajo()
        except Exception as e:  # una candidata fallida no debe tumbar el resto
            fallos += 1
            if destino.exists() and destino.stat().st_size == 0:
                destino.unlink()
            print(f"  falló: {e}", file=sys.stderr)
    print(f"Hecho: {len(trabajos) - fallos} de {len(trabajos)} generados en {carpeta.relative_to(RAIZ)}/")
    if fallos:
        sys.exit(1)


if __name__ == "__main__":
    main()
