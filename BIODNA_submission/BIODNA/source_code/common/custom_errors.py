"""Error classes used across BIODNA. Each message is safe to show to the user."""


class FileReadingError(Exception):
    """Raised when an uploaded file cannot be used."""




class QuestionBlockedError(Exception):
    """Raised when a question is stopped by the input guardrails."""
