"""Genera los planos (SVG) de las cajas estándar propuestas.

Cada plano muestra la caja desplegada (hoja neta) con:
  - Zonas de IMPRESIÓN FIJA: las imprime el proveedor en 1 tinta (Negro 90),
    son iguales para todas las referencias que usan ese formato.
  - Zonas de ROTULADO EN PLANTA: quedan en kraft limpio para imprimir aquí
    (inkjet o etiqueta) la marca, variedad, destino, código ITF-14 y lote.

Las medidas de los paneles salen de las fichas técnicas actuales del proveedor
(carpeta "Listado cajas"). Uso:  python3 generar_planos.py
"""
from pathlib import Path

SALIDA = Path(__file__).resolve().parent / "planos"

# código: (nombre, unidades, [pestaña de pegue, cara1, cara2, cara3, cara4],
#          aleta, alto del cuerpo, medidas internas, cartón, cierre, referencias que reemplaza)
FORMATOS = {
    "CE-12-ANT": ("Caja estándar x12 Aguardiente Antioqueño 750", 12,
                  [30, 388, 251, 390, 249], 122, 220, "384 x 245 x 210", "C620KF",
                  "Sin cierre licorera",
                  "60002594, 60002595, 60002597, 60002600, 60002608, 60002609, 60002652, 60002904"),
    "CE-20-ANT": ("Caja estándar x20 Aguardiente Antioqueño 750", 20,
                  [30, 486, 330, 488, 328], 162, 218, "482 x 324 x 208", "C540 KF",
                  "Cierre licorera caras 1 y 4 con score", "60002579, 60002580"),
    "CE-12-REAL": ("Caja estándar x12 Real NI 750", 12,
                   [30, 352, 266, 354, 264], 130, 255, "348 x 260 x 245", "C620KF",
                   "Sin cierre licorera", "60003294"),
    "CE-20-REAL": ("Caja estándar x20 Real NI 750", 20,
                   [30, 449, 366, 451, 364], 180, 253, "445 x 360 x 243", "C540 KF",
                   "Cierre licorera caras 1 y 4 con score", "60003155"),
    "CE-06-HER": ("Caja estándar x6 Herencia 750", 6,
                  [30, 240, 205, 238, 203], 100, 232, "233 x 200 x 222", "C540 KF",
                  "Cierre licorera caras 1 y 4 con score", "60003228, 60003229"),
}

KRAFT, LINEA, FIJO, LOCAL, TXT = "#d9b27c", "#7a5a2e", "#3a3a3a", "#1f6feb", "#222"


def rect(x, y, w, h, fill="none", stroke=LINEA, sw=1.2, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
            f'fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def texto(x, y, s, size=9, color=TXT, peso="normal", anchor="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" font-weight="{peso}" fill="{color}" text-anchor="{anchor}">{s}</text>')


def zona(x, y, w, h, tipo, titulo, lineas=()):
    """tipo = 'fijo' (proveedor, Negro 90) o 'local' (rotulado en planta)."""
    if tipo == "fijo":
        out = [rect(x, y, w, h, fill=FIJO, stroke=FIJO, op=0.18, sw=1)]
        color = FIJO
    else:
        out = [rect(x, y, w, h, fill=LOCAL, stroke=LOCAL, op=0.10, sw=1.4, dash="6,3")]
        color = LOCAL
    size = 8.5 if w > 110 else 7
    out.append(texto(x + w / 2, y + 13, titulo, size=size, color=color, peso="bold"))
    for i, l in enumerate(lineas):
        if 13 + (i + 1) * 10 < h - 2:
            out.append(texto(x + w / 2, y + 13 + (i + 1) * 10, l, size=size - 1.5, color=color))
    return out


def cara_larga(x, y, w, h, unidades):
    m = 12
    cod_w, cod_h = min(165, w - 2 * m), 52
    fijo_w, fijo_h = 95, 62
    out = []
    # Marca / variedad / destino (planta)
    marca_w = w - 2 * m - fijo_w - 8
    marca_h = h - 2 * m - cod_h - 8
    if marca_w >= 150:
        out += zona(x + m, y + m, marca_w, marca_h, "local", "ZONA A · MARCA Y VARIEDAD",
                    ["logo + variedad (Sin azúcar, 24°, Trad.)", "banda de color de la variedad",
                     "destino / FOR EXPORT"])
    else:
        out += zona(x + m, y + m, marca_w, marca_h, "local", "ZONA A · MARCA",
                    ["logo + variedad", "banda de color", "destino"])
    # Cantidad fija por formato (proveedor)
    out += zona(x + w - m - fijo_w, y + m, fijo_w, fijo_h, "fijo", f"{unidades} UNID. 750 ml",
                ["Glass bottles", "0.75 L"])
    # Sello FLA (proveedor)
    sello_h = max(0, marca_h - fijo_h - 8)
    if sello_h > 30:
        out += zona(x + w - m - fijo_w, y + m + fijo_h + 8, fijo_w, sello_h, "fijo", "SELLO FLA")
    # Código + lote (planta)
    out += zona(x + w - m - cod_w, y + h - m - cod_h, cod_w, cod_h, "local", "ZONA B · ITF-14 + LOTE",
                ["código de la referencia", "lote / fecha / booking"])
    return out


