"""Arma los diseños del piloto de la caja neutra x12 750/700 ml (TIPO 17).

Lee el catálogo del Taller de rótulos y escribe disenos_piloto.json con:
  - la caja neutra del proveedor (versión A 384x245x210 y versión B 384x242x210)
  - una caja por referencia: caja neutra + rótulos de planta de esa referencia

Uso: python3 disenos_piloto.py <catalogo.json> <salida.json>
"""
import json, sys

CAT = json.load(open(sys.argv[1], encoding="utf-8"))
E, R = CAT["elementos"], CAT["referencias"]
NEGRO, ROJO_PLANTA = "#1d1d1b", "#d0312d"

GEO_A = {"troquel": False, "P": [388, 251, 390, 249], "F": 122, "B": 220, "G": 30, "pegue": "izq"}
GEO_B = {"troquel": False, "P": [388, 248, 390, 246], "F": 121, "B": 220, "G": 30, "pegue": "izq"}

# Datos de rotulado de cada referencia (ITF-14 leído de las fichas: confirmar con el maestro GS1)
REFS = {
 "60002592": dict(desc="AGTE TRAD GENÉRICA EXP 700", marca="Aguardiente Antioqueño", variedad="Tradicional", tinta="Rojo 74", ml=700, mercado="Exportación genérica", itf="1770204900007"),
 "60002593": dict(desc="AGTE SIN AZÚCAR EUROPA 700", marca="Aguardiente Antioqueño", variedad="Sin azúcar", tinta="Azul 39", ml=700, mercado="Europa", itf="1770204900070"),
 "60002594": dict(desc="AGTE SIN AZÚCAR USA 750", marca="Aguardiente Antioqueño", variedad="Sin azúcar", tinta="Azul 39", ml=750, mercado="USA", itf="1066485800011"),
 "60002595": dict(desc="AGTE TRADICIONAL USA 750", marca="Aguardiente Antioqueño", variedad="Tradicional", tinta="Rojo 74", ml=750, mercado="USA", itf="1066485800003"),
 "60002596": dict(desc="AGTE 24° EUROPA 700", marca="Aguardiente Antioqueño", variedad="24° Sin azúcar", tinta="Verde 2081", ml=700, mercado="Europa", itf="1770204900184"),
 "60002597": dict(desc="AGTE 24° USA 750", marca="Aguardiente Antioqueño", variedad="24° Sin azúcar", tinta="Verde 2081", ml=750, mercado="USA", itf="1066485800032"),
 "60002600": dict(desc="AGTE SIN AZÚCAR CHILE 750", marca="Antioqueño Antioqueño", variedad="Sin azúcar", tinta="Azul 39", ml=750, mercado="Chile", itf="1770204900106"),
 "60002608": dict(desc="AGTE TRADICIONAL GENÉRICA EXP 750", marca="Aguardiente Antioqueño", variedad="Tradicional", tinta="Rojo 73", ml=750, mercado="Exportación genérica", itf="1770204900172"),
 "60002609": dict(desc="AGTE SIN AZÚCAR GENÉRICA EXP 750", marca="Aguardiente Antioqueño", variedad="Sin azúcar", tinta="Azul 39", ml=750, mercado="Exportación genérica", itf="1770204900169"),
 "60002652": dict(desc="AGTE 24° GENÉRICA EXP 750", marca="Aguardiente Antioqueño", variedad="24° Sin azúcar", tinta="Verde 2081", ml=750, mercado="Exportación genérica", itf="1770204900186"),
 "60002904": dict(desc="ANTIOQUEÑO ANTIOQUEÑO 24° EXP 750", marca="Antioqueño Antioqueño", variedad="24° Sin azúcar", tinta="Verde 2081", ml=750, mercado="Exportación genérica", itf="1770204900204"),
}

def digito(c13):
    s = sum(int(c13[12 - i]) * (3 if i % 2 == 0 else 1) for i in range(13))
    return (10 - s % 10) % 10

def volumen(ml):
    return "700 ml / 0.7 L" if ml == 700 else "750 ml / 0.75 L"

n = [0]
def it(tipo, ref, cara, x, y, w, quien, color=None, p=None, nombre=None):
    n[0] += 1
    d = {"id": f"pl{n[0]}", "tipo": tipo, "ref": ref, "cara": cara, "x": round(x, 1), "y": round(y, 1), "w": round(w, 1),
         "rot": 0, "color": color, "quien": quien, "oculto": False, "p": p or {}}
    if nombre: d["nombre"] = nombre
    return d

