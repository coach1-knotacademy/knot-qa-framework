// Baja la app de práctica (SauceLabs My Demo App para Android) a movil/apps/.
// Es una app PÚBLICA hecha para practicar automatización: no es de ningún banco y no maneja dinero real.
// Funciona igual en Windows, macOS y Linux: solo usa Node (sin curl, sin PowerShell, sin bash).
//
//   node scripts/descargar-app.js            (o: npm run app  /  npm.cmd run app en PowerShell)
//
// Detrás de un proxy corporativo: Node 22 NO lee el proxy del sistema por sí solo.
//   - Si TI te da el proxy:   $env:HTTPS_PROXY = 'http://proxy.empresa:8080'   (y se usa aquí)
//   - Si el proxy inspecciona SSL: $env:NODE_EXTRA_CA_CERTS = 'C:\ruta\certificado-de-ti.pem'
//   - Si nada funciona: baja el APK desde el navegador (URL de abajo) y déjalo en movil/apps/ con el mismo nombre.
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const crypto = require('crypto');
const tls = require('tls');

// Versión FIJA: si la app cambia, las pruebas no se rompen por sorpresa. Para cambiarla, se cambian las dos líneas.
const VERSION = '2.3.0';
const ARCHIVO = 'mda-2.3.0-27.apk';
const URL_APK = `https://github.com/saucelabs/my-demo-app-android/releases/download/${VERSION}/${ARCHIVO}`;
const TAMANO_ESPERADO = 18239748; // bytes, según la página de releases de GitHub

const CARPETA = path.join(__dirname, '..', 'apps');
const DESTINO = path.join(CARPETA, ARCHIVO);

function conProxy(url) {
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  if (!proxy) return null;
  return new URL(proxy);
}

// Pide una URL y sigue las redirecciones (GitHub manda a otro servidor para el archivo).
function bajar(url, saltos = 0) {
  return new Promise((resolve, reject) => {
    if (saltos > 5) return reject(new Error('Demasiadas redirecciones.'));
    const destino = new URL(url);
    const proxy = conProxy(url);
    const alListo = (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location) {
        res.resume();
        return resolve(bajar(new URL(res.headers.location, url).toString(), saltos + 1));
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`El servidor respondió ${res.statusCode} para ${url}`));
      }
      resolve(res);
    };
    if (!proxy) {
      https.get(destino, { headers: { 'User-Agent': 'descargar-app' } }, alListo).on('error', reject);
      return;
    }
    // Túnel por el proxy (CONNECT), sin librerías extra.
    const pedido = http.request({
      host: proxy.hostname,
      port: proxy.port || 8080,
      method: 'CONNECT',
      path: `${destino.hostname}:443`,
      headers: proxy.username ? { 'Proxy-Authorization': 'Basic ' + Buffer.from(`${decodeURIComponent(proxy.username)}:${decodeURIComponent(proxy.password)}`).toString('base64') } : {},
    });
    pedido.on('connect', (res, socket) => {
      if (res.statusCode !== 200) return reject(new Error(`El proxy respondió ${res.statusCode}`));
      https.get(destino, {
        agent: false,
        createConnection: () => tls.connect({ socket, servername: destino.hostname }),
        headers: { 'User-Agent': 'descargar-app' },
      }, alListo).on('error', reject);
    });
    pedido.on('error', reject);
    pedido.end();
  });
}

async function main() {
  fs.mkdirSync(CARPETA, { recursive: true });
  if (fs.existsSync(DESTINO) && fs.statSync(DESTINO).size === TAMANO_ESPERADO) {
    console.log(`Ya está: ${path.relative(process.cwd(), DESTINO)} (${(TAMANO_ESPERADO / 1e6).toFixed(1)} MB). No se baja de nuevo.`);
    return;
  }
  console.log(`Bajando la app de práctica ${VERSION}...\n  ${URL_APK}`);
  const res = await bajar(URL_APK);
  const temporal = DESTINO + '.parcial';
  const hash = crypto.createHash('sha256');
  let bytes = 0;
  await new Promise((resolve, reject) => {
    const salida = fs.createWriteStream(temporal);
    res.on('data', (trozo) => { bytes += trozo.length; hash.update(trozo); });
    res.pipe(salida);
    salida.on('finish', resolve);
    res.on('error', reject);
    salida.on('error', reject);
  });
  if (bytes !== TAMANO_ESPERADO) {
    fs.rmSync(temporal, { force: true });
    throw new Error(`El archivo llegó incompleto o es otro (${bytes} bytes, se esperaban ${TAMANO_ESPERADO}). ` +
      'Si estás detrás de un proxy, puede que te haya devuelto una página de bloqueo: pídele a TI que permita github.com.');
  }
  fs.renameSync(temporal, DESTINO);
  console.log(`Listo: ${path.relative(process.cwd(), DESTINO)} (${(bytes / 1e6).toFixed(1)} MB, sha256 ${hash.digest('hex').slice(0, 16)}...)`);
}

main().catch((error) => {
  console.error(`\nNo se pudo bajar la app: ${error.message}`);
  console.error(`Plan B: ábrela en el navegador, guárdala en movil/apps/${ARCHIVO} y vuelve a correr las pruebas.`);
  console.error(`  ${URL_APK}`);
  process.exit(1);
});
