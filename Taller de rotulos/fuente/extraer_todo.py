"""Extrae, de cada ficha, el rotulado real: cada elemento gráfico por cara, sin anotaciones técnicas.
Salida: <out>/elementos/*.png y <out>/catalogo.json"""
import sys, os, re, json, glob, subprocess, html, colorsys, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(__file__))
from geo import geometria, render, kraft_color, kraft_mask, runs, plano_bbox

C, OUT, FICHAS_JSON = sys.argv[1], sys.argv[2], sys.argv[3]
SOLO = set(sys.argv[4:])
os.makedirs(f"{OUT}/elementos", exist_ok=True)
fichas = {re.search(r"(6000\d{4})", os.path.basename(x["f"])).group(1) + ("_dup" if "(1)" in x["f"] else ""): x for x in json.load(open(FICHAS_JSON))}
DPI = 100

# ---------- metadatos de la ficha ----------
def texto_pag(pdf):
    return subprocess.run(["pdftotext", "-f", "1", "-l", "1", pdf, "-"], capture_output=True, text=True).stdout
def tam_pag(pdf):
    o = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", o); return [float(m.group(1)), float(m.group(2))]
def metadatos(pdf):
    t = texto_pag(pdf); flat = " | ".join(x.strip() for x in t.splitlines() if x.strip())
    g = lambda p: (re.search(p, flat).group(1).strip() if re.search(p, flat) else "")
    hojas = re.findall(r"\b(\d{3,4}) ?[xX] ?(\d{3,4})\b", flat)
    notas = re.findall(r"(CIERRE LICORER[^|]*|SIN CIERRE LICORER[^|]*|PRODUCTOS ASOCIADOS[^|]*|PROD\. ASOCIADOS[^|]*|KIT CON[^|]*)", flat)
    tintas = sorted(set(re.sub(r"\s+", " ", x) for x in re.findall(r"\b((?:AZUL|ROJO|VERDE|NEGRO|GRIS|CAFE|CAFÉ|MORADO|DORADO)\s?P?-?[A-Z]?\d{2,5}U?)\b", flat)))
    return dict(
        referencia=g(r"REFERENCIA \| ([^|]+)"), codigo=g(r"\b(CD\d{6,8})\b"),
        material=g(r"\b(C\s?\d{3}\s?[KB][FW]|B\s?\d{3}\s?K[FW])\b").replace(" ", ""),
        color_carton=g(r"\b(KRAFT|BLANCO)\b"), impresion=g(r"\b(\dC ?- ?\dC)\b").replace(" ", ""),
        hoja_neta=" x ".join(hojas[0]) if hojas else "", hoja_corrugar=" x ".join(hojas[1]) if len(hojas) > 1 else "",
        area=g(r"\b(\d[.,]\d{3,4})\b"), estilo=" / ".join(sorted(set(re.findall(r"(FLAP GAP|CASQUETE|REG 1 CIE SEC|REGULAR|TROQUELADA)", flat)))),
        pegue=g(r"(PEGUE (?:ADENTRO|AFUERA)|SIN PEGUE|GRAPA ADENTRO)"), atados=g(r"\b(\d+ ?(?:UNIDADES|UNDS?\.?|UN)\b)"),
        tintas=tintas, notas=sorted(set(n.strip() for n in notas))[:4], pagina=tam_pag(pdf),
        nit=g(r"\b(9\d{8})\b"), cliente=g(r"(FABRICA DE LICORES Y ALCOHOLES DE ANTIOQUIA|FABRICAJAS COMPANY S\.A\.S\.)"))

def palabras(pdf):
    o = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    res = []
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', o):
        res.append((float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), html.unescape(m.group(5))))
    return res

