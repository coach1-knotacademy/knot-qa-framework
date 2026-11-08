/**
 * DOBLE DE PRUEBA · Un cliente falso que cumple el contrato Cliente sin llamar al banco.
 * Mira NavegadorFalso.ts: es el mismo truco.
 */
import { Cliente, Cuenta } from '../../../src/legado/dip/Cliente';
import { Usuario } from '../../../src/datos/usuarios';

export class ClienteFalso implements Cliente {
  /** Los usuarios con los que se inició sesión, para comprobarlo en la prueba. */
  readonly sesiones: string[] = [];

  constructor(private readonly cuentasPreparadas: Cuenta[]) {}

  async iniciarSesion(usuario: Usuario): Promise<void> {
    // TODO RETO 5 (paso 3): anota el usuario:  this.sesiones.push(usuario.usuario);
    // Cuando termines, borra la línea "throw" de abajo.
    throw new Error('PENDIENTE (S4): completa ClienteFalso.iniciarSesion en tests/retos-s04/dobles/ClienteFalso.ts — ver retos/S04.md, reto 5');
  }

  async cuentas(): Promise<Cuenta[]> {
    // TODO RETO 5 (paso 3): devuelve las cuentas que llegaron en el constructor.
    // Cuando termines, borra la línea "throw" de abajo.
    throw new Error('PENDIENTE (S4): completa ClienteFalso.cuentas en tests/retos-s04/dobles/ClienteFalso.ts — ver retos/S04.md, reto 5');
  }
}
