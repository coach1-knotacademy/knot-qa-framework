/**
 * DESPUÉS (DIP) · El mismo resumen que ResumenAcoplado, pero RECIBE su cliente.
 *
 * Quien crea un ResumenDeCuentas decide qué cliente pasarle:
 *   new ResumenDeCuentas(new ClienteHttp(entorno.urlBase))   → en una prueba con el banco
 *   new ResumenDeCuentas(new ClienteFalso([...]))            → en una prueba de unidad
 */
import { Usuario } from '../../datos/usuarios';
import { Cliente } from './Cliente';

export class ResumenDeCuentas {
  constructor(private readonly cliente: Cliente) {}

  async saldoTotal(usuario: Usuario): Promise<number> {
    await this.cliente.iniciarSesion(usuario);
    const cuentas = await this.cliente.cuentas();
    return cuentas.reduce((total, cuenta) => total + cuenta.saldo, 0);
  }
}
