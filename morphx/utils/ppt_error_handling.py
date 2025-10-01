class PPTGeneratorError(Exception):
    """Base exception for PPT Generator errors."""
    pass


class ModelLoadError(PPTGeneratorError):
    """Raised when model fails to load."""
    pass


class ContentParsingError(PPTGeneratorError):
    """Raised when content cannot be parsed."""
    pass


class SlideGenerationError(PPTGeneratorError):
    """Raised when slide generation fails."""
    pass
