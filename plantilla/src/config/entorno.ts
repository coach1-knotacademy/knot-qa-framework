/**
 * CAPA DE CONFIGURACIÓN: la terminal se lee UNA sola vez, aquí. Todo lo demás pide "entorno".
 * Sin variables se usa "demo" (el Banco Demo en GitHub Pages). En PowerShell, para esa ventana:
 *   $env:AMBIENTE = 'qa'
 *   $env:CLAVE_BANCO = '...'
 *   npm.cmd test
 * Queda congelada: entorno.usuario = 'otro' lanza un error en vez de dañar las pruebas que siguen.
 */
import { configurarAmbiente, leer } from './ambientes';

// Lo único que usamos de Node.js es process.env: con esta línea no hace falta instalar @types/node.
declare const process: { env: Record<string, string | undefined>; loadEnvFile?: (ruta: string) => void };

// Si existe un archivo .env en esta carpeta, se carga (nunca se sube: está en .gitignore). La terminal manda.
try {
  process.loadEnvFile?.('.env');
} catch {
  // Sin archivo .env: se usan la terminal y el catálogo.
}

export const entorno = configurarAmbiente(leer(process.env, 'AMBIENTE') ?? 'demo', process.env);

/** Navegador: con PW_CHANNEL=msedge usa el Edge instalado (para equipos que no dejan descargar Chromium). */
export const canalDelNavegador = leer(process.env, 'PW_CHANNEL');
