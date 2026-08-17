# Diagnostics and Logging

DocMergeForge includes privacy-aware rotating logging and a structured diagnostics-export helper. These tools are intended to make technical failures supportable without treating manuscript content or passwords as ordinary log data.

## Logger identity

The application logger name is:

```text
docmergeforge
```

Use `get_logger()` when application code needs the configured shared logger rather than creating unrelated handlers.

## Configure logging

The logging layer exposes a configuration function conceptually equivalent to:

```python
configure_logging(path, level="INFO")
```

It:

1. creates the parent log directory;
2. configures the `docmergeforge` logger level;
3. disables propagation;
4. closes/removes existing handlers on that logger;
5. adds a rotating UTF-8 file handler;
6. attaches the privacy redaction filter.

## Rotation policy

Current file rotation settings are:

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

Common values:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Use DEBUG only when needed and review the resulting file before sharing because more technical context can reveal more path/filename metadata.

## Privacy redaction

`PrivacyFilter` rewrites messages/arguments through `redact_sensitive_text()` before a record is emitted.

Current redaction recognizes assignment-style keywords, case-insensitively, including:

```text
password
passwd
secret
token
authorization
```

For patterns similar to:

```text
password=my-secret
Token: abc123
```

the value is replaced with:

```text
[REDACTED]
```

## Bearer-token redaction

Bearer credentials matching the configured token pattern are replaced with:

```text
Bearer [REDACTED]
```

## Logging arguments

The privacy filter also handles `record.args`:

- dictionaries are mapped value-by-value through redaction;
- tuple-style arguments are converted/redacted item-by-item.

This reduces the chance that a sensitive value bypasses redaction simply because it was passed as a formatting argument instead of already being part of `record.msg`.

## Important redaction limitation

No regex redactor can identify every possible secret format.

Do not deliberately log sensitive values with the expectation that a filter will save them. Code should avoid putting passwords, authentication secrets, manuscript body text, or private keys into log calls in the first place.

Redaction is defense in depth, not permission to log secrets.

## Diagnostic export

The diagnostics export helper writes a JSON file containing:

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

The JSON export is written to:

```text
<target-suffix>.tmp
```

and then replaces the final target after the complete JSON has been written.

This reduces the chance that a normal interrupted write leaves a half-written final diagnostics JSON.

## What diagnostics should not contain

Contributors should not intentionally place any of the following into `warnings`/`recent_errors` or log messages:

- encrypted-PDF passwords;
- API/access tokens;
- Authorization headers;
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
7. do not include passwords/manuscript content;
8. attach only the minimum useful evidence to a public report.

See [Support](support.md).

## Contributor checklist for new diagnostics

When adding a log/error/export field:

- Is this information actually necessary?
- Could it contain a password/token?
- Could it contain manuscript body text?
- Could a filename/path expose sensitive metadata?
- Should it go through `redact_sensitive_text()`?
- Is a stable code/category better than embedding raw content?
- Does the unit test use synthetic secrets/content?
- Does documentation/privacy guidance need updating?

## Testing redaction

Security/privacy regression tests should include representative examples of:

```text
password=...
passwd: ...
secret=...
token: ...
authorization=...
Bearer ...
```

Tests should verify the sensitive value is absent and `[REDACTED]` is present.

Do not put real credentials into tests.
