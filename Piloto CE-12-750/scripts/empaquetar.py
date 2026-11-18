"""Comprime las fichas y planos generados por piloto_gen.js y los ordena en las carpetas del piloto.
Uso: python3 empaquetar.py <carpeta de salida de piloto_gen.js> <disenos_piloto.json> <carpeta del piloto>"""
import json, os, subprocess, sys, tempfile
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src, dis, dst = sys.argv[1:4]
D = json.load(open(dis, encoding="utf-8"))
c1, c2 = f"{dst}/1 Caja neutra (proveedor)", f"{dst}/2 Rotulado de planta por referencia"
os.makedirs(c1, exist_ok=True); os.makedirs(c2, exist_ok=True)
tmp = tempfile.mkdtemp()

def pdf(a, b, ancho=3800, q=82):
    info = subprocess.run(["pdfinfo", a], capture_output=True, text=True).stdout
    w_pt = float([l for l in info.splitlines() if l.startswith("Page size")][0].split()[2]); dpi = ancho / w_pt * 72
    subprocess.run(["pdftoppm", "-r", f"{dpi:.2f}", "-jpeg", "-jpegopt", f"quality={q}", "-singlefile", a, f"{tmp}/pg"], check=True)
    Image.open(f"{tmp}/pg.jpg").convert("RGB").save(b, "PDF", resolution=dpi, quality=q)

def png(a, b, ancho=2700):
    im = Image.open(a).convert("RGB"); im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(b, optimize=True)

for d in D["disenos"]:
    i = d["id"]
    if i.startswith("neutra"):
        base = f"{c1}/CE-12-750-{i[-1]}"
        pdf(f"{src}/{i}.pdf", f"{base} ficha.pdf"); png(f"{src}/{i}_tintas.png", f"{base} plano.png")
        Image.open(f"{src}/{i}_3d.png").save(f"{base} 3D.png", optimize=True)
    else:
        code = i[4:]; base = f"{c2}/{code} {D['refs'][code]['desc'].replace('°', '').replace('/', '-')}"
        pdf(f"{src}/{i}.pdf", f"{base} - ficha.pdf")
        png(f"{src}/{i}_quien-imprime.png", f"{base} - quien imprime.png"); png(f"{src}/{i}_solo-planta.png", f"{base} - solo planta.png")
print("listo")
