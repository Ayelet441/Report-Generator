import random
from datetime import datetime, timedelta
from typing import List, Optional
from models.type_b_report import TypeBAttendanceRow, TypeBReportSummary, TypeBAttendanceReport
from transformation.base_transformation import BaseTransformationStrategy



class TypeBTransformationStrategy(BaseTransformationStrategy):
    """
    Transformation strategy for Type B attendance reports.
    Generates dynamic, fully randomized synthetic attendance data on every execution
    while strictly enforcing format invariants and logical constraints.
    """

    def transform(self, report: TypeBReportSummary, seed: Optional[int] = None) -> TypeBAttendanceReport:
        """
        Transforms an existing report into a new variant with randomized valid times.

        Args:
            report (TypeBAttendanceReport): The original parsed report object.
            seed (Optional[int]): Ignored for dynamic variation unless explicitly forced.

        Returns:
            TypeBAttendanceReport: A new transformed report with unique synthetic values.
        """
        transformed_rows: List[TypeBAttendanceRow] = []
        total_monthly_hours = 0.0
        total_working_days = 0

        for row in report.rows:
            # Check if it's a working day (ignoring rest days/weekends)
            if row.entry_time and row.exit_time:
                # Randomize entry time dynamically (e.g., hours 08:00 or 09:00, minutes 00, 15, 30)
                entry_hour = random.choice([8, 9])
                entry_minute = random.choice([0, 15, 30])

                # Randomize work duration realistically
                work_duration_hours = random.choice([7.5, 8.0, 8.5, 9.0])

                entry_dt = datetime.strptime(f"{entry_hour:02d}:{entry_minute:02d}", "%H:%M")
                exit_dt = entry_dt + timedelta(hours=work_duration_hours)

                entry_str = entry_dt.strftime("%H:%M")
                exit_str = exit_dt.strftime("%H:%M")
                calculated_hours = round(work_duration_hours, 2)

                total_working_days += 1
                total_monthly_hours += calculated_hours

                new_row = TypeBAttendanceRow(
                    date=row.date,
                    day_of_week=row.day_of_week,
                    entry_time=entry_str,
                    exit_time=exit_str,
                    total_hours=calculated_hours,
                    notes=row.notes
                )
            else:
                # Preserve non-working days without hours
                new_row = TypeBAttendanceRow(
                    date=row.date,
                    day_of_week=row.day_of_week,
                    entry_time=None,
                    exit_time=None,
                    total_hours=0.0,
                    notes=row.notes
                )

            transformed_rows.append(new_row)

        # Calculate dynamic summary totals based on the newly generated rows
        hourly_rate = getattr(report.summary, 'hourly_rate', 35.0)
        total_payment = round(total_monthly_hours * hourly_rate, 2)

        new_summary = TypeBReportSummary(
            total_working_days=total_working_days,
            total_monthly_hours=round(total_monthly_hours, 2),
            hourly_rate=hourly_rate,
            total_payment=total_payment
        )

        return TypeBAttendanceReport(
            report_type=report.report_type,
            rows=transformed_rows,
            summary=new_summary,
            company_name=report.company_name,
            employee_name=report.employee_name
        )