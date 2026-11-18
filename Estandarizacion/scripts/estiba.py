import json, re, sys, functools
datos = json.load(open(sys.argv[1])); cat = json.load(open(sys.argv[2])); ocr = json.load(open(sys.argv[3]))
E = cat["elementos"]
# ---- valores de estiba de las fichas (OCR de la tabla) ----
real = {}
for code, r in cat["referencias"].items():
    for it in r["items"]:
        e = E.get(it.get("el"))
        if not e or not e["nombre"].upper().startswith("ESTIBA"): continue
        t = ocr.get(it["el"], ["", 0, 0])[0]
        m1 = re.search(r"(\d{1,2})\s*CAJAS", t, re.I); m2 = re.search(r"(\d{1,2})\s*TEND", t, re.I)
        if m1 or m2: real[code] = (int(m1.group(1)) if m1 else None, int(m2.group(1)) if m2 else None)
# ---- mejor patrón guillotina en estiba 1200x1000 (paso 5 mm) ----
def mejor(PL, PW, a, b, paso=5):
    a, b = a / paso, b / paso; W, H = PL // paso, PW // paso
    @functools.lru_cache(maxsize=None)
    def f(w, h):
        best = 0
        if w >= a and h >= b: best = max(best, int(w // a) * int(h // b))
        if w >= b and h >= a: best = max(best, int(w // b) * int(h // a))
        for x in set(int(i * a + j * b) for i in range(int(w // a) + 1) for j in range(int(w // b) + 1) if 0 < i * a + j * b < w):
            best = max(best, f(x, h) + f(w - x, h))
        for y in set(int(i * a + j * b) for i in range(int(h // a) + 1) for j in range(int(h // b) + 1) if 0 < i * a + j * b < h):
            best = max(best, f(w, y) + f(w, h - y))
        return best
    return f(int(W), int(H))
res = []
for r in datos:
    if not r["activo"] or r["tipo"] in ("TIPO 14", "TIPO 15"): continue
    oL, oA, oH = r["L"] + 8, r["A"] + 8, r["H"] + 15
    capa = mejor(1200, 1000, oL, oA)
    tend = 1355 // oH
    res.append(dict(code=r["code"], tipo=r["tipo"], n=r["n"], ext=[oL, oA, oH], capa=capa, tendidos=tend, real=real.get(r["code"]),
                    uso=round(capa * oL * oA / 1.2e6 * 100), botellas=capa * tend * (r["n"] or 0)))
json.dump(res, open(sys.argv[4], "w"), ensure_ascii=False)
vistos = set()
for x in sorted(res, key=lambda z: z["tipo"]):
    if x["tipo"] in vistos: continue
    vistos.add(x["tipo"]); reales = sorted(set(str(y["real"]) for y in res if y["tipo"] == x["tipo"] and y["real"]))
    print(f'{x["tipo"]:8} ext {x["ext"]} capa calc {x["capa"]:>2} ({x["uso"]}% área) tendidos {x["tendidos"]} → {x["botellas"]} bot/estiba | fichas (cajas x tendido, tendidos): {", ".join(reales)}')
