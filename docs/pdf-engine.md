# PDF Engine

The portable PDF engine appends source pages without rasterizing them, preserving page dimensions and rotations as represented by the source page objects. It can generate top-level Part bookmarks and master metadata.

Validation compares the merged page count with the exact sum of source page counts and reopens the temporary PDF before final placement.

Encrypted PDFs are rejected until a locally supplied password flow is available. The application never attempts to bypass protection and never stores passwords.
