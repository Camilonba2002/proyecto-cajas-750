# Diagnóstico de los 22 tipos de cajas

**Base:** 111 fichas técnicas en PDF de la carpeta [`Cajas tipos`](../Cajas%20tipos) (TIPO 01 a TIPO 22 y
OTROS) y el Excel `Cajas tipos.xlsx`. Todas las fichas son del mismo proveedor y usan el mismo formato
("D+D - FOR - 07/08 FICHA TÉCNICA (EM)").

**Archivos de apoyo:**
- [`inventario_fichas.csv`](inventario_fichas.csv): una fila por ficha con código, tipo, descripción del
  Excel, referencia de la ficha, medidas, hoja, cartón, cierre, tintas y páginas. Se abre en Excel.
- [`laminas/`](laminas): la primera ficha de cada tipo, para verlos todos de un vistazo.

---

## 1. Resumen

1. **Cada tipo es una estructura.** En 20 de los 22 tipos, todas las referencias tienen la misma medida
   interna y la misma hoja. El Excel ya agrupa bien: un tipo es una caja física, y las referencias de ese
   tipo solo cambian en el arte. Las excepciones son menores (sección 3.1).
2. **Hay dos tecnologías de caja:**
   - **20 tipos de caja regular de cartón corrugado kraft** (C540 KF o C620 KF), con "kit": caja +
     partición + división (3 páginas por ficha).
   - **2 tipos de bandeja troquelada** (TIPO 14 y 15, envase multicapa o Tetra de 1050 y 260 ml), en
     cartón B540 KW, sin kit, con manija y armado distinto.
3. **La diferencia entre nacional y exportación no está en la medida, sino en el cartón y el cierre.**
   Nacional: C540 KF con cierre licorera. Exportación (USA, Europa, Chile, genérica): C620 KF sin cierre
   licorera. Pasa dentro del mismo tipo (TIPO 07 y TIPO 13) y entre tipos (TIPO 05 y TIPO 19 son la misma
   caja, ver 3.2).
4. **El arte sigue un sistema claro, pero con variaciones sueltas.** Todas comparten los mismos bloques:
   sello FLA, unidades y volumen, código ITF-14 de 6,0" × 1,63", "DELICADO / ESTE LADO ARRIBA",
   estibado, certificaciones, peso y guía-señal de identificación. El color identifica la variedad.
   Hay variaciones que no responden a una regla, como el rojo 73 frente al rojo 74.
5. **El Excel y los archivos no cuadran del todo:** faltan 3 PDF, hay 1 PDF duplicado, 1 estado distinto
   y 8 descripciones que no coinciden con la ficha (sección 4).
6. **67 de las 100 fichas activas están marcadas "ENS" o "ENSAYO"** en la referencia. Hay que confirmar
   con el proveedor si son versiones aprobadas o pruebas.

---

## 2. Inventario por tipo

"Activas" cuenta los PDF fuera de la carpeta "No activo". En TIPO 14 hay un PDF duplicado.

