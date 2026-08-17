# Accessibility

DocMergeForge aims to make its desktop workflow usable with keyboard navigation and assistive technologies. The repository includes explicit accessibility metadata and an automated offscreen smoke check, but automated metadata/preference coverage is only one part of accessibility acceptance.

## Current automated coverage

Run the accessibility smoke locally:

```bash
python scripts/check_accessibility.py
```

The script forces Qt's offscreen platform where possible and constructs representative desktop dialogs without requiring interactive user input.

The Build Smoke workflow runs this script on Ubuntu, Windows, and macOS. Linux CI installs `libegl1` first because minimal Ubuntu runners can otherwise fail to import the PySide6 Qt runtime (`libEGL.so.1`).

Cross-platform evidence:

```text
Build Smoke run: 32033541402
Checkpoint includes: 5545ff6b67d53714cdd5ad2667920801eae5f9ae
Windows accessibility smoke: PASS
macOS accessibility smoke: PASS
Ubuntu accessibility smoke: PASS
```

This run verifies the expanded accessibility preference smoke described below. It is automated offscreen evidence, not human assistive-technology acceptance.

## What the smoke check verifies

### Order editor

The automated check verifies accessible metadata for the order dialog, search label/field, lock-order control, order list, validation summary, boundary preview, manual order buttons, and confirm/cancel buttons.

It also verifies that the search label's keyboard buddy points to the search field; search/order controls have accessible descriptions where needed; lock/manual order operations expose keyboard shortcuts; and manual-order buttons have accessible descriptions.

## Project setup coverage

The smoke check verifies accessible names for project setup, project name, project sources, output path picker, first/last part controls, SQL preset control, source list, add-folder/add-files/remove/clear actions, and create/cancel actions. Source-management buttons are also checked for keyboard shortcuts.

## Settings coverage

The automated settings check includes theme, merge profile, filename template, default output, temporary directory, worker count, logging level, checksum setting, automatic validation, PDF optimization, DOCX fidelity, LibreOffice integration, Word fidelity, crash recovery, recent history, reduced motion, text scale, and save/cancel actions.

The DOCX fidelity control is required to have a safety-oriented accessible description.

### Theme application smoke

The expanded preference smoke applies all three supported theme modes to the real `QApplication`:

- `dark` must apply the DocMergeForge dark stylesheet;
- `light` must apply the DocMergeForge light stylesheet;
- `system` must clear the application stylesheet and return control to the native Qt/platform style.

This is deterministic stylesheet-application evidence. It does not replace human visual review for OS high-contrast modes, focus visibility, warning/error contrast, or platform-specific rendering.

### Text-scale smoke

The automated preference matrix verifies the production `apply_text_scale()` bounds and round-trip behavior:

| Requested | Expected applied scale |
|---:|---:|
| 50% | clamped to 80% |
| 100% | 100% |
| 250% | clamped to 200% |

It also verifies that the original Qt base point size is captured once and that subsequent scaling is derived from that base rather than compounding the already-scaled font.

A `SettingsDialog` round-trip additionally verifies a stored `170%` value returns as `170`.

This does not replace manual layout review at real OS display scaling, long paths, translations, or narrow windows.

### Reduced-motion setting smoke

The automated preference test creates `AppSettings(reduced_motion=True)` through the real Settings dialog and verifies that the preference survives the dialog round-trip.

This proves the setting surface/serialization path used by the dialog. It does **not** claim that every future animation automatically honors reduced motion; any animated UI must still be reviewed and tested when introduced.

## Secondary-dialog coverage

The current smoke check also covers text/report dialog and report content, recent-project dialog/list/open action, merge-progress dialog, merge stage label, progress bar, current-file label, and the safe-cancel control plus its cancellation behavior description.

## Keyboard ordering workflow

The order editor is expected to support a keyboard-only workflow for reviewing/rearranging a manuscript sequence. The implementation includes shortcuts for relevant actions such as locking, sorting/moving, undo/redo, and restoring/automatic ordering where offered by the UI.

Human acceptance should verify that every action reachable by mouse is reasonably reachable by keyboard, focus order is logical and visibly indicated, moving an item gives understandable feedback, disabled controls are conveyed correctly, and confirmation/cancellation does not trap focus.

## Screen-reader acceptance

Automated `accessibleName` checks cannot prove that a real screen reader announces the interface well.

Before a stable release, manually test representative workflows with platform tools such as Windows Narrator and/or NVDA, macOS VoiceOver, and a suitable Linux screen reader in a supported desktop environment.

Recommended coverage includes onboarding; project creation; source selection; part range/order review; validation/preflight; settings; start/cancel merge; completion/failure dialogs; reports; recent projects; recovery/help/support.

## High contrast and themes

A control having an accessible name and passing stylesheet smoke does not guarantee sufficient visual contrast.

Manual acceptance should cover default/light/dark/system modes, Windows High Contrast where applicable, selected/focused/disabled states, warning/error text, progress indicators, links, and buttons. Avoid relying on color alone to communicate validation state.

## Text scaling

Automated scale bounds are now verified, but release acceptance should still test normal/increased text scale, OS-level display scaling, long translated/file-path text, and narrow window sizes. Labels must not be clipped in ways that hide meaning and controls must remain reachable without overlap.

## Reduced motion

The settings UI exposes and now automatically round-trips a reduced-motion preference. Any animated/progress feedback should respect the principle that essential state remains understandable without nonessential motion.

Manual acceptance should verify that reducing motion does not remove important progress/cancellation feedback. The current automated test does not make a global animation-compliance claim.

## Long paths and large projects

Accessibility acceptance should include realistic stress conditions such as long source paths, hundreds of document parts, long project names, many validation findings, large report text, and long recent-project entries. Lists should remain navigable and state should remain understandable without requiring precise pointing-device use.

## Error messages

Accessible errors should state what failed, which path/document is involved where safe, whether the operation published anything, the recommended next action, and whether recovery evidence must be preserved. A screen-reader user must not need to infer a critical failure from window color/icon alone.

## Accessibility regression command

Before pushing UI changes:

```bash
python scripts/check_accessibility.py
pytest
```

Build Smoke then verifies the offscreen metadata/preference smoke on all configured desktop runner operating systems.

## Definition of done for UI changes

For a new/changed interactive control:

- meaningful `accessibleName` exists;
- `accessibleDescription` exists when purpose/safety behavior is not obvious;
- visible label is associated with its field where appropriate;
- keyboard focus can reach it;
- keyboard activation/shortcut exists where needed;
- focus order is sensible;
- no information is conveyed only by color;
- text survives scaling;
- the accessibility smoke script is extended if the control is release-critical;
- human screen-reader testing is scheduled for release acceptance.

## Current limitation

The repository now has cross-platform automated accessibility metadata plus theme/text-scale/reduced-motion preference smoke evidence, but it does **not** claim full human accessibility acceptance across screen readers, keyboard-only end-to-end workflows, real OS high-contrast modes, display scaling/layout extremes, localization, or every assistive technology/platform combination.

That distinction must remain explicit in release notes until the full manual acceptance matrix is completed and recorded.
