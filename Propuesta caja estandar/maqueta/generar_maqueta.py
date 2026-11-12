"""Maqueta caja estándar x12 Antioqueño: NEGRO = lo imprime el proveedor, ROJO = lo imprimimos en planta.

Toma el arte real de la ficha 60002609 (CAJA x12 AGTE SIN AZ GENE EXP 750 KIT),
la rasteriza y reclasifica cada elemento gráfico:
  - FIJO (negro): común a las 8 cajas x12 (sellos, 12 unidades/750 ml, frágil, estibado,
    certificaciones, peso).
  - VARIABLE (rojo): cambia entre las 8 referencias (marca/variedad, color de la botella,
    destino, frases legales según mercado, ITF-14, guía de color).
Las anotaciones técnicas del proveedor (cotas, "Detalle A/B", asteriscos) no se imprimen y se omiten.

Uso:  python3 generar_maqueta.py   (requiere pdftoppm y Pillow)
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
PDF = next((AQUI.parent.parent / "Listado cajas").glob("60002609*.pdf"))
KRAFT = (212, 180, 105)
NEGRO, ROJO = (25, 25, 25), (210, 30, 30)
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FUENTE_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Rectángulos (x0, y0, x1, y1) en px del recorte a 72 dpi, escala 1/3 (se multiplican por 3).
FIJOS = {
    "Sello FLA (aleta sup. cara 1)": (162, 35, 245, 105),
    "DELICADO / FRAGILE": (250, 35, 370, 105),
    "Esquema de estibado 1,20 x 1,00": (730, 30, 910, 110),
    "12 UN. en vidrio / Glass bottles 750 ml (cara 1)": (228, 145, 390, 230),
    "12 UN. en vidrio / Glass bottles 750 ml (cara 2)": (440, 145, 600, 215),
    "Sello FLA (cara 2)": (478, 228, 558, 292),
    "12 UN. en vidrio / Glass bottles 750 ml (cara 3)": (833, 145, 995, 230),
    "12 UN. en vidrio / Glass bottles 750 ml (cara 4)": (1045, 145, 1205, 215),
    "Sello FLA (cara 4)": (1082, 228, 1162, 292),
    "Certificaciones y reciclaje (aleta inf. cara 1)": (85, 355, 330, 415),
    "Peso aprox. de la caja (aleta inf. cara 3)": (730, 375, 910, 412),
}
VARIABLES = {
    "Logo marca + variedad (aleta sup. cara 1)": (55, 36, 160, 108),
    "Botella con color de la variedad (cara 1)": (48, 133, 76, 191),
    "Logo marca + variedad grande (cara 1)": (42, 160, 228, 319),
    "Destino: PARA EXPORTACIÓN / FOR EXPORT (cara 1)": (236, 237, 386, 258),
    "Código ITF-14 de la referencia (cara 1)": (232, 260, 388, 318),
    "Botella con color de la variedad (cara 2)": (414, 133, 443, 191),
    "Frases legales según mercado (cara 2)": (438, 290, 605, 317),
    "Botella con color de la variedad (cara 3)": (652, 133, 681, 191),
    "Logo marca + variedad grande (cara 3)": (647, 160, 833, 319),
    "Destino: PARA EXPORTACIÓN / FOR EXPORT (cara 3)": (840, 237, 991, 258),
    "Código ITF-14 de la referencia (cara 3)": (838, 260, 992, 318),
    "Guía-señal de color de la variedad": (993, 265, 1013, 305),
    "Botella con color de la variedad (cara 4)": (1020, 133, 1051, 191),
    "Frases legales según mercado (cara 4)": (1035, 290, 1205, 317),
}

# Geometría de la caja desplegada (px del recorte, 1 mm ≈ 2,82 px)
TOP, CUERPO_Y0, CUERPO_Y1, BOT = 33, 377, 1000, 1344
ALETAS = [(106, 1182), (1209, 1891), (1921, 2998), (3026, 3715)]
CARAS = [(100, 1195), (1195, 1906), (1906, 3011), (3011, 3715)]


def rasterizar():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "base"
        subprocess.run(["pdftoppm", "-r", "72", "-png", "-f", "1", "-l", "1", "-x", "430", "-y", "850",
                        "-W", "3880", "-H", "1400", str(PDF), str(base)], check=True)
        return Image.open(f"{base}-1.png").convert("RGB")


def alfa_tinta(c):
    """Intensidad de tinta impresa (0..1); 0 para fondo y anotaciones técnicas."""
    r, g, b = c
    if r > 150 and r - g > 60:          # rojos/rosados: cotas y asteriscos de la ficha
        return 0.0
    if g > r + 10 and g >= b:           # verdes/turquesa: "Detalle A/B" y notas
        return 0.0
    d = ((r - KRAFT[0]) ** 2 + (g - KRAFT[1]) ** 2 + (b - KRAFT[2]) ** 2) ** 0.5
    return max(0.0, min(1.0, (d - 25) / 140))


def caja_base(w, h):
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    borde = (90, 70, 40)
    d.polygon([(100, CUERPO_Y0 + 20), (12, CUERPO_Y0 + 45), (12, CUERPO_Y1 - 45), (100, CUERPO_Y1 - 20)],
              fill=KRAFT, outline=borde, width=3)
    for x0, x1 in ALETAS:
        d.rectangle([x0, TOP, x1, CUERPO_Y0], fill=KRAFT, outline=borde, width=3)
        d.rectangle([x0, CUERPO_Y1, x1, BOT], fill=KRAFT, outline=borde, width=3)
    for x0, x1 in CARAS:
        d.rectangle([x0, CUERPO_Y0, x1, CUERPO_Y1], fill=KRAFT, outline=borde, width=3)
    for y in (CUERPO_Y0, CUERPO_Y1):    # líneas de doblez punteadas
        for x in range(100, 3715, 24):
            d.line([(x, y), (x + 12, y)], fill=(120, 95, 55), width=3)
    return im


def pintar(destino, original, rects, color):
    po, pd = original.load(), destino.load()
    for (x0, y0, x1, y1) in rects.values():
        for y in range(y0 * 3, y1 * 3):
            for x in range(x0 * 3, x1 * 3):
                a = alfa_tinta(po[x, y])
                if a > 0:
                    k = pd[x, y]
                    pd[x, y] = tuple(int(k[i] * (1 - a) + color[i] * a) for i in range(3))


def rotular_caras(im):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FUENTE_B, 26)
    for i, (x0, x1) in enumerate(CARAS, 1):
        d.text(((x0 + x1) / 2, CUERPO_Y1 - 22), f"CARA {i}", font=f, fill=(120, 95, 55), anchor="mm")


def hoja(vistas, ancho=2200):
    f_t = ImageFont.truetype(FUENTE_B, 40)
    f_s = ImageFont.truetype(FUENTE, 24)
    f_v = ImageFont.truetype(FUENTE_B, 30)
    esc = (ancho - 80) / vistas[0][1].width
    alto_v = int(vistas[0][1].height * esc)
    H = 210 + len(vistas) * (alto_v + 80) + 40
    out = Image.new("RGB", (ancho, H), "white")
    d = ImageDraw.Draw(out)
    d.text((40, 30), "Caja estándar x12 Aguardiente Antioqueño 750 · CE-12-ANT", font=f_t, fill=(20, 20, 20))
    d.text((40, 88), "Base: arte real de la ficha 60002609 (384 x 245 x 210 mm int., hoja 464 x 1308, C620KF kraft). "
                     "Aplica a las 8 referencias x12.", font=f_s, fill=(70, 70, 70))
    d.rectangle([40, 140, 70, 170], fill=NEGRO)
    d.text((82, 142), "NEGRO = lo imprime el proveedor (fijo, igual para las 8)", font=f_s, fill=NEGRO)
    d.rectangle([900, 140, 930, 170], fill=ROJO)
    d.text((942, 142), "ROJO = lo imprimimos en planta (cambia según la referencia)", font=f_s, fill=ROJO)
    y = 210
    for titulo, im in vistas:
        d.text((40, y), titulo, font=f_v, fill=(30, 30, 30))
        out.paste(im.resize((ancho - 80, alto_v), Image.LANCZOS), (40, y + 50))
        y += alto_v + 80
    return out


if __name__ == "__main__":
    orig = rasterizar()
    W, H = orig.size

    proveedor = caja_base(W, H); pintar(proveedor, orig, FIJOS, NEGRO); rotular_caras(proveedor)
    planta = caja_base(W, H); pintar(planta, orig, VARIABLES, ROJO); rotular_caras(planta)
    final = caja_base(W, H); pintar(final, orig, FIJOS, NEGRO); pintar(final, orig, VARIABLES, ROJO)
    rotular_caras(final)

    final.save(AQUI / "CE-12-ANT_final_negro_rojo.png")
    proveedor.save(AQUI / "CE-12-ANT_1_como_llega_del_proveedor.png")
    planta.save(AQUI / "CE-12-ANT_2_lo_que_imprimimos.png")
    lamina = hoja([("1. Como llega del proveedor (solo negro)", proveedor),
                   ("2. Lo que imprimimos en planta (solo rojo)", planta),
                   ("3. Caja terminada (negro + rojo)", final)])
    lamina.save(AQUI / "CE-12-ANT_comparativo.png")
    lamina.save(AQUI / "CE-12-ANT_comparativo.pdf", resolution=150)
    print("listo")
