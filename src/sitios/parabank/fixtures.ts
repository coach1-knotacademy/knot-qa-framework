/**
 * FIXTURES de ParaBank (S5): las piezas que recibe cada prueba, ya armadas.
 * Lo nuevo es "clienteNuevo": cada prueba recibe un cliente recién creado por la fábrica,
 * así ninguna depende de los datos de otra (ni de los del resto del mundo).
 */
import { test as base } from '@playwright/test';
import { ClienteParaBank, ClienteRegistrado } from './ClienteParaBank';
import { entornoParaBank } from './entorno';
import { fabricaDeClientes } from './fabricaDeClientes';
import { PaginaAbrirCuenta } from './paginas/PaginaAbrirCuenta';
import { PaginaIngreso } from './paginas/PaginaIngreso';
import { PaginaPagarFactura } from './paginas/PaginaPagarFactura';
import { PaginaPrestamo } from './paginas/PaginaPrestamo';
import { PaginaResumen } from './paginas/PaginaResumen';
import { PaginaTransferirParaBank } from './paginas/PaginaTransferir';

interface PiezasParaBank {
  /** Pausa de cortesía al terminar cada prueba (se activa sola). */
  cortesiaConElSitio: void;
  /** La capa de API de ParaBank. */
  parabank: ClienteParaBank;
  /** Un cliente creado por la fábrica para esta corrida (la prueba todavía no ha entrado por la pantalla). */
  clienteNuevo: ClienteRegistrado;
  /** El mismo cliente, con la sesión ya abierta en la pestaña del navegador. */
  clienteEnSesion: ClienteRegistrado;
  ingreso: PaginaIngreso;
  resumen: PaginaResumen;
  abrirCuenta: PaginaAbrirCuenta;
  transferir: PaginaTransferirParaBank;
  pagarFactura: PaginaPagarFactura;
  prestamo: PaginaPrestamo;
}

/** Lo que se comparte entre las pruebas de un mismo proceso (worker). */
interface PiezasDelWorker {
  clienteDeLaCorrida: ClienteRegistrado;
}

export const test = base.extend<PiezasParaBank, PiezasDelWorker>({
  /**
   * Un cliente NUEVO por cada proceso de pruebas, creado por la fábrica.
   * ¿Por qué no uno por prueba? Porque ParaBank tiene un límite real de peticiones (HTTP 429).
   * Registrar 15 clientes seguidos nos bloqueó 5 minutos. El diseño se adapta al sistema:
   * un cliente por corrida y cada prueba abre SUS PROPIAS cuentas, así no se pisan.
   */
  clienteDeLaCorrida: [
    async ({ playwright }, usar, workerInfo) => {
      const contexto = await playwright.request.newContext({ baseURL: workerInfo.project.use.baseURL });
      await usar(await new ClienteParaBank(contexto).registrar(fabricaDeClientes.nuevo()));
      await contexto.dispose();
    },
    { scope: 'worker' },
  ],
  /**
   * CORTESÍA con un sitio compartido: una pausa al terminar cada prueba (5 s, en entornoParaBank).
   * Así la suite completa queda por debajo del límite de peticiones de ParaBank, también desde
   * GitHub Actions, que comparte su dirección de internet con otros usuarios del sitio.
   * Se activa sola (auto: true); ninguna prueba la tiene que pedir.
   */
  cortesiaConElSitio: [
    async ({}, usar) => {
      await usar();
      await new Promise((listo) => setTimeout(listo, entornoParaBank.pausaEntrePruebasMs));
    },
    { auto: true },
  ],
  parabank: async ({ request }, usar) => {
    await usar(new ClienteParaBank(request));
  },
  clienteNuevo: async ({ clienteDeLaCorrida }, usar) => {
    await usar(clienteDeLaCorrida);
  },
  clienteEnSesion: async ({ page, clienteDeLaCorrida }, usar) => {
    // page.request comparte las cookies con la pestaña: entrar aquí deja la sesión abierta en el navegador.
    await new ClienteParaBank(page.request).iniciarSesionWeb(clienteDeLaCorrida.usuario, clienteDeLaCorrida.clave);
    await usar(clienteDeLaCorrida);
  },
  ingreso: async ({ page }, usar) => usar(new PaginaIngreso(page)),
  resumen: async ({ page }, usar) => usar(new PaginaResumen(page)),
  abrirCuenta: async ({ page }, usar) => usar(new PaginaAbrirCuenta(page)),
  transferir: async ({ page }, usar) => usar(new PaginaTransferirParaBank(page)),
  pagarFactura: async ({ page }, usar) => usar(new PaginaPagarFactura(page)),
  prestamo: async ({ page }, usar) => usar(new PaginaPrestamo(page)),
});

export { expect } from '@playwright/test';
