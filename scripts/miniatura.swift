// Miniaturas de una Sesión para YouTube (1280×720 JPG), en tres variantes para "Probar y comparar".
//
// Uso (desde la raíz del repo):
//     swift scripts/miniatura.swift 0001
//     swift scripts/miniatura.swift 0001 --texto "RAINY TOKYO NIGHT"
//
// Lee media/NNNN-slug/imagen.(png|jpg) y escribe en esa carpeta:
//     miniatura-a.jpg  texto grande arriba a la izquierda
//     miniatura-b.jpg  texto discreto abajo a la izquierda
//     miniatura-c.jpg  sin texto
// El texto sale, por defecto, de las comillas de la línea **Miniatura** del registro.
// Las tres llevan la lámpara de media/marca/marca-de-agua.png como sello si existe.
// Solo usa AppKit (viene con macOS): no hace falta instalar nada.

import AppKit
import Foundation

let ANCHO = 1280, ALTO = 720
let CREMA = NSColor(srgbRed: 0.96, green: 0.90, blue: 0.78, alpha: 1)
let AMBAR = NSColor(srgbRed: 0.88, green: 0.63, blue: 0.38, alpha: 1)

func fallar(_ msg: String) -> Never {
    FileHandle.standardError.write("ERROR: \(msg)\n".data(using: .utf8)!)
    exit(1)
}

// MARK: - Entrada

let fm = FileManager.default
let raiz = URL(fileURLWithPath: fm.currentDirectoryPath)
guard fm.fileExists(atPath: raiz.appendingPathComponent("sessions").path) else {
    fallar("ejecútalo desde la raíz del repo")
}

var args = Array(CommandLine.arguments.dropFirst())
guard let ident = args.first, !ident.hasPrefix("-") else {
    fallar("uso: swift scripts/miniatura.swift NNNN [--texto \"TEXTO\"]")
}
args.removeFirst()
var textoForzado: String?
if let i = args.firstIndex(of: "--texto"), i + 1 < args.count { textoForzado = args[i + 1] }

let numero = String(ident.split(separator: "-").first ?? "")
let registros = (try? fm.contentsOfDirectory(atPath: raiz.appendingPathComponent("sessions").path)) ?? []
guard let nombreRegistro = registros.sorted().first(where: { $0.hasPrefix("\(numero)-") && $0.hasSuffix(".md") }) else {
    fallar("no existe sessions/\(numero)-*.md")
}
let registro = (try? String(contentsOf: raiz.appendingPathComponent("sessions/\(nombreRegistro)"), encoding: .utf8)) ?? ""
let carpeta = raiz.appendingPathComponent("media/\(nombreRegistro.replacingOccurrences(of: ".md", with: ""))")

func primeraCaptura(_ patron: String, en texto: String) -> String? {
    guard let re = try? NSRegularExpression(pattern: patron, options: [.anchorsMatchLines]),
          let m = re.firstMatch(in: texto, range: NSRange(texto.startIndex..., in: texto)),
          let r = Range(m.range(at: 1), in: texto) else { return nil }
    return String(texto[r])
}

guard let titulo = textoForzado
    ?? primeraCaptura("^\\*\\*Miniatura\\*\\*:.*?\"([^\"]+)\"", en: registro)
    ?? primeraCaptura("^# (.+)$", en: registro) else {
    fallar("no encuentro el texto de la miniatura; pásalo con --texto")
}

let duracion: String = {
    guard let d = primeraCaptura("^duracion:\\s*(\\d+)\\s*([hm])", en: registro),
          let unidad = primeraCaptura("^duracion:\\s*\\d+\\s*([hm])", en: registro) else { return "" }
    let n = Int(d) ?? 0
    return unidad == "h" ? "\(n) HOUR\(n == 1 ? "" : "S")" : "\(n) MINUTES"
}()
let subtitulo = duracion.isEmpty ? "LOFI FOR STUDY & FOCUS" : "LOFI  ·  \(duracion)"

guard let rutaImagen = ["png", "jpg", "jpeg"].map({ carpeta.appendingPathComponent("imagen.\($0)") })
        .first(where: { fm.fileExists(atPath: $0.path) }),
      let imagen = NSImage(contentsOf: rutaImagen),
      let cgImagen = imagen.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    fallar("falta media/\(carpeta.lastPathComponent)/imagen.png o .jpg")
}
let sello = NSImage(contentsOf: raiz.appendingPathComponent("media/marca/marca-de-agua.png"))?
    .cgImage(forProposedRect: nil, context: nil, hints: nil)

// MARK: - Dibujo

func fuente(_ nombres: [String], _ tam: CGFloat) -> NSFont {
    for n in nombres { if let f = NSFont(name: n, size: tam) { return f } }
    return NSFont.systemFont(ofSize: tam, weight: .semibold)
}

func texto(_ s: String, fuente f: NSFont, color: NSColor, espaciado: CGFloat, sombra: CGFloat) -> NSAttributedString {
    let sh = NSShadow()
    sh.shadowColor = NSColor.black.withAlphaComponent(0.65)
    sh.shadowBlurRadius = sombra
    sh.shadowOffset = NSSize(width: 0, height: -2)
    return NSAttributedString(string: s, attributes: [.font: f, .foregroundColor: color, .kern: espaciado, .shadow: sh])
}

