# Kit móvil · Appium + WebdriverIO + TypeScript

Las **mismas capas** del framework de Playwright (config, páginas, datos, pruebas), ahora en un **celular Android**.
La app es pública y está hecha para practicar automatización: la **SauceLabs My Demo App** (una tienda; no es de ningún banco y no maneja dinero real).

> **¿Para quién?** Para quien tenga permisos de administrador en su equipo (hay que instalar Android Studio y activar la virtualización).
> Si no los tienes, el **plan B** es igual de válido: lee el código de `src/paginas/` y `tests/` y mira la demo grabada en la página del kit (`movil.html` en el sitio del curso).
> Para instalar en Windows: [`GUIA_INSTALACION_WINDOWS.md`](GUIA_INSTALACION_WINDOWS.md).

## Qué es cada pieza

| Pieza | Qué es | En este kit |
|---|---|---|
| **Cliente** | Tu código de prueba. Pide «toca esto», «lee aquello». | WebdriverIO + TypeScript (`tests/`, `src/`) |
| **Servidor** | Appium: recibe los pedidos por HTTP y los traduce. | `appium` en el puerto 4723 |
| **Driver** | El «traductor» de Appium para cada sistema operativo. | UiAutomator2 (Android) |
| **Dispositivo** | Donde corre la app. | El emulador de Android Studio (o un celular por USB) |

En Playwright, el cliente y el «servidor» vienen juntos. En Appium son **dos programas**: por eso se abren dos terminales.

## Cómo correrlo

Antes: Node 22, Appium 3 con el driver UiAutomator2, Android Studio con un emulador (AVD). La guía de Windows explica cada uno.

### macOS

```bash
cd movil
npm install             # una vez
npm run app             # una vez: baja el APK a apps/ (18 MB)
emulator -avd Medium_Phone &   # o ábrelo desde Android Studio → Device Manager
npm run appium          # terminal 1: el servidor (se deja abierto)
npm test                # terminal 2: las 4 pruebas
```

### Windows (PowerShell)

En PowerShell corporativo `npm` y `npx` suelen estar bloqueados por la política de scripts (`npm.ps1`). Se usan **`npm.cmd`** y **`npx.cmd`**: es lo mismo, sin cambiar ninguna política.

```powershell
cd movil
npm.cmd install
npm.cmd run app
# Abre el emulador desde Android Studio → Device Manager → ▶
npm.cmd run appium      # terminal 1 (se deja abierta)
npm.cmd test            # terminal 2
```

Correr un solo caso: `npm.cmd test -- --mochaOpts.grep "CP-402"`.
Grabar una demo que se pueda seguir con los ojos (pausa de 1,2 s después de cada paso): `$env:PASO_LENTO = '1200'; npm.cmd test`.

## Qué hay en cada carpeta

```
movil/
├── wdio.conf.ts               el "playwright.config.ts" de este kit: pruebas, reporte, ganchos de evidencia
├── especificaciones/
│   └── tienda.feature         los 4 casos en Gherkin (# language: es), con @CP-401…@CP-404
├── src/
│   ├── config/entorno.ts      CAPA CONFIG: host, puerto, dispositivo y APK salen de variables o .env
│   ├── paginas/               CAPA PÁGINAS: un Page Object por pantalla + la escalera de localizadores
│   ├── datos/                 CAPA DATOS: usuarios de ejemplo y productos (precios en centavos)
│   └── soporte/               app limpia antes de cada prueba y evidencia automática
├── tests/tienda.spec.ts       las pruebas: un it() por escenario, un paso() por línea del Gherkin
├── scripts/descargar-app.js   baja el APK (Node; Windows, macOS y Linux; respeta HTTPS_PROXY)
├── apps/                      aquí queda el APK (no se sube al repo)
└── evidencias/                capturas, video y pasos de cada corrida (solo se sube demo/)
```

## Los casos

| CP | Escenario | Qué verifica |
|---|---|---|
| CP-401 | Un comprador entra con su usuario y su clave | Ve «Products» y el menú ofrece «Log Out» |
| CP-402 | Un usuario bloqueado no puede entrar | «Sorry this user has been locked out.» y sigue en «Login» |
| CP-403 | Sin usuario, la app lo pide antes de intentar entrar | «Username is required» |
| CP-404 | Dos mochilas en el carrito suman el total correcto | «2 Items» y total «$ 59.98» |

Los usuarios son los de **ejemplo que la propia app muestra** en su pantalla de login. Antes de cada prueba la app se abre **limpia** (sin sesión y con el carrito vacío): ninguna prueba depende de otra.

## La escalera de localizadores móviles

Se sube un peldaño **solo** si el de abajo no existe en esa pantalla. Está escrita en [`src/paginas/localizadores.ts`](src/paginas/localizadores.ts).

| Peldaño | Estrategia | Ejemplo en el kit | Cuándo |
|---|---|---|---|
| 1 | **Accessibility id** (`content-desc`) | `~Tap to login with given credentials` | Siempre que exista: lo pone el desarrollador a propósito y no cambia con el diseño. Es el `getByRole` del móvil. |
| 2 | **resource-id** | `id=com.saucelabs.mydemoapp.android:id/nameET` | Si no hay accessibility id (los campos de esta app). Estable, pero es un nombre técnico. |
| 3 | **UiAutomator** | `android=new UiSelector().text("Sauce Labs Backpack")` | Cuando lo único que distingue al elemento es su texto (un producto en una lista). |
| 4 | **XPath** | — | **Nunca.** Es lento en móvil y se rompe con cualquier cambio. Si no hay peldaño 1-3, se le pide un `content-desc` al equipo de desarrollo. |

