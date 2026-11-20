/**
 * S5 · Recargas a celular en el Banco Demo, con los bloqueos que tiene una billetera real:
 * código extra para montos altos, límite diario y un operador externo que a veces no responde.
 *
 * Patrones que se ven aquí:
 *  - PAGE OBJECT: la prueba no tiene ni un localizador (están en src/paginas/PaginaRecargas.ts).
 *  - FACTORY: los datos salen de src/datos/fabricaDeRecargas.ts con nombres de negocio.
 */
import { abrirConSesion } from '../../src/flujos/sesion';
import { fabricaDeRecargas } from '../../src/datos/fabricaDeRecargas';
import { usuarios } from '../../src/datos/usuarios';
import { hallazgoEsperado } from '../../src/soporte/hallazgos';
import { test, expect } from '../../src/soporte/fixtures';

test.describe('Recargas por la pantalla', () => {
  test.beforeEach(async ({ page, cliente, paginaRecargas }) => {
    await abrirConSesion(page, cliente, usuarios.ana);
    await paginaRecargas.abrir();
  });

  test('una recarga normal da comprobante y descuenta de Ahorros', async ({ paginaRecargas }) => {
    await paginaRecargas.recargar(fabricaDeRecargas.valida());

    expect(await paginaRecargas.esperarResultado()).toContain('Recarga exitosa');
    await expect(paginaRecargas.saldoDisponible).toHaveText('$1.490.000');
  });

  // TRAZABILIDAD: el ID del caso manual (el del ALM) va en el nombre. Se corre solo con: -g "CP-021"
  test('CP-021 · una recarga de más de $50.000 pide código y con el del buzón queda hecha', async ({ paginaRecargas, cliente }) => {
    await paginaRecargas.recargar(fabricaDeRecargas.grande());
    await expect(paginaRecargas.campoCodigo).toBeVisible();

    const codigo = await cliente.leerCodigo(usuarios.ana.usuario);
    await paginaRecargas.confirmar(codigo);

    expect(await paginaRecargas.esperarResultado()).toContain('Valor: $60.000');
  });

  test('un celular de 6 dígitos se rechaza con un mensaje claro', async ({ paginaRecargas }) => {
    await paginaRecargas.recargar(fabricaDeRecargas.valida({ numero: '300123' }));

    expect(await paginaRecargas.esperarResultado()).toBe('El celular debe tener 10 dígitos y empezar por 3');
  });

  test('después de $200.000 en el día, el banco no deja recargar más', async ({ paginaRecargas, cliente }) => {
    // Preparar por API (rápido) y verificar en la pantalla (lo que ve el cliente): prueba híbrida.
    for (let i = 0; i < 4; i++) {
      expect((await cliente.recargar(fabricaDeRecargas.valida({ monto: 50_000 }))).estado).toBe(201);
    }

    await paginaRecargas.recargar(fabricaDeRecargas.valida({ monto: 1_000 }));

    expect(await paginaRecargas.esperarResultado()).toBe('Superaste el límite diario de recargas ($200.000)');
  });

  test('si el operador no responde, el cliente no pierde la plata', async ({ paginaRecargas, cliente }) => {
    hallazgoEsperado('BUG-04', 'si el operador no responde, igual se descuenta el saldo');

    await paginaRecargas.recargar(fabricaDeRecargas.aOperadorCaido({ monto: 20_000 }));

    expect(await paginaRecargas.esperarResultado()).toBe('El operador no responde. Intenta más tarde.');
    // Se actúa en la pantalla y se verifica en el servicio: el saldo real, no el que pinta la página.
    expect(await cliente.saldoDeAhorros()).toBe(1_500_000);
  });
});

test.describe('Lo que no controlas también se prueba', () => {
  test('si el servicio de saldos se cae, la pantalla lo dice y no se rompe', async ({ page, cliente, paginaRecargas }) => {
    // Simulamos la caída con Playwright: la petición nunca llega al banco.
    await page.route('**/api/cuentas', (ruta) => ruta.fulfill({ status: 503, body: '{}' }));
    await abrirConSesion(page, cliente, usuarios.ana);

    await paginaRecargas.abrir();

    await expect(paginaRecargas.saldoDisponible).toHaveText('no disponible');
    // S6 · Antes: page.getByRole('button', ...) aquí mismo, un localizador que se escapó del Page Object.
    await expect(paginaRecargas.botonRecargar).toBeEnabled();
  });
});

test.describe('Recargas por API', () => {
  test.beforeEach(async ({ cliente }) => {
    await cliente.iniciarSesion(usuarios.ana);
  });

  // Una prueba por operador, con la misma fábrica: si llega un operador nuevo, se agrega en un solo lugar.
  for (const recarga of fabricaDeRecargas.paraCadaOperador()) {
    test(`${recarga.operador} recibe una recarga normal`, async ({ cliente }) => {
      const { estado, datos } = await cliente.recargar(recarga);

      expect(estado).toBe(201);
      expect(datos.operador).toBe(recarga.operador);
    });
  }

  test('con un código equivocado la recarga grande no se hace', async ({ cliente }) => {
    const { estado, datos } = await cliente.recargar(fabricaDeRecargas.grande());
    expect(estado).toBe(202);

    const confirmacion = await cliente.confirmarRecarga(datos.idDesafio ?? '', '000000');

    expect(confirmacion.estado).toBe(401);
    expect(await cliente.saldoDeAhorros()).toBe(1_500_000);
  });
});
