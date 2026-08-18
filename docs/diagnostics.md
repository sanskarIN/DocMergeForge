# Diagnostics and Logging

DocMergeForge includes privacy-aware rotating logging and a structured diagnostics-export helper. These tools are intended to make technical failures supportable without treating manuscript content or passwords as ordinary log data.

## Logger identity

The maintained application logger name is:

```text
docmergeforge
```

Use `get_logger()` from `docmergeforge.diagnostics.logging` when application code needs the configured shared logger rather than creating unrelated handlers.

A former duplicate utility logger was removed because maintaining a second configuration path for the same logger could bypass the privacy filter or drift from the supported rotation/fallback behavior.

## Configure logging

The logging layer exposes:

```python
configure_logging(path, level="INFO")
```

It:

1. configures the `docmergeforge` logger level;
2. disables propagation;
3. closes/removes existing handlers on that logger;
4. attempts to create the parent log directory and rotating UTF-8 file handler;
5. falls back to a stream handler if the log path cannot be created/opened because of an `OSError`; and
6. attaches the same privacy redaction filter and formatter to either handler.

An unwritable log directory therefore must not prevent the desktop application from opening. The fallback is a resilience measure, not proof that persistent diagnostics are available; fix the filesystem problem if durable logs are required.

## Rotation policy

When the file handler is available, current rotation settings are:

```text
maxBytes = 5 * 1024 * 1024
backupCount = 3
encoding = utf-8
```

So a configured log file rotates at approximately 5 MiB and retains up to three backup files according to Python's `RotatingFileHandler` behavior.

This bounds ordinary diagnostic disk growth but is not a security retention policy. Organizations processing confidential publications should apply their own filesystem/retention rules.

## Log format

Current formatter:

```text
%(asctime)s %(levelname)s %(name)s %(message)s
```

A record therefore contains timestamp, severity, logger name, and message.

## Logging levels

`configure_logging()` converts the supplied level to uppercase and asks Python's `logging` module for that level. If the string is unknown, it falls back to `INFO`.

The desktop settings loader accepts these persisted values:

```text
DEBUG
INFO
WARNING
ERROR
```

Use DEBUG only when needed and review the resulting output before sharing because more technical context can reveal more path/filename metadata.

## Privacy redaction

`PrivacyFilter` rewrites messages/arguments through `redact_sensitive_text()` before a record is emitted.

Current assignment-style redaction recognizes common secret names case-insensitively, including variants of:

```text
password
passwd
secret
token
authorization
api_key / api-key
access_token / access-token
refresh_token / refresh-token
client_secret / client-secret
```

It handles ordinary and common JSON-style quoted assignments such as:

```text
password=my-secret
Token: abc123
{"api_key": "api123"}
{"client_secret": "client456"}
```

The secret value is replaced with `[REDACTED]` while preserving enough surrounding syntax to keep the diagnostic understandable.

## Authorization/header redaction

Bearer credentials matching the configured token pattern are replaced with:

```text
Bearer [REDACTED]
```

Common HTTP-style forms are also covered, including:

```text
Authorization: Basic <credential>
Authorization: Bearer <credential>
Api-Key: <credential>
X-Api-Key: <credential>
```

Their credential portion is removed before the record reaches the configured handler.

## Logging arguments

The privacy filter also handles `record.args`:

- dictionaries are mapped value-by-value through redaction;
- tuple-style arguments are converted/redacted item-by-item.

This reduces the chance that a sensitive value bypasses redaction simply because it was passed as a formatting argument instead of already being part of `record.msg`.

## Important redaction limitation

No regex redactor can identify every possible secret format.

Do not deliberately log sensitive values with the expectation that a filter will save them. Code should avoid putting passwords, authentication secrets, manuscript body text, private keys, or signing credentials into log calls in the first place.

Redaction is defense in depth, not permission to log secrets.

## Diagnostic export

The diagnostics export helper writes JSON containing:

```text
app_version
generated_at
platform
warnings
recent_errors
privacy_note
```

