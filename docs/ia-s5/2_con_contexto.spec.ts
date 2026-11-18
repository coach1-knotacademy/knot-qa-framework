// Generado por una IA (Claude Sonnet, actuando como asistente tipo Copilot) el 17 nov 2026,
// con el MISMO pedido, pero dentro del repo: leyó .github/copilot-instructions.md y los Page Objects.
// Se guarda tal cual, sin corregir.
import { cuentas, usuarios } from '../../src/datos/usuarios';
import { fabricaDeRecargas } from '../../src/datos/fabricaDeRecargas';
import { iniciarSesionPorUi } from '../../src/flujos/sesion';
import { test, expect } from '../../src/soporte/fixtures';

const pesos = (valor: number): string => `$${valor.toLocaleString('es-CO')}`;

test.describe('Recarga de celular con ingreso completo por la pantalla', () => {
  test('Ana recarga $60.000 a Claro con código de seguridad y el saldo de Ahorros baja', async ({
    paginas,
    paginaRecargas,
    cliente,
  }) => {
    // Ingreso por la UI: login, OTP leído del buzón y llegada al inicio.
    await iniciarSesionPorUi(paginas, usuarios.ana);

    await paginaRecargas.abrir();
    await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(cuentas.ahorros.saldoInicial));

    // Claro, 3001234567 y $60.000 salen de la fábrica (recarga "grande").
    const recarga = fabricaDeRecargas.grande();
    await paginaRecargas.recargar(recarga);

    // Más de $50.000: el banco pide un segundo código, que llega al buzón.
    await expect(paginaRecargas.campoCodigo).toBeVisible();
    await paginaRecargas.confirmar(await cliente.leerCodigo(usuarios.ana.usuario));

    const comprobante = await paginaRecargas.esperarResultado();
    expect(comprobante).toContain('Recarga exitosa');
    expect(comprobante).toContain(`Valor: ${pesos(recarga.monto)}`);

    // El saldo esperado sale de la regla: saldo inicial menos el valor de la recarga.
    await expect(paginaRecargas.saldoDisponible).toHaveText(pesos(cuentas.ahorros.saldoInicial - recarga.monto));
  });
});
