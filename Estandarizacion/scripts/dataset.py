import json, re, subprocess, glob, os, sys
import openpyxl
C = "/home/user/proyecto-cajas-750/Cajas tipos"
fichas = json.load(open(sys.argv[1])); cat = json.load(open(sys.argv[2])); ocr = json.load(open(sys.argv[3]))
ws = openpyxl.load_workbook(os.path.join(C, "Cajas tipos.xlsx")).active
xl = {}; tipo = None
for r in ws.iter_rows(min_row=2):
    if r[0].value: tipo = r[0].value.strip()
    col = r[1].fill.fgColor.rgb if r[1].fill.fill_type else None
    xl[str(r[1].value)] = dict(tipo=tipo, desc=(r[2].value or "").strip(), estado={"FFFFC000": "no activo", "FFFF0000": "no existe"}.get(col, "activo"))
def grid(pdf, n):
    t = subprocess.run(["pdftotext", "-f", "2", "-l", "2", pdf, "-"], capture_output=True, text=True).stdout
    xs = [int(v) for v in re.findall(r"^x(\d{1,2})$", t, re.M)][:2]
    if len(xs) == 2 and (xs[0] + 1) * (xs[1] + 1) == n: return sorted([xs[0] + 1, xs[1] + 1], reverse=True)
    return None
def factores(n, L, A):
    best = None
    for c in range(1, n + 1):
        if n % c: continue
        r = n // c
        if c < r: continue
        cl, ca = L / c, A / r
        s = abs(cl / ca - 1.0)
        if best is None or s < best[0]: best = (s, [c, r])
    return best[1]
filas = []
for f in fichas:
    m = re.search(r"(6000\d{4})", f["f"].split("/")[-1]); code = m.group(1)
    if "(1)" in f["f"]: continue
    x = xl.get(code, {}); d = x.get("desc", "") or f["ref"]
    if not f["dims"]: continue
    L, A, H = [int(v) for v in f["dims"].split("x")]
    n = int(re.search(r"X ?(\d+)", d.upper()).group(1)) if re.search(r"X ?(\d+)", d.upper()) else None
    vol = re.search(r"\b(260|330|375|700|750|1\.?000|1050|1\.?050|1750|2\.?000)\b", d.replace(".", ""))
    vol = int(vol.group(1).replace(".", "")) if vol else None
    D = d.upper()
    prod = "Ron" if "RON" in D and "LICOR" not in D and "CREMA" not in D else "Licor de ron" if "LICOR" in D or "CREMA" in D else "Doble Anís" if "DOBLE ANIS" in D else "Vodka" if "VODKA" in D else "Aguardiente"
    mercado = "USA" if "USA" in D else "Europa" if "EUROP" in D else "Chile" if "CHILE" in D else "Perú" if "PERU" in D else "Exportación" if ("EXP" in D or "GENE" in D) else "Nacional"
    envase = "Tetra" if "TETRA" in D else "PET" if "PET" in D else "Vidrio"
    pdf = os.path.join(C, f["f"])
    g = grid(pdf, n) if n else None
    if not g and n: g = factores(n, L, A)
    ref = cat["referencias"].get(code, {})
    meta = ref.get("meta", {})
    filas.append(dict(code=code, tipo=f["f"].split("/")[0], activo="No activo" not in f["f"] and x.get("estado") != "no activo", desc=d, n=n, vol=vol, producto=prod, mercado=mercado,
                      envase=envase, L=L, A=A, H=H, hoja=f["hoja"], carton=f["mat"] or meta.get("material", ""), cierre=f["cierre"], area=meta.get("area", ""),
                      grid=g, celda=[round(L / g[0], 1), round(A / g[1], 1)] if g else None, paginas=f["pag"]))
json.dump(filas, open(sys.argv[4], "w"), ensure_ascii=False, indent=0)
print(len(filas), "referencias")