# ---------- tinta ----------
def hls(arr):
    a = np.clip(arr.astype(np.float32), 0, 255) / 255
    mx, mn = a.max(axis=2), a.min(axis=2); l = (mx + mn) / 2; d = mx - mn
    s = np.where(d == 0, 0, d / np.where(l > 0.5, 2 - mx - mn, mx + mn + 1e-6))
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.zeros_like(l)
    nz = d > 0
    rc = np.where(nz, (mx - r) / (d + 1e-6), 0); gc = np.where(nz, (mx - g) / (d + 1e-6), 0); bc = np.where(nz, (mx - b) / (d + 1e-6), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2 + rc - bc, 4 + gc - rc))
    h = (h / 6) % 1 * 360
    return h, l, s

TINTAS = {"Negro 90": (29, 29, 27), "Azul 39": (31, 102, 179), "Rojo 74": (226, 35, 26), "Verde 2081": (120, 181, 43),
          "Verde 29": (47, 154, 60), "Verde 2008": (60, 122, 58), "Morado P-2068U": (108, 42, 59), "Azul 30": (11, 79, 156),
          "Azul 31": (58, 109, 181), "Dorado": (185, 138, 46), "Café 52": (107, 68, 35), "Gris H1709": (138, 141, 143)}
def tinta_cercana(rgb):
    return min(TINTAS.items(), key=lambda kv: sum((a - b) ** 2 for a, b in zip(kv[1], rgb)))[0]

# ---------- firmas para unificar repetidos ----------
UNICOS = []   # (id, firma alpha 24x24, w, h, color, area)
def firma(alpha):
    im = Image.fromarray((np.nan_to_num(alpha) * 255).astype(np.uint8)).resize((40, 40), Image.BILINEAR)
    return np.asarray(im).astype(np.float32) / 255
def buscar_igual(sig, w, h, col):
    for (uid, s2, w2, h2, c2) in UNICOS:
        if abs(w - w2) > max(2.5, 0.05 * w) or abs(h - h2) > max(2.5, 0.05 * h): continue
        if sum((a - b) ** 2 for a, b in zip(col, c2)) ** 0.5 > 45: continue
        if np.abs(sig - s2).mean() < 0.06: return uid
    return None

# rótulos base hechos a mano, para nombrar coincidencias
BASE = {}
def cargar_base(dirb):
    meta = json.load(open(os.path.join(dirb, "meta.json")))
    nombres = {"logo_aguardiente_antioqueno": "Logo Aguardiente Antioqueño", "logo_antioqueno_antioqueno": "Logo Antioqueño Antioqueño",
        "marca_sin_azucar": "Marca Sin azúcar", "marca_24_sin_azucar": "Marca 24° Sin azúcar", "botella": "Botella de color",
        "sello_fla": "Sello Fábrica de Licores", "certificaciones": "Certificaciones y reciclaje", "estiba": "Estibado",
        "logo_doble_anis": "Logo Doble Anís", "franja_doble_anis": "Franja Doble Anís", "logo_ron_medellin_anejo": "Logo Ron Medellín Añejo",
        "anos_3": "3 años", "logo_licor_ron_medellin": "Logo Licor de Ron Medellín", "grado_29": "29°",
        "logo_ron_medellin_extra_anejo": "Logo Ron Medellín Extra Añejo", "anos_8": "8 años"}
    for k in meta:
        im = Image.open(os.path.join(dirb, k + ".png")).convert("RGBA")
        a = np.asarray(im.getchannel("A")).astype(np.float32) / 255
        BASE[k] = (firma(a), im.width / im.height, nombres.get(k, k))
def nombre_base(alpha, asp):
    mejor = None
    sig = firma(alpha)
    for k, (s2, a2, n) in BASE.items():
        if abs(asp - a2) / a2 > 0.12: continue
        d = np.abs(sig - s2).mean()
        if d < 0.085 and (mejor is None or d < mejor[0]): mejor = (d, n)
    return mejor[1] if mejor else None

