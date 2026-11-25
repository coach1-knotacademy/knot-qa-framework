# language: es
#
# Tu CP en Gherkin (S7). Primero el escenario, después la prueba: cada paso es un test.step con el mismo texto
# (mira tests/CP-101-recarga.spec.ts). Sin clics ni localizadores: así lo firma negocio y no cambia con la pantalla.
# Revísalo en las actividades de la S7 (revisor de escenarios) antes de automatizarlo.

Característica: Recargar un celular desde la billetera
  Como cliente del banco
  quiero recargar un celular desde mi cuenta de Ahorros
  para no tener que ir a un punto físico

  @CP-101
  Escenario: Una recarga normal da comprobante y descuenta de Ahorros
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $10.000 a un celular Claro 3001234567
    Entonces ve el comprobante «Recarga exitosa»
    Y su saldo de Ahorros queda en $1.490.000
