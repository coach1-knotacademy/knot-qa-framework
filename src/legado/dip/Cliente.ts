/**
 * DESPUÉS (DIP) · El contrato: lo que ResumenDeCuentas necesita de un cliente.
 *
 * ResumenDeCuentas dependerá de esta interfaz y no de ClienteHttp. Así le podemos pasar
 * el cliente real (con el banco) o uno falso (en una prueba de unidad, sin banco).
 */
import { Cuenta } from '../../api/ClienteBanco';
import { Usuario } from '../../datos/usuarios';

export type { Cuenta };

export interface Cliente {
  iniciarSesion(usuario: Usuario): Promise<void>;
  // TODO RETO 5 (paso 1): agrega el método para pedir las cuentas:
  //   cuentas(): Promise<Cuenta[]>;
}
