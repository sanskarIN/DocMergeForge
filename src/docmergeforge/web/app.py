from __future__ import annotations

import re
import secrets
import shutil
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from starlette.background import BackgroundTask

from docmergeforge.core.models import DocumentKind, DocxSettings, InputDocument, PdfSettings
from docmergeforge.discovery.part_detection import natural_key
from docmergeforge.discovery.scanner import scan
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.platforms import current_runtime, support_matrix

_MAX_FILES = 500
_CHUNK_SIZE = 1024 * 1024
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._() \-\u0080-\uffff]+")

_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#0b1020">
  <meta name="description" content="DocMergeForge responsive PDF and DOCX merger">
  <link rel="manifest" href="/manifest.webmanifest">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <title>DocMergeForge Web</title>
  <style>
    :root { color-scheme: dark light; font-family: Inter, system-ui, sans-serif; }
    body { margin: 0; background: #0b1020; color: #eef2ff; min-height: 100vh; }
    main { max-width: 900px; margin: auto; padding: 28px 18px 48px; }
    .card { background: #141b30; border: 1px solid #2c3757; border-radius: 18px; padding: 20px; }
    h1 { margin-top: 0; font-size: clamp(1.8rem, 6vw, 3rem); }
    p { line-height: 1.55; }
    label { display: block; font-weight: 700; margin: 16px 0 7px; }
    input, button { box-sizing: border-box; width: 100%; min-height: 48px; border-radius: 12px; }
    input { border: 1px solid #46547a; background: #0f1629; color: #eef2ff; padding: 10px 12px; }
    input[type=file] { padding: 9px; }
    button { margin-top: 20px; border: 0; background: #6d7cff; color: white; font-weight: 800; cursor: pointer; }
    button:disabled { opacity: .55; cursor: progress; }
    .muted { color: #b7c0d9; }
    .status { min-height: 28px; margin-top: 16px; font-weight: 650; }
    .grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
    .pill { display: inline-block; border: 1px solid #46547a; border-radius: 999px; padding: 6px 10px; margin: 4px 4px 0 0; }
    a { color: #aeb8ff; }
    @media (prefers-color-scheme: light) {
      body { background: #f4f6fb; color: #182035; }
      .card { background: white; border-color: #d8deeb; }
      input { background: white; color: #182035; border-color: #aeb8cc; }
      .muted { color: #536079; }
    }
  </style>
</head>
<body>
<main>
  <section class="card">
    <h1>DocMergeForge</h1>
    <p>Merge PDF or DOCX parts from Windows, macOS, Linux, Android, iPhone/iPad, ChromeOS, or any modern browser.</p>
    <p class="muted">Files are processed by the DocMergeForge Python host you connected to. The default server binds only to this computer; LAN use requires an access token.</p>

    <form id="merge-form">
      <label for="files">PDF or DOCX files</label>
      <input id="files" name="files" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" multiple required>

      <div class="grid">
        <div>
          <label for="output-name">Output name (optional)</label>
          <input id="output-name" name="output_name" placeholder="My_Book_Master">
        </div>
        <div>
          <label for="password">PDF password (optional)</label>
          <input id="password" name="password" type="password" autocomplete="off">
        </div>
      </div>

      <button id="merge-button" type="submit">Merge and download</button>
      <div id="status" class="status" role="status" aria-live="polite"></div>
    </form>
  </section>

  <p class="muted">
    <span class="pill">PDF</span>
    <span class="pill">DOCX</span>
    <span class="pill">Responsive</span>
    <span class="pill">Local-first host</span>
  </p>
</main>
<script>
(() => {
  const params = new URLSearchParams(location.search);
  const queryToken = params.get("token");
  if (queryToken) {
    sessionStorage.setItem("docmergeforge-token", queryToken);
    params.delete("token");
    history.replaceState({}, "", location.pathname + (params.toString() ? "?" + params : ""));
  }

  const form = document.getElementById("merge-form");
  const files = document.getElementById("files");
  const button = document.getElementById("merge-button");
  const status = document.getElementById("status");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!files.files.length) return;
    const data = new FormData(form);
    const token = sessionStorage.getItem("docmergeforge-token");
    const headers = token ? {"X-DocMergeForge-Token": token} : {};
    button.disabled = true;
    status.textContent = `Uploading and merging ${files.files.length} file(s)…`;

    try {
      const response = await fetch("/api/merge", {method: "POST", body: data, headers});
      if (!response.ok) {
        let detail = `Merge failed (${response.status}).`;
        try {
          const body = await response.json();
          detail = body.detail || detail;
        } catch (_) {}
        throw new Error(detail);
      }
      const blob = await response.blob();
      const disposition = response.headers.get("Content-Disposition") || "";
      const match = disposition.match(/filename="?([^"]+)"?/i);
      const filename = match ? match[1] : "DocMergeForge_Merged";
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      status.textContent = `Done: ${filename}`;
    } catch (error) {
      status.textContent = error instanceof Error ? error.message : "Merge failed.";
    } finally {
      button.disabled = false;
    }
  });

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  }
})();
</script>
</body>
</html>
"""

_ICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="96" fill="#0b1020"/>
<path d="M116 112h168l112 112v176H116z" fill="#6d7cff"/>
<path d="M284 112v112h112" fill="none" stroke="#eef2ff" stroke-width="28"/>
<path d="M174 288h164M174 344h132" stroke="#eef2ff" stroke-width="24" stroke-linecap="round"/>
</svg>"""

_SW = """const CACHE='docmergeforge-shell-v1';
const SHELL=['/','/manifest.webmanifest','/icon.svg'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL))));
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
"""


def safe_filename(name: str | None, *, fallback: str = "upload") -> str:
    """Return a single safe filename component without preserving path traversal."""

    candidate = Path(name or fallback).name
    candidate = _SAFE_NAME.sub("_", candidate).strip(" .")
    if not candidate:
        candidate = fallback
    return candidate[:180]


def ordered_documents(input_root: Path) -> tuple[DocumentKind, list[InputDocument]]:
    """Discover one homogeneous PDF/DOCX upload set and order numbered parts naturally."""

    documents = [
        item
        for item in scan([input_root])
        if item.kind in {DocumentKind.PDF, DocumentKind.DOCX}
    ]
    if not documents:
        raise ValueError("No PDF or DOCX files were uploaded.")
    kinds = {item.kind for item in documents}
    if len(kinds) != 1:
        raise ValueError("Do not mix PDF and DOCX files in one web merge request.")
    kind = next(iter(kinds))
    documents.sort(
        key=lambda item: (
            item.part.number is None,
            item.part.number if item.part.number is not None else 10**12,
            natural_key(item.path.name),
        )
    )
    return kind, documents


def output_filename(requested: str | None, kind: DocumentKind) -> str:
    suffix = ".pdf" if kind == DocumentKind.PDF else ".docx"
    safe = safe_filename(requested, fallback="DocMergeForge_Merged")
    if safe.casefold().endswith(suffix):
        return safe
    stem = Path(safe).stem if Path(safe).suffix else safe
    return f"{stem}{suffix}"


def _authorized(request: Request, access_token: str | None) -> bool:
    if access_token is None:
        return True
    supplied = request.headers.get("X-DocMergeForge-Token", "")
    return secrets.compare_digest(supplied, access_token)


async def _save_uploads(
    uploads: list[UploadFile],
    input_root: Path,
    max_upload_bytes: int,
) -> int:
    total = 0
    for index, upload in enumerate(uploads, start=1):
        filename = safe_filename(upload.filename, fallback=f"upload-{index}")
        suffix = Path(filename).suffix.casefold()
        if suffix not in {".pdf", ".docx"}:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported upload type for {filename}. Only PDF and DOCX are accepted.",
            )
        destination_dir = input_root / f"{index:04d}"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / filename
        with destination.open("wb") as handle:
            while chunk := await upload.read(_CHUNK_SIZE):
                total += len(chunk)
                if total > max_upload_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail="Upload exceeds the configured DocMergeForge web size limit.",
                    )
                handle.write(chunk)
        await upload.close()
    return total


def create_app(
    *,
    access_token: str | None = None,
    max_upload_bytes: int = 4 * 1024 * 1024 * 1024,
) -> FastAPI:
    """Create the browser/PWA application around the existing merge engines."""

    if max_upload_bytes < 1:
        raise ValueError("max_upload_bytes must be positive.")

    app = FastAPI(
        title="DocMergeForge Web",
        version="1",
        docs_url="/api/docs",
        redoc_url=None,
    )

    @app.get("/", include_in_schema=False)
    async def index() -> HTMLResponse:
        return HTMLResponse(
            _HTML,
            headers={
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
            },
        )

    @app.get("/icon.svg", include_in_schema=False)
    async def icon() -> Response:
        return Response(_ICON, media_type="image/svg+xml")

    @app.get("/sw.js", include_in_schema=False)
    async def service_worker() -> Response:
        return Response(
            _SW,
            media_type="application/javascript",
            headers={"Service-Worker-Allowed": "/"},
        )

    @app.get("/manifest.webmanifest", include_in_schema=False)
    async def manifest() -> JSONResponse:
        return JSONResponse(
            {
                "name": "DocMergeForge",
                "short_name": "DocMergeForge",
                "description": "Responsive local-first PDF and DOCX merging client.",
                "start_url": "/",
                "scope": "/",
                "display": "standalone",
                "background_color": "#0b1020",
                "theme_color": "#0b1020",
                "icons": [
                    {
                        "src": "/icon.svg",
                        "sizes": "any",
                        "type": "image/svg+xml",
                        "purpose": "any maskable",
                    }
                ],
            }
        )

    @app.get("/healthz")
    async def health() -> dict[str, object]:
        return {"status": "ok", "runtime": current_runtime()}

    @app.get("/api/platforms")
    async def platforms() -> dict[str, object]:
        return {
            "runtime": current_runtime(),
            "targets": [target.to_dict() for target in support_matrix()],
        }

    @app.post("/api/merge")
    async def merge(
        request: Request,
        files: Annotated[list[UploadFile], File(description="PDF or DOCX parts")],
        output_name: Annotated[str | None, Form()] = None,
        password: Annotated[str | None, Form()] = None,
    ) -> Response:
        if not _authorized(request, access_token):
            raise HTTPException(status_code=401, detail="Invalid or missing access token.")
        if not files:
            raise HTTPException(status_code=400, detail="Select at least one PDF or DOCX file.")
        if len(files) > _MAX_FILES:
            raise HTTPException(
                status_code=400,
                detail=f"A maximum of {_MAX_FILES} files is accepted per web merge request.",
            )

        workspace = Path(tempfile.mkdtemp(prefix="docmergeforge-web-"))
        input_root = workspace / "inputs"
        input_root.mkdir()
        try:
            await _save_uploads(files, input_root, max_upload_bytes)
            try:
                kind, discovered = ordered_documents(input_root)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            final_name = output_filename(output_name, kind)
            output_path = workspace / final_name
            if kind == DocumentKind.PDF:
                encrypted = [item for item in discovered if item.encrypted]
                if encrypted and not password:
                    raise HTTPException(
                        status_code=422,
                        detail="One or more PDFs are encrypted. Enter their shared password.",
                    )
                PdfMergeEngine().merge(
                    discovered,
                    output_path,
                    PdfSettings(),
                    overwrite=True,
                    preserve_order=True,
                    password_provider=(lambda _path: password) if password else None,
                )
                media_type = "application/pdf"
            else:
                DocxMergeEngine().merge(
                    discovered,
                    output_path,
                    DocxSettings(),
                    overwrite=True,
                    preserve_order=True,
                )
                media_type = (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            return FileResponse(
                output_path,
                media_type=media_type,
                filename=final_name,
                headers={"Cache-Control": "no-store"},
                background=BackgroundTask(shutil.rmtree, workspace, ignore_errors=True),
            )
        except HTTPException:
            shutil.rmtree(workspace, ignore_errors=True)
            raise
        except Exception as exc:
            shutil.rmtree(workspace, ignore_errors=True)
            raise HTTPException(status_code=422, detail=f"Merge failed: {exc}") from exc

    return app
