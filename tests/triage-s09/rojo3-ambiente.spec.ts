/**
 * S9 · TRIAGE · ROJO 3 · CAJA: AMBIENTE (falta la clave)
 *
 * Este rojo NO es una prueba de este archivo, y no puede serlo: cuando falta la clave, la configuración
 * (src/config/ambientes.ts, S6) lanza un error AL CARGAR, en el segundo cero, y Playwright no corre
 * ninguna prueba. Si estuviera aquí, se caería el proyecto entero, no una prueba. Se corre aparte:
 *
 *   npm.cmd run triage:sin-clave
 *
 * (corre --project=triage contra el ambiente qa sin CLAVE_BANCO). Lo que sale en la consola:
 *
 *   Error: Falta CLAVE_BANCO para el ambiente qa. Defínela en la terminal: $env:CLAVE_BANCO = '...'
 *
 * LA EVIDENCIA ES LA CONSOLA, y también lo que NO hay: ni trace, ni captura, ni reporte. No llegó a abrir
 * el navegador. Esa ausencia dice «ambiente»: lo que la prueba necesita no está. Fallar de inmediato (S6),
 * con un mensaje que dice qué falta y cómo ponerlo, es lo correcto: es mejor que 40 pruebas en rojo con 401.
 *
 * ¿test.slow() o retries? No sirven: no hay ninguna prueba que reintentar ni que esperar.
 *
 * Si tu reto 1 de la S6 está pendiente, verás «PENDIENTE (S6): completa elegirAmbiente…» en lugar del mensaje
 * de la clave: es el mismo freno, todavía sin terminar. triage:sin-clave te muestra el mensaje real.
 *
 * Esta prueba solo está para que -g "rojo 3" diga dónde está el rojo 3, y para que el reporte lo nombre.
 */
import { test } from '@playwright/test';

test('rojo 3 · falta la clave: no corre aquí, se corre con npm.cmd run triage:sin-clave', () => {
  test.skip(true, 'Sin la clave, la configuración falla al cargar y no corre ninguna prueba (no hay trace). Se corre aparte: npm.cmd run triage:sin-clave. La evidencia es la consola: «Falta CLAVE_BANCO para el ambiente qa».');
});
