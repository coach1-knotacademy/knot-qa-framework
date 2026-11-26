# Guía rápida · Kit móvil en Windows

**Para quién:** quien tenga **permisos de administrador** en su equipo o un equipo de pruebas que TI ya preparó.
**Si no los tienes, no pierdas la tarde:** el plan B es leer el código del kit (`src/paginas/`, `tests/`) y ver la demo grabada en la página del kit. Eso ya enseña el 80 %.

Tiempo realista con permisos y buena red: **1 a 2 horas** (la mayor parte son descargas). Necesitas **16 GB de RAM** (8 GB arranca, pero sufre) y **unos 20 GB libres** en disco.

---

## Paso 0 · Lo que de verdad frena en un equipo corporativo

Revísalo **antes** de descargar nada. Si alguno de estos cuatro está cerrado, la solución pasa por TI, no por un truco.

### 1. Virtualización y permisos de administrador

El emulador de Android es una máquina virtual: necesita la virtualización del procesador **encendida en la BIOS** y un hipervisor de Windows.

- **¿Está encendida?** Administrador de tareas → Rendimiento → CPU → abajo dice **Virtualización: Habilitado**.
  Si dice *Deshabilitado*, se activa en la BIOS/UEFI (Intel VT-x o AMD-V/SVM). En un equipo corporativo, la BIOS suele tener clave: **pídeselo a TI**.
- **El hipervisor que usa el emulador** en Windows 10/11 es **Windows Hypervisor Platform (WHPX)**. Activarlo pide administrador y reinicio:

  ```powershell
  # PowerShell COMO ADMINISTRADOR (o que lo haga TI)
  Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform -All
  ```

  Si TI ya usa Hyper-V o la seguridad basada en virtualización (VBS, Credential Guard), WHPX convive con ellos; el viejo HAXM de Intel **no** (y ya no se mantiene: no lo instales).
- **Comprobar** (cuando ya tengas el SDK, paso 4):

  ```powershell
  & "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -accel-check
  ```

  Debe decir `WHPX ... is installed and usable` o algo equivalente. Si dice que no hay aceleración, el emulador o no arranca o va tan lento que Appium se rinde.

### 2. VDI o escritorio remoto (Citrix, Azure Virtual Desktop, VMware Horizon)

Si trabajas **dentro de una máquina virtual**, el emulador necesita **virtualización anidada** (una VM dentro de otra). Casi ninguna VDI corporativa la tiene.
Síntoma: `-accel-check` dice que no hay hipervisor, aunque en tu portátil físico sí lo haya.

Salidas honestas, en este orden:

1. Un **celular Android de pruebas por USB** (paso 7, opción B), si la política de TI permite USB y depuración ADB.
2. El **plan B**: leer el código y ver la demo grabada.
3. Una nube de dispositivos (BrowserStack, Sauce Labs, LambdaTest) **solo si tu empresa ya la contrata**: piden cuenta, igual que GitHub.

### 3. Proxy y certificados de inspección SSL

Muchos bancos revisan todo el tráfico HTTPS con un certificado propio. Síntomas: `npm ERR! code UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, `SELF_SIGNED_CERT_IN_CHAIN`, `PKIX path building failed` (Java/Gradle/Maven) o el SDK Manager de Android Studio que no baja nada.

**Pídele a TI dos datos:** la dirección del proxy (por ejemplo `http://proxy.empresa:8080`) y el **certificado raíz** de la inspección SSL en formato `.pem` o `.cer`. Con eso:

```powershell
# npm (Node y la instalación de Appium y sus drivers)
npm.cmd config set proxy http://proxy.empresa:8080
npm.cmd config set https-proxy http://proxy.empresa:8080
npm.cmd config set cafile "C:\certificados\raiz-empresa.pem"

# Node (el script que baja el APK y Appium mismo) — solo para esta terminal
$env:HTTPS_PROXY = 'http://proxy.empresa:8080'
$env:NODE_EXTRA_CA_CERTS = 'C:\certificados\raiz-empresa.pem'
```

- **Android Studio:** File → Settings → Appearance & Behavior → System Settings → **HTTP Proxy** → *Manual proxy configuration* (o *Auto-detect* si TI usa PAC). En la misma ventana, **Server Certificates** → aceptar el certificado de la empresa.
- **Java (Gradle o Maven, para la versión Java que verás en el banco):** el certificado va al almacén de confianza de **tu** JDK. Si el JDK está en `C:\Program Files`, este comando pide administrador (o que lo corra TI):

  ```powershell
  keytool -importcert -alias raiz-empresa -file C:\certificados\raiz-empresa.cer -cacerts -storepass changeit
  ```

  Proxy en Maven: `%USERPROFILE%\.m2\settings.xml` → `<proxies>`. En Gradle: `%USERPROFILE%\.gradle\gradle.properties` → `systemProp.https.proxyHost=...` y `systemProp.https.proxyPort=...`.
- **Nunca** apagues la verificación SSL (`strict-ssl false`, `NODE_TLS_REJECT_UNAUTHORIZED=0`): funciona hoy y deja el equipo abierto a cualquiera. La salida correcta es el certificado de TI.