| Tipo | Formato | Producto | Activas (no activas) | Medidas int. (mm) | Hoja neta (mm) | Cartón | Cierre licorera |
|---|---|---|---|---|---|---|---|
| 01 | x30 · 375 ml | Aguardiente y Doble Anís (vidrio y PET) | 8 (2) | 476×302×200 / 198 | 512 / 510 × 1606 | C540 KF (1 en C620) | Sí |
| 02 | x30 · 330 ml | Doble Anís | 2 | 467×297×185 | 491×1578 | C620 KF | Sí |
| 03 | x20 · 750 ml | Aguardiente nacional | 3 | 482×324×208 | 542×1662 | C540 KF | Sí |
| 04 | x12 · 750 ml | Doble Anís 30° | 2 | 372×278×252 | 542-544×1350 | C540 KF | Sí |
| 05 | x12 · 1000 ml | Aguardiente nacional | 3 | 384×242×264 | 516×1302 | C540 KF | Sí |
| 06 | x12 · 1000 ml | Ron 3 años | 2 | 377×282×292 | 584×1368 | C540 KF / C620 BW (blanco) | Uno sí, otro no |
| 07 | x6 · 1750 ml | Aguardiente y Doble Anís | 11 | 372×247×298 | 560×1288 | C540 KF nacional / C620 KF exp. | Nacional sí, exp. no |
| 08 | x6 · 2000 ml | Aguardiente y Ron 3 años | 3 (1) | 386×256×320 | 586×1334 | C540 KF | Sí |
| 09 | x30 · 375 ml | Ron y Licor Ron Medellín | 3 | 417×348×218 | 576×1580 | C540 KF | Sí |
| 10 | x20 · 750 ml | Ron y Licor Ron Medellín | 3 | 442×354×253 | 617×1642 | C540 KF | Sí |
| 11 | x12 · 750 ml | Ron 8 y 12 años | 2 | 507×326×218 | 554×1716 | C540 KF | Sí |
| 12 | x20 · 375 ml | Ron 8 años | 1 | 522×340×173 | 523×1774 | C540 KF | Sí |
| 13 | x6 · 750/700 ml | Ron 5, 8 y 12 años exportación + Crema de Ron | 8 | 323×255×222 (una: 318×250×214) | 486×1206 | C620 KF (crema: C540) | Exp. no, crema sí |
| 14 | x12 · 1050 ml | Envase multicapa (Tetra), Aguardiente y Ron | 4 (1) | 280×238×231 | 993×1836 | B540 KW | Bandeja troquelada |
| 15 | x24 · 260 ml | Envase multicapa (Tetra), Aguardiente y Ron | 5 | 297×212×129 | 741×1760 | B540 KW | Bandeja troquelada |
| 16 | x24 · 375 ml | Aguardiente exportación | 7 | 385×302×200 | 512×1424 | C620 KF | No |
| 17 | x12 · 750/700 ml | Aguardiente exportación | 11 (2) | 384×245×210 | 464×1308 | C620 KF | No |
| 18 | x12 · 750/700 ml | Ron 3 años exportación | 3 | 350×262×253 | 525×1274 | C620 KF | No |
| 19 | x12 · 1000 ml | Aguardiente exportación | 7 (3) | 384×242×264 | 516×1302 | C620 KF | No |
| 20 | x6 estuche + 1 vaso | Ron 5, 8 y 12 años | 3 | 444×360×224 | 594×1658 | C540 KF | Sí |
| 21 | x24 · 375 ml | Ron 3 años exportación | 2 | 414×274×218 | 508×1426 | C620 KF | No |
| 22 | x30 · 375 ml PET | Aguardiente PET | 3 | 473×298×208 | 518×1592 | C620 KF / KW | Sí |
| OTROS | varios | Vodka, estuche Real, Crema de Ron 375, Ron Pink | 4 (2) | cada una distinta | | C540 KF | Sí |

**Tamaño de los grupos:** los tipos con más referencias son 17 y 07 (11 cada uno), 01 (8), 13 (8),
16 (7) y 19 (7). Seis tipos tienen una sola o dos referencias.

---

## 3. Hallazgos estructurales

### 3.1 Tipos que no son del todo una sola caja
- **TIPO 13:** 60002963 (Ron 5 años 700) mide 318×250×214 y las otras 7 miden 323×255×222. Es otra caja.
- **TIPO 01:** dos subversiones casi iguales. Aguardiente: 476×302×198, hoja 510. Doble Anís:
  476×302×200, hoja 512. Además, 60002577 (Doble Anís sin azúcar PET) usa C620 KF y las demás C540 KF.
- **TIPO 07:** misma medida, pero dos especificaciones. Nacional (60002413, 2414, 2415, 2459, 2460) va
  con cierre licorera; USA y exportación genérica van sin cierre. 60002415 es nacional y está en C620 KF;
  las otras nacionales están en C540 KF.
