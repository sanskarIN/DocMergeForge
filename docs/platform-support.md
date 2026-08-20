# Platform Support

DocMergeForge has one document-processing core with multiple user interfaces. Platform support is intentionally described by **how the application is delivered**, so browser access is not confused with a native mobile package.

## Support matrix

| Platform | Native desktop GUI | CLI | Responsive web client | Current delivery |
| --- | --- | --- | --- | --- |
| Windows 10/11 | Yes | Yes | Yes | PyInstaller desktop build, Python source, browser |
| macOS | Yes | Yes | Yes | PyInstaller desktop build, Python source, browser |
| Linux | Yes | Yes | Yes | PyInstaller desktop build, Python source, browser |
| Android | No | No | Yes | Modern browser connected to a DocMergeForge web host |
| iPhone / iOS | No | No | Yes | Safari/modern browser connected to a DocMergeForge web host |
| iPad / iPadOS | No | No | Yes | Safari/modern browser connected to a DocMergeForge web host |
| ChromeOS | No | No | Yes | Modern browser connected to a DocMergeForge web host |
| Other modern browser platforms | No | No | Yes | Responsive browser client |

The maintained platform matrix is also exposed programmatically by `docmergeforge.platforms.support_matrix()` and by the web endpoint `GET /api/platforms`.

## Desktop platforms

Windows, macOS, and Linux continue to use the existing PySide6 desktop application and Python CLI. Native executables must be built on the target operating system. Signing, notarization, clean-machine acceptance, and release evidence remain separate release gates.

The core PDF/DOCX engines are shared between the desktop, CLI, and web interfaces. The web layer does not reimplement document merging.

## Browser, Android, iOS/iPadOS, and ChromeOS

Install the optional web runtime on a computer or server that can run DocMergeForge:

```bash
pip install -e ".[web]"
```

Start the loopback-only server:

```bash
docmergeforge-web
```

The default address is:

```text
http://127.0.0.1:8765/
```

This mode is intended for the same computer and requires no access token because the server is bound to loopback only.

### Use from a phone, tablet, Chromebook, or another computer on the LAN

A non-loopback bind is blocked unless an access token is configured. Generate an in-memory token automatically:

```bash
docmergeforge-web --host 0.0.0.0 --token auto
```

Or provide your own high-entropy token:

```bash
docmergeforge-web --host 0.0.0.0 --token "YOUR_LONG_RANDOM_TOKEN"
```

Then open the host computer's LAN address from the phone/tablet browser:

```text
http://HOST-LAN-IP:8765/
```

Enter the generated/configured value in **Access token (LAN only)**. The token is retained only in that browser tab's session storage and merge requests send it using the `X-DocMergeForge-Token` header.

For a one-time link handoff on a trusted LAN, the browser also accepts the token in the URL **fragment**:

```text
http://HOST-LAN-IP:8765/#token=YOUR_LONG_RANDOM_TOKEN
```

A fragment is handled by the browser and is not included in the HTTP request sent to the DocMergeForge host. The page moves the value into session storage and immediately removes the fragment from the visible address. Do **not** put an access token in a query string such as `?token=...`; query strings can be recorded by HTTP access logs, proxies, browser history, or other infrastructure before page JavaScript can remove them.

Do not expose the built-in HTTP server directly to the public Internet. For remote Internet access, place it behind a properly configured HTTPS reverse proxy, authentication layer, request-size limits, and normal server hardening.

## Web merge behavior

The responsive interface:

- accepts homogeneous PDF or DOCX upload sets;
- orders detected numbered parts naturally before merging;
- uses the existing validated `PdfMergeEngine` and `DocxMergeEngine`;
- accepts an optional shared PDF password for encrypted inputs;
- writes uploads and outputs only inside a temporary per-request workspace;
- closes upload handles even when upload validation or size enforcement fails;
- removes the temporary workspace after the response is sent or after an error;
- sanitizes uploaded filenames and output names;
- rejects unsupported upload types and mixed PDF/DOCX requests;
- limits each request to 500 uploaded files;
- defaults to a 4096 MiB total request-file limit, configurable with `--max-upload-mib`;
- sends completed output as a browser download;
- returns a generic remote error for unexpected engine failures while recording the exception in host logs;
- applies browser-shell anti-framing, referrer, content-type, permissions, and content-security headers;
- exposes `/healthz` and `/api/platforms` for status/capability checks.

The browser shell includes a web-app manifest and service worker. The shell can be installable where the browser and serving context permit it, but document merging still requires connectivity to the Python DocMergeForge host. This is not represented as fully offline in-browser document processing.

## Native Android and iOS packages

The current cross-platform mobile path is the responsive web client. The repository does **not** claim an Android APK/AAB or iOS IPA build, and it does not claim that CPython/PySide6 document processing runs natively inside those mobile packages.

A future native mobile shell can consume the same API or use a separately accepted mobile-compatible processing layer. Any such package needs its own filesystem picker, sandbox/storage, lifecycle, background-work, signing, store-distribution, accessibility, and device-test acceptance before it is described as native support.

## Browser privacy boundary

The original desktop and CLI workflows are local-first. Browser mode adds a network boundary between the browser and the Python host:

- on `127.0.0.1`, the browser and host are the same machine;
- on a LAN bind, uploaded manuscript bytes travel across that LAN to the selected DocMergeForge host;
- DocMergeForge does not upload them to a project-operated cloud service by default;
- HTTP on an untrusted network does not provide transport confidentiality;
- an access token controls merge requests but is not a substitute for HTTPS transport confidentiality.

Use loopback for the strongest local-first behavior. Use HTTPS and appropriate authentication when traffic leaves a trusted local machine/network.

## Verification

The normal quality workflow installs `.[dev,web]` on Python 3.12 and 3.13. Tests cover:

- the maintained platform matrix;
- safe loopback defaults;
- PDF browser upload/merge/download;
- DOCX browser upload/merge/download;
- token-protected merge requests;
- fragment-based token bootstrap and browser-shell security headers;
- generic remote handling for unexpected merge-engine errors;
- upload-size fail-closed behavior;
- mixed-format rejection;
- health and platform-capability endpoints.

These automated tests prove application-level behavior when they pass in CI; they are not a substitute for manual browser/device acceptance on every Android/iOS/browser version.
