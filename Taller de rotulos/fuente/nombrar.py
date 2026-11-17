"""Lee el texto de cada rótulo con OCR (español) y le da nombre y grupo (proveedor/planta)."""
import sys, os, re, json, subprocess, tempfile
from multiprocessing import Pool
from PIL import Image
OUT = sys.argv[1]
cat = json.load(open(f"{OUT}/catalogo.json"))
E = cat["elementos"]

def ocr_img(im):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: im.save(f.name)
    try:
        o = subprocess.run(["tesseract", f.name, "stdout", "-l", "spa", "--psm", "11", "tsv"], capture_output=True, text=True, timeout=40,
                           env={**os.environ, "OMP_THREAD_LIMIT": "1"}).stdout
    except Exception:
        o = ""
    finally: os.unlink(f.name)
    pal = []
    for ln in o.splitlines()[1:]:
        c = ln.split("\t")
        if len(c) == 12 and c[11].strip():
            try: conf = float(c[10])
            except: continue
            if conf >= 45: pal.append((int(c[7]) // 25, int(c[6]), c[11].strip(), conf))
    pal.sort()
    texto = " ".join(p[2] for p in pal)
    letras = sum(ch.isalpha() for ch in texto)
    punt = sum(p[3] * len(p[2]) for p in pal if len(re.sub(r"\W", "", p[2])) >= 2)
    return texto, letras, punt

def leer(uid):
    im = Image.open(f"{OUT}/elementos/{uid}.png").convert("RGBA")
    a = im.getchannel("A")
    g = Image.eval(a, lambda v: 255 - v)
    if g.height < 90: g = g.resize((round(g.width * 90 / g.height), 90), Image.LANCZOS)
    if g.width > 1600: g = g.resize((1600, round(g.height * 1600 / g.width)), Image.LANCZOS)
    lienzo = Image.new("L", (g.width + 40, g.height + 40), 255); lienzo.paste(g, (20, 20))
    mejor = ("", 0, -1)
    for rot in ([0, 180] + ([90, 270] if im.height > im.width * 1.6 else [])):
        r = ocr_img(lienzo.rotate(rot, expand=True, fillcolor=255) if rot else lienzo)
        if r[2] > mejor[2]: mejor = r
        if mejor[2] > 800: break
    return uid, mejor

import unicodedata, collections
def norm(w): return "".join(c for c in unicodedata.normalize("NFD", w.upper()) if unicodedata.category(c) != "Mn")
VOC = collections.defaultdict(collections.Counter)
for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ°]{3,}", open(os.environ.get("VOCAB", "/dev/null"), encoding="utf-8", errors="ignore").read()):
    VOC[norm(w)][w] += 1
for w in ["AGUARDIENTE","ANTIOQUEÑO","Antioqueño","Aguardiente","RON","MEDELLÍN","AÑEJO","EXTRA","AÑOS","años","SIN","AZÚCAR","DOBLE","ANÍS","LICOR","CREMA","DORADO","REAL","HERENCIA","VODKA","FRÁGIL","FRAGILE","DELICADO","BOTTLES","UNIDADES","Unidades","vidrio","Glass","bottles","EXPORT","EXPORTACIÓN","PARA","FOR","NATURAL","AÑEJAMIENTO","MULTICAPA","Envase","ENVASE","TRADICIONAL","GOLD","PINK","COPAS","ESTUCHE","VASO","MONTESSKAYA","ADICIONADO","IMPORTANTE","TOMAR","CAJA","DEBAJO","HALE","ALETAS"]:
    VOC[norm(w)][w] += 5
def limpiar_ocr(t):
    out = []
    for w in t.split():
        if re.fullmatch(r"[\d.,/°%x]+(ml|L|kg|m)?", w, re.I) and any(ch.isdigit() for ch in w): out.append(w); continue
        core = re.sub(r"[^A-Za-zÁÉÍÓÚÑáéíóúñ°]", "", w)
        if len(core) >= 3 and norm(core) in VOC: out.append(VOC[norm(core)].most_common(1)[0][0]); continue
        if w in ("/", "x", "y", "de", "DE", "LA", "EL", "A", "ml", "L", "&"): out.append(w)
    txt = " ".join(out)
    return txt if sum(len(re.sub(r"[^A-Za-zÁÉÍÓÚÑáéíóúñ]", "", w)) >= 3 for w in out) >= 1 else ""
def digito(c13):
    s = sum(int(c13[12 - i]) * (3 if i % 2 == 0 else 1) for i in range(13)); return (10 - s % 10) % 10
def itf_de(t):
    m = re.search(r"(\d)\s*(\d{2})\s*(\d{5})\s*(\d{5})\s*(\d)", t)
    if not m: return None
    c = "".join(m.groups())
    for cand in (c, "1" + c[1:], c[0] + "77" + c[3:] if c[1:3] != "06" else c):
        if digito(cand[:13]) == int(cand[13]): return cand[:13]
    return c[:13]

PROV = re.compile(r"(Cantidad:|\bARRIBA\b|\bAPROX|DELICADO|FR[AÁ]GIL|LADO ARRIBA|ESTIBA|ARRUME|TENDID|kg\b|Aprox|vidrio|UNIDADES|Unidades|Glass|BOTTLES|IMPORTANTE|HALE|ALETAS|RECICL|ICONTEC|NTC|Sello F|Certificaci|Estibado|empacor|BASC|Peso|ml\b|\bL\b|cajas)", re.I)
PLANTA = re.compile(r"(EXPORT|EXCESO|PROHIB|MODERACI|AÑEJAMIENTO|NATURAL|MENORES|DAÑINO|SALUD|Aguardiente|Antioque|Medell|RON\b|Ron\b|Doble|An[ií]s|Az[uú]car|Licor|Crema|Vodka|Real|Herencia|años|AÑOS|Tradicional)", re.I)

if __name__ == "__main__":
    cache_f = f"{OUT}/ocr_cache.json"
    res = json.load(open(cache_f)) if os.path.exists(cache_f) else {}
    pend = [u for u in E if u not in res]
    with Pool(4) as p:
        for k, (uid, r) in enumerate(p.imap_unordered(leer, pend, chunksize=4)):
            res[uid] = r
            if k % 100 == 0:
                json.dump(res, open(cache_f, "w")); print("ocr", len(res), "/", len(E), flush=True)
    json.dump(res, open(cache_f, "w"))
    for uid, e in E.items():
        texto_ocr, letras, punt = res[uid]
        crudo = re.sub(r"\s+", " ", texto_ocr).strip()
        if e["capa"] == "n" and e["w"] > 90 and e["w"] / max(1, e["h"]) > 2.2:
            cod = itf_de(crudo) or itf_de(e.get("texto", ""))
            if cod: e["itf"] = cod
        limpio = limpiar_ocr(crudo)
        mc = re.fullmatch(r"\s*(6|12|20|24|30)\s*", crudo)
        if mc and e["h"] >= 12 and e["capa"] == "n": limpio = f"Cantidad: {mc.group(1)}"
        e["ocr"] = limpio[:160]
        pdf_t = e.get("texto", "")
        if e.get("base"): nombre = e["base"]
        elif pdf_t and len(re.sub(r"\W", "", pdf_t)) >= 3: nombre = pdf_t
        elif limpio: nombre = limpio
        else:
            ancho = e["w"]
            nombre = ("Logo / gráfico " if ancho > 60 else "Gráfico ") + e["tinta"]
        nombre = nombre.strip()
        e["nombre"] = nombre[:52] + ("…" if len(nombre) > 52 else "")
        s = " ".join([e.get("base") or "", pdf_t, limpio])
        if PROV.search(s) and not re.search(r"EXPORT|EXCESO|PROHIB|MODERACI", s, re.I): g = "proveedor"
        elif PLANTA.search(s) or e["capa"] == "c": g = "planta"
        elif all(c.startswith("b") for c in e["caras"]): g = "proveedor"
        else: g = "planta"
        e["grupo"] = g
    # números de panel y cotas sueltas
    quitar = {u for u, e in E.items() if e["h"] < 15 and e["w"] < 45 and re.fullmatch(r"[\d\s.,]{1,4}", (e.get("texto") or e.get("ocr") or "x").strip() or "x")}
    for r in cat["referencias"].values(): r["items"] = [it for it in r["items"] if it.get("el") not in quitar]
    for u in quitar: E.pop(u)
    print("cotas y números quitados:", len(quitar))
    # marcas rojas sin texto en aletas inferiores (asteriscos de anotación)
    marca = {u for u, e in E.items() if e["tinta"].startswith("Rojo") and not e.get("ocr") and not e.get("texto") and e["w"] < 60 and e["h"] < 40}
    n0 = sum(len(r["items"]) for r in cat["referencias"].values())
    for r in cat["referencias"].values(): r["items"] = [it for it in r["items"] if not (it.get("el") in marca and it["cara"].startswith("b"))]
    usados = {it.get("el") for r in cat["referencias"].values() for it in r["items"]}
    for u in [u for u in E if u not in usados]: E.pop(u)
    print("marcas rojas quitadas:", n0 - sum(len(r["items"]) for r in cat["referencias"].values()))
    # códigos de barras -> ITF-14 editable
    itf = {u: e["itf"] for u, e in E.items() if e.get("itf")}
    for r in cat["referencias"].values():
        nuevos = []
        for it in r["items"]:
            if it.get("el") in itf:
                nuevos.append(dict(cara=it["cara"], x=it["x"], y=it["y"], w=it["w"], tipo="itf", codigo=itf[it["el"]], quien="planta"))
            else: nuevos.append(it)
        r["items"] = nuevos
    for u in itf: E.pop(u)
    print("códigos ITF convertidos:", len(itf))
    json.dump(cat, open(f"{OUT}/catalogo.json", "w"), ensure_ascii=False)
    con = sum(1 for e in E.values() if not e["nombre"].startswith(("Gráfico", "Logo / gráfico")))
    print("elementos", len(E), "con nombre legible", con, "proveedor", sum(e["grupo"] == "proveedor" for e in E.values()))
