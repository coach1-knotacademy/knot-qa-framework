/**
 * S5 · ParaBank, un banco de práctica real en internet. Pantalla de ingreso.
 * Cada prueba recibe un cliente NUEVO (fixture clienteNuevo → fabricaDeClientes).
 */
import { test, expect } from '../../src/sitios/parabank/fixtures';

test('un cliente nuevo entra y ve su cuenta principal', async ({ clienteNuevo, ingreso, resumen }) => {
  await ingreso.abrir();
  await ingreso.ingresar(clienteNuevo.usuario, clienteNuevo.clave);

  await expect(ingreso.saludo).toHaveText(`Welcome ${clienteNuevo.nombre} ${clienteNuevo.apellido}`);
  await expect(resumen.filaDe(clienteNuevo.cuentaPrincipal)).toBeVisible();
});
