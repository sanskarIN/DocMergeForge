class DocMergeForgeError(Exception):
    """Base exception."""


class ValidationError(DocMergeForgeError):
    """Raised when mandatory validation fails."""


class MergeCancelled(DocMergeForgeError):
    """Raised when a merge is cancelled safely."""


class InsufficientStorageError(DocMergeForgeError):
    """Raised when free space is below the required safe estimate."""


class UnsupportedDocumentError(DocMergeForgeError):
    """Raised when a document cannot be handled safely."""
