# Accessibility

DocMergeForge aims to make its desktop workflow usable with keyboard navigation and assistive technologies. The repository includes explicit accessibility metadata and an automated offscreen smoke check, but automated metadata coverage is only one part of accessibility acceptance.

## Current automated coverage

Run the accessibility smoke locally:

```bash
python scripts/check_accessibility.py
```

The script forces Qt's offscreen platform where possible and constructs representative desktop dialogs without requiring interactive user input.

The Build Smoke workflow runs this script on:

- Ubuntu;
- Windows;
- macOS.

Linux CI installs `libegl1` first because minimal Ubuntu runners can otherwise fail to import the PySide6 Qt runtime (`libEGL.so.1`).

## What the smoke check verifies

### Order editor

The automated check verifies accessible metadata for:

- order dialog;
- search label;
- search field;
- lock-order control;
- order list;
- validation summary;
- boundary preview;
- manual order buttons;
- confirm/cancel buttons.

It also verifies:

- the search label's keyboard buddy points to the search field;
- the search field has an accessible description;
- the order list has an accessible description;
- lock/manual order operations expose keyboard shortcuts;
- manual-order buttons have accessible descriptions.

## Project setup coverage

The smoke check verifies names for:

- project setup dialog;
- project name;
- project sources control;
- output path picker;
- first/last part controls;
- SQL preset checkbox/control;
- source list;
- add-folder button;
- add-files button;
- remove-source button;
- clear-source button;
- create/cancel actions.

Source-management buttons are also checked for keyboard shortcuts.

## Settings coverage

The automated settings check includes:

- theme;
- merge profile;
- filename template;
- default output;
- temporary directory;
- worker count;
- logging level;
- checksum setting;
- automatic validation;
- PDF optimization;
- DOCX fidelity;
- LibreOffice integration;
- Word fidelity;
- crash recovery;
- recent history;
- reduced motion;
- text scale;
- save/cancel actions.

The DOCX fidelity control is required to have a safety-oriented accessible description.

## Secondary-dialog coverage

The current smoke check also covers:

- text/report dialog and report content;
- recent-project dialog/list/open action;
- merge-progress dialog;
- merge stage label;
- progress bar;
- current-file label;
- safe-cancel control and cancellation behavior description.

## Keyboard ordering workflow

The order editor is expected to support a keyboard-only workflow for reviewing/rearranging a manuscript sequence. The implementation includes shortcuts for relevant actions such as locking, sorting/moving, undo/redo, and restoring/automatic ordering where offered by the UI.

Human acceptance should verify that:

1. every action reachable by mouse is reasonably reachable by keyboard;
2. focus order is logical;
3. focus is visibly indicated;
4. moving an item gives understandable feedback;
5. disabled controls are conveyed correctly;
6. confirmation/cancellation does not trap focus.

## Screen-reader acceptance

Automated `accessibleName` checks cannot prove that a real screen reader announces the interface well.

Before a stable release, manually test representative workflows with platform tools such as:

- Windows Narrator and/or NVDA;
- macOS VoiceOver;
- a suitable Linux screen reader in a supported desktop environment.

Recommended workflow coverage:

- onboarding;
- create project;
- add source folder/files;
- adjust part range;
- review order;
- validation/preflight results;
- settings;
- start/cancel merge;
- completion/failure dialog;
- reports;
- recent projects;
- recovery/help/support.

## High contrast and themes

A control having an accessible name does not guarantee sufficient visual contrast.

Manual acceptance should cover:

- default theme;
- supported dark/light/system theme behavior;
- Windows High Contrast where applicable;
- selected/focused/disabled states;
- warning/error text;
- progress indicators;
- links/buttons.

Avoid relying on color alone to communicate validation state.

## Text scaling

The settings model exposes text scaling. Release acceptance should test:

- normal scale;
- increased text scale;
- OS-level display scaling;
- long translated/file-path text;
- narrow window sizes.

Verify that labels are not clipped in ways that hide meaning and that controls remain reachable without overlapping.

## Reduced motion

The settings UI exposes a reduced-motion preference. Any animated/progress feedback should respect the principle that essential state must remain understandable without nonessential motion.

Manual acceptance should verify that reducing motion does not remove important progress/cancellation feedback.

## Long paths and large projects

Accessibility acceptance should include realistic stress conditions:

- long source paths;
- hundreds of document parts;
- long project names;
- many validation findings;
- large report text;
- long recent-project entries.

Lists should remain navigable and state should remain understandable without requiring precise pointing-device use.

## Error messages

Accessible errors should state:

- what failed;
- which path/document is involved where safe;
- whether the operation published anything;
- the recommended next action;
- whether recovery evidence must be preserved.

A screen reader user must not need to infer a critical failure from window color/icon alone.

## Accessibility regression command

Before pushing UI changes:

```bash
python scripts/check_accessibility.py
pytest
```

Build Smoke should then verify the metadata on all configured desktop runner operating systems.

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

The repository has automated accessibility metadata coverage and cross-platform smoke evidence, but it does **not** yet claim full human accessibility acceptance across all assistive technologies, display modes, and operating systems.

That distinction must remain explicit in release notes until the full manual acceptance matrix is completed and recorded.
