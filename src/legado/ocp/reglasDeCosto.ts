/**
 * DESPUÉS (OCP) · Una regla por tipo de cuenta y un registro que las reúne.
 *
 * Para agregar un tipo de cuenta se crea una regla NUEVA y se registra.
 * Las reglas que ya funcionan no se tocan.
 */
import { cuatroPorMil } from './calcularCosto';

/** El contrato que cumple toda regla de costo. */
export interface ReglaDeCosto {
  readonly tipoCuenta: string;
  calcular(monto: number): number;
}

/** Ejemplo ya resuelto: la regla de las cuentas de Ahorros. */
export class ReglaAhorros implements ReglaDeCosto {
  readonly tipoCuenta = 'Ahorros';

  calcular(monto: number): number {
    return cuatroPorMil(monto);
  }
}

export class ReglaCorriente implements ReglaDeCosto {
  readonly tipoCuenta = 'Corriente';

  calcular(monto: number): number {
    // TODO RETO 2 (paso 1): 4x1000 más la comisión fija de $2.000, como en calcularCosto.
    // Cuando termines, borra la línea "throw" de abajo.
    throw new Error('PENDIENTE (S4): completa ReglaCorriente.calcular en src/legado/ocp/reglasDeCosto.ts — ver retos/S04.md, reto 2');
  }
}

// TODO RETO 2 (paso 3): crea aquí la clase ReglaNomina para el tipo 'Nómina', que no tiene costo.
// Pista: copia ReglaAhorros, cambia el nombre de la clase, el tipoCuenta y haz que calcular devuelva 0.

/** Reúne las reglas y elige la que corresponde a cada tipo de cuenta. */
export class RegistroDeReglas {
  private readonly reglas = new Map<string, ReglaDeCosto>();

  registrar(regla: ReglaDeCosto): this {
    this.reglas.set(regla.tipoCuenta, regla);
    return this;
  }

  costo(tipoCuenta: string, monto: number): number {
    // TODO RETO 2 (paso 2): busca la regla con this.reglas.get(tipoCuenta).
    //   - Si no existe, lanza el mismo error que calcularCosto: `Tipo de cuenta desconocido: ${tipoCuenta}`
    //   - Si existe, devuelve regla.calcular(monto)
    // Cuando termines, borra la línea "throw" de abajo.
    throw new Error('PENDIENTE (S4): completa RegistroDeReglas.costo en src/legado/ocp/reglasDeCosto.ts — ver retos/S04.md, reto 2');
  }
}

/** Las reglas que usa el banco. Para un tipo nuevo, agrega una línea .registrar(...) */
export function reglasDelBanco(): RegistroDeReglas {
  // TODO RETO 2 (paso 3): registra también la ReglaNomina.
  return new RegistroDeReglas().registrar(new ReglaAhorros()).registrar(new ReglaCorriente());
}
