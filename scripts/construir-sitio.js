// Arma la carpeta sitio/ que se publica en GitHub Pages: la portada, el banco en línea, la calculadora, los laboratorios y actividades,
// las evidencias y (S6) los ambientes de práctica para Postman y la plantilla del framework.
// El banco en línea no tiene servidor: api-estatica.js hace de servidor dentro del navegador.
const fs = require('fs');
const path = require('path');

const SALIDA = 'sitio';
const BANCO = path.join(SALIDA, 'banco');
const PUBLICO = path.join('banco-demo', 'public');
fs.rmSync(SALIDA, { recursive: true, force: true });
fs.mkdirSync(BANCO, { recursive: true });

const NOMBRES = { login: 'index', otp: 'otp', inicio: 'inicio', transferir: 'transferir', recargas: 'recargas', buzon: 'buzon' };
for (const [origen, destino] of Object.entries(NOMBRES)) {
  const html = fs.readFileSync(path.join(PUBLICO, `${origen}.html`), 'utf8')
    .replace('href="/estilos.css"', 'href="estilos.css"')
    .replace('<script src="/comun.js"></script>', '<script src="reglas.js"></script><script src="api-estatica.js"></script><script src="comun.js"></script>')
    .replace(/href="\/(otp|inicio|transferir|recargas|buzon)"/g, 'href="$1.html"')
    .replace(/location\.href = '\/(otp|inicio)'/g, "location.href = '$1.html'");
  fs.writeFileSync(path.join(BANCO, `${destino}.html`), html);
}
fs.copyFileSync(path.join(PUBLICO, 'estilos.css'), path.join(BANCO, 'estilos.css'));
fs.copyFileSync(path.join(PUBLICO, 'api-estatica.js'), path.join(BANCO, 'api-estatica.js'));
fs.writeFileSync(path.join(BANCO, 'comun.js'), fs.readFileSync(path.join(PUBLICO, 'comun.js'), 'utf8').replace(/location\.href = '\/'/g, "location.href = 'index.html'"));
fs.writeFileSync(path.join(BANCO, 'reglas.js'),
  `(() => { const module = { exports: {} };\n${fs.readFileSync('banco-demo/reglas.js', 'utf8')}\nwindow.ReglasBanco = module.exports; })();\n`);

if (fs.existsSync(path.join('laboratorio', 'laboratorio_S4.html'))) fs.copyFileSync(path.join('laboratorio', 'laboratorio_S4.html'), path.join(SALIDA, 'laboratorio-s4.html'));
if (fs.existsSync(path.join('laboratorio', 'practica_extra_S4.html'))) fs.copyFileSync(path.join('laboratorio', 'practica_extra_S4.html'), path.join(SALIDA, 'practica-extra-s4.html'));
for (const [origen, destino] of [
  ['laboratorio_S5.html', 'laboratorio-s5.html'], ['actividades_S5.html', 'actividades-s5.html'],
  ['laboratorio_S6.html', 'laboratorio-s6.html'], ['actividades_S6.html', 'actividades-s6.html'], ['plantilla.html', 'plantilla.html'],
  // S7 · Gherkin con el revisor de escenarios, el kit del proyecto final y la guía de estudio (repaso opcional).
  ['actividades_S7.html', 'actividades-s7.html'], ['proyecto.html', 'proyecto.html'], ['guia_estudio.html', 'guia-estudio.html'],
]) {
  if (fs.existsSync(path.join('laboratorio', origen))) fs.copyFileSync(path.join('laboratorio', origen), path.join(SALIDA, destino));
}
// Las presentaciones de cada sesión en PDF, sin las notas del instructor (las enlaza la guía de estudio).
if (fs.existsSync('presentaciones')) fs.cpSync('presentaciones', path.join(SALIDA, 'presentaciones'), { recursive: true });
// S6 · Dos "ambientes" de práctica (QA y UAT) como archivos fijos: el mismo pedido de Postman, datos distintos.
// Sin servidor, sin datos reales y sin límite de peticiones. Y la colección y los ambientes para importar en Postman.
fs.cpSync(path.join('banco-demo', 'ambientes'), path.join(SALIDA, 'ambientes'), { recursive: true });
fs.cpSync(path.join('banco-demo', 'postman'), path.join(SALIDA, 'postman'), { recursive: true });
// S5 · El reporte de la suite de ParaBank (con videos y traces), si la corrida lo generó.
if (fs.existsSync(path.join('reporte-parabank', 'index.html'))) fs.cpSync('reporte-parabank', path.join(SALIDA, 'reportes', 'parabank'), { recursive: true });
if (fs.existsSync('evidencias.html')) fs.copyFileSync('evidencias.html', path.join(SALIDA, 'evidencias.html'));
fs.copyFileSync(path.join('banco-demo', 'calculadora.html'), path.join(SALIDA, 'calculadora.html'));
fs.copyFileSync(path.join('banco-demo', 'portada.html'), path.join(SALIDA, 'index.html'));
console.log('sitio/ listo');
