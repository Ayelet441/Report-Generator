import random
from datetime import datetime, timedelta
from typing import List, Optional
from models.type_a_report import TypeAAttendanceRow, TypeAReportSummary, TypeAAttendanceReport
from transformation.base_transformation import BaseTransformationStrategy


class TypeATransformationStrategy(BaseTransformationStrategy):
    """
    Transformation strategy for Type A attendance reports.
    Generates fully randomized, dynamic synthetic variations adhering to Format A invariants,
    using a fixed default value for workplaces, standard breaks,
    and hour tier distributions (100%, 125%, 150%, Shabbat).
    """

    def transform(self, report: TypeAAttendanceReport, seed: Optional[int] = None) -> TypeAAttendanceReport:
        """
        Transforms an existing Type A report into a new variant with randomized times and valid tier distribution.

        Args:
            report (TypeAAttendanceReport): The original parsed report object.
            seed (Optional[int]): Optional seed (unused for runtime dynamic variation).

        Returns:
            TypeAAttendanceReport: A new transformed report with unique synthetic values.
        """
        transformed_rows: List[TypeAAttendanceRow] = []
        total_working_days = 0
        total_monthly_hours = 0.0
        sum_100 = 0.0
        sum_125 = 0.0
        sum_150 = 0.0
        sum_shabbat = 0.0

        # Fixed default value for workplace instead of random selection
        default_workplace = "מקום עבודה"

        for row in report.rows:
            if row.entry_time and row.exit_time:
                # Randomize entry time and shift duration dynamically
                entry_hour = random.choice([8, 9])
                entry_minute = random.choice([0, 30])
                duration = random.choice([6.5, 7.5, 8.0])

                entry_dt = datetime.strptime(f"{entry_hour:02d}:{entry_minute:02d}", "%H:%M")
                exit_dt = entry_dt + timedelta(hours=duration)

                # Subtract a standard 30-minute break invariant
                break_hours = 0.5
                net_hours = max(0.0, duration - break_hours)

                entry_str = entry_dt.strftime("%H:%M")
                exit_str = exit_dt.strftime("%H:%M")

                # Check if the day is Shabbat based on day name or notes
                is_shabbat = "שבת" in row.day_of_week or "שבת" in (row.notes or "")

                h_100 = 0.0
                h_125 = 0.0
                h_150 = 0.0
                h_shabbat = 0.0

                # Distribute hours according to Format A business rules (tiers)
                if is_shabbat:
                    h_shabbat = net_hours
                    sum_shabbat += h_shabbat
                else:
                    h_100 = net_hours
                    sum_100 += h_100

                total_working_days += 1
                total_monthly_hours += net_hours

                new_row = TypeAAttendanceRow(
                    date=row.date,
                    day_of_week=row.day_of_week,
                    entry_time=entry_str,
                    exit_time=exit_str,
                    total_hours=round(net_hours, 2),
                    notes=row.notes,
                    workplace=default_workplace,
                    break_time="00:30",
                    hours_100=round(h_100, 2),
                    hours_125=round(h_125, 2),
                    hours_150=round(h_150, 2),
                    hours_shabbat_150=round(h_shabbat, 2)
                )
            else:
                # Preserve rest days without hours
                new_row = TypeAAttendanceRow(
                    date=row.date,
                    day_of_week=row.day_of_week,
                    entry_time=None,
                    exit_time=None,
                    total_hours=0.0,
                    notes=row.notes,
                    workplace="",
                    break_time="00:00",
                    hours_100=0.0,
                    hours_125=0.0,
                    hours_150=0.0,
                    hours_shabbat_150=0.0
                )

            transformed_rows.append(new_row)

        # Build dynamic summary totals matching Type A format requirements
        new_summary = TypeAReportSummary(
            total_working_days=total_working_days,
            total_monthly_hours=round(total_monthly_hours, 2),
            total_100_hours=round(sum_100, 2),
            total_125_hours=round(sum_125, 2),
            total_150_hours=round(sum_150, 2),
            total_sabbath_hours=round(sum_shabbat, 2),
            bonus=0.0,
            travel_expenses=0.0
        )

        return TypeAAttendanceReport(
            report_type=report.report_type,
            rows=transformed_rows,
            summary=new_summary,
            company_name=report.company_name,
            employee_name=report.employee_name
        )