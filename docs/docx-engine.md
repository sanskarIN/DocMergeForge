# DOCX Engine

DOCX files are OOXML ZIP packages. DocMergeForge validates package structure, required members, and XML readability before composition. Portable composition uses `docxcompose`, which handles many style, numbering, media, and relationship collisions better than naïve XML concatenation.

## Known fidelity limits

Macros, OLE objects, tracked changes, complex fields, custom XML, unsupported equations, and unusual external relationships may require Microsoft Word or LibreOffice for maximum fidelity. The portable engine must warn rather than claim perfect preservation.

Word table-of-contents fields may need to be updated after opening the final file.
