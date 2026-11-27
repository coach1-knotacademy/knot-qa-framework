// S7 y S8 · Revisa los .feature de especificaciones/ con las reglas de la lista de cotejo.
// S8 · Dice también cuántas pruebas salen de cada escenario (un Esquema da una por fila de «Ejemplos») y el total.
// Uso:  npm.cmd run revisar-escenarios            (todos)
//       npm.cmd run revisar-escenarios -- archivo.feature
const fs = require('fs');
const path = require('path');
const { revisar } = require('../laboratorio/revisor-escenarios.js');

const RAIZ = path.join(__dirname, '..');
const pedidos = process.argv.slice(2);
const archivos = pedidos.length
  ? pedidos
  : fs.readdirSync(path.join(RAIZ, 'especificaciones')).filter((a) => a.endsWith('.feature')).map((a) => path.join('especificaciones', a));

const ICONO = { ok: '✓', aviso: '!', error: '✗' };
const salen = (n) => (n === 1 ? 'sale 1 prueba' : `salen ${n} pruebas`);
let errores = 0;
let total = 0;
let escenarios = 0;
for (const archivo of archivos) {
  console.log(`\n${archivo}`);
  let delArchivo = 0;
  for (const e of revisar(fs.readFileSync(path.resolve(RAIZ, archivo), 'utf8'))) {
    console.log(`  ${e.esquema ? 'Esquema' : 'Escenario'} (línea ${e.linea}): ${e.titulo} · ${salen(e.pruebas)}`);
    for (const h of e.hallazgos) {
      console.log(`    ${ICONO[h.nivel]} ${h.texto}`);
      if (h.nivel === 'error') errores += 1;
    }
    delArchivo += e.pruebas;
    escenarios += 1;
  }
  console.log(`  En este archivo ${salen(delArchivo)}.`);
  total += delArchivo;
}
console.log(`\nEn total: ${escenarios} escenario(s) y ${salen(total)}.`);
console.log(errores ? `${errores} cosa(s) por corregir.` : 'Todo en orden.');
// No termina en error: es una ayuda para revisar, no una puerta. Lo que no puede saber lo decide la persona.
