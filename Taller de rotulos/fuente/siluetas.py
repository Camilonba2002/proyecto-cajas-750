import sys, os, glob
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(__file__))
from geo import geometria
C, OUT = sys.argv[1], sys.argv[2]
for tipo, code in [("TIPO 14", "60002073"), ("TIPO 15", "60002077")]:
    pdf = sorted(glob.glob(os.path.join(C, tipo, code + "*.pdf")))[0]
    g = geometria(pdf, 100); f = g["filled"]
    ys, xs = np.where(f); f = f[ys.min():ys.max()+1, xs.min():xs.max()+1]
    borde = f & ~ndi.binary_erosion(f, iterations=3)
    rgba = np.zeros(f.shape + (4,), np.uint8)
    rgba[f] = (212, 175, 109, 255); rgba[borde] = (125, 95, 42, 255)
    im = Image.fromarray(rgba, "RGBA"); im.thumbnail((1400, 1400), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True); im.save(os.path.join(OUT, f"silueta_{tipo.replace(' ', '_')}.png"), optimize=True)
    print(tipo, im.size)
