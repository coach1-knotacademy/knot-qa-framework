/**
 * PATRÓN FACTORY · clientes de ParaBank (S5)
 *
 * ParaBank es un sitio público y compartido: si todas las pruebas usaran el mismo cliente,
 * se pisarían los saldos entre ellas (y con el resto del mundo). La fábrica entrega un
 * cliente NUEVO y ÚNICO cada vez, con datos de mentira que sí pasan las validaciones.
 *
 * Gracias a eso ninguna prueba depende de lo que dejó otra persona en el sitio.
 */
import { entornoParaBank } from './entorno';

/** Los datos del formulario de registro de ParaBank. */
export interface DatosDeCliente {
  nombre: string;
  apellido: string;
  direccion: string;
  ciudad: string;
  departamento: string;
  codigoPostal: string;
  telefono: string;
  documento: string;
  usuario: string;
  clave: string;
}

let consecutivo = 0;

/** Un usuario que no se repite: hora + número al azar + consecutivo. Solo letras y números. */
function usuarioUnico(): string {
  consecutivo += 1;
  return `knot${Date.now().toString(36)}${Math.floor(Math.random() * 1296).toString(36)}${consecutivo}`;
}

export const fabricaDeClientes = {
  /**
   * Un cliente nuevo, listo para registrarse. Solo cambia lo que le importa a la prueba:
   *   fabricaDeClientes.nuevo({ nombre: 'Luis' })
   */
  nuevo(cambios: Partial<DatosDeCliente> = {}): DatosDeCliente {
    return {
      nombre: 'Ana',
      apellido: 'Prueba',
      direccion: 'Calle 100 # 10-20',
      ciudad: 'Bogota',
      departamento: 'DC',
      codigoPostal: '110111',
      telefono: '3001234567',
      documento: '123-45-6789',
      usuario: usuarioUnico(),
      clave: entornoParaBank.clave,
      ...cambios,
    };
  },
};
