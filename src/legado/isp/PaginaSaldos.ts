/**
 * La pantalla de saldos del framework anterior. Este archivo SÍ se modifica en el reto 4 de la S4.
 *
 * Solo sabe abrir, leer saldos y cerrar sesión, pero la interfaz gigante la obliga a tener
 * otros 5 métodos que lanzan "No aplica".
 */
import { Navegador } from '../navegador';
import { PaginaDelBanco } from './PaginaDelBanco';

// TODO RETO 4 (paso 2): cambia "implements PaginaDelBanco" por las interfaces pequeñas que
// sí cumple (SeAbre, ConsultaSaldos, CierraSesion) e impórtalas de './capacidades'.
// TODO RETO 4 (paso 3): borra los 5 métodos que lanzan "No aplica".
export class PaginaSaldos implements PaginaDelBanco {
  constructor(private readonly navegador: Navegador) {}

  async abrir(): Promise<void> {
    await this.navegador.ir('/inicio');
  }

  async saldoDe(cuenta: string): Promise<string> {
    return this.navegador.leer(`saldo ${cuenta}`);
  }

  async cerrarSesion(): Promise<void> {
    await this.navegador.pulsar('Salir');
  }

  async ingresar(): Promise<void> {
    throw new Error('No aplica en PaginaSaldos');
  }

  async validarOtp(): Promise<void> {
    throw new Error('No aplica en PaginaSaldos');
  }

  async transferir(): Promise<void> {
    throw new Error('No aplica en PaginaSaldos');
  }

  async descargarExtracto(): Promise<void> {
    throw new Error('No aplica en PaginaSaldos');
  }

  async cambiarClave(): Promise<void> {
    throw new Error('No aplica en PaginaSaldos');
  }
}
