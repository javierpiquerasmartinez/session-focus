#!/usr/bin/env python3
"""Montaje de una Sesión: Bucle repetido + Banda sonora encadenada.

Uso:
    python3 scripts/montaje.py 0001                 # Montaje completo
    python3 scripts/montaje.py 0001 --solo-comprobar  # solo revisa Bucle y Pistas
    python3 scripts/montaje.py 0001 --duracion 90m --crossfade 5

Lee media/<NNNN-slug>/{bucle.mp4,pistas/*.mp3} y escribe montaje.mp4 y
capitulos.txt en esa misma carpeta. Solo usa la biblioteca estándar y ffmpeg.
"""

import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

RAIZ = Path(__file__).resolve().parent.parent
EXT_AUDIO = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
SSIM_DUPLICADO = 0.98  # último fotograma ≈ primero: se elimina para no "tartamudear"
FACTOR_SALTO = 1.1  # la unión puede diferir hasta 1,1× lo que difieren dos fotogramas consecutivos
LUFS_OBJETIVO = -14


def fallar(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def ejecutar(cmd: List[str]) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        fallar(f"falló {' '.join(cmd[:3])}…\n{res.stderr[-2000:]}")
    return res


def sondear(ruta: Path) -> dict:
    res = ejecutar([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(ruta),
    ])
    return json.loads(res.stdout)


def resolver_sesion(ident: str) -> Tuple[Path, Optional[Path]]:
    """Devuelve (carpeta de media, archivo de registro) a partir de '0001' o '0001-slug'."""
    numero = ident.split("-")[0]
    carpetas = sorted((RAIZ / "media").glob(f"{numero}-*"))
    if not carpetas:
        fallar(f"no existe media/{numero}-*/")
    registros = sorted((RAIZ / "sessions").glob(f"{numero}-*.md"))
    return carpetas[0], (registros[0] if registros else None)


def parsear_duracion(texto: str) -> float:
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(h|m|s)?\s*", texto)
    if not m:
        fallar(f"duración no válida: {texto!r} (usa 2h, 90m o 7200s)")
    valor, unidad = float(m.group(1)), (m.group(2) or "s")
    return valor * {"h": 3600, "m": 60, "s": 1}[unidad]


def leer_registro(registro: Optional[Path]) -> Tuple[Optional[str], List[str]]:
    """Devuelve (duración del frontmatter, títulos de la sección '## Banda sonora')."""
    if not registro:
        return None, []
    texto = registro.read_text(encoding="utf-8")
    m = re.search(r"^duracion:\s*(\S+)", texto, re.MULTILINE)
    duracion = m.group(1) if m else None
    titulos: List[str] = []
    seccion = re.search(r"^## Banda sonora\s*\n(.*?)(?=^## |\Z)", texto, re.MULTILINE | re.DOTALL)
    if seccion:
        titulos = re.findall(r"^\s*\d+\.\s+(.+?)\s*$", seccion.group(1), re.MULTILINE)
    return duracion, titulos


def ssim(a: Path, b: Path) -> float:
    res = ejecutar(["ffmpeg", "-hide_banner", "-i", str(a), "-i", str(b), "-lavfi", "ssim", "-f", "null", "-"])
    m = re.search(r"All:(\d+(?:\.\d+)?)", res.stderr)
    if not m:
        fallar("no se pudo calcular el SSIM entre fotogramas")
    return float(m.group(1))


def info_video(bucle: Path) -> Tuple[int, float, int, int]:
    """(número de fotogramas, fps, ancho, alto) contando fotogramas reales."""
    res = ejecutar([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=nb_read_frames,r_frame_rate,width,height",
        "-print_format", "json", str(bucle),
    ])
    s = json.loads(res.stdout)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return int(s["nb_read_frames"]), float(num) / float(den), int(s["width"]), int(s["height"])


def comprobar_bucle(bucle: Path, tmp: Path) -> Tuple[int, float, bool, bool, int]:
    frames, fps, ancho, alto = info_video(bucle)
    rutas = {}
    for nombre, indice in (("primero", 0), ("segundo", 1), ("penultimo", frames - 2), ("ultimo", frames - 1)):
        rutas[nombre] = tmp / f"{nombre}.png"
        ejecutar([
            "ffmpeg", "-v", "error", "-y", "-i", str(bucle),
            "-vf", f"select=eq(n\\,{indice})", "-frames:v", "1", str(rutas[nombre]),
        ])
    s_ultimo = ssim(rutas["primero"], rutas["ultimo"])
    s_penultimo = ssim(rutas["primero"], rutas["penultimo"])
    # Referencia: cuánto se parecen dos fotogramas consecutivos normales del Bucle.
    s_normal = ssim(rutas["primero"], rutas["segundo"])
    duplicado = s_ultimo >= SSIM_DUPLICADO and s_ultimo > s_penultimo
    # Si se elimina el último fotograma, la unión real es penúltimo → primero.
    s_union = s_penultimo if duplicado else s_ultimo
    print(f"Bucle: {frames} fotogramas, {fps:.3f} fps, {ancho}x{alto}, {frames / fps:.2f} s")
    print(f"  SSIM primero↔último {s_ultimo:.4f} · primero↔penúltimo {s_penultimo:.4f} · "
          f"entre fotogramas consecutivos {s_normal:.4f}")
    if duplicado:
        print("  El último fotograma repite el primero: se eliminará para que la unión sea fluida.")
    d_union, d_normal = 1 - s_union, 1 - s_normal
    cierra = d_union <= d_normal * FACTOR_SALTO + 0.002
    if cierra:
        print("  Unión del Bucle OK: tan suave como dos fotogramas seguidos.")
    else:
        print(f"  AVISO: la unión del Bucle cambia {d_union / max(d_normal, 1e-6):.2f}× más que dos fotogramas "
              "seguidos; el Montaje la cerrará con un fundido (--fundido-bucle).")
    # Imagen lado a lado de la unión (último fotograma que suena | primero) para revisarla a ojo.
    antes = rutas["penultimo"] if duplicado else rutas["ultimo"]
    ejecutar([
        "ffmpeg", "-v", "error", "-y", "-i", str(antes), "-i", str(rutas["primero"]),
        "-filter_complex", "hstack", str(bucle.parent / "union-bucle.png"),
    ])
    return frames, fps, duplicado, cierra, alto


def filtro_acabado(alto_origen: int, alto: int) -> str:
    """Escala a 16:9 con `alto` líneas; si hay que agrandar, lanczos y un enfoque suave."""
    ancho = alto * 16 // 9
    filtros = [f"scale={ancho}:{alto}:flags=lanczos:force_original_aspect_ratio=decrease",
               f"pad={ancho}:{alto}:(ow-iw)/2:(oh-ih)/2"]
    if alto_origen < alto:
        filtros.append("unsharp=5:5:0.5:5:5:0")
    filtros.append("format=yuv420p")
    return ",".join(filtros)


def preparar_bucle(bucle: Path, frames: int, fps: float, duplicado: bool, fundido: float,
                   acabado: str, destino: Path) -> int:
    """Deja el Bucle listo para repetirse sin re-codificar. Devuelve los fotogramas de un ciclo.

    Con fundido > 0 cierra el ciclo él mismo: el final del clip se funde con su comienzo, y el
    ciclo empieza justo donde acaba ese comienzo, así que la repetición no tiene salto.
    """
    usados = frames - 1 if duplicado else frames
    if fundido > 0:
        n_fundido = round(fundido * fps)
        if n_fundido * 3 > usados:
            fallar(f"el fundido de {fundido} s es demasiado largo para un Bucle de {usados / fps:.1f} s")
        grafo = (
            f"[0:v]trim=end_frame={usados},setpts=PTS-STARTPTS,split[a][b];"
            f"[a]trim=start_frame={n_fundido},setpts=PTS-STARTPTS[cuerpo];"
            f"[b]trim=end_frame={n_fundido},setpts=PTS-STARTPTS[cabeza];"
            f"[cuerpo][cabeza]xfade=transition=fade:duration={n_fundido / fps:.4f}:"
            f"offset={(usados - 2 * n_fundido) / fps:.4f},{acabado}[v]"
        )
        ciclo = usados - n_fundido
    else:
        grafo = f"[0:v]trim=end_frame={usados},setpts=PTS-STARTPTS,{acabado}[v]"
        ciclo = usados
    ejecutar([
        "ffmpeg", "-v", "error", "-y", "-i", str(bucle), "-an",
        "-filter_complex", grafo, "-map", "[v]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-g", str(ciclo), "-keyint_min", str(ciclo), "-sc_threshold", "0",
        "-movflags", "+faststart", str(destino),
    ])
    return ciclo


def listar_pistas(carpeta: Path) -> List[Path]:
    return sorted(p for p in (carpeta / "pistas").glob("*") if p.suffix.lower() in EXT_AUDIO)


def duracion_audio(ruta: Path) -> Tuple[float, float]:
    """(duración total, duración útil sin el silencio del final)."""
    total = float(sondear(ruta)["format"]["duration"])
    res = ejecutar(["ffmpeg", "-hide_banner", "-nostats", "-i", str(ruta),
                    "-af", "silencedetect=n=-50dB:d=0.5", "-f", "null", "-"])
    inicios = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", res.stderr)]
    finales = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", res.stderr)]
    # Un silencio que llega hasta el final del archivo no tiene silence_end, o lo tiene en `total`.
    if inicios and (len(finales) < len(inicios) or finales[-1] >= total - 0.1):
        return total, min(total, inicios[-1] + 0.3)
    return total, total


def construir_audio(secuencia: List[Path], utiles: List[float], duracion: float, crossfade: float,
                    destino: Path) -> None:
    entradas: List[str] = []
    for p in secuencia:
        entradas += ["-i", str(p)]
    partes = [f"[{i}:a]atrim=0:{utiles[i]:.3f},aresample=48000,"
              f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]"
              for i in range(len(secuencia))]
    actual = "a0"
    for i in range(1, len(secuencia)):
        siguiente = f"x{i}"
        partes.append(f"[{actual}][a{i}]acrossfade=d={crossfade}:c1=tri:c2=tri[{siguiente}]")
        actual = siguiente
    fundido_final = min(8.0, duracion / 10)
    partes.append(
        f"[{actual}]atrim=0:{duracion:.3f},asetpts=PTS-STARTPTS,"
        f"loudnorm=I={LUFS_OBJETIVO}:TP=-1.5:LRA=11,aresample=48000,"
        f"afade=t=in:d=2,afade=t=out:st={duracion - fundido_final:.3f}:d={fundido_final:.3f}[salida]"
    )
    ejecutar([
        "ffmpeg", "-v", "error", "-y", *entradas,
        "-filter_complex", ";".join(partes), "-map", "[salida]",
        "-c:a", "aac", "-b:a", "192k", str(destino),
    ])