def proveedor(geo, tendido):
    """Impresión fija del proveedor: igual para las 11 referencias (1 tinta, Negro 90)."""
    P = geo["P"]; d3 = (P[2] - P[0]) / 2  # corrimiento de la cara 3 frente a la 1
    u = {"n": "12", "l1": "UN. vidrio", "l2": "Glass bottles"}
    s = [
        it("img", "sello_fla", "t1", 150, 30, 80, "proveedor", NEGRO, nombre="Sello FLA"),
        it("texto", "delicado_fragile", "t1", 252, 40, 96, "proveedor", NEGRO, {"texto": "DELICADO\nFRAGILE"}, "DELICADO / FRAGILE"),
        it("estiba", "estiba", "t3", 107, 17, 176, "proveedor", NEGRO, {"tendido": tendido, "tendidos": 6, "estibas": 1}, "Estibado"),
    ]
    for cara, dx in (("c1", 0), ("c3", d3 * 2)):
        s.append(it("unidades", "unidades", cara, 242 + dx, 8, 100, "proveedor", NEGRO, dict(u), "Unidades"))
    for cara, wc in (("c2", P[1]), ("c4", P[3])):
        s.append(it("unidades", "unidades", cara, (wc - 90) / 2, 12, 90, "proveedor", NEGRO, dict(u), "Unidades"))
        s.append(it("img", "sello_fla", cara, (wc - 70) / 2, 116, 70, "proveedor", NEGRO, nombre="Sello FLA"))
    s.append(it("img", "certificaciones", "b1", (P[0] - 250) / 2, 40, 250, "proveedor", NEGRO, nombre="Certificaciones"))
    s.append(it("texto", "peso", "b3", (P[2] - 140) / 2, 52, 140, "proveedor", NEGRO, {"texto": "0.339 kg Aprox."}, "Peso de la caja"))
    return s

def zonas(geo):
    """Zonas sin impresión del proveedor, reservadas para la planta."""
    P = geo["P"]; z = []
    for cara, dx in (("c1", 0), ("c3", P[2] - P[0])):
        z.append(it("zona", "zona", cara, 12, 10, 194, "planta", ROJO_PLANTA, {"texto": "ZONA 1 · MARCA Y VARIEDAD\nlogo, marca de variedad\ny botella de color", "r": 1.03}, "Zona 1 marca y variedad"))
        z.append(it("zona", "zona", cara, 212 + dx / 2, 96, 160, "planta", ROJO_PLANTA, {"texto": "ZONA 2 · VOLUMEN,\nDESTINO E ITF-14", "r": 0.72}, "Zona 2 volumen destino ITF"))
    for cara, wc in (("c2", P[1]), ("c4", P[3])):
        z.append(it("zona", "zona", cara, 12, 10, 38, "planta", ROJO_PLANTA, {"texto": "COLOR", "r": 1.55}, "Zona 3 señal de color"))
        z.append(it("zona", "zona", cara, (wc - 130) / 2, 88, 130, "planta", ROJO_PLANTA, {"texto": "ZONA 4 · VOLUMEN", "r": 0.16}, "Zona 4 volumen"))
        z.append(it("zona", "zona", cara, 14, 172, wc - 28, "planta", ROJO_PLANTA, {"texto": "ZONA 5 · FRASES LEGALES DEL MERCADO", "r": 40 / (wc - 28)}, "Zona 5 frases legales"))
    return z

# rótulos de la ficha actual que NO pasan a la planta
CODIGO_BARRAS_EL = {"75af58e5a7", "02a671df24"}   # ITF que quedó como imagen: se reemplaza por ITF editable
NO_PLANTA = {"fb9a38762d", "54c2b878a6",          # "UN" (es del proveedor)
             "5a301bee52"}                        # "750 ml / 0.75 L": se reemplaza por el texto de volumen
GEMELA = {"c1": "c3", "c3": "c1", "c2": "c4", "c4": "c2"}

