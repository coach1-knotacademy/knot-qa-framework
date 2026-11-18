# La IA y la arquitectura · S5

Tres pruebas que escribió una IA (Claude Sonnet, en el papel de un asistente tipo Copilot) el 17 de noviembre de 2026. Se guardan **tal cual**, sin corregir, para revisarlas en clase. Después se corrieron contra el Banco Demo.

| Archivo | Qué recibió la IA | Resultado real al correrla |
|---|---|---|
| [`1_sin_contexto.spec.ts`](1_sin_contexto.spec.ts) | Solo el pedido del tester, sin ver el repo | **Falla al primer paso**: inventó la ruta `/login`, que no existe, y se queda esperando el campo Usuario. Además escribe la URL y los datos a mano, pone los localizadores dentro de la prueba y no sabe que una recarga de $60.000 pide código |
| [`2_con_contexto.spec.ts`](2_con_contexto.spec.ts) | El **mismo** pedido, pero dentro del repo: leyó `.github/copilot-instructions.md` y los Page Objects | **Verde**. Usa el flujo de ingreso, la fábrica, el Page Object y el paso del código (que el pedido no mencionaba: lo sacó de la regla) |
| [`3_regresion_bug_4x1000.spec.ts`](3_regresion_bug_4x1000.spec.ts) | "Explora cómo se comporta la app hoy y **déjame la prueba en verde**" (solo con curl, sin ver el código) | **Rojo a propósito**. La IA notó que la respuesta decía `total: 100.400` pero el saldo bajó solo $100.000, y no quiso dejarla verde: "si hubiera puesto 150000, habría quedado verde, pero se estaría dando por bueno el comportamiento actual". Es el BUG-02 |

## Lo que muestran

1. **Mismo pedido, distinto resultado.** La diferencia no es la IA: es el contexto. Con un framework ordenado (Page Object, fábrica, configuración, fixtures) y unas instrucciones claras, la IA copia el molde.
2. **La IA no conoce lo que nadie le contó.** Sin el repo no sabía que más de $50.000 pide código. Con el repo lo dedujo de `banco-demo/reglas.js`.
3. **El valor esperado lo decide una persona.** Una herramienta que "graba lo que ve" (por ejemplo, las aserciones de `npm run grabar`) habría dejado `150.000` como esperado y la prueba saldría verde validando el bug. Esta IA lo detectó porque la propia respuesta se contradecía, pero no siempre pasa. La regla de negocio manda.

## Reglas de uso que salen de aquí

- A la IA solo va el repo de práctica o un sitio público. **Nunca** pantallas, datos, logs ni capturas del banco.
- Un `trace.zip` de Playwright guarda cookies y lo que se escribió: tampoco se pega en la IA si viene de un sistema real.
- Lo que la IA escribe se corre, se lee y se justifica antes de subirlo.
- Si la IA propone `npm install algo`, no se instala: hay paquetes inventados por la IA que después registran atacantes. Las dependencias nuevas pasan por TI.
