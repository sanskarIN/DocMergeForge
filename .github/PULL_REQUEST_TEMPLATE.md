## Summary
Describe the focused change and the user/problem it addresses.

## Scope
- [ ] The change is focused; unrelated refactors are separated.
- [ ] PDF and DOCX manuscript pipelines remain separate.
- [ ] Companion/source-code archives are not merged, extracted, or silently modified by manuscript code.
- [ ] Existing production-readiness gates are not weakened or bypassed.

## Validation
- [ ] `pre-commit validate-config` passes when configuration changed.
- [ ] `ruff check .` passes.
- [ ] `black --check --diff .` passes.
- [ ] `mypy src/docmergeforge` passes.
- [ ] `python scripts/check_docs_links.py` passes when documentation changed.
- [ ] `python scripts/check_repository_reference.py` passes when tracked files changed.
- [ ] Relevant unit/integration/regression tests pass.
- [ ] Source-integrity and no-overwrite behavior remain intact where applicable.
- [ ] Failure/cancellation/cleanup behavior has a regression when applicable.

## Document fidelity
- [ ] Not applicable, or representative synthetic fidelity coverage was added/updated.
- [ ] External LibreOffice/Word availability was not confused with production readiness.
- [ ] No external-office mode was marked production-ready without corresponding real acceptance evidence.

## Desktop / packaging / accessibility
- [ ] Not applicable, or keyboard/accessibility metadata and behavior were reviewed.
- [ ] Not applicable, or packaging preflight/smoke assumptions were updated and tested.
- [ ] No unsigned/unnotarized artifact is described as a signed production release.

## Documentation and evidence
- [ ] User/operator/developer documentation was updated when behavior changed.
- [ ] Added/renamed/deleted tracked paths are reflected in `docs/repository-reference.md`.
- [ ] `CHANGELOG.md` was updated for notable behavior.
- [ ] `what_changed.md` was updated for meaningful development/verification work.
- [ ] New run IDs/hashes/evidence are cited only when they were actually observed and verified.

## Privacy / security
- [ ] No private manuscript, password, token, signing key, confidential path, or unreviewed diagnostic was committed.
- [ ] New diagnostics/evidence remain privacy-aware and fail closed where safety cannot be proven.

## Notes for reviewers
List platform-specific assumptions, remaining acceptance gates, compatibility concerns, or follow-up work that should not be inferred as complete from this PR.