def cara_corta(x, y, w, h, unidades):
    m = 12
    out = []
    alto_c = h * 0.48
    out += zona(x + m, y + m, w - 2 * m, alto_c, "local", "ZONA C · VARIEDAD",
                ["variedad + color", "destino", "frases legales si el mercado las pide"])
    out += zona(x + m, y + m + alto_c + 8, w - 2 * m, h - 2 * m - alto_c - 8, "fijo",
                f"{unidades} UNID. 750 ml · SELLO FLA")
    return out


def plano(codigo, datos):
    nombre, unidades, paneles, aleta, cuerpo, med_int, carton, cierre, reemplaza = datos
    ancho = sum(paneles)
    alto = 2 * aleta + cuerpo
    ox, oy = 40, 95          # origen del dibujo
    W, H = ancho + 2 * ox, alto + oy + 175
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         rect(0, 0, W, H, fill="#ffffff", stroke="none"),
         texto(ox, 30, f"{codigo} — {nombre}", size=18, peso="bold", anchor="start"),
         texto(ox, 52, f"Medidas internas {med_int} mm · Hoja neta {alto} x {ancho} mm · "
               f"Cartón {carton} kraft · {cierre} · Impresión proveedor: 1 tinta Negro 90",
               size=11, anchor="start"),
         texto(ox, 70, f"Reemplaza: {reemplaza}", size=11, anchor="start", color="#555")]

    x = ox
    for i, pw in enumerate(paneles):
        if i == 0:   # pestaña de pegue
            s.append(rect(x, oy + aleta + 6, pw, cuerpo - 12, fill=KRAFT))
            s.append(texto(x + pw / 2, oy + aleta + cuerpo / 2, "pegue", size=7))
            x += pw
            continue
        # aletas superior e inferior + cuerpo
        s.append(rect(x + 2, oy, pw - 4, aleta, fill=KRAFT))
        s.append(rect(x, oy + aleta, pw, cuerpo, fill=KRAFT))
        s.append(rect(x + 2, oy + aleta + cuerpo, pw - 4, aleta, fill=KRAFT))
        s.append(texto(x + pw / 2, oy + aleta + cuerpo - 6, f"CARA {i}  ({pw} mm)", size=8, color=LINEA))
        larga = i in (1, 3)
        s += (cara_larga if larga else cara_corta)(x, oy + aleta, pw, cuerpo - 14, unidades)
        # Aletas: impresión fija
        if larga:
            s += zona(x + 14, oy + 10, pw - 28, aleta - 20, "fijo", "SÍMBOLOS DE MANEJO + ESTIBADO",
                      ["frágil · este lado arriba · no carear", "esquema estiba 1.20 x 1.00 m"])
            s += zona(x + 14, oy + aleta + cuerpo + 10, pw - 28, aleta - 20, "fijo",
                      "CERTIFICACIONES · RECICLAJE · PESO", ["guía-señal y ranuras de trazabilidad"])
        x += pw

    # cotas generales
    s.append(texto(ox + ancho / 2, oy - 8, f"{ancho} mm", size=10, color=LINEA))
    s.append(texto(ox - 8, oy + alto / 2, f"{alto}", size=10, color=LINEA, anchor="end"))

    # leyenda
    ly = oy + alto + 30
    s.append(rect(ox, ly, 26, 16, fill=FIJO, stroke=FIJO, op=0.18))
    s.append(texto(ox + 34, ly + 12, "Impresión FIJA del proveedor (flexo, 1 tinta Negro 90): "
                   "igual para todas las referencias del formato", size=11, anchor="start"))
    s.append(rect(ox, ly + 26, 26, 16, fill=LOCAL, stroke=LOCAL, op=0.10, dash="6,3"))
    s.append(texto(ox + 34, ly + 38, "Zona de ROTULADO EN PLANTA (kraft limpio): marca, variedad, "
                   "color, destino, ITF-14, lote — se imprime según la necesidad", size=11, anchor="start"))
    s.append(texto(ox, ly + 70, "Esquema de zonas, no es arte final: las medidas exactas de cada zona "
                   "se ajustan con el proveedor y con la impresora elegida.", size=10, anchor="start",
                   color="#777"))
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    for codigo, datos in FORMATOS.items():
        (SALIDA / f"{codigo}.svg").write_text(plano(codigo, datos), encoding="utf-8")
        print("ok", codigo)
