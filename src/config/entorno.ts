/**
 * CAPA DE CONFIGURACIÓN: dónde están el sistema y las credenciales de prueba.
 *
 * Desde la S6 el valor sale de un AMBIENTE (local, qa o uat), como los "environments" de Postman.
 * El catálogo y los controles están en ambientes.ts; aquí solo se lee la terminal UNA vez.
 * Si no dices nada, se usa "local": el Banco Demo de tu equipo, como siempre.
 *
 * Ejemplo en PowerShell, solo para esa terminal:
 *   $env:AMBIENTE = 'qa'
 *   $env:CLAVE_BANCO = '...'
 *   npm.cmd test
 *
 * La forma no cambió (entorno.urlBase, entorno.usuario, entorno.clave): nada del resto del repo se entera.
 * SINGLETON (S5): un módulo se carga una sola vez, así que hay UNA configuración para toda la corrida.
 */
import * as path from 'path';
import { configurarAmbiente, leer } from './ambientes';

// Si existe un archivo .env en la raíz del repo, sus valores se cargan aquí. El .env NUNCA se sube
// (está en .gitignore); el modelo sin valores es .env.ejemplo. Lo que escribas en la terminal ($env:...)
// manda sobre el archivo. Si no hay .env (lo normal en clase), no pasa nada.
try {
  process.loadEnvFile(path.join(__dirname, '..', '..', '.env'));
} catch {
  // Sin archivo .env: se usan la terminal y los valores del catálogo.
}

export const entorno = configurarAmbiente(leer(process.env, 'AMBIENTE') ?? 'local', process.env);
