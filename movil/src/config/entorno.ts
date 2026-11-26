/**
 * CAPA DE CONFIGURACIÓN (la misma idea que src/config/entorno.ts del framework de Playwright).
 *
 * Aquí se decide UNA vez dónde está el servidor de Appium, qué dispositivo se usa y qué app se instala.
 * Nada de eso va escrito en las pruebas ni en las páginas: si mañana cambia el puerto o el emulador,
 * se cambia una variable y no se toca el código.
 *
 * Orden de prioridad: lo que escribas en la terminal ($env:DISPOSITIVO = '...') > el archivo .env > el valor por omisión.
 */
import * as fs from 'node:fs';
import * as path from 'node:path';

// movil/ (esta carpeta está en movil/src/config/).
export const RAIZ_MOVIL = path.resolve(import.meta.dirname, '..', '..');

// Si hay un .env en movil/, se carga. Nunca se sube (está en .gitignore). Si no hay, no pasa nada.
try {
  process.loadEnvFile(path.join(RAIZ_MOVIL, '.env'));
} catch {
  // Sin archivo .env: se usan la terminal y los valores por omisión.
}

function leer(nombre: string, porOmision: string): string {
  const valor = process.env[nombre]?.trim();
  return valor ? valor : porOmision;
}

function numero(nombre: string, porOmision: number): number {
  const texto = leer(nombre, String(porOmision));
  const valor = Number(texto);
  if (!Number.isInteger(valor) || valor <= 0) {
    throw new Error(`La variable ${nombre} debe ser un número entero positivo y vale «${texto}».`);
  }
  return valor;
}

const rutaApp = path.resolve(RAIZ_MOVIL, leer('RUTA_APP', path.join('apps', 'mda-2.3.0-27.apk')));

export const entorno = {
  /** Servidor de Appium: es un programa aparte que se deja corriendo (npm.cmd run appium). */
  host: leer('APPIUM_HOST', '127.0.0.1'),
  puerto: numero('APPIUM_PUERTO', 4723),
  /** El nombre que muestra «adb devices». */
  dispositivo: leer('DISPOSITIVO', 'emulator-5554'),
  /** Opcional. Vacío = la que tenga el dispositivo. */
  versionAndroid: leer('VERSION_ANDROID', ''),
  rutaApp,
  /** La app de práctica: paquete Android (sirve para limpiarla entre pruebas). */
  paquete: 'com.saucelabs.mydemoapp.android',
  /** El primer arranque instala dos apps de Appium en el dispositivo: en equipos lentos tarda. */
  tiempoArranque: numero('TIEMPO_ARRANQUE', 120_000),
  /**
   * Pausa extra después de cada paso, en milisegundos (0 = a toda velocidad).
   * Solo para grabar una demo que se pueda seguir con los ojos: como slowMo en Playwright.
   */
  pasoLento: Number(leer('PASO_LENTO', '0')) || 0,
  /** Dónde quedan capturas y videos de cada corrida. */
  carpetaEvidencias: path.join(RAIZ_MOVIL, 'evidencias'),
} as const;

/** Falla temprano y en español si falta el APK, en vez de un error largo de Appium. */
export function verificarApp(): void {
  if (!fs.existsSync(entorno.rutaApp)) {
    throw new Error(
      `No encuentro la app en ${entorno.rutaApp}.\n` +
      '  Bájala con:  npm.cmd run app   (en macOS: npm run app)\n' +
      '  O cambia la ruta con la variable RUTA_APP (ver .env.ejemplo).',
    );
  }
}

/**
 * Las CAPACIDADES: lo que el cliente le pide al servidor de Appium al abrir la sesión.
 * Es el equivalente de "abrir el navegador" en Playwright, pero en un celular.
 * Están en UN solo lugar: wdio.conf.ts las toma de aquí.
 */
export function capacidades(): WebdriverIO.Capabilities {
  return {
    platformName: 'Android',
    'appium:automationName': 'UiAutomator2',
    'appium:deviceName': entorno.dispositivo,
    'appium:udid': entorno.dispositivo,
    ...(entorno.versionAndroid ? { 'appium:platformVersion': entorno.versionAndroid } : {}),
    'appium:app': entorno.rutaApp,
    'appium:appWaitActivity': '*',
    // Acepta solo los permisos que pida la app (cámara, ubicación): sin ventanas que tapen la prueba.
    'appium:autoGrantPermissions': true,
    // Si no llega ningún comando en 5 minutos, Appium cierra la sesión (no deja el celular "tomado").
    'appium:newCommandTimeout': 300,
    'appium:uiautomator2ServerLaunchTimeout': entorno.tiempoArranque,
    'appium:uiautomator2ServerInstallTimeout': entorno.tiempoArranque,
    'appium:adbExecTimeout': 60_000,
  };
}
