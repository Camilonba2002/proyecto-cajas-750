// Genera fichas PDF y PNG de los diseños del piloto con el Taller de rótulos (servido en 127.0.0.1:8765)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [spec, outDir, solo] = process.argv.slice(2);
  const D = JSON.parse(fs.readFileSync(spec, 'utf8')).disenos.filter(d => !solo || solo.split(',').includes(d.id));
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  const errs = [];
  p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await p.goto('http://127.0.0.1:8765/index.html');
  await p.waitForFunction(() => Object.keys(CAT.referencias).length > 0, null, { timeout: 60000 });
  await p.waitForTimeout(1500);
  await p.evaluate(() => { window.__out = []; guardarArchivo = async (nombre, data) => { const blob = data instanceof Blob ? data : new Blob([data]); window.__out.push({ nombre, b64: (await aDataURL(blob)).split(',')[1] }); }; });
  for (const d of D) {
    await p.evaluate(async d => { S.colores = 'reales'; S.filtro = 'todo'; await restaurar(JSON.parse(JSON.stringify(d))); }, d);
    await p.waitForTimeout(700);
    const tareas = [['pdf', 'reales', 'todo', '.pdf'], ['png', 'quien', 'todo', '_quien-imprime.png'], ['png', 'reales', 'todo', '_tintas.png']];
    if (d.id.startsWith('ref_')) tareas.push(['png', 'reales', 'planta', '_solo-planta.png']);
    for (const [fmt, col, fil, suf] of tareas) {
      await p.evaluate(async ([fmt, col, fil]) => { S.colores = col; S.filtro = fil; render(); window.__out = []; await exportar(fmt); }, [fmt, col, fil]);
      const o = await p.evaluate(() => window.__out);
      if (!o.length) { errs.push('sin archivo ' + d.id + suf); continue; }
      fs.writeFileSync(path.join(outDir, d.id + suf), Buffer.from(o[0].b64, 'base64'));
    }
    // vista 3D
    await p.evaluate(() => { S.colores = 'reales'; S.filtro = 'todo'; S.rot = { x: -16, y: -36 }; render(); aplicarRot(); });
    await p.waitForTimeout(500);
    const esc = await p.$('#escena'); if (esc) await esc.screenshot({ path: path.join(outDir, d.id + '_3d.png') });
    console.log('ok', d.id);
  }
  console.log(errs.join('\n') || 'sin errores');
  await b.close();
})();
