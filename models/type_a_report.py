from dataclasses import dataclass
from typing import Optional
from models.base_report import AttendanceRow, AttendanceReport, ReportSummary

@dataclass(frozen=True)
class TypeAAttendanceRow(AttendanceRow):
    """
    Attendance row specific to Type A reports.
    Extends base row with break time and overtime percentages.
    """
    work_place: str                 # Specific field for Type A: Workplace location
    break_time: Optional[str]       # Specific field for Type A: Break duration
    hours_100: float                # 100% regular hours
    hours_125: float                # 125% overtime hours
    hours_150: float                # 150% overtime hours
    sabbatical_150: float           # Sabbath/Holiday 150% hours


@dataclass(frozen=True)
class TypeAReportSummary(ReportSummary):
    """
    Report summary specific to Type A reports.
    """
    total_100_hours: float
    total_125_hours: float
    total_150_hours: float
    total_sabbath_hours: float
    bonus: float
    travel_expenses: float


@dataclass(frozen=True)
class TypeAAttendanceReport(AttendanceReport):
    """
    Complete report container for Type A format.
    """
    company_name: str
    employee_name: str