The privacy note currently states:

```text
Document body text and passwords are intentionally excluded.
```

## Export timestamp

`generated_at` uses a UTC ISO-8601 timestamp.

## Platform metadata

The export includes `platform.platform()` output so support can distinguish operating-system/runtime environments.

Platform metadata can still be identifying in some contexts. Review it before publishing diagnostics in a public issue.

## Atomic diagnostics export

Diagnostics export uses the same shared atomic text-persistence primitive as app settings, recent-project history, and project JSON.

Each export:

1. creates a unique sibling temporary file;
2. writes UTF-8 JSON;
3. flushes and `fsync`s that temporary file;
4. promotes it with `os.replace(...)`; and
5. removes temporary residue if writing or replacement fails.

The implementation does not depend on one predictable `<target>.tmp` filename. A failed replacement leaves the previously published target intact.

## What diagnostics should not contain

Contributors should not intentionally place any of the following into `warnings`/`recent_errors` or log messages:

- encrypted-PDF passwords;
- API/access/refresh tokens;
- Authorization headers;
- client secrets;
- private signing keys/certificate secrets;
- complete manuscript body text;
- complete private companion source code;
- unnecessary personally identifying data.

## What diagnostics can legitimately contain

Useful support evidence can include:

- sanitized file paths;
- filenames/part numbers when required to identify a failure;
- stage name;
- exception type/message;
- package/application version;
- OS/platform;
- validation/recovery error details;
- storage/free-space errors;
- document kind;
- warning code/severity.

Prefer minimal information needed to diagnose the technical problem.

## Paths are sensitive metadata

A log that says:

```text
C:\Users\Alice\Client-X\Secret-Book\Part 12.docx
```

can expose meaningful private information without any manuscript body text.

When sharing publicly, sanitize it to something such as:

```text
C:\Users\USER\PROJECT\Part 12.docx
```

while preserving structural details needed to reproduce path-related bugs.

## Recovery diagnostics

Recovery errors can contain:

- output/staging paths;
- journal path;
- conflicting final path;
- state/fingerprint-related messages.

Do not upload an entire confidential transaction staging folder merely because a support request involves recovery. Preserve it locally, then share sanitized metadata/error text first.

## Audit output is separate

`docmergeforge audit` prints targeted publication findings as JSON. That output is not the same as the rotating application log and can contain detected email/GitHub URL information in finding messages.

Review audit JSON independently before sharing.

## CLI stdout is separate

Commands such as `validate`, `merge --dry-run`, `recover-output`, `audit`, and `compare` print machine-readable evidence to stdout. That content may include paths and should receive the same privacy review before publication.

## Support workflow

Recommended diagnostics procedure:

1. reproduce the failure once using the smallest safe project;
2. record DocMergeForge commit/version and OS;
3. collect the relevant error/log excerpt;
4. export structured diagnostics if the desktop support flow offers it;
5. open the file and inspect it manually;
6. redact private paths/names as needed;
7. do not include passwords/manuscript content; and
8. attach only the minimum useful evidence to a public report.

See [Support](support.md).

## Contributor checklist for new diagnostics

When adding a log/error/export field:

- Is this information actually necessary?
- Could it contain a password/token/API key/client secret?
- Could it contain manuscript body text?
- Could a filename/path expose sensitive metadata?
- Should it go through `redact_sensitive_text()`?
- Is a stable code/category better than embedding raw content?
- Does the unit test use synthetic secrets/content?
- Does documentation/privacy guidance need updating?

## Testing redaction

Security/privacy regression tests should include representative synthetic examples of:

```text
password=...
passwd: ...
secret=...
token: ...
{"api_key": "..."}
{"client_secret": "..."}
Authorization: Basic ...
Authorization: Bearer ...
X-Api-Key: ...
```

Tests should verify the sensitive value is absent and `[REDACTED]` is present. Logging tests should also preserve the privacy filter when file logging falls back to the stream handler.

Do not put real credentials into tests.
