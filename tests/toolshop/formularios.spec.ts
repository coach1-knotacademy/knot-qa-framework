/**
 * Kit «web real» · Toolshop: validaciones del formulario de contacto y del ingreso (CP-505 a CP-507).
 * Escenarios en especificaciones/toolshop.feature.
 *
 * Son las pruebas que un tester manual hace en cada formulario: obligatorios y formato.
 * Ninguna envía datos de verdad: el sitio valida antes de mandar, y eso es justo lo que se prueba.
 *
 * Correr:  npx.cmd playwright test --project=toolshop formularios
 */
import { fabricaDeContactos } from '../../src/sitios/toolshop/fabricaDeLaTienda';
import { test, expect } from '../../src/sitios/toolshop/fixtures';

test('CP-505 · El contacto sin datos pide los obligatorios', { tag: '@CP-505' }, async ({ contacto }) => {
  await test.step('Dado que Ana está en el formulario de contacto', async () => {
    await contacto.abrir();
  });

  await test.step('Cuando lo envía sin datos', async () => {
    await contacto.enviarVacio();
  });

  await test.step('Entonces ve «First name is required», «Email is required» y «Message is required»', async () => {
    await expect(contacto.error('First name is required')).toBeVisible();
    await expect(contacto.error('Email is required')).toBeVisible();
    await expect(contacto.error('Message is required')).toBeVisible();
  });
});

test('CP-506 · El contacto con un correo mal escrito se rechaza', { tag: '@CP-506' }, async ({ contacto }) => {
  const datos = fabricaDeContactos.conCorreoInvalido();

  await test.step('Dado que Ana está en el formulario de contacto', async () => {
    await contacto.abrir();
  });

  await test.step(`Cuando lo envía con el correo «${datos.correo}»`, async () => {
    await contacto.enviar(datos);
  });

  await test.step('Entonces ve «Email format is invalid»', async () => {
    await expect(contacto.error('Email format is invalid')).toBeVisible();
  });
});

test('CP-507 · El ingreso sin correo ni clave pide los dos', { tag: '@CP-507' }, async ({ ingreso }) => {
  await test.step('Dado que Ana está en la pantalla de ingreso', async () => {
    await ingreso.abrir();
  });

  await test.step('Cuando intenta ingresar sin escribir nada', async () => {
    await ingreso.ingresar();
  });

  await test.step('Entonces ve «Email is required» y «Password is required»', async () => {
    await expect(ingreso.error('Email is required')).toBeVisible();
    await expect(ingreso.error('Password is required')).toBeVisible();
  });
});
