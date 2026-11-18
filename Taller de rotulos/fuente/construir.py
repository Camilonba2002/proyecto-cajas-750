"""Arma la carpeta publicable del taller (con --solo-pagina actualiza solo index.html).
- index.html: la plantilla con los rótulos base incrustados.
- catalogo.json, el/*.png: rotulado real extraído de las fichas (extraer_todo.py).
- fonts/: Oswald para que la ficha PDF salga con la misma letra.
- piloto.json: diseños del piloto de la caja neutra x12 750 (si existe la carpeta del piloto).
Uso: python3 construir.py <carpeta_extraccion>"""
import base64, json, shutil, sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
EXT = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else RAIZ / "datos"
PUB = RAIZ / "publicar"
ROT = RAIZ / "rotulos"
meta = json.loads((ROT / "meta.json").read_text())
assets = {k: {"src": "data:image/png;base64," + base64.b64encode((ROT / f"{k}.png").read_bytes()).decode(),
              "w": m["w"], "h": m["h"], "mono": m["modo"] == "mono"} for k, m in meta.items()}
html = (AQUI / "taller.template.html").read_text(encoding="utf-8").replace("/*__ASSETS__*/{}", json.dumps(assets, separators=(",", ":")))

def piloto():
    """Diseños del piloto de la caja neutra (Piloto CE-12-750/disenos_piloto.json) -> publicar/piloto.json"""
    f = RAIZ.parent / "Piloto CE-12-750" / "disenos_piloto.json"
    if not f.exists(): return
    d = json.loads(f.read_text(encoding="utf-8"))["disenos"]
    campos = ("id", "nombre", "tipo", "refCode", "geo", "origen", "items", "extra")
    (PUB / "piloto.json").write_text(json.dumps({"disenos": [{k: x[k] for k in campos} for x in d]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
if "--solo-pagina" in sys.argv:
    (PUB / "index.html").write_text(html, encoding="utf-8"); piloto(); print("index.html actualizado"); sys.exit(0)
if PUB.exists(): shutil.rmtree(PUB)
(PUB / "el").mkdir(parents=True); (PUB / "fonts").mkdir()
(PUB / "index.html").write_text(html, encoding="utf-8")
cat = json.loads((EXT / "catalogo.json").read_text())
for e in cat["elementos"].values():
    for k in ("base", "capa", "caras"): e.pop(k, None)
for r in cat["referencias"].values():
    r["items"] = [{k: v for k, v in it.items()} for it in r["items"]]
(PUB / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
usados = set(cat["elementos"])
from PIL import Image
import io
datos = {}
for f in (EXT / "elementos").glob("*.png"):
    if f.stem in usados:
        b = io.BytesIO(); Image.open(f).save(b, "WEBP", quality=86, method=4)
        datos[f.stem] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
# un paquete de imágenes por tipo de caja
por_tipo = {}
for code, r in cat["referencias"].items():
    por_tipo.setdefault(r["tipo"], set()).update(it["el"] for it in r["items"] if it.get("el"))
for tipo, ids in por_tipo.items():
    (PUB / "el" / (tipo.replace(" ", "_") + ".json")).write_text(json.dumps({i: datos[i] for i in sorted(ids) if i in datos}, separators=(",", ":")))
for uid, e in cat["elementos"].items():
    e["paquete"] = next(t for t in sorted(por_tipo) if uid in por_tipo[t])
(PUB / "catalogo.json").write_text(json.dumps(cat, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
for f in (EXT / "siluetas").glob("*.png"): shutil.copy(f, PUB / "el" / f.name)
for f in (AQUI / "fonts").glob("*.woff2"): shutil.copy(f, PUB / "fonts" / f.name)
piloto()
tam = sum(p.stat().st_size for p in PUB.rglob("*") if p.is_file())
print("archivos:", sum(1 for p in PUB.rglob("*") if p.is_file()), "· tamaño:", round(tam / 1e6, 1), "MB")
