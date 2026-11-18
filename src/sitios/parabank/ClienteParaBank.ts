/**
 * CAPA DE API de ParaBank (S5): habla con sus servicios REST, como lo harías en Postman.
 *   https://parabank.parasoft.com/parabank/services/bank/...
 * Pide JSON con el encabezado Accept. Las rutas no empiezan con "/" para que se sumen a la urlBase.
 */
import { APIRequestContext } from '@playwright/test';
import { DatosDeCliente } from './fabricaDeClientes';

export type TipoDeCuenta = 'CHECKING' | 'SAVINGS';

export interface CuentaParaBank {
  id: number;
  customerId: number;
  type: TipoDeCuenta | 'LOAN';
  balance: number;
}

export interface Movimiento {
  id: number;
  accountId: number;
  type: 'Credit' | 'Debit';
  amount: number;
  description: string;
}

/** Un cliente que ya existe en ParaBank: sus datos, su número de cliente y su primera cuenta. */
export interface ClienteRegistrado extends DatosDeCliente {
  id: number;
  cuentaPrincipal: number;
}

const JSON_POR_FAVOR = { Accept: 'application/json' };

/**
 * BLOQUEO REAL: ParaBank está detrás de Cloudflare, que corta a quien hace demasiadas peticiones
 * seguidas (HTTP 429 "Too Many Requests") y dice cuántos segundos esperar (Retry-After).
 * En vez de un error raro, la prueba falla con un mensaje que explica qué pasó.
 */
export function revisarLimite<T extends { status(): number; headers(): Record<string, string> }>(respuesta: T): T {
  if (respuesta.status() === 429) {
    const espera = respuesta.headers()['retry-after'] ?? '?';
    throw new Error(`ParaBank nos frenó: HTTP 429 (demasiadas peticiones, lo bloquea Cloudflare). Hay que esperar ${espera} segundos. No es un bug de la prueba ni del banco: es la protección del sitio.`);
  }
  return respuesta;
}

export class ClienteParaBank {
  private readonly request: Pick<APIRequestContext, 'get' | 'post'>;

  constructor(request: APIRequestContext) {
    // Toda petición pasa por revisarLimite: si Cloudflare nos frena, el error lo dice claro.
    this.request = {
      get: async (url, opciones) => revisarLimite(await request.get(url, opciones)),
      post: async (url, opciones) => revisarLimite(await request.post(url, opciones)),
    };
  }

  /**
   * Registra al cliente con el mismo formulario de la pantalla (ParaBank no tiene servicio de registro).
   * Primero abre la página para recibir la cookie de sesión, como lo haría el navegador.
   */
  async registrar(datos: DatosDeCliente): Promise<ClienteRegistrado> {
    await this.request.get('register.htm');
    const respuesta = await this.request.post('register.htm', {
      form: {
        'customer.firstName': datos.nombre,
        'customer.lastName': datos.apellido,
        'customer.address.street': datos.direccion,
        'customer.address.city': datos.ciudad,
        'customer.address.state': datos.departamento,
        'customer.address.zipCode': datos.codigoPostal,
        'customer.phoneNumber': datos.telefono,
        'customer.ssn': datos.documento,
        'customer.username': datos.usuario,
        'customer.password': datos.clave,
        repeatedPassword: datos.clave,
      },
    });
    const pagina = await respuesta.text();
    if (!pagina.includes('Your account was created successfully')) {
      const motivo = pagina.match(/<span[^>]*class="error"[^>]*>([^<]+)</)?.[1] ?? `respuesta ${respuesta.status()}`;
      throw new Error(`ParaBank no registró a ${datos.usuario}: ${motivo}`);
    }
    const { datos: cliente } = await this.login(datos.usuario, datos.clave);
    const { datos: cuentas } = await this.cuentas(cliente.id);
    return { ...datos, id: cliente.id, cuentaPrincipal: cuentas[0].id };
  }

  /** Abre sesión en la PANTALLA (cookie de la pestaña) con el mismo formulario del inicio. */
  async iniciarSesionWeb(usuario: string, clave: string): Promise<void> {
    // maxRedirects: 0 → no se descarga la página siguiente: una petición menos al sitio.
    const respuesta = await this.request.post('login.htm', { form: { username: usuario, password: clave }, maxRedirects: 0 });
    if (!(respuesta.headers()['location'] ?? '').includes('overview')) throw new Error(`ParaBank no dejó entrar a ${usuario}`);
  }

  /** GET login/{usuario}/{clave}: devuelve el cliente si los datos son correctos. */
  async login(usuario: string, clave: string): Promise<{ estado: number; datos: { id: number; firstName: string } }> {
    const respuesta = await this.request.get(`services/bank/login/${usuario}/${clave}`, { headers: JSON_POR_FAVOR });
    const texto = await respuesta.text();
    return { estado: respuesta.status(), datos: respuesta.ok() ? JSON.parse(texto) : { id: 0, firstName: texto } };
  }

  /** GET customers/{id}/accounts */
  async cuentas(idCliente: number): Promise<{ estado: number; datos: CuentaParaBank[] }> {
    const respuesta = await this.request.get(`services/bank/customers/${idCliente}/accounts`, { headers: JSON_POR_FAVOR });
    return { estado: respuesta.status(), datos: await respuesta.json() };
  }

  /** Saldo de una cuenta. */
  async saldoDe(idCuenta: number): Promise<number> {
    const respuesta = await this.request.get(`services/bank/accounts/${idCuenta}`, { headers: JSON_POR_FAVOR });
    return (await respuesta.json()).balance;
  }

  /** POST createAccount: abre una cuenta nueva con plata de otra cuenta del cliente. */
  async abrirCuenta(idCliente: number, tipo: TipoDeCuenta, desde: number): Promise<CuentaParaBank> {
    const codigo = tipo === 'CHECKING' ? 0 : 1;
    const respuesta = await this.request.post(`services/bank/createAccount?customerId=${idCliente}&newAccountType=${codigo}&fromAccountId=${desde}`, { headers: JSON_POR_FAVOR });
    return respuesta.json();
  }

  /** POST transfer: mueve plata entre dos cuentas. ParaBank responde con un texto. */
  async transferir(desde: number, hacia: number, monto: number): Promise<{ estado: number; mensaje: string }> {
    const respuesta = await this.request.post(`services/bank/transfer?fromAccountId=${desde}&toAccountId=${hacia}&amount=${monto}`, { headers: JSON_POR_FAVOR });
    return { estado: respuesta.status(), mensaje: await respuesta.text() };
  }

  /** GET accounts/{id}/transactions */
  async movimientos(idCuenta: number): Promise<Movimiento[]> {
    const respuesta = await this.request.get(`services/bank/accounts/${idCuenta}/transactions`, { headers: JSON_POR_FAVOR });
    return respuesta.json();
  }
}
