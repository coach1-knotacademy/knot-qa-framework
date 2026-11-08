/**
 * CÓDIGO HEREDADO · L de SOLID: sustitución de Liskov (LSP).
 *
 * Regla: si una clase hereda de otra, debe poder usarse en su lugar sin sorpresas.
 *
 * Aquí PaginaConsulta hereda de PaginaTransferencia solo "para reutilizar saldoDe".
 * Pero una consulta NO transfiere: su transferir() lanza un error. Cualquier código que
 * reciba "una PaginaTransferencia" puede recibir una PaginaConsulta y romperse.
 *
 * Este archivo SÍ se modifica en el reto 3 de la S4.
 */
import { Navegador } from '../navegador';

/**
 * TODO RETO 3: esta clase padre todavía no la usa nadie.
 *   1. Mueve aquí saldoDe(), que es lo que comparten las dos páginas.
 *   2. Haz que PaginaTransferencia y PaginaConsulta hereden de PaginaDeCuentas
 *      (extends PaginaDeCuentas) y borra su constructor: lo heredan de aquí.
 *   3. Borra el transferir() de PaginaConsulta: una consulta no transfiere.
 * Pista: cuando PaginaConsulta ya no herede de PaginaTransferencia, el compilador te
 * mostrará el código que la usaba como si pudiera transferir.
 */
export abstract class PaginaDeCuentas {
  constructor(protected readonly navegador: Navegador) {}

  abstract abrir(): Promise<void>;
}

export class PaginaTransferencia {
  constructor(protected readonly navegador: Navegador) {}

  async abrir(): Promise<void> {
    await this.navegador.ir('/transferir');
  }

  async saldoDe(cuenta: string): Promise<string> {
    return this.navegador.leer(`saldo ${cuenta}`);
  }

  async transferir(destino: string, monto: number): Promise<void> {
    await this.navegador.escribir('Cuenta destino', destino);
    await this.navegador.escribir('Monto', String(monto));
    await this.navegador.pulsar('Transferir');
  }
}

/** Solo consulta saldos. */
export class PaginaConsulta extends PaginaTransferencia {
  async abrir(): Promise<void> {
    await this.navegador.ir('/inicio');
  }

  async transferir(): Promise<void> {
    throw new Error('PaginaConsulta no puede transferir');
  }
}

/** Código que confía en la jerarquía: a toda PaginaTransferencia le pide transferir. */
export async function transferirDesdeTodas(paginas: PaginaTransferencia[], destino: string, monto: number): Promise<void> {
  for (const pagina of paginas) {
    await pagina.abrir();
    await pagina.transferir(destino, monto);
  }
}
