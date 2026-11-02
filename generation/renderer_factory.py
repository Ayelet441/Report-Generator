from typing import Dict, Type
from generation.base_renderer import BaseRenderer
from generation.pdf_renderer.pdf_renderer import PdfRenderer
from generation.pdf_renderer.type_a_pdf_renderer import TypeAPdfRenderer
from generation.pdf_renderer.type_b_pdf_renderer import TypeBPdfRenderer


class RendererFactory:
    """
    Factory class responsible for instantiating the appropriate PDF renderer
    based on the report format type (e.g., TYPE_A or TYPE_B).
    """

    # Mapping of report types to their concrete PDF renderer classes
    _pdf_renderers: Dict[str, Type[PdfRenderer]] = {
        "TYPE_A": TypeAPdfRenderer,
        "TYPE_B": TypeBPdfRenderer,
    }

    @classmethod
    def get_renderer(cls, report_type: str, output_format: str = "pdf") -> BaseRenderer:
        """
        Returns an instance of the corresponding renderer for the given report type and output format.

        Args:
            report_type (str): The type of the report ('TYPE_A' or 'TYPE_B').
            output_format (str): The desired output format (default is 'pdf').

        Returns:
            BaseRenderer: An instance of a concrete renderer implementation.

        Raises:
            ValueError: If the report type or output format is unsupported.
        """
        format_normalized = output_format.lower()

        if format_normalized == "pdf":
            renderer_class = cls._pdf_renderers.get(report_type.upper())
            if not renderer_class:
                raise ValueError(f"Unsupported report type '{report_type}' for PDF rendering.")
            return renderer_class()
        else:
            raise ValueError(f"Unsupported output format '{output_format}'. Currently only 'pdf' is supported.")