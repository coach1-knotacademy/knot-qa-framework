// Generado por una IA (Claude Sonnet, actuando como asistente tipo Copilot) el 24 nov 2026,
// con EXACTAMENTE el mismo pedido que 1b (el CP-102 completo, con URL, usuario y clave), pero dentro
// del repo: leyó .github/copilot-instructions.md y el código de src/. No ejecutó nada. Se guarda tal cual.
/**
 * CP-102 · Recarga de más de $50.000 con código de seguridad (OTP).
 *
 * Precondición: Ana inició sesión y Ahorros tiene $1.500.000.
 * El ingreso NO es el objetivo de esta prueba, así que la sesión se abre por API
 * (abrirConSesion) y la prueba se enfoca en la recarga.
 */
import { abrirConSesion } from '../../src/flujos/sesion';
import { fabricaDeRecargas } from '../../src/datos/fabricaDeRecargas';
import { cuentas, usuarios } from '../../src/datos/usuarios';
import { test, expect } from '../../src/soporte/fixtures';

test.describe('CP-102 · Recarga de más de $50.000', () => {
  test('CP-102 · pide código de seguridad y con el del buzón queda hecha y descuenta de Ahorros', async ({
    page,
    cliente,
    paginaRecargas,
    paginaBuzon,
  }) => {
    // Precondición: Ana con sesión abierta y saldo inicial de Ahorros conocido.
    await abrirConSesion(page, cliente, usuarios.ana);

    // Paso 1: ir a «Recargar celular».
    await paginaRecargas.abrir();
    await expect(paginaRecargas.saldoDisponible).toHaveText('$1.500.000'); // saldo de partida de Ahorros

    // Pasos 2 y 3: Claro, 3001234567, $60.000 (la fábrica "grande" ya trae estos datos) y «Recargar».
    const recarga = fabricaDeRecargas.grande({ operador: 'Claro' });
    await paginaRecargas.recargar(recarga);

    // Resultado esperado 1: antes de recargar, el banco pide el «Código de seguridad».
    await expect(paginaRecargas.campoCodigo).toBeVisible();

    // Paso 4: leer el NUEVO código en el buzón (solo después de que el banco lo pidió) y confirmar.
    const codigo = await paginaBuzon.leerUltimoCodigo(usuarios.ana.usuario);
    await paginaRecargas.confirmar(codigo);

    // Resultado esperado 2: comprobante con «Recarga exitosa» y «Valor: $60.000».
    await expect(paginaRecargas.comprobante).toContainText('Recarga exitosa');
    await expect(paginaRecargas.comprobante).toContainText('Valor: $60.000');

    // Resultado esperado 3: Ahorros queda en $1.500.000 - $60.000 = $1.440.000.
    expect(cuentas.ahorros.saldoInicial - recarga.monto).toBe(1_440_000);
    await expect(paginaRecargas.saldoDisponible).toHaveText('$1.440.000');
  });
});

// Lo que dijo la IA (resumen fiel): reutilizó los fixtures (paginaRecargas, paginaBuzon, cliente), el flujo
// abrirConSesion, fabricaDeRecargas.grande() y usuarios/cuentas; la URL y las credenciales salen de
// src/config/entorno.ts. Supuestos que declaró sin verificar: el buzón muestra primero el mensaje más
// reciente, y el saldo en pantalla se actualiza tras la recarga.
