# Taller de rótulos de cajas

Herramienta visual para trabajar el rotulado de las cajas: poner, quitar y mover rótulos sobre la caja
**desarmada** y verla **armada en 3D**.

**Artefacto publicado:** https://claude.ai/artifact/PvyeVwiFzGyJMo95ccDTN2

## Qué hace
- **Tipo y referencia:** al elegir un tipo o una referencia se carga su rotulado real, extraído de su
  ficha. Están las 106 fichas legibles de `Cajas tipos`.
- **Biblioteca:** reúne los 1.524 rótulos distintos encontrados en las fichas, con búsqueda y filtros
  (esta referencia, este tipo o todas las fichas), más rótulos editables: textos, código ITF-14, estibado
  y arte base.
- **Proveedor y planta:** cada rótulo se marca como **Proveedor** (fijo) o **Planta** (variable). El
  modo «Quién imprime» lo pinta en negro o en rojo.
- **Nueva caja:** se crea vacía, con lo fijo del proveedor de una referencia, o como copia de una
  referencia. **Reiniciar** vuelve al punto de partida.
- **Descargas:** ficha de diseño en PDF con la estructura y el tamaño de página de las fichas del tipo
  (encabezado técnico, plano con cotas y ampliación de rótulos), PNG de la caja desarmada y JSON.
- **Diseños e ideas:** quedan guardados dentro del artefacto.

## Cómo se construyó
1. `fuente/extraer_todo.py` recorre los PDF:
   - Detecta el plano (caras, aletas y lado del pegue).
   - Separa la tinta por color y quita las anotaciones técnicas (cotas, «Detalle A/B», asteriscos y
     líneas de doblez).
   - Agrupa cada rótulo y unifica los repetidos entre fichas.
2. `fuente/nombrar.py` lee el texto de cada rótulo con OCR (tesseract, español), le da nombre, lo
   clasifica como proveedor o planta y convierte los códigos de barras en ITF-14 editables.
3. `fuente/construir.py` arma la carpeta `publicar/`: la página, `catalogo.json`, un paquete de imágenes
   por tipo y las fuentes.

## Límites conocidos
- Algunos rótulos sin texto quedan con nombre genérico («Logo / gráfico Negro 90»).
- Algunas anotaciones del proveedor pueden quedar como rótulo. Se quitan desde Capas.
- Los TIPO 14 y 15 son bandejas troqueladas: se trabajan sobre el plano real y no tienen vista 3D.
- Quedaron fuera 4 fichas no activas de formato antiguo: 60002598, 60002601, 60002602 y 60002612.