### 4. El antivirus (Defender u otro)

Puede bloquear o poner en cuarentena `adb.exe`, el emulador, un ZIP o archivos de `node_modules`, o volver todo muy lento.

- **No lo desactives nunca**, ni «un ratico». Tampoco cambies el nombre de archivos para esquivarlo.
- Pídele a TI una **exclusión de carpetas** concretas: `%LOCALAPPDATA%\Android\Sdk`, `%USERPROFILE%\.android`, `%USERPROFILE%\.appium` y la carpeta del repo. Lleva el nombre exacto del archivo bloqueado (sale en *Seguridad de Windows → Historial de protección*).

---

## Paso 1 · Node.js 22 (LTS)

- Verificado con **Node 22.18.0** (sirve cualquier 22.12 o superior). Descarga: nodejs.org → *Windows Installer (.msi)* de la versión 22 LTS.
- Sin administrador: el **ZIP** de Node 22 descomprimido en tu carpeta de usuario y agregado al `PATH` de usuario también sirve.

```powershell
node --version     # v22.x
npm.cmd --version  # 10 u 11
```

En PowerShell usa **`npm.cmd`** y **`npx.cmd`**: si la política de scripts bloquea `npm.ps1`, así no hay que cambiarla.

## Paso 2 · JDK 21

- Verificado con **OpenJDK 21.0.10**. En Windows: **Eclipse Temurin 21 (LTS)**, instalador `.msi`, marcando *Set JAVA_HOME variable*.
- Si no marcaste la opción, crea la variable **de usuario** (no pide administrador):

```powershell
[Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-21.0.10.7-hotspot', 'User')
# Cierra y abre la terminal
java -version
```

(La ruta exacta depende de la versión que bajes: ábrela en el Explorador y cópiala.)

## Paso 3 · Android Studio, SDK y herramientas

- Verificado con **Android Studio 2026.2**. Instálalo con las opciones por omisión: trae el **SDK**, **Platform-Tools** (adb) y el **Emulator**.
- En *More Actions → SDK Manager → SDK Tools* marca también **Android SDK Command-line Tools (latest)**.
- Versiones con las que se probó el kit: Platform-Tools **35.0.2**, Emulator **37.2.13**, Command-line Tools **19.0**, Build-Tools **36.0.0**.

Variables **de usuario** (sin administrador):

```powershell
$sdk = "$env:LOCALAPPDATA\Android\Sdk"
[Environment]::SetEnvironmentVariable('ANDROID_HOME', $sdk, 'User')
$ruta = [Environment]::GetEnvironmentVariable('Path', 'User')
[Environment]::SetEnvironmentVariable('Path', "$ruta;$sdk\platform-tools;$sdk\emulator", 'User')
# Cierra y abre la terminal
adb version
emulator -list-avds
```

## Paso 4 · El emulador (AVD)

Android Studio → **Device Manager** → **+ Create Virtual Device**:

1. Teléfono: **Medium Phone** (o Pixel 8).
2. Imagen del sistema: en un equipo **Intel o AMD** elige una **x86_64** con *Google APIs* (API 35 o 36). En esta guía se verificó con **Android 17 (API 37), Google Play, arm64** en una Mac con Apple Silicon: en Windows Intel/AMD la imagen debe ser **x86_64**, nunca arm64. La app de práctica funciona desde Android 5 (API 21).
3. RAM del AVD: 2048 MB está bien.

Arráncalo con ▶ y espera a ver el escritorio de Android. Comprueba:

```powershell
adb devices          # debe salir: emulator-5554   device
```

**El primer arranque es lento:** Google Play actualiza apps por detrás durante unos minutos. Si Appium falla en ese rato con `instrumentation process cannot be initialized`, espera y repite. Si aparece «System UI isn't responding», toca **Wait**.

## Paso 5 · Appium 3 y el driver UiAutomator2

Versiones con las que se verificó el kit: **Appium 3.2.0** y **UiAutomator2 7.0.0**. Fíjalas para que nadie del equipo tenga otra:

```powershell
npm.cmd install -g appium@3.2.0
appium --version                                  # 3.2.0
appium driver install uiautomator2@7.0.0
appium driver list --installed                    # uiautomator2@7.0.0 [installed (npm)]
```

(`npm -g` no pide administrador si Node se instaló para tu usuario. Si te lo pide, instala Node en tu carpeta de usuario: paso 1.)

## Paso 6 · El doctor

```powershell
appium driver doctor uiautomator2
```

Debe terminar con **`0 required fixes needed`**. Los avisos *optional* (bundletool, gstreamer, ffmpeg) **no** hacen falta para este kit. Si hay *required fixes*, casi siempre es `ANDROID_HOME` o `JAVA_HOME` (pasos 2 y 3): cierra y abre la terminal después de crear las variables.

## Paso 7 · Correr el kit

```powershell
cd ruta\del\repo\movil
npm.cmd install         # instala WebdriverIO 9.29.1 y TypeScript 5.9.3 SOLO en esta carpeta
npm.cmd run app         # baja el APK de práctica (18 MB) a apps\
```

