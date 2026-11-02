from dataclasses import dataclass
from typing import Optional
from models.base_report import AttendanceRow, ReportSummary, AttendanceReport

@dataclass(frozen=True)
class TypeBAttendanceRow(AttendanceRow):
    """
    Attendance row specific to Type B reports.
    Extends base row with custom notes.
    """
    comments: Optional[str]         # Specific field for Type B: Row comments


@dataclass(frozen=True)
class TypeBReportSummary(ReportSummary):
    """
    Report summary specific to Type B reports.
    Extends base summary with hourly rate and total payment.
    """
    hourly_rate: float              # Rate per hour
    total_payment: float            # Total payment calculated for the month


@dataclass(frozen=True)
class TypeBAttendanceReport(AttendanceReport):
    """
    Complete report container for Type B format.
    """
    employee_name: str
    employee_card_id: str