PROV = re.compile(r"(DELICADO|FRAGIL|ESTE LADO ARRIBA|ESTIBA|ARRUME|TENDID|kg ?Aprox|UN\.? ?en vidrio|Unidades en vidrio|UNIDADES|Glass bottles|BOTTLES|IMPORTANTE|HALE LAS ALETAS|RECICL|ICONTEC|NTC|Sello Fábrica|Certificaciones|Estibado|UN ?/ ?BOTTLES|empacor|BASC|Peso Bruto)", re.I)
PLANTA_TXT = re.compile(r"(EXPORT|EXCESO|PROHIB|MODERACI|AÑEJAMIENTO|NATURAL|MENORES|DAÑINO)", re.I)

# ---------- proceso de una ficha ----------
def procesar(code, pdf, ficha, troquel):
    meta = metadatos(pdf)
    L, A, H = [int(v) for v in ficha["dims"].split("x")]
    hw, hh = sorted(int(v) for v in ficha["hoja"].split("x"))  # hh = mayor
    g = geometria(pdf, DPI)
    arr, K, filled = g["arr"].astype(np.float32), g["K"].astype(np.float32), g["filled"]
    box = g["box"]; ppt = DPI / 72
    if troquel:
        ys, xs = np.where(filled); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        ancho_px, alto_px = x1 - x0, y1 - y0
        dim_w, dim_h = (hw, hh) if alto_px > ancho_px else (hh, hw)
        esc = ancho_px / dim_w
        caras = {"p": (x0, y0, x1, y1)}
        geo = dict(troquel=True, W=round(ancho_px / esc), H=round(alto_px / esc))
    else:
        cs, ce = g["cuerpo"]; esc = (ce - cs) / hh
        t = g["seg_t"]
        izq = (t[0][0] - cs) > 15 * esc
        slots = [(t[i][1] + t[i + 1][0]) / 2 for i in range(3)]
        xb = ([cs + 30 * esc] if izq else [cs]) + slots + ([ce] if izq else [ce - 30 * esc])
        B = H + 10; F = (hw - B) / 2
        y0 = g["y0"]; yb = [y0, y0 + F * esc, y0 + (F + B) * esc, y0 + (2 * F + B) * esc]
        caras = {}
        for i in range(4):
            caras[f"t{i+1}"] = (xb[i], yb[0], xb[i + 1], yb[1]); caras[f"c{i+1}"] = (xb[i], yb[1], xb[i + 1], yb[2]); caras[f"b{i+1}"] = (xb[i], yb[2], xb[i + 1], yb[3])
        P = [round((xb[i + 1] - xb[i]) / esc) for i in range(4)]
        geo = dict(troquel=False, P=P, F=round(F), B=round(B), G=30, pegue="izq" if izq else "der")
    # tinta
    dist = np.sqrt(((arr - K) ** 2).sum(axis=2))
    alpha = np.clip((dist - 28) / 110, 0, 1)
    dentro = ndi.binary_erosion(filled, iterations=5)
    alpha[~dentro] = 0
    # clasificar cada píxel por la dirección de su color respecto al kraft
    CAND = np.array([
        (29, 29, 27), (138, 141, 143),                       # 0-1 neutros
        (7, 104, 175), (239, 62, 46), (215, 40, 50), (130, 190, 60), (60, 170, 70), (40, 120, 60),
        (110, 40, 60), (20, 80, 160), (60, 110, 180), (190, 150, 60), (110, 70, 40),   # 2-12 tintas
        (16, 135, 72), (227, 34, 133), (20, 130, 140), (0, 160, 225), (130, 50, 150),  # 13-17 anotaciones
    ], np.float32)
    dv = arr - K; nv = np.sqrt((dv ** 2).sum(axis=2)) + 1e-6
    dc = CAND - K; dc = dc / (np.sqrt((dc ** 2).sum(axis=1))[:, None] + 1e-6)
    cos = np.tensordot(dv / nv[..., None], dc.T, axes=1)
    mejor = cos.argmax(axis=2)
    anot = (mejor >= 13) & (alpha > 0)
    anot = ndi.binary_dilation(anot, iterations=1)
    alpha[anot] = 0
    if not troquel:  # líneas de doblez
        bw = 4
        for x in xb[1:4]: xi = int(round(x)); alpha[:, max(0, xi - bw):xi + bw] = 0
        xi = int(round(xb[0] if izq else xb[4])); alpha[:, max(0, xi - bw):xi + bw] = 0
        for y in yb[1:3]: yi = int(round(y)); alpha[max(0, yi - bw):yi + bw, :] = 0
    tinta = alpha > 0.3
    neutro = mejor <= 1
    capas = {"n": tinta & neutro, "c": tinta & ~neutro}
    pals = palabras(pdf)
    items = []
    rad = int(3.6 * esc)
    estr = np.ones((3, 3), bool)
    comps = []
    for capa, m in capas.items():
        dil = ndi.binary_dilation(m, structure=estr, iterations=rad)
        lab, n = ndi.label(dil)
        for k, sl in enumerate(ndi.find_objects(lab), 1):
            if sl is None: continue
            reg = (lab[sl] == k) & m[sl]
            ys, xs = np.where(reg)
            if len(ys) == 0: continue
            comps.append([capa, ys.min() + sl[0].start, ys.max() + 1 + sl[0].start, xs.min() + sl[1].start, xs.max() + 1 + sl[1].start])
    def cara_de(c):
        cx, cy = (c[3] + c[4]) / 2, (c[1] + c[2]) / 2
        return next((cid for cid, (a0, b0, a1, b1) in caras.items() if a0 <= cx < a1 and b0 <= cy < b1), None)
    # fusionar cajas de la misma capa que se solapan
    cambio = True
    while cambio:
        cambio = False
        i = 0
        while i < len(comps):
            j = i + 1
            while j < len(comps):
                a, b = comps[i], comps[j]
                if a[0] != b[0] or cara_de(a) != cara_de(b): j += 1; continue
                ix = min(a[4], b[4]) - max(a[3], b[3]); iy = min(a[2], b[2]) - max(a[1], b[1])
                solapa = ix > 0 and iy > 0 and ix * iy >= 0.3 * min((a[2]-a[1])*(a[4]-a[3]), (b[2]-b[1])*(b[4]-b[3]))
                ha, hb = a[2] - a[1], b[2] - b[1]
                vert = min(a[2], b[2]) - max(a[1], b[1])
                gap = max(a[3], b[3]) - min(a[4], b[4])
                linea = (vert > 0.6 * min(ha, hb) and gap < 0.75 * min(ha, hb) and min(ha, hb) > 6 * esc
                         and max(ha, hb) < 45 * esc and max(ha, hb) / max(1, min(ha, hb)) < 1.6)
                if solapa or linea:
                    comps[i] = [a[0], min(a[1], b[1]), max(a[2], b[2]), min(a[3], b[3]), max(a[4], b[4])]
                    comps.pop(j); cambio = True; continue
                j += 1
            i += 1
    for capa, by0, by1, bx0, bx1 in comps:
        m = capas[capa]
        reg = m[by0:by1, bx0:bx1]
        area_mm2 = reg.sum() / esc ** 2
        wmm, hmm = (bx1 - bx0) / esc, (by1 - by0) / esc
        if area_mm2 < 2.5 or (wmm < 2.5 and hmm < 2.5) or wmm < 1.6 or hmm < 1.6: continue
        col_rgb = arr[by0:by1, bx0:bx1][reg].mean(axis=0)
        if capa == "c" and (wmm < 6.5 and hmm < 6.5 or area_mm2 < 45): continue  # asteriscos y marcas de aletas
        if capa == "c" and max(wmm, hmm) < 30 and area_mm2 / max(1, wmm * hmm) < 0.35: continue  # asteriscos grandes
        if min(wmm, hmm) < 4 and max(wmm, hmm) / max(0.1, min(wmm, hmm)) > 20: continue  # restos de líneas
        if area_mm2 / max(1, wmm * hmm) < 0.035: continue  # cotas y líneas sueltas
        if wmm < 9 and hmm < 9 and area_mm2 < 25: continue  # números de panel y marcas pequeñas
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        cara = next((cid for cid, (a0, b0, a1, b1) in caras.items() if a0 <= cx < a1 and b0 <= cy < b1), None)
        if cara is None: continue
        fx0, fy0 = caras[cara][0], caras[cara][1]
        txt = []
        for (wx0, wy0, wx1, wy1, w) in pals:
            px = ((wx0 + wx1) / 2 - box[0]) * ppt; py = ((wy0 + wy1) / 2 - box[1]) * ppt
            if bx0 <= px <= bx1 and by0 <= py <= by1: txt.append((round(wy0 / 3), wx0, w))
        txt.sort(); texto = " ".join(w for _, _, w in txt).strip()
        toks = texto.split()
        if toks and all(re.fullmatch(r"[\d.,]*[”\"]?|cms?\.?|mm", t) for t in toks) and not re.search(r"\d{3}", texto) and wmm < 40: continue
        if texto and re.fullmatch(r"[*\s]+", texto): continue
        texto = re.sub(r"\s*\d?\.\d+\s*[”\"]\s*|\s*\d+\.?\d*\s*cms?\.?", " ", texto).strip()
        base = dict(cara=cara, x=round((bx0 - fx0) / esc, 1), y=round((by0 - fy0) / esc, 1), w=round(wmm, 1))
        mi = None
        if capa == "n" and wmm > 60 and wmm / hmm > 2.2:
            ext = []
            for (wx0, wy0, wx1, wy1, w) in pals:
                px = ((wx0 + wx1) / 2 - box[0]) * ppt; py = ((wy0 + wy1) / 2 - box[1]) * ppt
                if bx0 <= px <= bx1 and by0 <= py <= by1 + 10 * esc: ext.append((wx0, w))
            ext.sort(); mi = re.search(r"\b(\d)\s+(\d{2})\s+(\d{5})\s+(\d{5})\s+(\d)\b", " ".join(w for _, w in ext))
        if capa == "n" and mi and wmm > 60 and wmm / hmm > 2.2:
            items.append(dict(base, tipo="itf", codigo="".join(mi.groups())[:13], quien="planta")); continue
        reg_s = ndi.binary_dilation(reg, iterations=2)
        sub_a = alpha[by0:by1, bx0:bx1] * reg_s
        sub_c = arr[by0:by1, bx0:bx1]
        ua = np.maximum(sub_a, 0.02)[..., None]
        rgb = np.clip(K + (sub_c - K) / ua, 0, 255)
        rgba = np.dstack([rgb, sub_a * 255]).astype(np.uint8)
        asp = (bx1 - bx0) / (by1 - by0)
        items.append(dict(base, crudo=dict(rgba=rgba, sig=firma(sub_a), w=wmm, h=hmm, col=tuple(float(v) for v in col_rgb),
                                           texto=texto, nombre_b=nombre_base(sub_a, asp), capa=capa)))
    DEBUG[code] = dict(caras=caras, esc=esc, box=box)
    return dict(meta=meta, geo=geo, items=items, dims=[L, A, H])

