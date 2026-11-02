from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time
from typing import Optional, List

@dataclass(frozen=True)
class AttendanceRow(ABC):
    """
    Abstract base class representing a single attendance row in the report.
    Field definitions are immutable (frozen=True) to ensure data integrity.
    """
    date: str               # The date of the attendance entry
    day_of_week: str        # The day of the week corresponding to the date
    entry_time: Optional[time]   # Employee arrival/entry time
    exit_time: Optional[time]    # Employee departure/exit time
    total_hours: float      # Total working hours calculated for the row


@dataclass(frozen=True)
class ReportSummary(ABC):
    """
    Abstract base class representing the monthly summary details of the attendance report.
    """
    total_working_days: int       # Total accumulated working days in the month
    total_monthly_hours: float    # Total accumulated working hours in the month


@dataclass(frozen=True)
class AttendanceReport(ABC):
    """
    Abstract base class representing the complete attendance report structure,
    combining the report type, individual daily rows, and monthly summary.
    """
    report_type: str                  # Identifier for the report format (e.g., Type A or Type B)
    rows: List[AttendanceRow]         # Collection of daily attendance rows
    summary: ReportSummary            # Monthly summary statistics object