**Opción A · emulador:** abre el AVD (paso 4). **Opción B · celular de pruebas por USB:** Ajustes → Acerca del teléfono → toca 7 veces *Número de compilación* → Opciones de desarrollador → *Depuración USB*. Conéctalo, acepta la huella en el celular y mira su serial en `adb devices`; luego `$env:DISPOSITIVO = 'SERIAL'`. Usa un equipo de pruebas, **no tu celular personal ni uno con apps o datos del banco**.

```powershell
# Terminal 1 (se deja abierta)
npm.cmd run appium

# Terminal 2
npm.cmd test
```

Resultado esperado: `4 passing` y la carpeta `evidencias\corrida-<fecha>\` con capturas, videos y `pasos.txt`.

## Paso 8 · Appium Inspector (para ver los localizadores)

Es la «herramienta de desarrollador» del celular: muestra el árbol de la pantalla con `content-desc`, `resource-id` y `text`.

- Descarga: GitHub → *appium/appium-inspector* → *Releases* → `Appium-Inspector-<versión>-win-x64.exe` (la más reciente al escribir esto: **2026.11.6**). Si TI no deja instalar `.exe`, está el `.zip` portátil de la misma página.
- Conexión: Remote Host `127.0.0.1`, Port `4723`, Path `/`. Capacidades (JSON):

```json
{
  "platformName": "Android",
  "appium:automationName": "UiAutomator2",
  "appium:deviceName": "emulator-5554",
  "appium:app": "C:\\ruta\\del\\repo\\movil\\apps\\mda-2.3.0-27.apk"
}
```

- Sin Inspector también se puede: `await driver.getPageSource()` dentro de una prueba devuelve el mismo árbol en XML.

> Nota honesta: el kit se verificó de punta a punta en macOS (Apple Silicon). Las versiones son las mismas para Windows; lo que cambia es la imagen del emulador (x86_64) y lo que diga TI sobre virtualización, proxy y antivirus.

---

## Pídele ayuda a tu IA (Copilot)

Copia el prompt, pega **solo** la salida que pide y nada más. **Nunca** pegues datos del banco: ni nombres de servidores internos, ni usuarios, claves, tokens, capturas de apps del banco o datos de clientes. Si la salida trae algo así (por ejemplo, la dirección interna del proxy), **reemplázalo** por `<PROXY>` o `<USUARIO>` antes de pegar.

**1 · El doctor**

> Estoy instalando Appium 3.2.0 con el driver UiAutomator2 7.0.0 en Windows 11 para automatizar una app Android de práctica en un emulador. Te pego la salida de `appium driver doctor uiautomator2`. Dime, en orden, qué *required fix* corrijo primero, con el comando exacto de PowerShell. No me propongas desactivar el antivirus ni la verificación SSL, y si algo necesita administrador, dímelo para pedírselo a TI.
> ```
> (pega aquí la salida)
> ```

**2 · El emulador no arranca**

> Este es el error al iniciar el emulador de Android Studio (AVD con imagen x86_64, API 35) en un portátil corporativo con Windows 11. Te pego también la salida de `emulator -accel-check`. ¿Es la virtualización de la BIOS, WHPX/Hyper-V, o estoy en una VDI sin virtualización anidada? Dame la forma de comprobarlo y qué le pido exactamente a TI.
> ```
> (pega el error y la salida de -accel-check)
> ```

**3 · npm o la descarga fallan por certificado**

> `npm.cmd install` (o la descarga del APK) falla con este error en un equipo corporativo con proxy de inspección SSL. TI me dio el certificado raíz en `C:\certificados\raiz-empresa.pem`. Dame los comandos de `npm config` y la variable `NODE_EXTRA_CA_CERTS` para que funcione **sin** desactivar `strict-ssl`.
> ```
> (pega el error, con la dirección del proxy reemplazada por <PROXY>)
> ```

**4 · Appium no crea la sesión**

> Mi prueba de WebdriverIO 9 contra Appium 3.2.0 + UiAutomator2 falla al crear la sesión. Te pego las últimas 40 líneas de la terminal donde corre `appium` y el mensaje de la prueba. El emulador sale como `device` en `adb devices`. ¿Cuál es la causa más probable y qué capacidad o tiempo de espera ajusto?
> ```
> (pega aquí)
> ```

**5 · Un localizador no encuentra el elemento**

> En una app Android de práctica (SauceLabs My Demo App), este elemento no se encuentra con WebdriverIO. Te pego el fragmento del `getPageSource()` donde está el elemento y el localizador que usé. Propón uno siguiendo esta escalera: accessibility id (`~…`), luego resource-id (`id=paquete:id/…`), luego `android=new UiSelector()…`. No uses XPath.
> ```
> (pega el fragmento del XML y tu localizador)
> ```

**6 · Pasarlo a Java**

> Traduce este Page Object de TypeScript con WebdriverIO a Java con Appium java-client 9 y JUnit 5, manteniendo los mismos localizadores (`AppiumBy.accessibilityId`, `AppiumBy.id`, `AppiumBy.androidUIAutomator`) y una espera explícita con `WebDriverWait`. No uses XPath.
> ```
> (pega aquí src/paginas/PaginaLogin.ts)
> ```
