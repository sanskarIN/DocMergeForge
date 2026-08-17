# Troubleshooting

## A part is missing
Confirm the filename contains `Part`, `Chapter`, or `Volume` followed by the correct number, or use a supported explicit ordering workflow.

## Duplicate part
Remove the duplicate from the selected inputs. Duplicate part numbers are a blocking validation error.

## Encrypted PDF
Open the source using its legitimate password. Password bypass is not supported.

## DOCX validation fails
Open and re-save the file in Microsoft Word or LibreOffice, then rerun validation.

## Not enough disk space
Choose an output/temp location with more free space. DocMergeForge reserves headroom for atomic temporary outputs and publication staging.

## Output folder is not writable
Choose a destination where the current user can create and remove files. Preflight performs a short writeability probe before expensive merge work begins.

## An interrupted publication transaction is detected
Do not manually delete `.docmergeforge-staging-*` folders. They can contain rollback evidence from an interrupted publication.

Run the explicit recovery command against the same output directory:

```bash
docmergeforge recover-output --output-dir /path/to/output
```

A journal still in the `promoting` phase is rolled back to its pre-publication state. A journal already marked `committed` or `rolled-back` only needs stale staging cleanup.

Recovery fails closed if a final file was changed after the interruption or the journal cannot prove which file belongs to the interrupted transaction. In that case DocMergeForge preserves the journal and files instead of overwriting or deleting uncertain data.

## Final validation failed
The output is not promoted as complete. Original files remain unchanged.
