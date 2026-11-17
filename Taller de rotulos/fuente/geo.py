"""Detección de la geometría del plano (caja desarmada) en una ficha."""
import subprocess, tempfile, glob, re
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def render(pdf, dpi, box=None):
    with tempfile.TemporaryDirectory() as t:
        a = ["pdftoppm", "-r", str(dpi), "-png", "-f", "1", "-l", "1"]
        if box:
            s = dpi / 72; x0, y0, x1, y1 = box
            a += ["-x", str(int(x0*s)), "-y", str(int(y0*s)), "-W", str(int((x1-x0)*s)), "-H", str(int((y1-y0)*s))]
        subprocess.run(a + [pdf, t + "/a"], check=True)
        return np.asarray(Image.open(glob.glob(t + "/a*.png")[0]).convert("RGB")).astype(np.int16)

def kraft_color(arr):
    px = arr.reshape(-1, 3)
    # descartar blancos/grises y tintas: kraft es amarillo-marrón claro
    r, g, b = px[:, 0], px[:, 1], px[:, 2]
    m = (r > 150) & (r < 235) & (g > 120) & (g < 210) & (b > 40) & (b < 150) & (r - b > 60)
    if m.sum() < 100: return None
    q = (px[m] // 6) * 6
    vals, cnt = np.unique(q, axis=0, return_counts=True)
    return vals[cnt.argmax()] + 3

def kraft_mask(arr, K, tol=26):
    return (np.abs(arr - K).max(axis=2) < tol)

def runs(row, minlen):
    """segmentos True de longitud >= minlen: lista (ini, fin)"""
    d = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
    ini = np.where(d == 1)[0]; fin = np.where(d == -1)[0]
    return [(a, b) for a, b in zip(ini, fin) if b - a >= minlen]

def plano_bbox(pdf):
    lo = render(pdf, 20)
    K = kraft_color(lo[int(lo.shape[0]*.15):int(lo.shape[0]*.75), :int(lo.shape[1]*.85)])
    m = kraft_mask(lo, K, 30)
    H, W = m.shape
    m[:int(H*.12)] = False; m[int(H*.75):] = False; m[:, int(W*.86):] = False
    m = ndi.binary_closing(m, iterations=2)
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    k = int(np.argmax(sizes)) + 1
    ys, xs = np.where(lab == k)
    s = 72 / 20
    return (xs.min()*s - 12, ys.min()*s - 12, (xs.max()+1)*s + 12, (ys.max()+1)*s + 12), K

def geometria(pdf, dpi=100, hojaW=None):
    box, _ = plano_bbox(pdf)
    arr = render(pdf, dpi, box)
    K = kraft_color(arr)
    km = kraft_mask(arr, K)
    filled = ndi.binary_fill_holes(ndi.binary_closing(km, iterations=3))
    # quedarse con la componente más grande (el plano)
    lab, n = ndi.label(filled); sizes = ndi.sum(filled, lab, range(1, n+1)); filled = lab == (int(np.argmax(sizes)) + 1)
    H, W = filled.shape
    ys, xs = np.where(filled)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    minlen = (x1 - x0) * 0.08
    cuenta = np.array([len(runs(filled[y, x0:x1], minlen)) if y0 <= y < y1 else 0 for y in range(H)])
    ancho = np.array([filled[y, x0:x1].sum() for y in range(H)])
    # filas de cuerpo: 1 segmento continuo y ancho casi total
    cuerpo = (cuenta == 1) & (ancho > (x1 - x0) * 0.9)
    yc = np.where(cuerpo)[0]
    by0, by1 = yc.min(), yc.max() + 1
    # aletas: filas con 4 segmentos
    fila_t = int(y0 + (by0 - y0) * 0.5); fila_b = int(by1 + (y1 - by1) * 0.5)
    seg_t = runs(filled[fila_t, :], minlen); seg_b = runs(filled[fila_b, :], minlen)
    cuerpo_seg = runs(filled[(by0 + by1)//2, :], minlen)[0]
    return dict(arr=arr, K=K, filled=filled, box=box, dpi=dpi, x0=x0, x1=x1, y0=y0, y1=y1, by0=by0, by1=by1,
                seg_t=seg_t, seg_b=seg_b, cuerpo=cuerpo_seg)
