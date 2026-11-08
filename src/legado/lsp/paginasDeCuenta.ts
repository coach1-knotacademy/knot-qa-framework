/**
 * CÓDIGO HEREDADO · L de SOLID: sustitución de Liskov (LSP). Versión corregida (reto 3 de la S4).
 *
 * Regla: si una clase hereda de otra, debe poder usarse en su lugar sin sorpresas.
 *
 * Antes, PaginaConsulta heredaba de PaginaTransferencia solo "para reutilizar saldoDe" y su
 * transferir() lanzaba un error. Ahora lo común vive en PaginaDeCuentas y cada hija hereda
 * solo lo que de verdad puede hacer.
 */
import { Navegador } from '../navegador';

/** Lo que comparten TODAS las páginas de cuentas. */
export abstract class PaginaDeCuentas {
  constructor(protected readonly navegador: Navegador) {}

  abstract abrir(): Promise<void>;

  async saldoDe(cuenta: string): Promise<string> {
    return this.navegador.leer(`saldo ${cuenta}`);
  }
}

export class PaginaTransferencia extends PaginaDeCuentas {
  async abrir(): Promise<void> {
    await this.navegador.ir('/transferir');
  }

  async transferir(destino: string, monto: number): Promise<void> {
    await this.navegador.escribir('Cuenta destino', destino);
    await this.navegador.escribir('Monto', String(monto));
    await this.navegador.pulsar('Transferir');
  }
}

/** Solo consulta saldos. Ya no promete transferir. */
export class PaginaConsulta extends PaginaDeCuentas {
  async abrir(): Promise<void> {
    await this.navegador.ir('/inicio');
  }
}

/** Código que confía en la jerarquía: a toda PaginaTransferencia le pide transferir. */
export async function transferirDesdeTodas(paginas: PaginaTransferencia[], destino: string, monto: number): Promise<void> {
  for (const pagina of paginas) {
    await pagina.abrir();
    await pagina.transferir(destino, monto);
  }
}
