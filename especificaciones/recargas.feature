# language: es
#
# S7 · Los casos de prueba del Banco Demo (CP-101 a CP-106), escritos en Gherkin.
#
# Gherkin es el CP de siempre con otra sintaxis: Dado (la precondición), Cuando (lo que hace el cliente)
# y Entonces (el resultado esperado). Se escribe en el idioma del negocio, nunca con clics ni localizadores:
# así lo firma el líder antes de automatizar y sigue sirviendo aunque cambie la pantalla.
#
# El ID del caso del ALM va en la etiqueta (@CP-101): es la trazabilidad que pide auditoría.
# El CP-101 está ejecutado en tests/recargas/CP-101-gherkin.spec.ts (cada paso es un test.step).
# Revisar los escenarios:  npm.cmd run revisar-escenarios

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

  # ── Práctica de la S7: un escenario por sala. Solo Dado, Cuando y Entonces, sin clics ni localizadores. ──

  @CP-102
  Escenario: Una recarga de más de $50.000 pide código de seguridad
    # Sala 1: escribe aquí el escenario del CP-102 (actividades S7 → «Tu CP en Gherkin»).

  @CP-103
  Escenario: Un celular de 6 dígitos se rechaza
    # Sala 2: escribe aquí el escenario del CP-103.

  @CP-104
  Escenario: Una recarga por encima del máximo se rechaza
    # Sala 3: escribe aquí el escenario del CP-104.

  @CP-105
  Escenario: Pasado el límite diario no se puede recargar
    # Sala 4: escribe aquí el escenario del CP-105.

  @CP-106
  Escenario: Si el operador no responde, el cliente no pierde la plata
    # Sala 5: escribe aquí el escenario del CP-106.
