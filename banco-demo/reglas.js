// Reglas de negocio del Banco Demo. Las usan el servidor y las pruebas.

/** 4x1000: impuesto de 4 pesos por cada 1.000 transferidos, en pesos enteros. */
function calcularGmf(monto) {
  return Math.round((monto * 4) / 1000); // <-- LÍNEA DEL LAB: cambia round por floor
}

const MONTO_MINIMO = 1000;
const MONTO_MAXIMO = 2000000;

/** Devuelve el mensaje de error de la transferencia, o null si es válida. */
function validarTransferencia({ origen, destino, monto, saldo }) {
  if (!/^\d{10}$/.test(String(destino ?? ''))) return 'La cuenta destino debe tener 10 dígitos';
  if (String(destino) === String(origen)) return 'La cuenta destino debe ser diferente a la de origen';
  if (!Number.isInteger(monto) || monto <= 0) return 'El monto debe ser un número entero positivo';
  if (monto <= MONTO_MINIMO) return 'El monto mínimo es $1.000';
  if (monto > MONTO_MAXIMO) return 'El monto máximo por transferencia es $2.000.000';
  if (monto + calcularGmf(monto) > saldo) return 'Saldo insuficiente';
  return null;
}

// ---------- Recargas a celular (S5) ----------
// Como en una billetera digital real: operadores, montos, un código extra para montos altos y un límite diario.
const OPERADORES = ['Claro', 'Movistar', 'Tigo', 'WOM'];
const RECARGA_MINIMA = 1000;
const RECARGA_MAXIMA = 100000;
/** Desde este monto (sin incluirlo) el banco pide un código de seguridad adicional. */
const RECARGA_CON_CODIGO = 50000;
const LIMITE_DIARIO_RECARGAS = 200000;
/**
 * Números "mágicos" del ambiente de pruebas, como las tarjetas de prueba de una pasarela de pagos:
 * con ellos el operador simulado responde siempre lo mismo y se pueden probar los casos difíciles.
 */
const NUMEROS_SANDBOX = { operadorCaido: '3000000504' };

/** Devuelve el mensaje de error de la recarga, o null si es válida. */
function validarRecarga({ operador, numero, monto, saldo, recargadoHoy = 0 }) {
  if (!OPERADORES.includes(operador)) return 'Elige un operador';
  if (!/^3\d{9}$/.test(String(numero ?? ''))) return 'El celular debe tener 10 dígitos y empezar por 3';
  if (!Number.isInteger(monto) || monto <= 0) return 'El monto debe ser un número entero positivo';
  if (monto < RECARGA_MINIMA) return 'La recarga mínima es $1.000';
  if (monto > RECARGA_MAXIMA) return 'La recarga máxima es $100.000';
  if (recargadoHoy + monto > LIMITE_DIARIO_RECARGAS) return 'Superaste el límite diario de recargas ($200.000)';
  if (monto > saldo) return 'Saldo insuficiente';
  return null;
}

/**
 * Aplica la recarga sobre la sesión (todo vive en memoria). Lo usan el servidor y la versión en línea.
 * El operador simulado responde según el número: con NUMEROS_SANDBOX.operadorCaido no contesta.
 */
function hacerRecarga(sesion, { operador, numero, monto }, comprobante) {
  const ahorros = sesion.cuentas[0];
  ahorros.saldo -= monto;
  if (numero === NUMEROS_SANDBOX.operadorCaido) {
    return { estado: 504, demora: 1500, datos: { error: 'El operador no responde. Intenta más tarde.' } };
  }
  sesion.recargadoHoy = (sesion.recargadoHoy || 0) + monto;
  return { estado: 201, demora: 400, datos: { comprobante, operador, numero, monto, saldo: ahorros.saldo } };
}

module.exports = {
  hacerRecarga,
  calcularGmf, validarTransferencia, MONTO_MINIMO, MONTO_MAXIMO,
  OPERADORES, RECARGA_MINIMA, RECARGA_MAXIMA, RECARGA_CON_CODIGO, LIMITE_DIARIO_RECARGAS, NUMEROS_SANDBOX, validarRecarga,
};
