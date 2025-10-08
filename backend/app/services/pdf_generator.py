import os
import io
import base64
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

def generate_sla_pdf(template_data: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate a PDF document from SLA template data.
    
    Args:
        template_data: Dictionary containing SLA template information
        output_path: Optional path to save the PDF file. If not provided, 
                    returns base64-encoded PDF data.
                    
    Returns:
        If output_path is provided: path to saved PDF file
        Otherwise: base64-encoded PDF data string
    """
    # Use a buffer if no output path is provided
    buffer = io.BytesIO() if not output_path else None
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path or buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Initialize styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='Label',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER
    ))
    
    # Build content
    content = []
    
    # Add title
    content.append(Paragraph(f"SERVICE LEVEL AGREEMENT", styles['Title']))
    content.append(Paragraph(template_data.get("name", "Service Level Agreement"), styles['Subtitle']))
    content.append(Spacer(1, 0.25*inch))
    
    # Add agreement info
    # Extract SLA data properly handling different data structures
    sla_data = {}
    if "template_data" in template_data:
        if isinstance(template_data["template_data"], dict):
            sla_data = template_data["template_data"]
        elif isinstance(template_data["template_data"], str):
            # Handle case where template_data might be serialized
            try:
                import json
                sla_data = json.loads(template_data["template_data"])
            except:
                sla_data = {"description": template_data.get("description", "")}
    else:
        # Use available fields from the template directly
        sla_data = {
            "name": template_data.get("name", ""),
            "description": template_data.get("description", ""),
            "service_type": template_data.get("service_type", ""),
            "industry": template_data.get("industry", "")
        }
    
    # Format date
    formatted_date = datetime.now().strftime("%d %B %Y")
    content.append(Paragraph(f"Generated on: {formatted_date}", styles['Normal']))
    content.append(Spacer(1, 0.25*inch))
    
    # Agreement Overview Section
    content.append(Paragraph("AGREEMENT OVERVIEW", styles['SectionHeader']))
    content.append(Paragraph(sla_data.get("overview", "This Service Level Agreement (SLA) describes the levels of service provided to the customer."), styles['Normal']))
    content.append(Spacer(1, 0.15*inch))
    
    # Parties Involved
    if "parties" in sla_data:
        provider = sla_data.get("parties", {}).get("provider", "Provider")
        customer = sla_data.get("parties", {}).get("customer", "Customer")
        content.append(Paragraph(f"Between <b>{provider}</b> (\"Provider\") and <b>{customer}</b> (\"Customer\")", styles['Normal']))
    
    content.append(Spacer(1, 0.25*inch))
    
    # Service Description
    content.append(Paragraph("SERVICE DESCRIPTION", styles['SectionHeader']))
    content.append(Paragraph(sla_data.get("service_description", "Description of services provided."), styles['Normal']))
    content.append(Spacer(1, 0.25*inch))
    
    # Service Hours
    content.append(Paragraph("SERVICE HOURS", styles['SectionHeader']))
    service_hours = sla_data.get("service_hours", {})
    if service_hours:
        hours_data = [
            ["Service Type", "Hours", "Days"]
        ]
        
        for service_type, hours_info in service_hours.items():
            hours_data.append([
                service_type,
                hours_info.get("hours", ""),
                hours_info.get("days", "")
            ])
        
        hours_table = Table(hours_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        hours_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(hours_table)
    else:
        content.append(Paragraph("Standard business hours apply.", styles['Normal']))
    
    content.append(Spacer(1, 0.25*inch))
    
    # Performance Metrics
    content.append(Paragraph("PERFORMANCE METRICS", styles['SectionHeader']))
    metrics = sla_data.get("metrics", [])
    if metrics:
        metrics_data = [
            ["Metric", "Target", "Measurement"]
        ]
        
        for metric in metrics:
            metrics_data.append([
                metric.get("name", ""),
                metric.get("target", ""),
                metric.get("measurement", "")
            ])
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(metrics_table)
    else:
        content.append(Paragraph("No specific performance metrics defined.", styles['Normal']))
    
    content.append(Spacer(1, 0.25*inch))
    
    # Support Response Times
    content.append(Paragraph("SUPPORT RESPONSE TIMES", styles['SectionHeader']))
    support = sla_data.get("support", [])
    if support:
        support_data = [
            ["Severity", "Description", "Response Time", "Resolution Time"]
        ]
        
        for level in support:
            support_data.append([
                level.get("severity", ""),
                level.get("description", ""),
                level.get("response_time", ""),
                level.get("resolution_time", "")
            ])
        
        support_table = Table(support_data, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1.5*inch])
        support_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(support_table)
    else:
        content.append(Paragraph("Standard support response times apply.", styles['Normal']))
    
    content.append(Spacer(1, 0.25*inch))
    
    # Terms and Conditions
    content.append(Paragraph("TERMS AND CONDITIONS", styles['SectionHeader']))
    content.append(Paragraph(sla_data.get("terms", "Standard terms and conditions apply."), styles['Normal']))
    
    # Add footer
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(inch, 0.5*inch, f"SLA Document - Page {doc.page}")
        canvas.drawRightString(letter[0] - inch, 0.5*inch, "Powered by Chakra SLM")
        canvas.restoreState()
    
    # Build the PDF
    doc.build(content, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    # Return base64-encoded data if no output path
    if not output_path:
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        return base64.b64encode(pdf_bytes).decode('utf-8')
    else:
        return output_path