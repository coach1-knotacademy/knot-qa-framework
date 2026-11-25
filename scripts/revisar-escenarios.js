// S7 · Revisa los .feature de especificaciones/ con las reglas de la lista de cotejo.
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
let errores = 0;
for (const archivo of archivos) {
  console.log(`\n${archivo}`);
  for (const e of revisar(fs.readFileSync(path.resolve(RAIZ, archivo), 'utf8'))) {
    console.log(`  Escenario (línea ${e.linea}): ${e.titulo}`);
    for (const h of e.hallazgos) {
      console.log(`    ${ICONO[h.nivel]} ${h.texto}`);
      if (h.nivel === 'error') errores += 1;
    }
  }
}
console.log(errores ? `\n${errores} cosa(s) por corregir.` : '\nTodo en orden.');
// No termina en error: es una ayuda para revisar, no una puerta. Lo que no puede saber lo decide la persona.
