from abc import abstractmethod
from generation.base_renderer import BaseRenderer
from models.base_report import AttendanceReport


class PdfRenderer(BaseRenderer):
    """
    Abstract base class specialized for PDF rendering.
    Handles shared configurations for PDF generation (such as RTL layout,
    Hebrew font registration, and page setups) while leaving the specific
    layout implementation to concrete subclasses.
    """

    def __init__(self, font_path: str = None):
        """
        Initializes the PDF renderer with optional font configurations for Hebrew support.

        Args:
            font_path (str, optional): Path to a TrueType font supporting Hebrew.
        """
        self.font_path = font_path

    @abstractmethod
    def render(self, report: AttendanceReport, output_path: str) -> None:
        """
        Abstract render method to be implemented by format-specific PDF renderers.
        """
        pass