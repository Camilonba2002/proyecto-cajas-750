# Taller de rótulos de cajas

Herramienta visual para trabajar la caja estándar: poner, quitar y mover los rótulos conocidos sobre la
caja **desarmada** y verla **armada en 3D**.

**Artefacto publicado:** https://claude.ai/artifact/PvyeVwiFzGyJMo95ccDTN2

## Qué hace
- Los 22 tipos de caja con sus medidas internas y su hoja neta. Las medidas de cada panel son aproximadas
  (L+4, A+6, L+6, A+4 mm), y los TIPO 14 y 15 (bandejas troqueladas) se muestran como caja regular aproximada.
- Biblioteca de rótulos con el arte real recortado de las fichas: logos de marca, Sin azúcar, 24°,
  sello FLA, certificaciones, estibado, Doble Anís, Ron Medellín, entre otros. También hay textos editables
  (unidades, destino, frases legales, peso, lote) y un código ITF-14 que calcula el dígito de control.
- Cada rótulo se marca como **Proveedor** (fijo) o **Planta** (variable). El modo «Quién imprime» lo pinta
  en negro o en rojo.
- Plantillas por variedad (Sin azúcar, Tradicional, 24°), marca y mercado (Nacional, USA, Exportación genérica, Chile).
- Diseños e ideas guardados dentro del artefacto, más rótulos nuevos subidos como imagen.
- Descarga en PNG de la caja desarmada y en JSON del diseño.

## Archivos
- `taller_de_rotulos.html`: la página publicada, con las imágenes incrustadas.
- `rotulos/`: los rótulos recortados de las fichas (PNG con fondo transparente) y `meta.json`.
- `fuente/taller.template.html`: el código de la página.
- `fuente/construir.py`: arma la página con las imágenes (`python3 fuente/construir.py`).
- `fuente/extraer_rotulos.py`: recorta los rótulos de los PDF de `Cajas tipos` (requiere `pdftoppm` y Pillow).
