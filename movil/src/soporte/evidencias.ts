/**
 * EVIDENCIA AUTOMÁTICA: una captura por cada paso del escenario, otra si algo falla, y un video
 * de cada prueba. Todo queda en movil/evidencias/corrida-<fecha>/<CP>/ sin que la prueba lo pida.
 *
 * Es lo mismo que screenshot: 'on' y video: 'on' en playwright.config.ts, pero escrito a mano:
 * en Appium el cliente le pide al servidor la imagen (driver.saveScreenshot) y el video
 * (driver.startRecordingScreen / stopRecordingScreen, que en Android usa el grabador del propio celular).
 */
import * as fs from 'node:fs';
import * as path from 'node:path';
import { driver } from '@wdio/globals';
import { entorno } from '../config/entorno';

/** Una carpeta por corrida. La fecha se fija una vez (en wdio.conf.ts) para que todas las pruebas usen la misma. */
export function carpetaDeLaCorrida(): string {
  const nombre = process.env.KNOT_CORRIDA ?? 'corrida-sin-fecha';
  return path.join(entorno.carpetaEvidencias, nombre);
}

/** "@CP-401 Escenario: ..." → "CP-401". Si no hay etiqueta, el título en minúsculas y sin espacios. */
function nombreDeCarpeta(titulo: string): string {
  const cp = titulo.match(/CP-\d+/);
  return cp ? cp[0] : titulo.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40);
}

function nombreDeArchivo(texto: string): string {
  return texto
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
}

// Estado de la prueba que está corriendo (Mocha corre una a la vez en este kit).
let carpetaActual = '';
let numeroDePaso = 0;
let bitacora: string[] = [];

export function empezarPrueba(titulo: string): void {
  carpetaActual = path.join(carpetaDeLaCorrida(), nombreDeCarpeta(titulo));
  fs.mkdirSync(carpetaActual, { recursive: true });
  numeroDePaso = 0;
  bitacora = [titulo];
}

export async function capturar(nombre: string): Promise<string> {
  const archivo = path.join(carpetaActual, `${nombre}.png`);
  await driver.saveScreenshot(archivo);
  return archivo;
}

/**
 * Un PASO del escenario (como test.step de Playwright): se escribe en la consola con el texto
 * del Gherkin, se ejecuta y deja su captura numerada: 01-dado-que-...png, 02-cuando-...png
 */
export async function paso(texto: string, accion: () => Promise<void>): Promise<void> {
  numeroDePaso++;
  const numero = String(numeroDePaso).padStart(2, '0');
  try {
    await accion();
    if (entorno.pasoLento) await driver.pause(entorno.pasoLento);
    bitacora.push(`  ✓ ${texto}`);
    console.log(`  ✓ ${texto}`);
  } catch (error) {
    bitacora.push(`  ✗ ${texto}`);
    console.log(`  ✗ ${texto}`);
    throw error;
  } finally {
    // Medio segundo para que termine la animación de la pantalla: es para que la FOTO salga bien,
    // no para sincronizar la prueba (eso lo hacen los waitForDisplayed y los expect, que esperan solos).
    await driver.pause(500);
    await capturar(`${numero}-${nombreDeArchivo(texto)}`).catch(() => undefined);
  }
}

export async function iniciarVideo(): Promise<void> {
  // Resolución a la mitad y poca tasa de bits: un video de 20 s pesa ~1 MB y se ve bien.
  await driver.startRecordingScreen({ videoSize: '540x1200', bitRate: 1_500_000, timeLimit: 180 });
}

export async function terminarPrueba(paso: boolean, error?: Error): Promise<void> {
  if (!paso) {
    await capturar('FALLO').catch(() => undefined);
    bitacora.push(`  FALLÓ: ${error?.message.replace(/\s+/g, ' ').trim().slice(0, 300) ?? 'sin mensaje'}`);
  }
  try {
    // El grabador de Android solo guarda cuadros cuando la pantalla cambia: un segundo más para que
    // el video alcance a mostrar la última pantalla (el resultado) antes de cortarse.
    await driver.pause(1_000);
    const video = await driver.stopRecordingScreen();
    if (video) fs.writeFileSync(path.join(carpetaActual, 'video.mp4'), Buffer.from(video, 'base64'));
  } catch (e) {
    bitacora.push(`  (no se pudo guardar el video: ${(e as Error).message.split('\n')[0]})`);
  }
  fs.writeFileSync(path.join(carpetaActual, 'pasos.txt'), bitacora.join('\n') + '\n', 'utf8');
}
