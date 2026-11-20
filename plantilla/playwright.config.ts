import { defineConfig, devices } from '@playwright/test';
import { canalDelNavegador, entorno } from './src/config/entorno';

/**
 * Configuración de Playwright. La dirección del sistema sale de src/config/entorno.ts, nunca de aquí.
 */
export default defineConfig({
  testDir: 'tests',
  // Una prueba en rojo es un hallazgo o un error de la prueba: no se reintenta.
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  // El reporte dice contra qué ambiente se corrió. Nunca la clave: el reporte se comparte.
  metadata: { ambiente: entorno.nombre, 'dirección': entorno.urlBase },
  use: {
    ...devices['Desktop Chrome'],
    baseURL: entorno.urlBase,
    channel: canalDelNavegador,
    screenshot: 'only-on-failure',
    // OJO: el trace guarda lo que se escribió en la pantalla, incluida la clave. Si viene de un sistema
    // real, no lo publiques ni lo pegues en un chat o en la IA.
    trace: 'retain-on-failure',
  },
});
