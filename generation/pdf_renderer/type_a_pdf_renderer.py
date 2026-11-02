import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from models.type_a_report import TypeAAttendanceReport
from generation.pdf_renderer.pdf_renderer import PdfRenderer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('HebrewArial', 'C:\\Windows\\Fonts\\arial.ttf'))

def fix_hebrew(text: str) -> str:
    """הופכת את סדר האותיות כדי ש-ReportLab תציג עברית מימין לשמאל בצורה תקינה."""
    if not text:
        return ""
    return text[::-1]

class TypeAPdfRenderer(PdfRenderer):
    """
    Concrete PDF renderer for Type A attendance reports.
    Renders the transformed report into a PDF document matching Format A structure:
    - Company and employee details header
    - Detailed daily breakdown table (Date, Day, Workplace, Entry, Exit, Break, Total, Tiers)
    - Comprehensive summary table at the bottom of the report
    """

    def render(self, report: TypeAAttendanceReport, output_path: str) -> None:
        """
        Renders a TypeAAttendanceReport object to a PDF file at the specified output path.

        Args:
            report (TypeAAttendanceReport): The structured report object to render.
            output_path (str): Destination file path for the PDF.
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elements = []
        styles = getSampleStyleSheet()

        # Base style definitions
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='HebrewArial',
            fontSize=16,
            alignment=1,  # Center alignment
            spaceAfter=15
        )

        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName='HebrewArial',
            fontSize=11,
            alignment=2,  # Right alignment for Hebrew context
            spaceAfter=10
        )

        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName='HebrewArial',
            fontSize=8,
            alignment=1  # Center alignment for table cells
        )

        summary_cell_style = ParagraphStyle(
            'SummaryCellStyle',
            parent=styles['Normal'],
            fontName='HebrewArial',
            fontSize=9,
            alignment=2  # Right alignment
        )

        # 1. Document Title & Company Metadata Header
        company_name = getattr(report, 'company_name', 'שם החברה בע"מ')
        employee_name = getattr(report, 'employee_name', 'לא צוין')

        elements.append(Paragraph(fix_hebrew(company_name), title_style))
        elements.append(Paragraph(fix_hebrew(f"שם עובד: {employee_name}"), header_style))
        elements.append(Spacer(1, 10))

        # 2. Main Daily Attendance Table Headers
        raw_headers = ['שבת 150%', '150%', '125%', '100%', 'סה"כ', 'הפסקה', 'יציאה', 'כניסה', 'מקום', 'יום', 'תאריך']
        header_row = [Paragraph(fix_hebrew(h), cell_style) for h in raw_headers]
        table_data = [header_row]

        # Build rows data
        for row in report.rows:
            if row.entry_time and row.exit_time:
                table_data.append([
                    Paragraph(f"{getattr(row, 'hours_shabbat_150', 0.0):.2f}", cell_style),
                    Paragraph(f"{getattr(row, 'hours_150', 0.0):.2f}", cell_style),
                    Paragraph(f"{getattr(row, 'hours_125', 0.0):.2f}", cell_style),
                    Paragraph(f"{getattr(row, 'hours_100', row.total_hours):.2f}", cell_style),
                    Paragraph(f"{row.total_hours:.2f}", cell_style),
                    Paragraph(str(getattr(row, 'break_time', '00:30')), cell_style),
                    Paragraph(str(row.exit_time), cell_style),
                    Paragraph(str(row.entry_time), cell_style),
                    Paragraph(fix_hebrew(str(getattr(row, 'workplace', 'מקום עבודה'))), cell_style),
                    Paragraph(fix_hebrew(str(row.day_of_week)), cell_style),
                    Paragraph(str(row.date), cell_style)
                ])
            else:
                table_data.append([
                    Paragraph('0.00', cell_style),
                    Paragraph('0.00', cell_style),
                    Paragraph('0.00', cell_style),
                    Paragraph('0.00', cell_style),
                    Paragraph('0.00', cell_style),
                    Paragraph('00:00', cell_style),
                    Paragraph('-', cell_style),
                    Paragraph('-', cell_style),
                    Paragraph('-', cell_style),
                    Paragraph(fix_hebrew(str(row.day_of_week)), cell_style),
                    Paragraph(str(row.date), cell_style)
                ])

        # Style main table
        main_table = Table(table_data, colWidths=[45, 40, 40, 40, 45, 45, 45, 45, 60, 50, 70])
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9F9')])
        ]))

        elements.append(main_table)
        elements.append(Spacer(1, 20))

        # 3. Bottom Detailed Summary Table (Matching Format A Invariant)
        summary = report.summary
        raw_summary_data = [
            ['ימים', str(summary.total_working_days)],
            ['סה"כ שעות', f"{summary.total_monthly_hours:.2f}"],
            ['100% שעות', f"{getattr(summary, 'total_100', summary.total_monthly_hours):.2f}"],
            ['125% שעות', f"{getattr(summary, 'total_125', 0.0):.2f}"],
            ['150% שעות', f"{getattr(summary, 'total_150', 0.0):.2f}"],
            ['150% שבת', f"{getattr(summary, 'total_shabbat_150', 0.0):.2f}"],
            ['בונוס', f"{getattr(summary, 'bonus', 0.0):.2f}"],
            ['נסיעות', f"{getattr(summary, 'travel', 0.0):.2f}"]
        ]

        summary_table_data = []
        for label, val in raw_summary_data:
            summary_table_data.append([
                Paragraph(val, cell_style),
                Paragraph(fix_hebrew(label), summary_cell_style)
            ])

        summary_table = Table(summary_table_data, colWidths=[80, 100])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ECF0F1')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(summary_table)

        # Build PDF document
        doc.build(elements)