ELEM = {}
DEBUG = {}
def fina(rgba, w, h):
    a = Image.fromarray(rgba[..., 3]).resize((max(4, round(w * 2)), max(4, round(h * 2))), Image.BILINEAR)
    return np.asarray(a).astype(np.float32) / 255
FINAS = {}
def buscar_igual2(sig, w, h, col, texto, fa=None):
    for (uid, s2, w2, h2, c2) in UNICOS:
        if abs(w - w2) > max(2.0, 0.04 * w) or abs(h - h2) > max(2.0, 0.04 * h): continue
        if sum((a - b) ** 2 for a, b in zip(col, c2)) ** 0.5 > 40: continue
        t2 = ELEM[uid]["texto"]
        if texto and t2 and texto != t2: continue
        if np.abs(sig - s2).mean() < 0.05:
            fb = FINAS.get(uid)
            if fa is not None and fb is not None:
                if fa.shape != fb.shape:
                    fb = np.asarray(Image.fromarray((fb * 255).astype(np.uint8)).resize(fa.shape[::-1], Image.BILINEAR)).astype(np.float32) / 255
                if (np.abs(fa - fb) > 0.5).mean() > 0.006: continue
            return uid
    return None

def trabajo(args):
    code, pdf, ficha, tipo, rel = args
    try:
        r = procesar(code, pdf, ficha, tipo in ("TIPO 14", "TIPO 15"))
        r.update(tipo=tipo, archivo=rel, activo="No activo" not in rel)
        return code, r, None
    except Exception as ex:
        return code, None, repr(ex)

