"""Arma taller_de_rotulos.html: incrusta los rótulos (PNG) en la plantilla.
Uso: python3 construir.py"""
import base64, json
from pathlib import Path
AQUI = Path(__file__).resolve().parent
ROT = AQUI.parent / "rotulos"
meta = json.loads((ROT / "meta.json").read_text())
assets = {}
for k, m in meta.items():
    b64 = base64.b64encode((ROT / f"{k}.png").read_bytes()).decode()
    assets[k] = {"src": "data:image/png;base64," + b64, "w": m["w"], "h": m["h"], "mono": m["modo"] == "mono"}
html = (AQUI / "taller.template.html").read_text(encoding="utf-8")
html = html.replace("/*__ASSETS__*/{}", json.dumps(assets, separators=(",", ":")))
salida = AQUI.parent / "taller_de_rotulos.html"
salida.write_text(html, encoding="utf-8")
print(salida, round(salida.stat().st_size / 1024), "KB")
