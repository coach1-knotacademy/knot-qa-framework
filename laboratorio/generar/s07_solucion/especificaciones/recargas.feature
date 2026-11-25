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

  # ── Solución de la práctica de la S7 (un escenario por sala) ──

  @CP-102
  Escenario: Una recarga de más de $50.000 pide código de seguridad
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $60.000 a un celular Claro 3001234567
    Entonces el banco le pide el «Código de seguridad»
    Cuando confirma con el código que le llegó por SMS
    Entonces ve el comprobante con «Valor: $60.000»
    Y su saldo de Ahorros queda en $1.440.000

  @CP-103
  Escenario: Un celular de 6 dígitos se rechaza
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $10.000 al celular 300123
    Entonces ve el mensaje «El celular debe tener 10 dígitos y empezar por 3»
    Y su saldo de Ahorros sigue en $1.500.000

  @CP-104
  Escenario: Una recarga por encima del máximo se rechaza
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $150.000 a un celular Claro 3001234567
    Entonces ve el mensaje «La recarga máxima es $100.000»
    Y el banco no le pide el «Código de seguridad»
    Y su saldo de Ahorros sigue en $1.500.000

  @CP-105
  Escenario: Pasado el límite diario no se puede recargar
    Dado que Ana tiene la sesión abierta
    Y hoy ya recargó $200.000
    Cuando recarga $1.000 a un celular Claro 3001234567
    Entonces ve el mensaje «Superaste el límite diario de recargas ($200.000)»

  @CP-106
  Escenario: Si el operador no responde, el cliente no pierde la plata
    # Hoy sale ROJO en el Banco Demo (BUG-04): el saldo se descuenta igual. Es un rojo del SISTEMA:
    # el esperado sale de la regla del negocio, no de lo que hace la pantalla.
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $20.000 al celular de prueba 3000000504, cuyo operador no responde
    Entonces ve el mensaje «El operador no responde. Intenta más tarde.»
    Y su saldo de Ahorros sigue en $1.500.000
