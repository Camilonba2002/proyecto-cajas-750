"""Matriz de rotulado de planta del piloto CE-12-750 (una fila por referencia).
Uso: python3 matriz.py <catalogo.json> <datos_por_referencia.json> <disenos_piloto.json> <salida.csv>"""
import csv, json, re, sys
cat, datos, dis, salida = sys.argv[1:5]
C = json.load(open(cat, encoding="utf-8")); E, R = C["elementos"], C["referencias"]
DT = {r["code"]: r for r in json.load(open(datos, encoding="utf-8"))}
P = json.load(open(dis, encoding="utf-8")); REFS, ITF = P["refs"], P["itf14"]
LEGAL = {"col": "Colombia (3 frases: exceso de alcohol / menores de edad / daño a la salud)",
         "chile": "Chile (Beber con moderación / prohibida su venta a menores de 18 años)", "no": "Sin frases (USA)"}
filas = []
for code, d in REFS.items():
    r = R[code]; noms = [E[i["el"]]["nombre"].upper() for i in r["items"] if i.get("el") in E]
    destino = "FOR EXPORT" if any(n.strip() == "FOR EXPORT" for n in noms) else "PARA EXPORTACIÓN / FOR EXPORT"
    legal = LEGAL["chile"] if any("MENORES DE 18" in n for n in noms) else LEGAL["col"] if any("EXCESO DE ALCOHOL" in n for n in noms) else LEGAL["no"]
    peso = next((re.search(r"\d[.,]\d{3}", E[i["el"]]["nombre"]).group(0).replace(",", ".") for i in r["items"]
                 if i.get("el") in E and "APROX" in E[i["el"]]["nombre"].upper() and re.search(r"\d[.,]\d{3}", E[i["el"]]["nombre"])), "")
    h = DT[code]["hojas"]
    filas.append({
        "codigo": code, "descripcion": d["desc"], "ficha_actual": r["meta"].get("codigo", ""),
        "caja_base_piloto": "CE-12-750-A (neutra)", "marca": d["marca"], "variedad": d["variedad"], "tinta_variedad": d["tinta"],
        "volumen_ml": d["ml"], "texto_volumen": "700 ml / 0.7 L" if d["ml"] == 700 else "750 ml / 0.75 L",
        "mercado": d["mercado"], "destino": destino, "frases_legales": legal,
        "itf14_base_13": d["itf"], "digito_control": ITF[code][-1], "itf14": ITF[code],
        "itf14_estado": "Leído de la ficha del proveedor: verificar con el maestro GS1",
        "particion_actual": h[1].replace(" ", ""), "particion_piloto": "542x542",
        "division_actual": h[2].replace(" ", ""), "division_piloto": "1110x1029",
        "peso_caja_ficha_kg": peso, "carton": DT[code]["carton"], "cierre": DT[code]["cierre"],
        "nota": "; ".join(x for x in [
            "Volumen 700 ml: lo imprime la planta" if d["ml"] == 700 else "",
            "Partición 557x557 pasa a 542x542 (validar ajuste)" if h[1].replace(" ", "") != "542x542" else "",
            "La ficha declara Rojo 73; las demás Tradicional usan Rojo 74: unificar" if d["tinta"] == "Rojo 73" else "",
        ] if x)})
with open(salida, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0]), delimiter=";"); w.writeheader(); w.writerows(filas)
print(len(filas), "filas")
for x in filas: print(x["codigo"], x["destino"], "|", x["frases_legales"][:12], "|", x["peso_caja_ficha_kg"], x["particion_actual"], x["nota"])
