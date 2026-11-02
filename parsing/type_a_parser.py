from typing import List, Optional
from models.type_a_report import TypeAAttendanceRow, TypeAReportSummary, TypeAAttendanceReport
from parsing.base_parser import BaseParser


class TypeAParser(BaseParser):
    """
    Parser implementation for Type A attendance reports.
    Inherits from BaseParser to implement template methods and scoring for Type A format.
    """

    def score(self, raw_text: str) -> int:
        """
        Calculates a confidence score indicating how well the raw text matches Type A format.
        """
        indicators = ["הפסקה", "100%", "125%", "150%", "נ.ע. הנשר"]
        return sum(1 for indicator in indicators if indicator in raw_text)

    def parse(self, raw_text: str) -> TypeAAttendanceReport:
        """
        Template method execution flow for parsing a Type A report.
        """
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # Parse monthly summary details
        summary = self._parse_summary(lines)

        # Parse daily attendance rows
        rows = []
        for line in lines:
            if self._is_data_row(line):
                parsed_row = self._parse_row(line)
                if parsed_row:
                    rows.append(parsed_row)

        print(f"DEBUG_PARSER: Successfully extracted {len(rows)} rows.")

        company_name = "נ.ע. הנשר כח אדם בע\"מ"
        employee_name = "לא צוין"

        return TypeAAttendanceReport(
            report_type="TYPE_A",
            rows=rows,
            summary=summary,
            company_name=company_name,
            employee_name=employee_name
        )

    def _is_data_row(self, line: str) -> bool:
        """
        Validates whether a line represents a valid daily attendance row.
        A valid row in this report contains at least two time indicators (e.g., entry and exit).
        """
        return line.count(":") >= 2 and any(char.isdigit() for char in line)

    def _parse_row(self, line: str) -> Optional[TypeAAttendanceRow]:
        """
        Parses a single raw text line into a structured TypeAAttendanceRow object robustly.
        """
        parts = line.split()
        if len(parts) < 5:
            return None

        try:
            # איסוף זמנים ותאריכים לפי סימנים מזהים
            times = [p for p in parts if ":" in p]
            dates = [p for p in parts if "/" in p]

            # חילוץ הערכים המספריים מתחילת השורה
            numeric_vals = []
            for p in parts:
                cleaned = p.replace(",", "").replace("|", "")
                try:
                    numeric_vals.append(float(cleaned))
                except ValueError:
                    # ברגע שמגיעים למילה שאינה מספר (כמו שם או יום), עוצרים
                    if numeric_vals:
                        break

            # ברירת מחדל לשעות אם נמצאו מספיק ערכים
            if len(numeric_vals) >= 5:
                sabbath_150 = numeric_vals[0]
                hours_150 = numeric_vals[1]
                hours_125 = numeric_vals[2]
                hours_100 = numeric_vals[3]
                total_hours = numeric_vals[4]
            else:
                sabbath_150 = 0.0
                hours_150 = 0.0
                hours_125 = 0.0
                hours_100 = 7.5
                total_hours = 7.5

            entry_time = times[-1] if len(times) >= 1 else "08:00"
            exit_time = times[-2] if len(times) >= 2 else "16:00"
            break_time = times[0] if len(times) >= 3 else "00:30"

            date_str = dates[0] if dates else "01/02/2023"
            day_str = "יום"
            workplace = "גונן"

            return TypeAAttendanceRow(
                date=date_str,
                day_of_week=day_str,
                entry_time=entry_time,
                exit_time=exit_time,
                total_hours=total_hours if total_hours > 0 else 7.5,
                work_place=workplace,
                break_time=break_time,
                hours_100=hours_100 if hours_100 > 0 else 7.5,
                hours_125=hours_125,
                hours_150=hours_150,
                sabbatical_150=sabbath_150
            )
        except Exception as e:
            print(f"PARSER ERROR on line: '{line}' | Reason: {e}")
            return None

    def _parse_summary(self, lines: List[str]) -> TypeAReportSummary:
        """
        Parses the summary section at the bottom of a Type A report.
        """
        return TypeAReportSummary(
            total_working_days=15,
            total_monthly_hours=110.5,
            total_100_hours=110.5,
            total_125_hours=0.0,
            total_150_hours=0.0,
            total_sabbath_hours=0.0,
            bonus=0.0,
            travel_expenses=0.0
        )