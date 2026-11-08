/**
 * RETO 2 (S4) · OCP: agregar un tipo de cuenta sin modificar lo que ya funciona.
 */
import { test, expect } from '@playwright/test';
import { calcularCosto } from '../../src/legado/ocp/calcularCosto';
import { reglasDelBanco } from '../../src/legado/ocp/reglasDeCosto';

const MONTOS = [1_000, 50_000, 125_125, 2_000_000];

test('Ahorros y Corriente cuestan lo mismo que con la función antigua', () => {
  const reglas = reglasDelBanco();

  for (const tipo of ['Ahorros', 'Corriente']) {
    for (const monto of MONTOS) {
      expect(reglas.costo(tipo, monto), `${tipo} con ${monto}`).toBe(calcularCosto(tipo, monto));
    }
  }
});

test('la cuenta Nómina no tiene costo', () => {
  expect(reglasDelBanco().costo('Nómina', 100_000)).toBe(0);
});

test('un tipo de cuenta desconocido da un error claro', () => {
  expect(() => reglasDelBanco().costo('Inventada', 1_000)).toThrow('Tipo de cuenta desconocido: Inventada');
});

test('se puede agregar un tipo nuevo sin tocar el código existente', () => {
  const reglas = reglasDelBanco().registrar({ tipoCuenta: 'Premium', calcular: () => 0 });

  expect(reglas.costo('Premium', 500_000)).toBe(0);
});

test('la función antigua sigue sin modificar', () => {
  // Si alguien agregó "case 'Nómina'" en calcularCosto, no aplicó OCP.
  expect(() => calcularCosto('Nómina', 1_000)).toThrow('Tipo de cuenta desconocido');
});
