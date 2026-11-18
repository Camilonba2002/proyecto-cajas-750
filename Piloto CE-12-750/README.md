# Piloto · Caja neutra x12 750/700 ml (CE-12-750)

TIPO 17, aguardiente de exportación. Las 11 referencias activas (60002592, 60002593, 60002594, 60002595, 60002596, 60002597, 60002600, 60002608, 60002609, 60002652, 60002904) pasan a una sola caja.

- **El proveedor imprime** lo que es igual en las 11, en una tinta (Negro 90): sello FLA, DELICADO / FRAGILE, «12 UN. vidrio / Glass bottles», la tabla de estiba, las certificaciones y el peso.
- **La planta rotula** en 5 zonas que el proveedor deja sin impresión: marca y variedad, volumen, destino, ITF-14 y frases legales.
- Resultado: de 33 códigos de material (caja, partición y división) se pasa a 3, y de 11 juegos de clichés a 1. Con la versión B (ancho interior 242 mm) caben 72 cajas por estiba en vez de 60.

Plan completo (fases, pruebas, criterios, decisiones, riesgos y texto para el proveedor): página **Piloto caja neutra x12 750** en claude.ai, cuya fuente está en `plan/`.

## Contenido

| Carpeta o archivo | Qué es |
|---|---|
| `1 Caja neutra (proveedor)/` | Ficha PDF, plano y vista 3D de la versión A (384 × 245 × 210, medidas de hoy) y de la versión B (384 × 242 × 210, para pruebas). Es lo que se envía al proveedor. |
| `2 Rotulado de planta por referencia/` | Por cada referencia: ficha PDF, plano «quién imprime» (negro = proveedor, rojo = planta) y plano «solo planta». |
| `matriz_rotulado.csv` | Datos de rotulado por referencia: marca, variedad, tinta, volumen, mercado, destino, frases legales, ITF-14 con dígito de control, partición, división y peso de la ficha. Separador `;`. |
| `disenos_piloto.json` | Los 13 diseños (2 cajas neutras y 11 referencias). También se abren en el Taller de rótulos, pestaña Diseños, sección «Piloto». |
| `plan/` | Página del plan con sus imágenes. |
| `scripts/` | Cómo se generó todo (ver abajo). |

## Datos por confirmar

- **ITF-14**: se leyeron de las fichas del proveedor y el dígito de control se calculó. Hay que verificarlos con el maestro GS1 antes de imprimir.
- **Peso impreso**: 0.339 kg Aprox. es el valor más frecuente en las fichas (6 de 11; 4 dicen 0.334 y 1 dice 0.322). Lo confirma el proveedor.
- **60002608** declara Rojo 73; las demás Tradicional usan Rojo 74.
- **60002597** usa hoy la partición 557 × 557; el piloto la pasa a 542 × 542.
- Las referencias de **Europa** llevan hoy las 3 frases legales de Colombia: confirmar con comercio exterior.

## Volver a generar

Requiere el Taller servido en local (`python3 -m http.server 8765` dentro de `Taller de rotulos/publicar`) y Playwright.

```bash
python3 scripts/disenos_piloto.py "../Taller de rotulos/publicar/catalogo.json" disenos_piloto.json
node scripts/piloto_gen.js disenos_piloto.json <carpeta temporal>
python3 scripts/empaquetar.py <carpeta temporal> disenos_piloto.json .
python3 scripts/matriz.py "../Taller de rotulos/publicar/catalogo.json" ../Estandarizacion/datos_por_referencia.json disenos_piloto.json matriz_rotulado.csv
python3 scripts/plan.py
```

`plan.py` arma `plan/index.html` a partir de `scripts/plan.template.html` y de la matriz. Las imágenes de `plan/img` salen de los PNG de `piloto_gen.js`. Después de cambiar los diseños, correr `python3 construir.py --solo-pagina` en `Taller de rotulos/fuente` para actualizar `piloto.json` del Taller.