**Error real del proyecto anterior:** `//*[contains(text(),'Login')]` no encuentra nada en UiAutomator2. En Android el texto es un **atributo** (`@text`), no un nodo de texto como en HTML. El equivalente correcto es el peldaño 3: `new UiSelector().text("Login")` (exacto) o `.textContains("Log")`.

¿Cómo ver qué tiene cada elemento? Con **Appium Inspector** (ver la guía) o con `await driver.getPageSource()`, que devuelve el árbol de la pantalla con `text`, `content-desc` y `resource-id`.

## La evidencia

Sin pedirlo en la prueba, cada corrida deja en `evidencias/corrida-<fecha>/<CP>/`:

- una **captura por paso** (`01-dado-que-….png`, `02-cuando-….png`…), con el texto del Gherkin;
- **`FALLO.png`** si algo falla, y el mensaje en `pasos.txt`;
- **`video.mp4`** de la prueba (`driver.startRecordingScreen` / `stopRecordingScreen`, el grabador del propio Android, a 540×1200);
- **`pasos.txt`**: el escenario con ✓ o ✗ en cada paso.

`evidencias/` no se sube al repo (puede tener datos de la corrida). Solo `evidencias/demo/` (tres capturas y un video corto) se publica en el sitio como demo grabada.

## Variables (capa config)

Nada de host, puerto, dispositivo ni ruta del APK está escrito en el código. Sin variables se usa lo normal; para cambiar algo, ver [`.env.ejemplo`](.env.ejemplo):

| Variable | Por omisión |
|---|---|
| `APPIUM_HOST` / `APPIUM_PUERTO` | `127.0.0.1` / `4723` |
| `DISPOSITIVO` | `emulator-5554` (lo que muestra `adb devices`) |
| `VERSION_ANDROID` | vacía: la del dispositivo |
| `RUTA_APP` | `apps/mda-2.3.0-27.apk` |
| `TIEMPO_ARRANQUE` | `120000` ms (el primer arranque instala el servidor de UiAutomator2 en el celular) |
| `PASO_LENTO` | `0` ms (solo para grabar demos) |

## Rosetta: TypeScript (este kit) ↔ Java (lo que verás en el banco)

En muchos bancos el móvil se automatiza en Java con `java-client` de Appium (Maven, JUnit o TestNG, a veces con Cucumber o Serenity). La idea es la misma; cambia la sintaxis.

| Qué | TypeScript + WebdriverIO | Java + java-client 9.x |
|---|---|---|
| Abrir la sesión | `capabilities` en `wdio.conf.ts` | `new AndroidDriver(new URL(url), new UiAutomator2Options().setApp(ruta))` |
| Peldaño 1 | `$('~View menu')` | `driver.findElement(AppiumBy.accessibilityId("View menu"))` |
| Peldaño 2 | `$('id=com.saucelabs.mydemoapp.android:id/nameET')` | `driver.findElement(AppiumBy.id("com.saucelabs.mydemoapp.android:id/nameET"))` |
| Peldaño 3 | `$('android=new UiSelector().text("Products")')` | `driver.findElement(AppiumBy.androidUIAutomator("new UiSelector().text(\"Products\")"))` |
| Tocar / escribir | `await el.click()` / `await el.setValue('…')` | `el.click()` / `el.sendKeys("…")` |
| Esperar | `await el.waitForDisplayed()` | `new WebDriverWait(driver, Duration.ofSeconds(15)).until(ExpectedConditions.visibilityOfElementLocated(by))` |
| Verificar | `await expect(el).toHaveText('$ 59.98')` (reintenta solo) | `assertEquals("$ 59.98", el.getText())` (después de esperar) |
| Captura | `await driver.saveScreenshot(ruta)` | `((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE)` |
| Video | `driver.startRecordingScreen()` / `stopRecordingScreen()` | `driver.startRecordingScreen(new AndroidStartScreenRecordingOptions()…)` / `driver.stopRecordingScreen()` |
| App limpia | `driver.execute('mobile: clearApp', { appId })` | `driver.executeScript("mobile: clearApp", Map.of("appId", paquete))` |
| Escenario / paso | `it('@CP-401 …')` / `paso('Dado …')` | `@Test` (JUnit) o `@Dado("…")` (Cucumber) |
| Antes / después | `beforeTest` / `afterTest` | `@BeforeEach` / `@AfterEach` |
| Config | `process.env.DISPOSITIVO` / `.env` | `System.getenv("DISPOSITIVO")` / `.properties` |
| Correr | `npm.cmd test` | `mvn test` |

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| `Appium no responde en http://127.0.0.1:4723/status` | Falta la terminal 1: `npm.cmd run appium`. |
| `No encuentro la app en …apps/…apk` | `npm.cmd run app`, o baja el APK desde el navegador y déjalo en `apps/`. |
| `Could not find a connected Android device` | El emulador no está prendido o `DISPOSITIVO` no coincide con `adb devices`. |
| `The instrumentation process cannot be initialized within …ms` | El emulador recién arrancado está ocupado (actualizaciones de Google Play). Espera un minuto y repite, o sube `TIEMPO_ARRANQUE`. |
| `System UI isn't responding` en la pantalla del emulador | Emulador sin aceleración por hardware o con poca RAM: toca **Wait**; revisa la virtualización (guía, paso 0). |

Diagnóstico del entorno: `npm.cmd run doctor` (es `appium driver doctor uiautomator2`).
