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
    // TODO RETO 5 (paso 2): la misma lógica de ResumenAcoplado.saldoTotal, pero usando
    // this.cliente en lugar de crear un ClienteHttp. Aquí no debe aparecer la palabra "new".
    // Pista: necesitas el paso 1 (cuentas() en la interfaz Cliente) para poder llamar
    //        a this.cliente.cuentas().
    // Cuando termines, borra la línea "throw" de abajo.
    throw new Error('PENDIENTE (S4): completa ResumenDeCuentas.saldoTotal en src/legado/dip/ResumenDeCuentas.ts — ver retos/S04.md, reto 5');
  }
}