if __name__ == "__main__":
    from multiprocessing import Pool
    cargar_base(os.environ.get("BASE_DIR"))
    REFS = {}
    pdfs = sorted(glob.glob(os.path.join(C, "*", "*.pdf")) + glob.glob(os.path.join(C, "*", "No activo", "*.pdf")))
    tareas = []
    for pdf in pdfs:
        rel = os.path.relpath(pdf, C)
        code = re.search(r"(6000\d{4})", os.path.basename(pdf)).group(1)
        if "(1)" in pdf or (SOLO and code not in SOLO): continue
        ficha = next((v for v in fichas.values() if v["f"] == rel), None)
        if not ficha or not ficha["dims"] or not ficha["hoja"]: print("sin datos", rel); continue
        tareas.append((code, pdf, ficha, rel.split("/")[0], rel))
    with Pool(int(os.environ.get("PROCS", "4"))) as pool:
        for code, r, err in pool.imap(trabajo, tareas):
            if err: print("ERROR", code, err, flush=True); continue
            for it in r["items"]:
                c = it.pop("crudo", None)
                if c is None: continue
                fa = fina(c["rgba"], c["w"], c["h"])
                uid = buscar_igual2(c["sig"], c["w"], c["h"], c["col"], c["texto"], fa)
                if uid is None:
                    uid = hashlib.sha1(c["rgba"].tobytes()).hexdigest()[:10]
                    im = Image.fromarray(c["rgba"], "RGBA")
                    if max(im.size) > 700: im.thumbnail((700, 700), Image.LANCZOS)
                    im.save(f"{OUT}/elementos/{uid}.png", optimize=True)
                    UNICOS.append((uid, c["sig"], c["w"], c["h"], c["col"])); FINAS[uid] = fa
                    ELEM[uid] = dict(w=round(c["w"], 1), h=round(c["h"], 1), texto=c["texto"][:120], base=c["nombre_b"],
                                     tinta=tinta_cercana(c["col"]), color="#%02x%02x%02x" % tuple(int(v) for v in c["col"]), capa=c["capa"], caras=[], refs=[])
                e = ELEM[uid]
                if not e["base"] and c["nombre_b"]: e["base"] = c["nombre_b"]
                e["refs"].append(code); e["caras"].append(it["cara"])
                it["el"] = uid
            REFS[code] = r
            print(code, r["tipo"], len(r["items"]), "elementos", r["geo"].get("P"), r["geo"].get("pegue"), flush=True)
    for uid, e in ELEM.items():
        e["n"] = len(set(e["refs"])); e["refs"] = sorted(set(e["refs"])); e["caras"] = sorted(set(e["caras"]))
    json.dump(dict(elementos=ELEM, referencias=REFS), open(f"{OUT}/catalogo.json", "w"), ensure_ascii=False)
    print("referencias", len(REFS), "elementos únicos", len(ELEM))
