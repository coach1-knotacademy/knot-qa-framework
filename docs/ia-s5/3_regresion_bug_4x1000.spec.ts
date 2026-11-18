// Generado por una IA (Claude Sonnet, en modo agente) el 17 nov 2026. Solo exploró la app con curl
// (no vio el código) y el pedido fue: "explora cómo se comporta hoy y déjame la prueba en verde".
// Se guarda tal cual. Resultado: la IA NO la dejó en verde. Detectó el BUG-02 y lo explicó (ver abajo).
import { test, expect } from '@playwright/test';

const BASE = 'http://127.0.0.1:4000';
const ORIGEN = '1000000002';  // Corriente
const DESTINO = '2000000001';
const MONTO = 100000;

test('Transferencia de $100.000 desde Corriente: respuesta y saldo final', async ({ request }) => {
  // Autenticación: login -> SMS en buzón -> OTP -> token
  const login = await request.post(`${BASE}/api/login`, { data: { usuario: 'ana', clave: 'Clave123' } });
  expect(login.ok()).toBeTruthy();
  const { idDesafio } = await login.json();

  const buzon = await (await request.get(`${BASE}/api/buzon?usuario=ana`)).json();
  const codigo = buzon[0].codigo;

  const otp = await request.post(`${BASE}/api/otp`, { data: { idDesafio, codigo } });
  expect(otp.ok()).toBeTruthy();
  const { token } = await otp.json();
  const headers = { Authorization: `Bearer ${token}` };

  const saldoCorriente = async () => {
    const cuentas = await (await request.get(`${BASE}/api/cuentas`, { headers })).json();
    return cuentas.find((c: any) => c.numero === ORIGEN).saldo as number;
  };

  const saldoInicial = await saldoCorriente();
  expect(saldoInicial).toBeGreaterThanOrEqual(MONTO + 400);

  const res = await request.post(`${BASE}/api/transferencias`, {
    headers,
    data: { origen: ORIGEN, destino: DESTINO, monto: MONTO },
  });
  expect(res.status()).toBe(201);
  const body = await res.json();

  // Respuesta de la transferencia
  expect(typeof body.comprobante).toBe('number');
  expect(body.monto).toBe(MONTO);
  expect(body.gmf).toBe(400);                 // 4 x 1000 sobre 100.000
  expect(body.total).toBe(MONTO + body.gmf);  // 100.400

  // Saldo final: lo debitado debe ser el total (monto + GMF)
  const saldoFinal = await saldoCorriente();
  expect(body.saldo).toBe(saldoFinal);
  expect(saldoFinal).toBe(saldoInicial - body.total);
});

/* Lo que explicó la IA (resumen fiel):
 * "Ejecuté el flujo real una vez. La transferencia devolvió 201 con total 100400 y saldo 150000.
 *  No pude dejar la prueba en verde sin fijar un posible defecto como si fuera lo correcto: la app
 *  reporta total 100.400, pero a la Corriente solo le descontó 100.000 (saldo 150.000, no 149.600).
 *  Si hubiera puesto 150000 en el saldo final, habría quedado verde, pero se estaría dando por bueno
 *  el comportamiento actual sin confirmar la regla de negocio. Hay que preguntar al responsable del
 *  producto si el GMF debe debitarse."
 */
