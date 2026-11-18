"""Arma plan/index.html (página del plan del piloto) con los datos de matriz_rotulado.csv.
Uso: python3 plan.py  (desde la carpeta del piloto)"""
import csv, json
from pathlib import Path
A = Path(__file__).resolve().parent.parent
filas = list(csv.DictReader(open(A / "matriz_rotulado.csv", encoding="utf-8-sig"), delimiter=";"))
HEX = {"Azul 39": "#1f66b3", "Rojo 74": "#e2231a", "Rojo 73": "#c8102e", "Verde 2081": "#78b52b"}
REP = {"60002609": "Ficha base del diseño · sin azúcar genérica", "60002594": "USA: «FOR EXPORT» y sin frases legales", "60002596": "Europa 700 ml: el volumen lo imprime la planta"}
datos = [{**{k: f[k] for k in ("codigo", "descripcion", "ficha_actual", "marca", "variedad", "tinta_variedad", "texto_volumen", "mercado", "destino", "frases_legales", "itf14", "peso_caja_ficha_kg", "particion_actual", "nota")},
          "hex": HEX.get(f["tinta_variedad"], "#888"), "rep": REP.get(f["codigo"], "")} for f in filas]
def fila(f):
    rep = ' <span class="pill ok">corrida piloto</span>' if f["codigo"] in REP else ""
    return (f'<tr><td><b>{f["codigo"]}</b>{rep}</td><td>{f["descripcion"]}</td><td>{f["mercado"]}</td><td class="n">{f["volumen_ml"]}</td>'
            f'<td><i class="sw" style="background:{HEX.get(f["tinta_variedad"],"#888")}"></i>{f["variedad"]} · {f["tinta_variedad"]}</td>'
            f'<td>{f["destino"]}</td><td>{f["frases_legales"].split(" (")[0]}</td><td class="mono">{f["itf14"]}</td></tr>')
tabla = "\n".join(fila(f) for f in filas)
html = (A / "scripts" / "plan.template.html").read_text(encoding="utf-8")
html = html.replace("/*__REFS__*/[]", json.dumps(datos, ensure_ascii=False)).replace("<!--__TABLA__-->", tabla)
(A / "plan" / "index.html").write_text(html, encoding="utf-8")
print("plan/index.html", len(html) // 1024, "KB")
