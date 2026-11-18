import io
import os
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from apps.reports.models import Report

class SecurityReportPDFGenerator:
    """
    Renders professional, audit-grade PDF security reports containing executive
    summaries, evidence references, and developer remediation guidance.
    """
    @staticmethod
    def generate_pdf_report(report: Report) -> ContentFile:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1e1b4b'),
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#64748b')
        )
        heading2_style = ParagraphStyle(
            'ReportH2',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#312e81'),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#334155')
        )
        code_style = ParagraphStyle(
            'ReportCode',
            parent=styles['Code'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#0f172a'),
            backColor=colors.HexColor('#f1f5f9'),
            borderColor=colors.HexColor('#cbd5e1'),
            borderWidth=1,
            borderPadding=4
        )

        story = []

        # Header
        scan = report.scan
        story.append(Paragraph("SecureMind AI — Security Assessment Report", title_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Target: <b>{scan.asset.domain}</b> | Date: {report.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')} | Type: {report.get_report_type_display()}", subtitle_style))
        story.append(Spacer(1, 15))

        # Executive Metrics Table
        metrics = report.metrics_summary or {}
        story.append(Paragraph("Executive Summary & Risk Metrics", heading2_style))
        
        summary_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Findings", str(metrics.get("total_findings", 0)), "Critical Severity", str(metrics.get("critical", 0))],
            ["High Severity", str(metrics.get("high", 0)), "Medium Severity", str(metrics.get("medium", 0))],
            ["Low / Info", str(metrics.get("low", 0)), "Confirmed Verified", str(metrics.get("confirmed_count", 0))],
        ]

        summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Detailed Findings Section
        story.append(Paragraph("Vulnerability Findings & Evidence", heading2_style))

        findings = scan.findings.select_related('remediation').prefetch_related('evidences').all()
        if not findings:
            story.append(Paragraph("No vulnerabilities or security anomalies were identified in this assessment.", body_style))
        else:
            for i, f in enumerate(findings, 1):
                sev_color = {
                    'critical': '#e11d48',
                    'high': '#ea580c',
                    'medium': '#d97706',
                    'low': '#0284c7'
                }.get(f.severity.lower(), '#64748b')

                finding_elements = []
                finding_elements.append(Paragraph(f"<b>#{i}. {f.title}</b> [<font color='{sev_color}'><b>{f.severity.upper()}</b></font>]", ParagraphStyle('FTitle', parent=body_style, fontSize=11, leading=14)))
                finding_elements.append(Spacer(1, 2))
                finding_elements.append(Paragraph(f"<b>URL:</b> {f.affected_url} | <b>CWE:</b> {f.cwe_id or 'N/A'} | <b>Status:</b> {f.verification_status}", body_style))
                finding_elements.append(Spacer(1, 4))
                finding_elements.append(Paragraph(f"<b>Description:</b> {f.description}", body_style))

                # Remediation
                if hasattr(f, 'remediation') and f.remediation:
                    rem = f.remediation
                    finding_elements.append(Spacer(1, 4))
                    finding_elements.append(Paragraph(f"<b>Remediation Guidance:</b> {rem.explanation}", body_style))
                    finding_elements.append(Paragraph(f"<b>Fix Strategy:</b> {rem.remediation_strategy}", body_style))

                finding_elements.append(Spacer(1, 10))
                story.append(KeepTogether(finding_elements))

        # Disclaimer
        story.append(Spacer(1, 15))
        story.append(Paragraph("<b>Disclaimer & Assessment Scope:</b> SecureMind AI security assessments are defensive evaluations conducted strictly within authorized scope. Findings are verified against observed HTTP responses.", ParagraphStyle('Disc', parent=body_style, fontSize=8, leading=10, textColor=colors.HexColor('#94a3b8'))))

        doc.build(story)
        buffer.seek(0)
        return ContentFile(buffer.getvalue(), name=f"securemind_report_{scan.asset.domain}_{report.id}.pdf")
