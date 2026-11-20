import { defineConfig, devices } from '@playwright/test';
import { entorno } from './src/config/entorno';
import { entornoParaBank } from './src/sitios/parabank/entorno';

/**
 * Configuración de Playwright. Cada carpeta de tests/ es un "proyecto":
 *   npx playwright test --project=ui
 * Cada proyecto dice su carpeta (testDir): plantilla/ (S6) es un framework aparte y no entra aquí.
 */

// Lo que comparten las pruebas que abren navegador.
const conNavegador = {
  ...devices['Desktop Chrome'],
  baseURL: entorno.urlBase,
  // En equipos que no dejan descargar Chromium: PW_CHANNEL=msedge usa el Edge instalado.
  channel: process.env.PW_CHANNEL,
  screenshot: 'on' as const,
  trace: 'retain-on-failure' as const,
};

// Proyectos pedidos en la línea de comandos (--project=ui o --project ui).
const pedidos = process.argv.flatMap((a, i, todos) => (a.startsWith('--project=') ? [a.slice(10)] : a === '--project' ? [todos[i + 1]] : []));

// ParaBank (S5) es un sitio real en internet: solo corre si se pide (npm run parabank).
// La marca queda en una variable de entorno para que los procesos de Playwright la vean igual.
if (pedidos.includes('parabank')) process.env.KNOT_PARABANK = '1';
const conParaBank = process.env.KNOT_PARABANK === '1';

// Estos proyectos no usan el Banco Demo: si solo corres esos, no se inicia.
const SIN_BANCO_DEMO = ['unidad', 'retos-s05', 'retos-s06', 'parabank'];
const soloUnidad = pedidos.length > 0 && pedidos.every((p) => SIN_BANCO_DEMO.includes(p));
// S6 · Fuera de "local" (AMBIENTE=qa o uat) el sistema ya existe en otro lado: no se inicia el Banco Demo.
const sinServidorLocal = soloUnidad || entorno.nombre !== 'local';

export default defineConfig({
  // Uno a la vez: varias pruebas leen el mismo buzón de SMS y así no se cruzan los códigos.
  workers: 1,
  // Una prueba en rojo es un hallazgo o un error de la prueba: no se reintenta.
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }], ['json', { outputFile: 'resultados.json' }]],
  // S6 · El reporte dice contra qué ambiente se corrió. Nunca la clave: el reporte se comparte.
  metadata: { ambiente: entorno.nombre, 'dirección': entorno.urlBase },

  // Banco Demo: se inicia solo y no necesita internet.
  webServer: sinServidorLocal
    ? undefined
    : {
        command: 'node banco-demo/server.js',
        url: `${entorno.urlBase}/api/salud`,
        reuseExistingServer: true,
        timeout: 60_000,
      },

  projects: [
    // S3 · Así se escribe al empezar: todo dentro de la prueba.
    { name: 'antes', testDir: 'tests/antes', use: conNavegador },
    // Pruebas que usan las capas.
    { name: 'ui', testDir: 'tests/ui', use: conNavegador },
    { name: 'api', testDir: 'tests/api', use: { baseURL: entorno.urlBase } },
    { name: 'migracion', testDir: 'tests/migracion', use: { baseURL: entorno.urlBase } },
    // S3 · Retos de clases y capas.
    { name: 'retos-s03', testDir: 'tests/retos-s03', use: conNavegador },
    // S4 · Retos de SOLID: pruebas de unidad, sin navegador y sin servidor.
    { name: 'unidad', testDir: 'tests/retos-s04' },
    // S5 · Recargas a celular: Page Object, Factory y bloqueos reales (código, límite, operador caído).
    { name: 'recargas', testDir: 'tests/recargas', use: conNavegador },
    // S5 · Retos de patrones: fábrica de datos y una tarea de Screenplay. Sin navegador ni servidor.
    { name: 'retos-s05', testDir: 'tests/retos-s05' },
    // S6 · Reto 1, ambientes: pruebas de unidad de la configuración. Sin navegador ni servidor.
    { name: 'retos-s06', testDir: 'tests/retos-s06', testIgnore: /reto2-/ },
    // S6 · Reto 2, localizadores robustos: con navegador, contra Recargas de hoy y la del rediseño.
    { name: 'retos-s06-ui', testDir: 'tests/retos-s06', testMatch: /reto2-.*\.spec\.ts/, use: conNavegador },
    // S5 · ParaBank, un banco de práctica real en internet. Se graba todo: video, pantallazos y trace.
    // Un solo proceso a la vez: el sitio corta a quien hace demasiadas peticiones (HTTP 429).
    ...(conParaBank
      ? [{
          name: 'parabank',
          testDir: 'tests/parabank',
          timeout: 60_000,
          use: {
            ...devices['Desktop Chrome'],
            baseURL: entornoParaBank.urlBase,
            channel: process.env.PW_CHANNEL,
            screenshot: 'on' as const,
            trace: 'on' as const,
            video: 'on' as const,
            actionTimeout: 15_000,
            // Más despacio a propósito: el video se puede seguir y no se pasa el límite de peticiones (HTTP 429).
            launchOptions: { slowMo: 250 },
          },
        }]
      : []),
  ],
});