- **TIPO 06:** 60002612 (no activo según el Excel) está en cartón **blanco** C620 BW con tinta Café 52 y
  sin cierre. 60002745 está en kraft C540 KF con cierre.
- **TIPO 04 y TIPO 17:** diferencias de 1-2 mm en la hoja entre referencias (544 frente a 542 y 463 frente
  a 464). Parecen ajustes de dibujo, no cajas distintas.

### 3.2 Tipos distintos que en realidad comparten caja o medida
- **TIPO 05 y TIPO 19 son la misma caja:** 384×242×264, hoja 516×1302. Solo cambian cartón y cierre:
  TIPO 05 es nacional (C540 KF, con cierre) y TIPO 19 es exportación (C620 KF, sin cierre).
- **TIPO 17 (x12 750/700) y TIPO 05/19 (x12 1000)** tienen casi la misma base: 384×245 frente a 384×242.
  Cambia la altura (210 frente a 264). Es la misma huella de estiba.
- **TIPO 01 (x30 375 vidrio) y TIPO 22 (x30 375 PET):** 476×302×200 frente a 473×298×208. Además, el
  Doble Anís PET (60002576 y 2577) ya se empaca en la caja del TIPO 01. Vale la pena validar si el
  Aguardiente PET también cabe en la del TIPO 01.
- **TIPO 01 (x30 375) y TIPO 16 (x24 375):** mismo ancho (302) y mismo alto (200). Es la misma botella
  con otra cantidad.
- **OTROS:** 60003019 (Ron Pink) tiene la misma medida que 60003020 (Real Gold, no activo):
  318×212×238, hoja 460×1110.

### 3.3 Cartón
- **C540 KF:** nacional y ron nacional. **C620 KF:** toda la exportación y TIPO 02 y 22.
- **B540 KW:** solo las bandejas troqueladas de multicapa (TIPO 14 y 15).
- **C620 BW (blanco):** solo 60002612 (TIPO 06).

---

## 4. Excel frente a archivos

| Situación | Detalle |
|---|---|
| En el Excel sin PDF | 60002571 (marcada "no existe"), 60002960 ("no existe"), **60002076 CAJA X 12 AGTE 24° TETRA 1050** (activa, sin ficha), PENDIENTE 1 y PENDIENTE 2 |
| PDF duplicado | 60002073 está dos veces en TIPO 14 (una con "(1)" en el nombre) |
| Estado distinto | 60002612: el Excel la marca no activa, pero el PDF no está en "No activo" |
| PENDIENTE 2 | Dice "CAJA X 30 RON 5 AÑOS 750", pero está en TIPO 10, que es x20. Probablemente es x20 |
| Descripción distinta | 60002961: Excel "EUROPA 40°", ficha "EXPO 35°" |
| | 60002951: Excel "RON 3 AÑOS USA 40°", ficha "RON X 12 NEGRO USA 750 NP" |
| | 60002592: Excel "EUROPA 700", ficha "GENERICA EXP 700" |
| | 60002605: Excel "EUROP 1000", ficha "EXPORTACIÓN 1000" |
| | 60002544: Excel "DOBLE ANIS 24°", ficha "DOBLE ANIS SIN AZ 24°" |
| | 60002415: Excel "AGTE 24°", ficha "AGTE SIN AZ 24°" |
| | 60000604: Excel y nombre del archivo "VODKA GUALA"; el arte de la caja dice **"VODKA MONTESSKAYA"** |
| | 60002020: la ficha no trae referencia legible (formato antiguo) |
| Otro cliente | 60002038 (TIPO 16) está a nombre de **FABRICAJAS COMPANY S.A.S., NIT 900943413**; las demás, a nombre de la Fábrica de Licores y Alcoholes de Antioquia |

---

## 5. Hallazgos del arte

