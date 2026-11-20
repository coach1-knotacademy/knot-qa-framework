/**
 * RETO 1 (S6) · AMBIENTES: local, qa, uat… y producción bloqueada.
 * Pruebas de unidad: sin navegador y sin banco. Cada prueba le pasa a la configuración un objeto
 * con las variables que quiere simular (como si las hubieras escrito en la terminal con $env:).
 * Cada paso tiene su propia prueba: si uno queda pendiente, los demás se pueden revisar igual.
 */
import { test, expect } from '@playwright/test';
import { claveDelAmbiente, configurarAmbiente, elegirAmbiente, urlDelAmbiente } from '../../src/config/ambientes';

test('modelo · local usa el Banco Demo de tu equipo y la clave de práctica', () => {
  expect(configurarAmbiente('local', {})).toEqual({ nombre: 'local', urlBase: 'http://127.0.0.1:4000', usuario: 'ana', clave: 'Clave123' });
  // Lo que traiga la terminal manda sobre el catálogo.
  expect(configurarAmbiente('local', { URL_BANCO: 'http://127.0.0.1:4001', USUARIO_BANCO: 'luis' })).toMatchObject({ urlBase: 'http://127.0.0.1:4001', usuario: 'luis' });
});

test('paso 1 · qa y uat apuntan a su dirección del catálogo, y URL_BANCO la reemplaza', () => {
  expect(urlDelAmbiente('qa', {})).toBe('https://qa.banco-demo.ejemplo');
  expect(urlDelAmbiente('uat', {})).toBe('https://uat.banco-demo.ejemplo');
  expect(urlDelAmbiente('qa', { URL_BANCO: 'https://qa2.banco-demo.ejemplo' })).toBe('https://qa2.banco-demo.ejemplo');
});

test('paso 2 · fuera de local, si falta CLAVE_BANCO falla de inmediato y dice qué hacer', () => {
  expect(() => claveDelAmbiente('qa', {})).toThrow("Falta CLAVE_BANCO para el ambiente qa. Defínela en la terminal: $env:CLAVE_BANCO = '...'");
  // Vacía cuenta como que no está (por ejemplo, "CLAVE_BANCO=" en un .env copiado sin llenar).
  expect(() => claveDelAmbiente('uat', { CLAVE_BANCO: '' })).toThrow('Falta CLAVE_BANCO para el ambiente uat');
  expect(claveDelAmbiente('uat', { CLAVE_BANCO: 'la-de-uat' })).toBe('la-de-uat');
});

test('paso 3 · producción, o cualquier ambiente que no esté en el catálogo, queda bloqueado', () => {
  for (const nombre of ['produccion', 'PRODUCCION', 'prod', 'pruebas', '']) {
    expect(() => elegirAmbiente(nombre), `pediste "${nombre}"`).toThrow('Este framework no corre contra producción');
  }
  expect(elegirAmbiente('qa')).toBe('qa');
  expect(elegirAmbiente('uat')).toBe('uat');
});

test('paso 4 · la configuración queda congelada: cambiarla a mitad de la corrida da error', () => {
  const config = configurarAmbiente('local', {});
  expect(Object.isFrozen(config), 'PENDIENTE (S6): congelar() todavía deja cambiar la configuración (entorno.usuario = "luis" pasaría) — ver retos/S06.md, reto 1').toBe(true);

  expect(() => {
    (config as { usuario: string }).usuario = 'luis';
  }).toThrow(TypeError);
  expect(config.usuario).toBe('ana');
});
