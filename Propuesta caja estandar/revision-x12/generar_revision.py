"""Comparativo elemento por elemento de las 8 cajas x12 de Aguardiente Antioqueño.

Extrae el plano (página 1) de cada ficha, lo lleva a la misma escala (1308 x 464 mm)
y arma una lámina por zona de la caja con las 8 referencias lado a lado.
Uso:  python3 generar_revision.py   (requiere pdftoppm y Pillow)
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FICHAS = AQUI.parent.parent / "Listado cajas"
CODIGOS = {"60002594": "Sin azúcar USA", "60002595": "Tradicional USA", "60002597": "24° USA",
           "60002600": "Sin azúcar Chile", "60002608": "Tradicional Gene Exp",
           "60002609": "Sin azúcar Gene Exp", "60002652": "24° Gene Exp", "60002904": "Antio Antio 24° Exp"}
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MM = 3000 / 1308  # px por mm en el plano normalizado
ZONAS = {  # (x0, y0, x1, y1) en mm sobre la hoja neta 1308 x 464
    "01_aleta_superior_cara1": (30, 0, 418, 122),
    "02_aleta_superior_cara3": (669, 0, 1059, 122),
    "03_cara1_principal": (30, 122, 418, 342),
    "04_cara2_lateral": (418, 122, 669, 342),
    "05_aleta_inferior_cara1": (30, 342, 418, 464),
    "06_aleta_inferior_cara2": (418, 342, 669, 464),
    "07_aleta_inferior_cara3": (669, 342, 1059, 464),
}


def render(pdf, dpi, tmp, nombre, recorte=None):
    args = ["pdftoppm", "-r", str(dpi), "-png", "-f", "1", "-l", "1"]
    if recorte:
        x, y, w, h = recorte
        args += ["-x", str(x), "-y", str(y), "-W", str(w), "-H", str(h)]
    subprocess.run(args + [str(pdf), str(tmp / nombre)], check=True)
    return Image.open(tmp / f"{nombre}-1.png").convert("RGB")


def caja_kraft(im, desde_y=0.20, hasta_y=0.72, hasta_x=0.86):
    W, H = im.size
    K = max(im.getcolors(W * H), key=lambda t: t[0] if t[1] != (255, 255, 255) else 0)[1]
    es = lambda c: all(abs(c[i] - K[i]) < 22 for i in range(3))
    px = im.load()
    y0, y1, x1 = int(H * desde_y), int(H * hasta_y), int(W * hasta_x)
    cols = [sum(es(px[x, y]) for y in range(y0, y1, 2)) for x in range(x1)]
    filas = [sum(es(px[x, y]) for x in range(0, x1, 2)) for y in range(H)]
    xs = [x for x, v in enumerate(cols) if v > 0.25 * (y1 - y0) / 2]
    ys = [y for y, v in enumerate(filas) if v > 0.25 * x1 / 2]
    return xs[0], ys[0], xs[-1], ys[-1]


def plano(codigo, tmp):
    pdf = next(FICHAS.glob(codigo + "*.pdf"))
    lo = render(pdf, 20, tmp, codigo + "_lo")
    x0, y0, x1, y1 = caja_kraft(lo)
    s = 72 / 20
    X0, Y0, X1, Y1 = int(x0 * s) - 8, int(y0 * s) - 8, int(x1 * s) + 8, int(y1 * s) + 8
    im = render(pdf, 72, tmp, codigo, (X0, Y0, X1 - X0, Y1 - Y0))
    a, b, c, d = caja_kraft(im, 0, 1, 1)
    return im.crop((a, b, c, d)).resize((3000, 1064), Image.LANCZOS)


if __name__ == "__main__":
    f = ImageFont.truetype(FUENTE, 22)
    with tempfile.TemporaryDirectory() as t:
        planos = {c: plano(c, Path(t)) for c in CODIGOS}
    laminas = []
    for zona, (a, b, c, d) in ZONAS.items():
        recortes = [planos[k].crop((int(a * MM), int(b * MM), int(c * MM), int(d * MM))) for k in CODIGOS]
        w, h = recortes[0].size
        n = 2 if w > 700 else 4
        out = Image.new("RGB", (n * (w + 10), ((8 + n - 1) // n) * (h + 36)), "white")
        dr = ImageDraw.Draw(out)
        for i, (k, r) in enumerate(zip(CODIGOS, recortes)):
            x, y = (i % n) * (w + 10), (i // n) * (h + 36)
            dr.text((x + 4, y + 5), f"{k} · {CODIGOS[k]}", font=f, fill="black")
            out.paste(r, (x, y + 32))
        out.save(AQUI / f"{zona}.png")
        laminas.append(out)
    laminas[0].save(AQUI / "comparativo_8_cajas_x12.pdf", save_all=True, append_images=laminas[1:],
                    resolution=110)
    print("listo")
