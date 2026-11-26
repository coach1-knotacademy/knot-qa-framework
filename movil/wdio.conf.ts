/**
 * Configuración de WebdriverIO: el CLIENTE que le habla al servidor de Appium.
 * (Es el playwright.config.ts de este kit: dónde están las pruebas, el reporte y la evidencia).
 *
 *   Terminal 1:  npm.cmd run appium     ← el servidor (se deja abierto)
 *   Terminal 2:  npm.cmd test           ← las pruebas
 *
 * Nada de host, puerto, dispositivo ni ruta del APK está escrito aquí: sale de src/config/entorno.ts.
 */
import { capacidades, entorno, verificarApp } from './src/config/entorno';
import { abrirAppLimpia } from './src/soporte/app';
import { empezarPrueba, iniciarVideo, terminarPrueba } from './src/soporte/evidencias';

// Una carpeta de evidencias por corrida (la ven todas las pruebas, porque se hereda del proceso principal).
const ahora = new Date();
const dos = (n: number) => String(n).padStart(2, '0');
process.env.KNOT_CORRIDA ??= `corrida-${ahora.getFullYear()}${dos(ahora.getMonth() + 1)}${dos(ahora.getDate())}-${dos(ahora.getHours())}${dos(ahora.getMinutes())}${dos(ahora.getSeconds())}`;

export const config: WebdriverIO.Config = {
  runner: 'local',
  hostname: entorno.host,
  port: entorno.puerto,
  path: '/',

  specs: ['./tests/**/*.spec.ts'],
  // Un solo celular, una prueba a la vez.
  maxInstances: 1,
  capabilities: [capacidades()],

  logLevel: 'warn',
  // Cuánto espera un $('...') a que el elemento aparezca (el auto-wait de Playwright, aquí a mano).
  waitforTimeout: 15_000,
  // El primer arranque instala el servidor de UiAutomator2 en el celular: puede tardar.
  connectionRetryTimeout: entorno.tiempoArranque + 60_000,
  connectionRetryCount: 2,

  framework: 'mocha',
  mochaOpts: { ui: 'bdd', timeout: 180_000 },
  // addConsoleLogs: los pasos del escenario (Dado/Cuando/Entonces) salen en el reporte.
  reporters: [['spec', { addConsoleLogs: true, realtimeReporting: false }]],

  /** Antes de todo: ¿está el APK? ¿responde Appium? Mejor un mensaje claro que un error de 80 líneas. */
  onPrepare: async () => {
    try {
      verificarApp();
    } catch (error) {
      console.error(`\n${(error as Error).message}\n`);
      process.exit(1);
    }
    const url = `http://${entorno.host}:${entorno.puerto}/status`;
    try {
      const respuesta = await fetch(url, { signal: AbortSignal.timeout(5_000) });
      if (!respuesta.ok) throw new Error(`respondió ${respuesta.status}`);
    } catch {
      console.error(
        `\nAppium no responde en ${url}.\n` +
        '  Abre OTRA terminal en la carpeta movil/ y deja corriendo:  npm.cmd run appium   (macOS: npm run appium)\n' +
        '  ¿Usas otro puerto? Cambia APPIUM_PUERTO (ver .env.ejemplo).\n',
      );
      process.exit(1);
    }
  },

  /** Antes de cada prueba: app limpia, carpeta de evidencias y a grabar. */
  beforeTest: async (prueba) => {
    empezarPrueba(prueba.title);
    await abrirAppLimpia();
    await iniciarVideo();
  },

  /** Después de cada prueba: captura si falló, video y la bitácora de pasos. */
  afterTest: async (_prueba, _contexto, resultado) => {
    await terminarPrueba(resultado.passed, resultado.error);
  },
};
