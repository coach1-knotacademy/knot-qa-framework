// Integraciones · Lleva el resultado de la corrida a las tarjetas de Trello: «del reporte al ticket».
//
// Lee resultados.json (el reporte JSON que ya genera Playwright), busca el ID del caso (@CP-xxx) de cada prueba
// y, por cada CP, comenta en la tarjeta de Trello cuyo nombre empieza con ese ID, y la mueve a la lista
// «Verde» o «Rojo». Así el líder ve el estado en el tablero, sin abrir el reporte.
//
// Uso:
//   npx.cmd playwright test --project=toolshop          (genera resultados.json)
//   node scripts/reportar-a-trello.js                    ENSAYO: muestra lo que haría, no toca Trello
//   node scripts/reportar-a-trello.js --publicar         publica (necesita las claves en .env)
//
// Claves (en .env, que nunca se sube): TRELLO_KEY, TRELLO_TOKEN y TRELLO_TABLERO (el id corto del tablero, el de la URL).
// Se sacan en https://trello.com/power-ups/admin (API key) y con el enlace «Token» de esa misma página.
// En Jira con Xray la idea es la misma: se importa el resultado (JUnit o JSON) a la ejecución de prueba de cada caso.
const fs = require('fs');
const path = require('path');

const RAIZ = path.join(__dirname, '..');
const publicar = process.argv.includes('--publicar');

function leerEnv() {
  const archivo = path.join(RAIZ, '.env');
  const vars = {};
  if (fs.existsSync(archivo)) {
    for (const linea of fs.readFileSync(archivo, 'utf8').split(/\r?\n/)) {
      const m = linea.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m && m[2]) vars[m[1]] = m[2];
    }
  }
  return { ...vars, ...process.env };
}

// Recorre el reporte JSON de Playwright y junta, por CP, el estado y la duración.
function casosDelReporte() {
  const archivo = path.join(RAIZ, 'resultados.json');
  if (!fs.existsSync(archivo)) throw new Error('No encuentro resultados.json: corre primero las pruebas (npx.cmd playwright test ...).');
  const reporte = JSON.parse(fs.readFileSync(archivo, 'utf8'));
  const casos = new Map();
  const recorrer = (suite) => {
    for (const s of suite.suites || []) recorrer(s);
    for (const spec of suite.specs || []) {
      const ids = new Set([...(spec.tags || []).map((t) => t.replace(/^@/, '')), ...(spec.title.match(/CP-\d+/g) || [])]);
      for (const id of [...ids].filter((x) => /^CP-\d+$/.test(x))) {
        for (const prueba of spec.tests || []) {
          const r = (prueba.results || [])[prueba.results.length - 1] || {};
          const previo = casos.get(id);
          const estado = prueba.status === 'expected' ? 'verde' : prueba.status === 'skipped' ? 'omitida' : 'rojo';
          const error = (r.error && r.error.message ? r.error.message : '').split('\n')[0].replace(/\u001b\[[0-9;]*m/g, '');
          // Si un CP tiene varias pruebas, manda el peor estado.
          if (!previo || estado === 'rojo') casos.set(id, { id, titulo: spec.title, proyecto: prueba.projectName, estado, ms: r.duration || 0, error });
        }
      }
    }
  };
  for (const suite of reporte.suites || []) recorrer(suite);
  return [...casos.values()].sort((a, b) => a.id.localeCompare(b.id));
}

function comentario(c) {
  const icono = c.estado === 'verde' ? '✅' : c.estado === 'rojo' ? '❌' : '⏭️';
  const lineas = [
    `${icono} ${c.id} · ${c.estado.toUpperCase()} (${(c.ms / 1000).toFixed(1)} s) · proyecto ${c.proyecto}`,
    `Prueba: ${c.titulo}`,
  ];
  if (c.error) lineas.push(`Error: ${c.error.slice(0, 300)}`, '¿Rojo del sistema, del script o del ambiente? Revisa el trace en el reporte.');
  lineas.push(`Corrida: ${new Date().toISOString()} · reporte: playwright-report/index.html`);
  return lineas.join('\n');
}

async function trello(env, metodo, ruta, parametros = {}) {
  const url = new URL(`https://api.trello.com/1${ruta}`);
  for (const [k, v] of Object.entries({ ...parametros, key: env.TRELLO_KEY, token: env.TRELLO_TOKEN })) url.searchParams.set(k, v);
  const r = await fetch(url, { method: metodo });
  if (!r.ok) throw new Error(`Trello respondió ${r.status} en ${metodo} ${ruta}`);
  return r.json();
}

(async () => {
  const casos = casosDelReporte();
  if (!casos.length) { console.log('El reporte no tiene pruebas con @CP-xxx: nada que reportar.'); return; }

  if (!publicar) {
    console.log(`ENSAYO (no se toca Trello). Con --publicar se comentaría en ${casos.length} tarjeta(s):\n`);
    for (const c of casos) console.log(`→ tarjeta «${c.id} …» · mover a ${c.estado === 'verde' ? '«3 · Verde»' : '«4 · Rojo»'}\n${comentario(c).replace(/^/gm, '   ')}\n`);
    return;
  }

  const env = leerEnv();
  for (const k of ['TRELLO_KEY', 'TRELLO_TOKEN', 'TRELLO_TABLERO']) if (!env[k]) throw new Error(`Falta ${k} en .env (o en la terminal). Ver el comentario al inicio de este archivo.`);
  const tarjetas = await trello(env, 'GET', `/boards/${env.TRELLO_TABLERO}/cards`, { fields: 'name,idList' });
  const listas = await trello(env, 'GET', `/boards/${env.TRELLO_TABLERO}/lists`, { fields: 'name' });
  const lista = (prefijo) => listas.find((l) => l.name.startsWith(prefijo));
  for (const c of casos) {
    const tarjeta = tarjetas.find((t) => t.name.startsWith(c.id));
    if (!tarjeta) { console.log(`· ${c.id}: no hay tarjeta en el tablero, se omite`); continue; }
    await trello(env, 'POST', `/cards/${tarjeta.id}/actions/comments`, { text: comentario(c) });
    const destino = c.estado === 'verde' ? lista('3') : c.estado === 'rojo' ? lista('4') : null;
    if (destino) await trello(env, 'PUT', `/cards/${tarjeta.id}`, { idList: destino.id });
    console.log(`✓ ${c.id}: comentado${destino ? ` y movido a «${destino.name}»` : ''}`);
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
