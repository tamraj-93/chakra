"""
Healthcare SLA document formatter.
Creates standardized SLA documents with healthcare-specific sections and formatting.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class HealthcareSLAFormatter:
    """
    Formatter for creating healthcare-specific SLA documents in different formats.
    Supports Markdown, HTML, and JSON formats with appropriate healthcare sections.
    """
    
    def __init__(self):
        """Initialize the formatter"""
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "templates")
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "output")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def format_sla(self, sla_data: Dict[str, Any], output_format: str = "markdown") -> Dict[str, Any]:
        """
        Format SLA data into the specified output format with healthcare-specific sections
        
        Args:
            sla_data: The SLA data collected from consultation
            output_format: The desired output format ("markdown", "html", or "json")
            
        Returns:
            Dict containing the formatted content and metadata
        """
        # Normalize and validate SLA data
        validated_data = self._validate_healthcare_sla(sla_data)
        
        if output_format.lower() == "markdown":
            content = self._format_markdown(validated_data)
        elif output_format.lower() == "html":
            content = self._format_html(validated_data)
        elif output_format.lower() == "json":
            content = json.dumps(validated_data, indent=2)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"healthcare_sla_{timestamp}.{self._get_extension(output_format)}"
        file_path = os.path.join(self.output_dir, filename)
        
        # Save the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "content": content,
            "file_path": file_path,
            "filename": filename,
            "format": output_format
        }
    
    def _validate_healthcare_sla(self, sla_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize healthcare SLA data, ensuring all required sections are present
        """
        # Make a copy to avoid modifying the original
        validated = dict(sla_data)
        
        # Ensure all required healthcare sections exist
        required_sections = {
            "hipaa_compliance": {
                "encryption_standards": "AES-256 encryption for all PHI at rest and in transit",
                "access_controls": "Role-based access with multi-factor authentication",
                "audit_logging": "Comprehensive audit logging with 7-year retention",
                "breach_notification": "Notification within 24 hours of discovery"
            },
            "availability_requirements": {
                "uptime_percentage": "99.95%",
                "maintenance_windows": "2:00 AM - 5:00 AM local time, maximum 4 hours monthly",
                "downtime_notification": "72 hours advance notice for scheduled maintenance"
            },
            "disaster_recovery": {
                "recovery_time_objective": "4 hours",
                "recovery_point_objective": "15 minutes",
                "backup_frequency": "Real-time replication with full backups every 24 hours"
            }
        }
        
        # Add any missing required healthcare sections with default values
        for section, defaults in required_sections.items():
            if section not in validated:
                validated[section] = defaults
            else:
                # Ensure all required fields exist in each section
                for field, default_value in defaults.items():
                    if field not in validated[section]:
                        validated[section][field] = default_value
        
        return validated
    
    def _format_markdown(self, sla_data: Dict[str, Any]) -> str:
        """Format SLA data as Markdown with healthcare-specific sections"""
        # Build the markdown content
        md_content = []
        
        # Title and header
        title = sla_data.get("title", "Healthcare Service Level Agreement")
        md_content.append(f"# {title}")
        md_content.append("")
        
        # Agreement parties
        md_content.append("## Agreement Overview")
        md_content.append("")
        md_content.append("This Service Level Agreement (\"SLA\") is entered into by and between:")
        md_content.append("")
        md_content.append(f"**Healthcare Provider**: {sla_data.get('customer_name', '[HEALTHCARE PROVIDER NAME]')} (\"Customer\")")
        md_content.append(f"**Service Provider**: {sla_data.get('provider_name', '[SERVICE PROVIDER NAME]')} (\"Provider\")")
        md_content.append("")
        md_content.append("This SLA defines the terms and conditions under which the Provider will deliver services to the Customer, with specific consideration for healthcare operations, patient safety, and regulatory compliance.")
        md_content.append("")
        
        # Service description
        if "service_description" in sla_data:
            md_content.append("## 1. Service Description")
            md_content.append("")
            md_content.append(sla_data["service_description"].get("overview", "The Provider will deliver services as described below."))
            md_content.append("")
            
            # List service components if available
            if "components" in sla_data["service_description"]:
                for i, component in enumerate(sla_data["service_description"]["components"], 1):
                    md_content.append(f"{i}. **{component.get('name', f'Component {i}')}**: {component.get('description', '')}")
                md_content.append("")
        
        # HIPAA Compliance Section (Healthcare-specific)
        md_content.append("## 2. HIPAA Compliance and Security")
        md_content.append("")
        
        hipaa = sla_data.get("hipaa_compliance", {})
        md_content.append("### 2.1. Data Security Requirements")
        md_content.append("")
        md_content.append(f"- **Encryption**: {hipaa.get('encryption_standards', 'AES-256 encryption for all PHI')}")
        md_content.append(f"- **Access Controls**: {hipaa.get('access_controls', 'Role-based access with multi-factor authentication')}")
        md_content.append(f"- **Audit Logging**: {hipaa.get('audit_logging', 'Comprehensive audit logging with 7-year retention')}")
        md_content.append("")
        
        md_content.append("### 2.2. Breach Notification Procedures")
        md_content.append("")
        md_content.append(f"- **Notification Timeline**: {hipaa.get('breach_notification', 'Notification within 24 hours of discovery')}")
        md_content.append(f"- **Reporting Process**: {hipaa.get('reporting_process', 'Detailed incident reports and coordination with Customer on notifications to patients and regulators')}")
        md_content.append("")
        
        # Availability Requirements (Healthcare-specific formatting)
        md_content.append("## 3. Service Availability")
        md_content.append("")
        
        availability = sla_data.get("availability_requirements", {})
        md_content.append("### 3.1. Uptime Guarantees")
        md_content.append("")
        md_content.append("| Service Component | Guaranteed Uptime | Maximum Monthly Downtime |")
        md_content.append("|-------------------|------------------|--------------------------|")
        
        uptime = availability.get("uptime_percentage", "99.95%")
        # Convert uptime percentage to downtime minutes
        downtime_mins = 43.8  # Default for 99.9% (43.8 minutes per month)
        if uptime == "99.95%":
            downtime_mins = 21.9
        elif uptime == "99.99%":
            downtime_mins = 4.38
        
        md_content.append(f"| Core Clinical Functions | {uptime} | {downtime_mins} minutes |")
        md_content.append("")
        
        md_content.append("### 3.2. Scheduled Maintenance")
        md_content.append("")
        md_content.append(f"- Regular maintenance will be performed {availability.get('maintenance_windows', 'between 1:00 AM and 5:00 AM local time')}")
        md_content.append(f"- Advance notice: {availability.get('downtime_notification', '72 hours advance notice for scheduled maintenance')}")
        md_content.append("")
        
        # Disaster Recovery (Healthcare-specific section)
        md_content.append("## 4. Disaster Recovery and Business Continuity")
        md_content.append("")
        
        dr = sla_data.get("disaster_recovery", {})
        md_content.append("### 4.1. Recovery Objectives")
        md_content.append("")
        md_content.append(f"- **Recovery Time Objective (RTO)**: {dr.get('recovery_time_objective', '4 hours')}")
        md_content.append(f"- **Recovery Point Objective (RPO)**: {dr.get('recovery_point_objective', '15 minutes')}")
        md_content.append("")
        
        md_content.append("### 4.2. Backup and Redundancy")
        md_content.append("")
        md_content.append(f"- **Backup Frequency**: {dr.get('backup_frequency', 'Real-time replication with full backups every 24 hours')}")
        md_content.append(f"- **Testing**: {dr.get('testing_frequency', 'Quarterly disaster recovery testing with documentation')}")
        md_content.append("")
        
        # Support section
        if "support" in sla_data:
            md_content.append("## 5. Support and Incident Management")
            md_content.append("")
            
            support = sla_data["support"]
            md_content.append("### 5.1. Support Levels and Response Times")
            md_content.append("")
            md_content.append("| Priority | Definition | Response Time | Resolution Target |")
            md_content.append("|----------|------------|--------------|-------------------|")
            
            # Add support tiers if available
            if "tiers" in support:
                for tier in support["tiers"]:
                    md_content.append(f"| {tier.get('name', 'P1')} | {tier.get('description', 'Critical')} | {tier.get('response_time', '15 minutes')} | {tier.get('resolution_time', '2 hours')} |")
            else:
                # Default tiers
                md_content.append("| P1 - Critical | Complete system unavailability or patient safety issue | 15 minutes | 2 hours |")
                md_content.append("| P2 - High | Major functionality affected | 30 minutes | 4 hours |")
                md_content.append("| P3 - Medium | Partial functionality affected | 2 hours | 8 hours |")
                md_content.append("| P4 - Low | Minor issue | 4 hours | 24 hours |")
            
            md_content.append("")
        
        # Add compliance certification section (healthcare-specific)
        md_content.append("## 6. Compliance Certifications and Attestations")
        md_content.append("")
        md_content.append("The Provider maintains the following certifications relevant to healthcare services:")
        md_content.append("")
        
        certifications = sla_data.get("certifications", ["HITRUST CSF", "SOC 2 Type II", "HIPAA Security Assessment"])
        for cert in certifications:
            md_content.append(f"- {cert}")
        
        md_content.append("")
        md_content.append("Current attestations and certifications will be made available upon request.")
        md_content.append("")
        
        # Add signature section
        md_content.append("## Approval and Acceptance")
        md_content.append("")
        md_content.append("This Service Level Agreement is accepted by the authorized representatives of both parties:")
        md_content.append("")
        md_content.append("**For Healthcare Provider**:")  
        md_content.append("Name: ______________________________")  
        md_content.append("Title: ______________________________")  
        md_content.append("Signature: ______________________________")  
        md_content.append("Date: ______________________________")
        md_content.append("")
        md_content.append("**For Service Provider**:")  
        md_content.append("Name: ______________________________")  
        md_content.append("Title: ______________________________")  
        md_content.append("Signature: ______________________________")  
        md_content.append("Date: ______________________________")
        
        return "\n".join(md_content)
    
    def _format_html(self, sla_data: Dict[str, Any]) -> str:
        """Format SLA data as HTML with healthcare-specific styling and sections"""
        # Convert to markdown first, then apply HTML styling
        markdown_content = self._format_markdown(sla_data)
        
        # Convert markdown to simple HTML (in a real implementation, use a proper markdown parser)
        # This is a simplified conversion for demonstration
        html_content = markdown_content.replace("# ", "<h1>").replace("\n## ", "</p>\n<h2>")
        html_content = html_content.replace("\n### ", "</p>\n<h3>")
        html_content = html_content.replace("\n- ", "</p>\n<li>").replace("\n\n", "</p>\n<p>")
        
        # Add healthcare-specific styling
        html_style = """
        <style>
            body { 
                font-family: Arial, sans-serif; 
                line-height: 1.6;
                color: #333;
                max-width: 1100px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 { 
                color: #0056b3; 
                border-bottom: 2px solid #0056b3;
                padding-bottom: 10px;
            }
            h2 { 
                color: #0056b3; 
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }
            h3 { color: #0275d8; }
            table { 
                border-collapse: collapse; 
                width: 100%;
                margin: 20px 0;
            }
            th, td { 
                border: 1px solid #ddd; 
                padding: 8px; 
                text-align: left;
            }
            th { 
                background-color: #f5f9ff;
            }
            .hipaa-section {
                background-color: #f5f9ff;
                border-left: 4px solid #0056b3;
                padding: 10px 15px;
                margin: 15px 0;
            }
            .signature-area {
                margin-top: 50px;
                border-top: 1px solid #ddd;
                padding-top: 20px;
            }
            .compliance-badge {
                display: inline-block;
                background-color: #e9f5e9;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 5px 10px;
                margin: 5px;
                font-size: 0.9em;
            }
        </style>
        """
        
        # Wrap the content in a complete HTML document
        html_document = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>{sla_data.get('title', 'Healthcare Service Level Agreement')}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {html_style}
        </head>
        <body>
            <div class="healthcare-sla">
                {html_content}
            </div>
            
            <div class="healthcare-compliance-footer">
                <p><strong>HIPAA Compliance Notice:</strong> This SLA is designed to support HIPAA compliance requirements for covered entities and business associates.</p>
            </div>
        </body>
        </html>
        """
        
        return html_document
    
    def _get_extension(self, format_type: str) -> str:
        """Get the appropriate file extension for the format type"""
        extensions = {
            "markdown": "md",
            "html": "html",
            "json": "json"
        }
        return extensions.get(format_type.lower(), "txt")