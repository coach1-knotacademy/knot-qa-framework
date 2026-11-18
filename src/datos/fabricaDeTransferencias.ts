/**
 * RETO 1 (S5) · FACTORY: la fábrica de transferencias del Banco Demo.
 *
 * Modelo: src/datos/fabricaDeRecargas.ts (ya está completa). Aquí se hace lo mismo para
 * las transferencias: una base válida y métodos con nombre de negocio que solo cambian un dato.
 */
import { cuentas } from './usuarios';

/** Lo que se necesita para transferir (sirve para PaginaTransferir y para ClienteBanco). */
export interface Transferencia {
  origen: string;
  destino: string;
  monto: number;
}

export const fabricaDeTransferencias = {
  /** Una transferencia que el banco acepta: de Ahorros a la cuenta de otro cliente, por $100.000. */
  valida(cambios: Partial<Transferencia> = {}): Transferencia {
    return { origen: cuentas.ahorros.numero, destino: cuentas.destino, monto: 100_000, ...cambios };
  },

  /** Paso 1 · La misma transferencia, pero desde la cuenta Corriente. */
  desdeCorriente(cambios: Partial<Transferencia> = {}): Transferencia {
    return fabricaDeTransferencias.valida({ origen: cuentas.corriente.numero, ...cambios });
  },

  /** Paso 2 · Por el monto mínimo que acepta el banco: exactamente $1.000. */
  alMontoMinimo(cambios: Partial<Transferencia> = {}): Transferencia {
    return fabricaDeTransferencias.valida({ monto: 1_000, ...cambios });
  },

  /** Paso 3 · A la misma cuenta de origen (el banco debe rechazarla). Respeta el origen que pida la prueba. */
  aLaMismaCuenta(cambios: Partial<Transferencia> = {}): Transferencia {
    const base = fabricaDeTransferencias.valida(cambios);
    return { ...base, destino: base.origen };
  },
};
