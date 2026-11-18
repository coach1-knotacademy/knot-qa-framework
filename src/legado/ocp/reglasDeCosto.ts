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
    return cuatroPorMil(monto) + 2_000;
  }
}

/** Tipo nuevo: se agregó SIN modificar calcularCosto ni las otras reglas. */
export class ReglaNomina implements ReglaDeCosto {
  readonly tipoCuenta = 'Nómina';

  calcular(): number {
    return 0;
  }
}

/** Reúne las reglas y elige la que corresponde a cada tipo de cuenta. */
export class RegistroDeReglas {
  private readonly reglas = new Map<string, ReglaDeCosto>();

  registrar(regla: ReglaDeCosto): this {
    this.reglas.set(regla.tipoCuenta, regla);
    return this;
  }

  costo(tipoCuenta: string, monto: number): number {
    const regla = this.reglas.get(tipoCuenta);
    if (!regla) {
      throw new Error(`Tipo de cuenta desconocido: ${tipoCuenta}`);
    }
    return regla.calcular(monto);
  }
}

/** Las reglas que usa el banco. Para un tipo nuevo, agrega una línea .registrar(...) */
export function reglasDelBanco(): RegistroDeReglas {
  return new RegistroDeReglas().registrar(new ReglaAhorros()).registrar(new ReglaCorriente()).registrar(new ReglaNomina());
}
