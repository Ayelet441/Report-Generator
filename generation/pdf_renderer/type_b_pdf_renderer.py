import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from models.type_b_report import TypeBAttendanceReport
from generation.pdf_renderer.pdf_renderer import PdfRenderer


class TypeBPdfRenderer(PdfRenderer):
    """
    Concrete PDF renderer for Type B attendance reports.
    Renders the transformed report into a PDF document matching Format B structure:
    - Main document title ("כרטיס עובד לחודש")
    - Financial and work summary table placed at the top
    - Daily attendance table with entry/exit times, total hours, and notes
    """

    def render(self, report: TypeBAttendanceReport, output_path: str) -> None:
        """
        Renders a TypeBAttendanceReport object to a PDF file at the specified output path.

        Args:
            report (TypeBAttendanceReport): The structured report object to render.
            output_path (str): Destination file path for the PDF.
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=30,
            bottomMargin=30
        )

        elements = []
        styles = getSampleStyleSheet()

        # Base style definitions
        title_style = ParagraphStyle(
            'TitleStyleB',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=1,  # Center alignment
            spaceAfter=15
        )

        # 1. Document Title
        elements.append(Paragraph("כרטיס עובד לחודש", title_style))
        elements.append(Spacer(1, 10))

        # 2. Top Summary Table (Format B Specific)
        summary = report.summary
        hourly_rate = getattr(summary, 'hourly_rate', 35.0)
        total_payment = getattr(summary, 'total_payment', summary.total_monthly_hours * hourly_rate)
        employee_name = getattr(report, 'employee_name', 'לא צוין')

        top_summary_data = [
            [f"סה\"כ ימי עבודה: {summary.total_working_days}", f"שם העובד: {employee_name}"],
            [f"מחיר לשעה: {hourly_rate:.2f} ש\"ח", f"סה\"כ שעות חודשיות: {summary.total_monthly_hours:.2f}"],
            [f"סה\"כ לתשלום: {total_payment:.2f} ש\"ח", ""]
        ]

        top_table = Table(top_summary_data, colWidths=[240, 240])
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ECF0F1')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('SPAN', (0, 2), (1, 2)),  # Merge full row for total payment
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(top_table)
        elements.append(Spacer(1, 20))

        # 3. Main Daily Attendance Table Headers
        table_data = [[
            'הערות', 'סה"כ שעות', 'שעת יציאה', 'שעת כניסה', 'יום בשבוע', 'תאריך'
        ]]

        # Build rows data
        for row in report.rows:
            entry = row.entry_time if row.entry_time else "-"
            exit_t = row.exit_time if row.exit_time else "-"
            total_str = f"{row.total_hours:.2f}" if row.total_hours > 0 else "-"
            notes = getattr(row, 'notes', '') or ""

            table_data.append([
                notes,
                total_str,
                exit_t,
                entry,
                row.day_of_week,
                row.date
            ])

        # Style main table
        main_table = Table(table_data, colWidths=[100, 70, 70, 70, 80, 90])
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9F9')])
        ]))

        elements.append(main_table)

        # Build PDF document
        doc.build(elements)