def marca_tiempo(segundos: float) -> str:
    s = int(segundos)
    h, m, s = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sesion", help="número de la Sesión (0001) o NNNN-slug")
    ap.add_argument("--duracion", help="duración del Montaje (2h, 90m, 7200s); por defecto la del registro o 2h")
    ap.add_argument("--crossfade", type=float, default=4.0, help="segundos de fundido entre Pistas (4)")
    ap.add_argument("--fundido-bucle", type=float,
                    help="segundos de fundido para cerrar el Bucle; por defecto 0 si cierra solo y 1.5 si no")
    ap.add_argument("--alto", type=int, default=1080, choices=[1080, 1440, 2160],
                    help="resolución vertical del Montaje (1080); 1440 o 2160 hacen que YouTube use más bitrate")
    ap.add_argument("--vista-previa", action="store_true",
                    help="solo genera vista-previa-bucle.mp4 (el Bucle preparado repetido 3 veces) para revisarlo")
    ap.add_argument("--solo-comprobar", action="store_true", help="revisa Bucle y Pistas sin montar")
    args = ap.parse_args()

    carpeta, registro = resolver_sesion(args.sesion)
    dur_registro, titulos = leer_registro(registro)
    duracion = parsear_duracion(args.duracion or dur_registro or "2h")

    bucle = carpeta / "bucle.mp4"
    if not bucle.exists():
        fallar(f"falta {bucle.relative_to(RAIZ)}")
    pistas = listar_pistas(carpeta) if (carpeta / "pistas").exists() else []

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        frames, fps, duplicado, cierra, alto_origen = comprobar_bucle(bucle, tmp)
        acabado = filtro_acabado(alto_origen, args.alto)
        if alto_origen != args.alto:
            print(f"  Se reescalará de {alto_origen}p a {args.alto}p (lanczos{' + enfoque suave' if alto_origen < args.alto else ''}).")
        fundido = args.fundido_bucle if args.fundido_bucle is not None else (0.0 if cierra else 1.5)
        if fundido:
            print(f"  Cierre del Bucle: fundido de {fundido} s.")
        preparado = tmp / "bucle-preparado.mp4"

        if args.vista_previa:
            ciclo = preparar_bucle(bucle, frames, fps, duplicado, fundido, acabado, preparado)
            vista = carpeta / "vista-previa-bucle.mp4"
            ejecutar(["ffmpeg", "-v", "error", "-y", "-stream_loop", "2", "-i", str(preparado),
                      "-c", "copy", str(vista)])
            print(f"Vista previa: {vista.relative_to(RAIZ)} (3 ciclos de {ciclo / fps:.2f} s, sin audio)")
            return

        if not pistas:
            if args.solo_comprobar:
                print("Aún no hay Pistas en pistas/.")
                return
            fallar(f"no hay Pistas en {(carpeta / 'pistas').relative_to(RAIZ)}/")

        medidas = [duracion_audio(p) for p in pistas]
        duraciones = [util for _, util in medidas]  # sin el silencio final de cada Pista
        minimo = min(duraciones)
        if minimo <= args.crossfade * 2:
            fallar(f"hay una Pista de {minimo:.1f} s, demasiado corta para un fundido de {args.crossfade} s")
        banda = sum(duraciones) - args.crossfade * (len(pistas) - 1)
        print(f"Banda sonora: {len(pistas)} Pistas, {marca_tiempo(banda)} por vuelta")
        for p, (total, util) in zip(pistas, medidas):
            recorte = f" (se recortan {total - util:.1f} s de silencio final)" if total - util > 0.5 else ""
            print(f"  {p.name}: {marca_tiempo(util)}{recorte}")
        if titulos and len(titulos) != len(pistas):
            print(f"  AVISO: el registro tiene {len(titulos)} títulos y hay {len(pistas)} Pistas; "
                  "los capítulos usarán nombres genéricos.")
            titulos = []

        # Secuencia: las Pistas en orden, repetidas hasta cubrir la duración.
        secuencia: List[int] = []
        cubierto = 0.0
        while cubierto < duracion:
            i = len(secuencia) % len(pistas)
            cubierto += duraciones[i] - (args.crossfade if secuencia else 0)
            secuencia.append(i)
        vueltas = math.ceil(len(secuencia) / len(pistas))
        print(f"Montaje: {marca_tiempo(duracion)}, la Banda sonora suena {vueltas} veces ({len(secuencia)} Pistas en total)")

        if args.solo_comprobar:
            return

        audio = tmp / "audio.m4a"
        print("Preparando el Bucle…")
        preparar_bucle(bucle, frames, fps, duplicado, fundido, acabado, preparado)
        print("Construyendo la Banda sonora (fundidos + normalización a -14 LUFS)…")
        construir_audio([pistas[i] for i in secuencia], [duraciones[i] for i in secuencia],
                        duracion, args.crossfade, audio)

        montaje = carpeta / "montaje.mp4"
        print("Uniendo vídeo y audio…")
        ejecutar([
            "ffmpeg", "-v", "error", "-y",
            "-stream_loop", "-1", "-i", str(preparado), "-i", str(audio),
            "-map", "0:v", "-map", "1:a", "-c", "copy", "-t", f"{duracion:.3f}",
            "-movflags", "+faststart", str(montaje),
        ])

    # Capítulos: una entrada por Pista sonada, con su inicio real tras los fundidos.
    lineas: List[str] = []
    inicio = 0.0
    for n, i in enumerate(secuencia):
        if inicio >= duracion - 10:  # YouTube exige capítulos de al menos 10 s
            break
        nombre = titulos[i] if titulos else f"Track {i + 1:02d}"
        lineas.append(f"{marca_tiempo(inicio)} {nombre}")
        inicio += duraciones[i] - args.crossfade
    capitulos = carpeta / "capitulos.txt"
    capitulos.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    final = sondear(montaje)
    tam = int(final["format"]["size"]) / 1024 ** 2
    print(f"\nListo: {montaje.relative_to(RAIZ)} ({marca_tiempo(float(final['format']['duration']))}, {tam:.0f} MB)")
    print(f"Capítulos: {capitulos.relative_to(RAIZ)} ({len(lineas)} entradas)")


if __name__ == "__main__":
    main()
