# language: es
#
# S8 · Una prueba, muchos datos: el Esquema del escenario y sus Ejemplos.
#
# Los pasos se escriben UNA vez, con <marcadores>; cada fila de «Ejemplos» es UNA prueba.
# La regla para que una fila entre en la tabla: mismos pasos, otro dato, el mismo tipo de «Entonces».
# Si una fila cambia el camino o el resultado (por ejemplo, pide código), es otro Esquema.
#
# El <marcador> en el título es el título único: cada fila sale con su nombre en el reporte que lee negocio.
# Las tablas tienen los mismos datos que src/datos/fabricaDeRecargas.ts.
# SOLUCIÓN de las 5 salas. El CP-104 está ejecutado en tests/recargas/CP-104-limites.spec.ts;
# las otras cuatro, en laboratorio/generar/s08_solucion/tests/recargas/ (se copian a tests/recargas/ para correrlas).
# Todas con el mismo patrón: un test() por fila, el dato en el título y la etiqueta @CP-xxx.
# Revisar los escenarios:  npm.cmd run revisar-escenarios

Característica: Recargar un celular con muchos datos
  Como cliente del banco
  quiero que cada monto, celular y operador se pruebe con la misma regla
  para que negocio vea en el reporte qué datos se probaron

  # ── Sala 1 · CP-103 · Celular mal escrito ──
  @CP-103
  Esquema del escenario: Un celular mal escrito se rechaza: <celular> (<caso>)
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $10.000 al celular <celular>
    Entonces ve el mensaje «El celular debe tener 10 dígitos y empezar por 3»
    Y su saldo de Ahorros sigue en $1.500.000

    Ejemplos:
      | celular     | caso          |
      | 300123      | 6 dígitos     |
      | 30012345678 | 11 dígitos    |
      | 2001234567  | empieza por 2 |

  # ── Sala 2 · CP-104 · Monto fuera de rango ──
  @CP-104
  Esquema del escenario: Un monto fuera de rango se rechaza: <monto>
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga <monto> a un celular Claro 3001234567
    Entonces ve el mensaje «<mensaje>»
    Y su saldo de Ahorros sigue en $1.500.000

    Ejemplos:
      | monto    | mensaje                       |
      | $999     | La recarga mínima es $1.000   |
      | $100.001 | La recarga máxima es $100.000 |
      | $150.000 | La recarga máxima es $100.000 |

  # ── Sala 3 · CP-101 · Recarga válida sin código ──
  @CP-101
  Esquema del escenario: Una recarga sin código da comprobante y descuenta: <monto>
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga <monto> a un celular Claro 3001234567
    Entonces ve el comprobante «Recarga exitosa» con «Valor: <monto>»
    Y su saldo de Ahorros queda en <saldo_final>

    Ejemplos:
      | monto   | saldo_final |
      | $1.000  | $1.499.000  |
      | $10.000 | $1.490.000  |
      | $50.000 | $1.450.000  |

  # ── Sala 4 · CP-105 · Límite diario ──
  @CP-105
  Esquema del escenario: Pasado el límite diario no se puede recargar: <ya_recargo> + <monto>
    Dado que Ana tiene la sesión abierta y hoy ya recargó <ya_recargo>
    Cuando recarga <monto> a un celular Claro 3001234567
    Entonces ve el mensaje «Superaste el límite diario de recargas ($200.000)»

    Ejemplos:
      | ya_recargo | monto   |
      | $190.000   | $20.000 |
      | $200.000   | $1.000  |
      | $160.000   | $50.000 |

  # ── Sala 5 · CP-107 · Una recarga por operador ──
  @CP-107
  Esquema del escenario: Cada operador recibe la recarga: <operador>
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $10.000 a un celular <operador> 3001234567
    Entonces ve el comprobante «Recarga exitosa» con «<operador> · 3001234567»
    Y su saldo de Ahorros queda en $1.490.000

    Ejemplos:
      | operador |
      | Claro    |
      | Movistar |
      | Tigo     |
      | WOM      |

  # El CP-106 (el operador no responde, BUG-04) no va aquí: es un solo dato. Entra en el triage de la S9.