/// Parte el título en dos líneas equilibradas si es largo ("RAINY TOKYO" / "NIGHT").
func lineas(_ s: String, maxCaracteres: Int) -> [String] {
    let palabras = s.split(separator: " ").map(String.init)
    guard s.count > maxCaracteres, palabras.count > 1 else { return [s] }
    var mejor = [s], peor = Int.max
    for corte in 1..<palabras.count {
        let a = palabras[..<corte].joined(separator: " "), b = palabras[corte...].joined(separator: " ")
        let desequilibrio = abs(a.count - b.count)
        if desequilibrio < peor { peor = desequilibrio; mejor = [a, b] }
    }
    return mejor
}

func degradado(_ ctx: CGContext, desde: CGPoint, hasta: CGPoint, opacidad: CGFloat) {
    let colores = [NSColor.black.withAlphaComponent(opacidad).cgColor, NSColor.black.withAlphaComponent(0).cgColor] as CFArray
    let g = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(), colors: colores, locations: [0, 1])!
    ctx.drawLinearGradient(g, start: desde, end: hasta, options: [.drawsBeforeStartLocation])
}

func lienzo(_ dibujar: (CGContext) -> Void) -> Data {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: ANCHO, pixelsHigh: ALTO, bitsPerSample: 8,
                               samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                               bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    let ctx = NSGraphicsContext.current!.cgContext
    ctx.interpolationQuality = .high

    // Imagen a sangre (cubre todo el lienzo, recortando lo que sobre).
    let iw = CGFloat(cgImagen.width), ih = CGFloat(cgImagen.height)
    let escala = max(CGFloat(ANCHO) / iw, CGFloat(ALTO) / ih)
    let w = iw * escala, h = ih * escala
    ctx.draw(cgImagen, in: CGRect(x: (CGFloat(ANCHO) - w) / 2, y: (CGFloat(ALTO) - h) / 2, width: w, height: h))

    // Viñeta suave para centrar la mirada.
    let centro = CGPoint(x: CGFloat(ANCHO) / 2, y: CGFloat(ALTO) / 2)
    let viñeta = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(),
                            colors: [NSColor.black.withAlphaComponent(0).cgColor,
                                     NSColor.black.withAlphaComponent(0.35).cgColor] as CFArray,
                            locations: [0.55, 1])!
    ctx.drawRadialGradient(viñeta, startCenter: centro, startRadius: 0, endCenter: centro,
                           endRadius: CGFloat(ANCHO) * 0.62, options: [.drawsAfterEndLocation])

    dibujar(ctx)

    // Sello: la lámpara arriba a la derecha (abajo a la derecha la tapa la duración de YouTube).
    if let sello = sello {
        ctx.setAlpha(0.9)
        ctx.draw(sello, in: CGRect(x: CGFloat(ANCHO) - 112, y: CGFloat(ALTO) - 112, width: 88, height: 88))
        ctx.setAlpha(1)
    }
    NSGraphicsContext.restoreGraphicsState()
    return rep.representation(using: .jpeg, properties: [.compressionFactor: 0.92])!
}

let serif = ["Baskerville-SemiBold", "Baskerville-Bold", "Georgia-Bold"]
let serifCursiva = ["Baskerville-SemiBoldItalic", "Baskerville-Italic", "Georgia-Italic"]
let sans = ["AvenirNext-DemiBold", "Avenir-Heavy", "HelveticaNeue-Medium"]

let variantes: [(String, (CGContext) -> Void)] = [
    ("a", { ctx in
        // Texto grande en mayúsculas, arriba a la izquierda, sobre un degradado oscuro.
        // El subtítulo va encima como antetítulo, para no invadir lo que haya bajo el título.
        degradado(ctx, desde: CGPoint(x: 0, y: CGFloat(ALTO)), hasta: CGPoint(x: 820, y: 230), opacidad: 0.7)
        let ante = texto(subtitulo, fuente: fuente(sans, 28), color: AMBAR, espaciado: 7, sombra: 8)
        var y = CGFloat(ALTO) - 58 - ante.size().height
        ante.draw(at: CGPoint(x: 70, y: y))
        y -= 4
        for linea in lineas(titulo.uppercased(), maxCaracteres: 12) {
            let t = texto(linea, fuente: fuente(serif, 104), color: CREMA, espaciado: 3, sombra: 14)
            y -= t.size().height * 0.9
            t.draw(at: CGPoint(x: 64, y: y))
        }
    }),
    ("b", { ctx in
        // Texto discreto en cursiva, abajo a la izquierda.
        degradado(ctx, desde: CGPoint(x: 0, y: 0), hasta: CGPoint(x: 0, y: 260), opacidad: 0.6)
        let nombre = titulo.capitalized
        texto(subtitulo, fuente: fuente(sans, 22), color: AMBAR, espaciado: 6, sombra: 6)
            .draw(at: CGPoint(x: 58, y: 48))
        texto(nombre, fuente: fuente(serifCursiva, 64), color: CREMA, espaciado: 1, sombra: 10)
            .draw(at: CGPoint(x: 54, y: 84))
    }),
    ("c", { _ in }),
]

for (nombre, dibujar) in variantes {
    let destino = carpeta.appendingPathComponent("miniatura-\(nombre).jpg")
    do { try lienzo(dibujar).write(to: destino) } catch { fallar("no se pudo escribir \(destino.path): \(error)") }
    print("media/\(carpeta.lastPathComponent)/\(destino.lastPathComponent)")
}
print("Texto: \"\(titulo)\" · \(subtitulo)")
