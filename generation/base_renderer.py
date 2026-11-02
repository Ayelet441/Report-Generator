from abc import ABC, abstractmethod
from models.base_report import AttendanceReport


class BaseRenderer(ABC):
    """
    Abstract base class for all attendance report renderers.
    Defines the general contract for transforming a report model into an output file.
    """

    @abstractmethod
    def render(self, report: AttendanceReport, output_path: str) -> None:
        """
        Renders the given attendance report to the specified output path.

        Args:
            report (AttendanceReport): The structured attendance report object.
            output_path (str): The target file path for the generated output.
        """
        pass