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
# El CP-104 está ejecutado en tests/recargas/CP-104-limites.spec.ts (un test() por fila, con @CP-104).
# Revisar los escenarios:  npm.cmd run revisar-escenarios

Característica: Recargar un celular con muchos datos
  Como cliente del banco
  quiero que cada monto, celular y operador se pruebe con la misma regla
  para que negocio vea en el reporte qué datos se probaron

  # ── Sala 1 · CP-103 · Celular mal escrito ──
  # Completa el «Entonces» y la tabla «Ejemplos» (columnas: celular, caso). Pregunta de la sala: Tres datos, un mismo mensaje: ¿hacen falta las tres filas?
  @CP-103
  Esquema del escenario: Un celular mal escrito se rechaza: <celular>
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $10.000 al celular <celular>

  # ── Sala 2 · CP-104 · Monto fuera de rango (resuelto: es el mírame de la clase) ──
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
  # Completa el «Entonces» y la tabla «Ejemplos» (columnas: monto, saldo_final). Pregunta de la sala: ¿Y $50.001?
  @CP-101
  Esquema del escenario: Una recarga sin código da comprobante y descuenta: <monto>
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga <monto> a un celular Claro 3001234567

  # ── Sala 4 · CP-105 · Límite diario ──
  # Completa el «Entonces» y la tabla «Ejemplos» (columnas: ya_recargo, monto). Pregunta de la sala: ¿El dato del «Dado» también va en la tabla? ¿Y $180.000 + $20.000?
  @CP-105
  Esquema del escenario: Pasado el límite diario no se puede recargar: <ya_recargo> + <monto>
    Dado que Ana tiene la sesión abierta y hoy ya recargó <ya_recargo>
    Cuando recarga <monto> a un celular Claro 3001234567

  # ── Sala 5 · CP-107 · Una recarga por operador ──
  # Completa el «Entonces» y la tabla «Ejemplos» (columnas: operador). Pregunta de la sala: Esto ya existe en el repo (`fabricaDeRecargas.paraCadaOperador`). ¿Para qué escribir la tabla?
  @CP-107
  Esquema del escenario: Cada operador recibe la recarga: <operador>
    Dado que Ana tiene la sesión abierta y $1.500.000 en Ahorros
    Cuando recarga $10.000 a un celular <operador> 3001234567

  # El CP-106 (el operador no responde, BUG-04) no va aquí: es un solo dato. Entra en el triage de la S9.
