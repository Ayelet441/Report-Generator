from abc import ABC, abstractmethod
from typing import Optional
from models.base_report import AttendanceReport, AttendanceRow


class BaseTransformationStrategy(ABC):
    """
    Abstract Base Class for attendance report transformation strategies.
    Defines the contract for creating transformed (synthetic) report variations
    while enforcing logic invariants.
    """

    @abstractmethod
    def transform(self, report: AttendanceReport, seed: Optional[int] = None) -> AttendanceReport:
        """
        Transforms an existing AttendanceReport object into a new, logically valid AttendanceReport.

        Args:
            report (AttendanceReport): The original parsed report object.
            seed (Optional[int]): Optional random seed to guarantee deterministic output.

        Returns:
            AttendanceReport: A new transformed AttendanceReport instance.
        """
        pass