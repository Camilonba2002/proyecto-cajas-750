# Estandarización de cajas: patrones y propuestas

**Informe publicado:** https://claude.ai/artifact/4VCr6cWgLj7SSLTPYG2SML
(la misma página está en `estandarizacion.html`).

## Resumen
- 98 referencias activas generan **273 códigos de material** (caja impresa + partición + división).
- Detrás de los 22 tipos hay **11 familias de botella**, según la celda de la partición.
- **Escenarios:**
  - **E1 · Caja neutra por tipo** (sin cambiar medidas): ≈ 47 códigos.
  - **E2 · Caja por familia de botella:** ≈ 38 códigos (−86 %).
  - **E3 · Rediseño modular:** ≈ 30 códigos.
- **Estiba:** las x12 de Aguardiente pueden pasar de 10 a 12 cajas por tendido (+20 % de botellas por estiba).
  - El TIPO 05/19 lo permite ya, sin cambiar la caja.
  - El TIPO 17 necesita bajar su ancho interior de 245 a 242 mm.
- **Tablas de estiba imposibles:** TIPO 06, 18 y 20.

## Archivos
- `estandarizacion.html`: el informe.
- `datos_por_referencia.json`: datos de cada ficha (medidas, grilla de botellas, celda, cartón, cierre, áreas).
- `calculo_estiba.json`: cajas por tendido calculadas en estiba de 1,20 × 1,00 m.
- `scripts/`: cómo se calcularon (`dataset.py`, `estiba.py`).

## Fuentes científicas
Búsqueda hecha con Consensus. Elicit no estuvo disponible porque el plan de la cuenta no incluye acceso por API. Las referencias están al final del informe.
