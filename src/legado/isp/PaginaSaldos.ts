/**
 * La pantalla de saldos del framework anterior, corregida en el reto 4 de la S4.
 *
 * Antes implementaba la interfaz gigante PaginaDelBanco y tenía 5 métodos que lanzaban
 * "No aplica". Ahora implementa solo las capacidades que de verdad tiene.
 */
import { Navegador } from '../navegador';
import { CierraSesion, ConsultaSaldos, SeAbre } from './capacidades';

export class PaginaSaldos implements SeAbre, ConsultaSaldos, CierraSesion {
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
}
