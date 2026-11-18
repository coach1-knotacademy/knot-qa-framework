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
    this.sesiones.push(usuario.usuario);
  }

  async cuentas(): Promise<Cuenta[]> {
    return this.cuentasPreparadas;
  }
}
