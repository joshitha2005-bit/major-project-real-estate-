"""
Cloud-Based Real Estate Analysis - Home Loan PDF Report Generator
Generates a downloadable, high-fidelity PDF mortgage comparison report using ReportLab.
"""

import io
from datetime import datetime, timezone
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

class LoanPdfService:

    @staticmethod
    def generate_loan_report_pdf(report_data: Dict[str, Any]) -> bytes:
        """
        Builds a comprehensive PDF report from loan comparison data.
        Returns the raw PDF bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=12
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=8,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#334155')
        )
        table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor('#0F172A')
        )
        table_cell_text = ParagraphStyle(
            'TableCellText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor('#334155')
        )
        disclaimer_style = ParagraphStyle(
            'DisclaimerText',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7,
            leading=9,
            textColor=colors.HexColor('#64748B')
        )

        elements = []

        # 1. Header & Branding Banner
        elements.append(Paragraph("Cloud-Based Real Estate Analysis — Home Loan & Mortgage Evaluation Report", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now(timezone.utc).strftime('%B %d, %Y, %H:%M UTC')} | Verified Banking Data (October 2026)", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=0, spaceAfter=10))

        # 2. Property & Borrower Overview (2-Column Key Value Cards)
        prop_summary = report_data.get("property_summary", {})
        user_inputs = report_data.get("user_inputs", {})
        metrics = report_data.get("loan_metrics", {})

        prop_id = prop_summary.get("property_id", "N/A")
        prop_title = prop_summary.get("title", f"Property #{prop_id}")
        prop_loc = prop_summary.get("location", "Bengaluru")
        prop_price = prop_summary.get("property_price", 0.0)
        prop_bhk = prop_summary.get("bhk", "N/A")
        prop_sqft = prop_summary.get("total_sqft", "N/A")

        user_name = user_inputs.get("full_name", "Applicant")
        user_income = user_inputs.get("monthly_income", 0.0)
        user_emp = user_inputs.get("employment_type", "Salaried")
        user_emi = user_inputs.get("existing_monthly_emi", 0.0)
        loan_amount = metrics.get("loan_amount", 0.0)
        down_payment = metrics.get("down_payment", 0.0)
        ltv_pct = metrics.get("actual_ltv_pct", 0.0)
        tenure_yrs = metrics.get("tenure_years", 20)

        overview_data = [
            [
                Paragraph("<b>PROPERTY DETAILS</b>", table_cell_bold),
                Paragraph("<b>BORROWER & LOAN PROFILE</b>", table_cell_bold)
            ],
            [
                Paragraph(f"<b>Title:</b> {prop_title[:45]}", table_cell_text),
                Paragraph(f"<b>Applicant:</b> {user_name} ({user_emp})", table_cell_text)
            ],
            [
                Paragraph(f"<b>Location:</b> {prop_loc} | <b>BHK:</b> {prop_bhk}", table_cell_text),
                Paragraph(f"<b>Monthly Income:</b> ₹{user_income:,.0f} | <b>Existing EMI:</b> ₹{user_emi:,.0f}", table_cell_text)
            ],
            [
                Paragraph(f"<b>Area:</b> {prop_sqft} sq.ft | <b>Listing Price:</b> ₹{prop_price:,.0f}", table_cell_text),
                Paragraph(f"<b>Down Payment:</b> ₹{down_payment:,.0f} | <b>Loan Req:</b> ₹{loan_amount:,.0f}", table_cell_text)
            ],
            [
                Paragraph(f"<b>Loan-to-Value (LTV):</b> {ltv_pct:.1f}% (RBI Cap: {metrics.get('rbi_max_ltv_pct', 80)}%)", table_cell_text),
                Paragraph(f"<b>Preferred Tenure:</b> {tenure_yrs} Years ({tenure_yrs * 12} Months)", table_cell_text)
            ]
        ]

        overview_table = Table(overview_data, colWidths=[270, 270])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#0F172A')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 10))

        # 3. Indicative Loan Summary Metrics (KPI strip)
        kpi_data = [
            [
                Paragraph(f"<font color='#0284C7'><b>₹{metrics.get('estimated_monthly_emi', 0):,}</b></font><br/><font size=6.5>Est. Starting EMI</font>", table_cell_bold),
                Paragraph(f"<font color='#0D9488'><b>₹{metrics.get('total_interest', 0):,}</b></font><br/><font size=6.5>Est. Total Interest</font>", table_cell_bold),
                Paragraph(f"<font color='#4F46E5'><b>₹{metrics.get('total_repayment', 0):,}</b></font><br/><font size=6.5>Total Repayment</font>", table_cell_bold),
                Paragraph(f"<font color='#D97706'><b>{ltv_pct:.1f}%</b></font><br/><font size=6.5>Loan-to-Value (LTV)</font>", table_cell_bold)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[135, 135, 135, 135])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))

        # 4. Multi-Bank Comparison Table
        elements.append(Paragraph("Verified Indian Home Loan Providers & Rate Comparison", section_heading))
        banks = report_data.get("bank_comparisons", [])

        table_header = [
            Paragraph("<b>Bank / Provider</b>", table_cell_bold),
            Paragraph("<b>Rate (p.a.)</b>", table_cell_bold),
            Paragraph("<b>Type</b>", table_cell_bold),
            Paragraph("<b>Starting EMI</b>", table_cell_bold),
            Paragraph("<b>Total Interest</b>", table_cell_bold),
            Paragraph("<b>Indicative Status</b>", table_cell_bold),
            Paragraph("<b>Processing Fee</b>", table_cell_bold)
        ]
        comparison_rows = [table_header]

        for b in banks:
            b_name = b.get("bank_name", "Bank")
            b_rate = f"{b.get('interest_rate_min', 0):.2f}%"
            b_type = b.get("bank_type", "Public")[:7]
            b_emi = f"₹{b.get('estimated_monthly_emi_min', 0):,}"
            b_int = f"₹{b.get('total_interest_min', 0):,}"
            b_status = b.get("indicative_eligibility", "Indicative")
            b_fee = b.get("processing_fee", "Standard")[:22]

            status_color = "#16A34A" if "Eligible" in b_status else "#D97706"
            status_html = f"<font color='{status_color}'><b>{b_status}</b></font>"

            comparison_rows.append([
                Paragraph(f"<b>{b_name}</b>", table_cell_bold),
                Paragraph(b_rate, table_cell_text),
                Paragraph(b_type, table_cell_text),
                Paragraph(b_emi, table_cell_bold),
                Paragraph(b_int, table_cell_text),
                Paragraph(status_html, table_cell_text),
                Paragraph(b_fee, table_cell_text)
            ])

        comp_table = Table(comparison_rows, colWidths=[120, 55, 45, 75, 75, 80, 90])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(comp_table)
        elements.append(Spacer(1, 10))

        # 5. Personalized Observations ("Why these options?")
        observations = report_data.get("personalized_observations", [])
        if observations:
            elements.append(Paragraph("Personalized Financial Insights & Observations", section_heading))
            for obs in observations:
                elements.append(Paragraph(f"• {obs}", body_style))
                elements.append(Spacer(1, 3))
            elements.append(Spacer(1, 8))

        # 6. Disclaimer & Regulatory Compliance
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceBefore=4, spaceAfter=6))
        elements.append(Paragraph(
            "<b>STATUTORY DISCLAIMER & DATA SOURCING:</b> "
            "All interest rates, processing fees, indicative eligibility evaluations, and EMI projections depicted herein "
            "are compiled strictly from verified public disclosures and official bank publications as of October 2026. "
            "Cloud-Based Real Estate Analysis is an analytical technology platform and not a licensed financial advisor, loan broker, or credit institution. "
            "Indicative eligibility does NOT constitute formal credit sanction or an offer of financing. "
            "Final sanction, applicable interest rate, loan amount, and underwriting terms are subject to formal application, "
            "CIBIL credit score evaluation, income documentation, and property legal title verification by the respective lending institution.",
            disclaimer_style
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