### 5.1 Lo que se repite en todas
Sello Fábrica de Licores de Antioquia, cantidad y volumen ("12 Unidades en vidrio 750 ml", "UN / BOTTLES"
en exportación), código ITF-14 con la misma medida (6,0" × 1,63"), "DELICADO / ESTE LADO ARRIBA",
dibujo de estibado 1,20 × 1,00 m, certificaciones en la aleta inferior, peso aproximado, guía-señal de
identificación y ranuras de trazabilidad (Detalle A y B). Las bandejas multicapa agregan "¡IMPORTANTE!
Tomar la caja por debajo, no hale las aletas".

### 5.2 Código de color por producto
| Producto | Color |
|---|---|
| Aguardiente Sin azúcar | Azul 39 |
| Aguardiente Tradicional | Rojo 74 o **Rojo 73** (sin regla clara: 73 en 60002608, 2590, 2606, 2665, 2572, 2599, 2601) |
| Aguardiente 24° | Verde 2081 |
| Doble Anís | Rojo 74 / Azul 31 / Verde 29, con franja decorativa |
| Ron 3 años | Solo Negro 90 |
| Ron 5 años | Azul 30 |
| Ron 8 años | Morado P-2068U |
| Ron 12 años | Verde 2008 |
| Ron Dorado | Dorado |
| Licor Ron Medellín 29° | Verde 29 |
| Antiguas (no activas) | Café 52, Verde 3213, Gris H1709 |

Casi todas son de 2 tintas (Negro 90 + color de la variedad). Ron 3 años y multicapa de ron son de 1 tinta.

### 5.3 Marcas en las cajas
Aguardiente Antioqueño, Antioqueño Antioqueño (exportación), Aguardiente Doble Anís, Ron Medellín
(Añejo, Extra Añejo), Licor de Ron Medellín, Licor Crema de Ron Medellín, Vodka Montesskaya y Aguardiente
Real.

---

## 6. Diagnóstico

**Lo positivo:**
- La familia de cajas ya está bastante ordenada. Un tipo del Excel equivale a una caja física, y el arte
  sigue una plantilla común del mismo proveedor.
- Esto facilita estandarizar: en la mayoría de tipos, las referencias solo se diferencian por marca,
  variedad, color, destino y código. Es justo lo que se puede imprimir en planta.

**Lo que hay que resolver primero:**
1. **Depurar el maestro:** corregir las 8 descripciones, crear o ubicar la ficha de 60002076, quitar el
   PDF duplicado, mover 60002612 a "No activo" y definir PENDIENTE 1 y 2.
2. **Confirmar el estado de las 67 fichas "ENS/ENSAYO"** con el proveedor.
3. **Aclarar 60000604** (Guala o Montesskaya) y **60002038** (ficha a nombre de otro cliente).
4. **Definir una sola regla nacional/exportación** de cartón y cierre. Hoy hay excepciones: 60002415,
   60002577, TIPO 02 y TIPO 22 con C620 y cierre licorera.
5. **Unificar el rojo de Tradicional** (73 o 74).

**Oportunidades de reducir tipos:**
- **TIPO 05 + TIPO 19:** misma caja. Puede ser un solo tipo con dos especificaciones (nacional y
  exportación), o una sola si se acepta un cartón y cierre únicos.
- **TIPO 01 + TIPO 22:** validar si el Aguardiente PET cabe en la caja del TIPO 01, como ya pasa con el
  Doble Anís PET.
- **TIPO 13:** sacar 60002963 a su propio tipo, o ajustarla a la medida de las otras 7.
- **Tipos de 1 o 2 referencias** (02, 04, 06, 11, 12, 18, 21): revisar si su volumen justifica una caja
  propia.

**Siguiente paso sugerido:** aplicar la idea de caja neutra (proveedor imprime lo fijo, planta imprime
lo variable) empezando por los tipos más grandes: 17, 07, 01, 13, 16 y 19.
