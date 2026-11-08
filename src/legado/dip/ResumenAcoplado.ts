/**
 * CÓDIGO HEREDADO · D de SOLID: inversión de dependencias (DIP).
 *
 * El problema está en la línea marcada: la clase CREA por dentro su cliente HTTP concreto.
 * Consecuencias:
 *   - Para probar una simple suma hay que tener el banco encendido (tests/antes/resumen-acoplado.spec.ts).
 *   - No se puede probar qué pasa con 0 cuentas o con un error del servicio sin cambiar el banco.
 *
 * No la modifiques: es el "antes". El reto 5 de la S4 escribe ResumenDeCuentas.ts.
 */
import { entorno } from '../../config/entorno';
import { Usuario } from '../../datos/usuarios';
import { ClienteHttp } from './ClienteHttp';

export class ResumenAcoplado {
  async saldoTotal(usuario: Usuario): Promise<number> {
    const cliente = new ClienteHttp(entorno.urlBase); // <-- crea su dependencia adentro
    await cliente.iniciarSesion(usuario);
    const cuentas = await cliente.cuentas();
    return cuentas.reduce((total, cuenta) => total + cuenta.saldo, 0);
  }
}
