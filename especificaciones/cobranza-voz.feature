# language: es
#
# KIT DE VOZ · Cobranza amable por un agente de voz con IA.
# Empresa, clientes, montos y fechas son FICTICIOS. Los audios son sintéticos (TTS): nunca llamadas reales,
# porque son datos personales (Ley 1581) y la voz que identifica a una persona es un dato biométrico.
#
# Lo que se prueba es la TRANSCRIPCIÓN de la llamada, no el audio: frases obligatorias, lo prohibido,
# la intención del cliente, los datos y el WER contra el guion con un umbral (nunca coincidencia exacta).
#
# Es un «Esquema del escenario»: los pasos se escriben UNA vez y cada fila de «Ejemplos» es una prueba.
# Es el puente al DDT de la S8: agregar un caso es agregar una fila (y su guion en voz/guiones.json).
# Ejecutado en tests/voz/cobranza.spec.ts (cada paso es un test.step).  Correr:  npx.cmd playwright test --project=voz
# Revisar:  npm.cmd run revisar-escenarios -- especificaciones/cobranza-voz.feature
#
# CP-305 tiene un defecto SEMBRADO (VOZ-01): el agente no avisa que la llamada se graba. Queda en rojo a propósito.

Característica: Cobranza amable por un agente de voz con IA
  Como líder de calidad del canal de voz
  quiero revisar la transcripción de cada llamada del agente
  para saber que cumple la política de cobranza y entiende lo que dice el cliente

  @voz @CP-301 @CP-302 @CP-303 @CP-304 @CP-305 @CP-306
  Esquema del escenario: El agente cumple el guion y entiende al cliente: <caso>
    Dado la llamada «<llamada>» transcrita del audio sintético
    Cuando el oráculo revisa la transcripción contra el guion
    Entonces el agente dice «<frases>» y ninguna frase prohibida
    Y la intención del cliente es «<intencion>» con monto <monto> y fecha «<fecha>»
    Y el WER contra el guion es de máximo 15 %

    Ejemplos:
      | llamada | caso                         | frases                                     | intencion            | monto  | fecha           |
      | CP-301  | promesa de pago con fecha    | identificación, motivo, grabación, acuerdo | promesa_de_pago      | 185000 | 15 de diciembre |
      | CP-302  | ya pagó                      | identificación, motivo, grabación          | ya_pago              | 240000 | 20 de noviembre |
      | CP-303  | no reconoce la deuda         | identificación, motivo, grabación          | no_reconoce_la_deuda | 95000  | ninguna         |
      | CP-304  | pide hablar con una persona  | identificación, motivo, grabación, acuerdo | pide_una_persona     | 310000 | ninguna         |
      | CP-305  | olvida el aviso de grabación | identificación, motivo, grabación, acuerdo | promesa_de_pago      | 120000 | 30 de noviembre |
      | CP-306  | línea con ruido              | identificación, motivo, grabación, acuerdo | promesa_de_pago      | 450000 | 10 de diciembre |
