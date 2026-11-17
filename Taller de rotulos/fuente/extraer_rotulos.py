import sys, subprocess, tempfile, glob, os, colorsys, json, base64, io
from PIL import Image
C = sys.argv[1]; OUT = sys.argv[2]
def pdf(code): return glob.glob(os.path.join(C, "*", code + "*.pdf"))[0]
# id, código, caja pt (x0,y0,x1,y1), modo, filtro, ancho final
# modo: "mono" (alpha, se recolorea) | "color" (conserva colores)
# filtro: "negro" solo tinta neutra | "color" solo tinta saturada | "todo"
OPT = {
 "marca_sin_azucar": dict(umbral=110),
 "marca_24_sin_azucar": dict(bg=(255,255,255)),
 "grado_29": dict(bg=(255,255,255)), "estiba": dict(bg=(255,255,255)),
 "logo_doble_anis": dict(hue="purple", bg=(255,255,255)), "franja_doble_anis": dict(hue="purple"),
 "anos_8": dict(hue="red"), "logo_ron_medellin_extra_anejo": dict(hue="none", bg=(255,255,255)),
 "logo_antioqueno_antioqueno": dict(fill=121, bg=(255,255,255)),
 "logo_aguardiente_antioqueno": dict(bg=(255,255,255)), "sello_fla": dict(bg=(255,255,255)),
 "logo_ron_medellin_anejo": dict(bg=(255,255,255)), "anos_3": dict(bg=(255,255,255)),
 "logo_licor_ron_medellin": dict(bg=(255,255,255)),
}
R = [
 ("logo_aguardiente_antioqueno", "60002595", (2704, 2592, 3448, 3168), "mono", "negro", 700),
 ("logo_antioqueno_antioqueno", "60002904", (192, 2652, 1000, 3288), "mono", "negro", 700),
 ("marca_sin_azucar",            "60002594", (1060, 1590, 1350, 1775), "mono", "color", 360),
 ("marca_24_sin_azucar",         "60002597", (3070, 2900, 3350, 3170), "mono", "color", 360),
 ("botella",                     "60002609", (2236, 2484, 2324, 2652), "mono", "todo", 120),
 ("sello_fla",                   "60002595", (852, 2780, 1288, 3128), "mono", "negro", 400),
 ("certificaciones",             "60002609", (650, 1946, 1400, 2090), "mono", "negro", 900),
 ("estiba",                      "60002609", (860, 2350, 1250, 2712), "mono", "negro", 360),
 ("logo_doble_anis",             "60002463", (640, 2740, 1820, 3860), "color", "todo", 600),
 ("franja_doble_anis",           "60002463", (752, 1532, 2020, 1600), "color", "todo", 1200),
 ("logo_ron_medellin_anejo",     "60002942", (2672, 2640, 3448, 2800), "mono", "negro", 700),
 ("anos_3",                      "60002942", (3552, 2620, 3680, 2848), "mono", "negro", 160),
 ("logo_licor_ron_medellin",     "60002741", (300, 3048, 2300, 3448), "mono", "negro", 800),
 ("grado_29",                    "60002741", (1020, 3480, 1540, 3820), "mono", "color", 320),
 ("logo_ron_medellin_extra_anejo","60002751", (340, 3060, 2380, 3448), "mono", "todo", 800),
 ("anos_8",                      "60002751", (1160, 1772, 1380, 2125), "mono", "color", 200),
]
DPI = 200
meta = {}
ONLY = set(sys.argv[3:])
for rid, code, (x0, y0, x1, y1), modo, filtro, wfin in R:
    if ONLY and rid not in ONLY: continue
    s = DPI / 72
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-f", "1", "-l", "1", "-x", str(int(x0*s)), "-y", str(int(y0*s)),
                        "-W", str(int((x1-x0)*s)), "-H", str(int((y1-y0)*s)), pdf(code), t + "/a"], check=True)
        im = Image.open(glob.glob(t + "/a*.png")[0]).convert("RGB")
    W, H = im.size
    cols = im.getcolors(W * H)
    o = OPT.get(rid, {})
    bg = o.get("bg") or max(cols, key=lambda c: c[0])[1]
    hue_mode = o.get("hue", "all")
    from PIL import ImageFilter
    removed = Image.new("L", (W, H), 0); pr = removed.load()
    strong = Image.new("L", (W, H), 0); ps = strong.load()
    px = im.load()
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); po = out.load()
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            d = ((r-bg[0])**2 + (g-bg[1])**2 + (b-bg[2])**2) ** 0.5
            a = max(0.0, min(1.0, (d - 30) / 120))
            if a == 0: continue
            h, l, sat = colorsys.rgb_to_hls(r/255, g/255, b/255)
            hue = h * 360
            # quitar anotaciones técnicas: rosado/magenta, púrpura, cian de cotas, verde "Detalle"
            if hue_mode == "all" and sat > 0.45 and l > 0.25 and hue >= 300: continue
            if hue_mode == "red" and (hue < 20 or hue > 340) and sat > 0.5 and l > 0.35: continue
            if hue_mode in ("all", "purple") and 250 <= hue < 300 and sat > 0.35: continue
            neutral = sat < 0.30 or l < 0.22
            if filtro == "negro" and not neutral:
                pr[x, y] = int(a * 255); continue
            if filtro == "color" and neutral: continue
            if sat > 0.5 and a > 0.8: ps[x, y] = 255
            if modo == "mono":
                po[x, y] = (255, 255, 255, int(a * 255))
            else:
                ua = max(a, 0.01)
                c = tuple(int(max(0, min(255, bg[i] + (v - bg[i]) / ua))) for i, v in enumerate((r, g, b)))
                po[x, y] = c + (int(a * 255),)
    if o.get("umbral"):
        m = strong
        for _ in range(2): m = m.filter(ImageFilter.MaxFilter(5))
        from PIL import ImageChops
        out.putalpha(ImageChops.multiply(out.getchannel("A"), m))
    if o.get("fill"):
        k = o["fill"]; al = out.getchannel("A")
        small = al.resize((al.width // 4, al.height // 4))
        n = max(1, k // 4 // 8)
        c2 = small
        for _ in range(n): c2 = c2.filter(ImageFilter.MaxFilter(9))
        for _ in range(n): c2 = c2.filter(ImageFilter.MinFilter(9))
        closed = c2.resize(al.size)
        rm = removed.point(lambda v: 255 if v > 0 else 0)
        al2 = Image.composite(closed, al, rm)
        out.putalpha(al2)
    bb = out.getbbox()
    if bb: out = out.crop(bb)
    if out.width > wfin: out = out.resize((wfin, max(1, round(out.height * wfin / out.width))), Image.LANCZOS)
    if modo == "mono":
        out = out.getchannel("A"); la = Image.merge("LA", (Image.new("L", out.size, 255), out)); la.save(f"{OUT}/{rid}.png", optimize=True)
    else:
        out.save(f"{OUT}/{rid}.png", optimize=True)
    meta[rid] = dict(w=out.width, h=out.height, modo=modo, kb=round(os.path.getsize(f"{OUT}/{rid}.png")/1024, 1))
    print(rid, meta[rid])
old = json.load(open(f"{OUT}/meta.json")) if os.path.exists(f"{OUT}/meta.json") else {}
old.update(meta); json.dump(old, open(f"{OUT}/meta.json", "w"))