def planta(code, geo):
    r, d = R[code], REFS[code]
    caras = {f"c{i+1}": w for i, w in enumerate(geo["P"])}
    base = []
    for x in r["items"]:
        if x["cara"] not in caras: continue          # la planta rotula solo las 4 caras (caja armada)
        if x.get("tipo") == "itf": continue
        e = E[x["el"]]
        if e["grupo"] != "planta" or x["el"] in CODIGO_BARRAS_EL or x["el"] in NO_PLANTA: continue
        base.append(dict(el=x["el"], cara=x["cara"], x=x["x"], y=x["y"], w=x["w"]))
    # caras gemelas iguales (1 = 3, 2 = 4), sin copiar lo que cruza la esquina
    for b in list(base):
        h = E[b["el"]]["h"] * b["w"] / E[b["el"]]["w"]
        if b["x"] < 0 or b["x"] + b["w"] > caras[b["cara"]] + 0.5: continue
        g = GEMELA[b["cara"]]
        if any(o["el"] == b["el"] and o["cara"] == g for o in base): continue
        dx = 3 if b["cara"] == "c1" and b["x"] > 200 else (-3 if b["cara"] == "c3" and b["x"] > 200 else 0)
        base.append(dict(b, cara=g, x=b["x"] + dx))
    s = [it("el", b["el"], b["cara"], b["x"], b["y"], b["w"], "planta") for b in base]
    cod = d["itf"]
    for cara, x in (("c1", 215.4), ("c3", 218.4)):
        s.append(it("itf", "itf14", cara, x, 146.5, 152.8, "planta", NEGRO, {"codigo": cod}, "Código ITF-14"))
        s.append(it("texto", "texto", cara, x + 76.4 - 55, 100, 110, "planta", NEGRO, {"texto": volumen(d["ml"])}, "Volumen"))
    for cara in ("c2", "c4"):
        s.append(it("texto", "texto", cara, (caras[cara] - 100) / 2, 90, 100, "planta", NEGRO, {"texto": volumen(d["ml"])}, "Volumen"))
    return s

def extra(nombre_cod, notas, dims, aclar, impresion):
    return {"codigo": nombre_cod, "notas": notas, "dims": dims, "aclaratorias": aclar, "impresion": impresion,
            "material": "C620KF", "color_carton": "KRAFT", "estilo": "REGULAR (RSC)", "pegue": "PEGADO", "atados": "25 UN."}

out = []
for ver, geo, dims, tendido in (("A", GEO_A, [384, 245, 210], 10), ("B", GEO_B, [384, 242, 210], 12)):
    items = proveedor(geo, tendido) + zonas(geo)
    out.append({"id": f"neutra_{ver}", "nombre": f"CE-12-750-{ver} · Caja neutra x12 750/700 ml" + ("" if ver == "A" else " (ancho 242)"),
                "tipo": "TIPO 17", "refCode": "60002609", "geo": geo, "items": items,
                "origen": {"modo": "proveedor", "code": "60002609", "tipo": "TIPO 17"},
                "extra": extra(f"POR ASIGNAR (CE-12-750-{ver})",
                               ["CAJA NEUTRA · 1 TINTA NEGRO 90 · SIN MARCA NI VOLUMEN",
                                "ZONAS ROJAS PUNTEADAS: SIN IMPRESIÓN, LAS ROTULA LA PLANTA"],
                               dims,
                               ["Negro: impresión fija del proveedor.", "Rojo punteado: zona sin impresión.",
                                f"Estiba: {tendido} x tendido, 6 tendidos.", "Reemplaza 11 cajas impresas.",
                                "Peso y medidas: confirmar."] ,
                               "1 TINTA · NEGRO 90")})
for code in REFS:
    d = REFS[code]
    items = proveedor(GEO_A, 10) + planta(code, GEO_A)
    out.append({"id": f"ref_{code}", "nombre": f"{code} · {d['desc']} · sobre CE-12-750-A",
                "tipo": "TIPO 17", "refCode": code, "geo": GEO_A, "items": items,
                "origen": {"modo": "proveedor", "code": code, "tipo": "TIPO 17"},
                "extra": extra("CE-12-750-A + ROTULADO PLANTA",
                               [f"CAJA BASE CE-12-750-A · ROTULADO DE PLANTA {code}",
                                f"{d['mercado'].upper()} · {d['ml']} ml · ITF {d['itf']}{digito(d['itf'])}"],
                               [384, 245, 210],
                               ["Negro: proveedor (caja neutra).", "Rojo: lo imprime la planta.",
                                f"Variedad: {d['variedad']} ({d['tinta']}).", "ITF: confirmar con maestro GS1.",
                                "Colores simulados."],
                               "PROVEEDOR 1T + PLANTA")})

json.dump({"refs": REFS, "itf14": {c: d["itf"] + str(digito(d["itf"])) for c, d in REFS.items()}, "disenos": out},
          open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "diseños;", {c: d["itf"] + str(digito(d["itf"])) for c, d in REFS.items()})
