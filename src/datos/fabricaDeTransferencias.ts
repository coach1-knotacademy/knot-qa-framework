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
    // TODO paso 1: llama a valida() con el origen de la cuenta Corriente (cuentas.corriente.numero) y los cambios.
    //   Mira grande() en fabricaDeRecargas.ts: es la misma forma.
    throw new Error('PENDIENTE (S5): completa fabricaDeTransferencias.desdeCorriente en src/datos/fabricaDeTransferencias.ts — ver retos/S05.md, reto 1');
  },

  /** Paso 2 · Por el monto mínimo que acepta el banco: exactamente $1.000. */
  alMontoMinimo(cambios: Partial<Transferencia> = {}): Transferencia {
    // TODO paso 2: igual al paso 1, pero cambiando el monto a 1_000.
    throw new Error('PENDIENTE (S5): completa fabricaDeTransferencias.alMontoMinimo en src/datos/fabricaDeTransferencias.ts — ver retos/S05.md, reto 1');
  },

  /** Paso 3 · A la misma cuenta de origen (el banco debe rechazarla). Respeta el origen que pida la prueba. */
  aLaMismaCuenta(cambios: Partial<Transferencia> = {}): Transferencia {
    // TODO paso 3: arma la base con valida(cambios) y devuelve una copia con destino = base.origen.
    throw new Error('PENDIENTE (S5): completa fabricaDeTransferencias.aLaMismaCuenta en src/datos/fabricaDeTransferencias.ts — ver retos/S05.md, reto 1');
  },
};
