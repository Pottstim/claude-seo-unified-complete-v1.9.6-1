#!/usr/bin/env python3
"""
PDF Report Generator for SEO Analysis
Generates professional, branded client reports
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from io import BytesIO

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class SEOReportGenerator:
    """Generate professional PDF SEO reports"""
    
    def __init__(
        self,
        business_name: str = "Legrand Consulting",
        logo_path: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        website: Optional[str] = None
    ):
        self.business_name = business_name
        self.logo_path = logo_path
        self.contact_email = contact_email or "contact@example.com"
        self.contact_phone = contact_phone
        self.website = website
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
    
    def generate(
        self,
        analysis_data: Dict[str, Any],
        output_path: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> str:
        """
        Generate a PDF report from analysis data.
        
        Args:
            analysis_data: The SEO analysis results
            output_path: Where to save the PDF (auto-generated if None)
            client_name: Client name for the report header
            
        Returns:
            Path to the generated PDF file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = analysis_data.get("url", "unknown").replace("https://", "").replace("http://", "").split("/")[0]
            output_path = f"output/reports/{domain}_{timestamp}.pdf"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='MainTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a5f')
        ))
        styles.add(ParagraphStyle(
            name='SubTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.HexColor('#64748b')
        ))
        styles.add(ParagraphStyle(
            name='ScoreTitle',
            parent=styles['Heading2'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a5f')
        ))
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#1e3a5f')
        ))
        styles.add(ParagraphStyle(
            name='IssueText',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            textColor=colors.HexColor('#374151')
        ))
        
        # Build content
        story = []
        
        # Header
        story.append(Paragraph(self.business_name, styles['MainTitle']))
        story.append(Paragraph("SEO Analysis Report", styles['SubTitle']))
        story.append(Spacer(1, 10))
        
        # Client info table
        client_info = [
            ["Client:", client_name or "Not specified"],
            ["Website:", analysis_data.get("url", "N/A")],
            ["Analysis Date:", datetime.now().strftime("%B %d, %Y")],
            ["Report ID:", analysis_data.get("report_id", "N/A")]
        ]
        
        client_table = Table(client_info, colWidths=[1.5*inch, 4*inch])
        client_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 30))
        
        # Overall Score
        health_score = analysis_data.get("health_score", 0)
        score_color = self._get_score_color(health_score)
        
        story.append(Paragraph("Overall SEO Health Score", styles['ScoreTitle']))
        story.append(Spacer(1, 10))
        
        # Score display
        score_data = [[
            Paragraph(f"<font size='48' color='#{score_color}'>{health_score}</font>", styles['Normal']),
            Paragraph(self._get_score_description(health_score), styles['Normal'])
        ]]
        score_table = Table(score_data, colWidths=[2*inch, 4.5*inch])
        score_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 30))
        
        # Category Scores
        story.append(Paragraph("Category Scores", styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        scores = analysis_data.get("scores", {})
        category_data = [["Category", "Score", "Status"]]
        
        categories = [
            ("Technical SEO", scores.get("technical", 0)),
            ("Content Quality", scores.get("content", 0)),
            ("On-Page SEO", scores.get("onpage", 0)),
            ("Schema Markup", scores.get("schema", 0)),
            ("Performance", scores.get("performance", 0)),
            ("AI Readiness", scores.get("ai_readiness", 0)),
            ("Image SEO", scores.get("images", 0))
        ]
        
        for name, score in categories:
            status = self._get_status_label(score)
            category_data.append([name, f"{score}/100", status])
        
        cat_table = Table(category_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 30))
        
        # Critical Issues
        findings = analysis_data.get("findings", {})
        critical = findings.get("critical", [])
        if critical:
            story.append(Paragraph("🚨 Critical Issues", styles['SectionHeader']))
            for issue in critical[:10]:  # Limit to 10
                issue_text = f"• {issue.get('issue', str(issue))}"
                if issue.get('location'):
                    issue_text += f" <font color='#64748b'>({issue['location']})</font>"
                story.append(Paragraph(issue_text, styles['IssueText']))
            story.append(Spacer(1, 20))
        
        # Warnings
        warnings = findings.get("warnings", [])
        if warnings:
            story.append(Paragraph("⚠️ Warnings", styles['SectionHeader']))
            for issue in warnings[:10]:
                issue_text = f"• {issue.get('issue', str(issue))}"
                story.append(Paragraph(issue_text, styles['IssueText']))
            story.append(Spacer(1, 20))
        
        # Opportunities
        opportunities = findings.get("opportunities", [])
        if opportunities:
            story.append(Paragraph("💡 Opportunities", styles['SectionHeader']))
            for issue in opportunities[:10]:
                issue_text = f"• {issue.get('issue', str(issue))}"
                story.append(Paragraph(issue_text, styles['IssueText']))
            story.append(Spacer(1, 20))
        
        # Recommendations (new page)
        recommendations = analysis_data.get("recommendations", [])
        if recommendations:
            story.append(PageBreak())
            story.append(Paragraph("Prioritized Action Plan", styles['MainTitle']))
            story.append(Spacer(1, 20))
            
            rec_data = [["#", "Action Item", "Priority", "Impact"]]
            for i, rec in enumerate(recommendations[:15], 1):
                rec_data.append([
                    str(i),
                    rec.get("title", str(rec)),
                    rec.get("priority", "Medium"),
                    rec.get("impact", "-")
                ])
            
            rec_table = Table(rec_data, colWidths=[0.5*inch, 3.5*inch, 1*inch, 1*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(rec_table)
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Spacer(1, 10))
        
        footer_text = f"""
        <font size='9' color='#64748b'>
        This report was generated by {self.business_name}.<br/>
        For questions or follow-up analysis, contact: {self.contact_email}
        </font>
        """
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _get_score_color(self, score: int) -> str:
        """Get color for score"""
        if score >= 80:
            return "22c55e"  # Green
        elif score >= 60:
            return "eab308"  # Yellow
        elif score >= 40:
            return "f97316"  # Orange
        else:
            return "ef4444"  # Red
    
    def _get_score_description(self, score: int) -> str:
        """Get description for score"""
        if score >= 80:
            return "Excellent SEO health. The website is well-optimized with minor opportunities for improvement."
        elif score >= 60:
            return "Good SEO health. Several areas could benefit from optimization to improve search visibility."
        elif score >= 40:
            return "Fair SEO health. Multiple issues require attention to improve search engine performance."
        else:
            return "Poor SEO health. Significant improvements needed across multiple areas."
    
    def _get_status_label(self, score: int) -> str:
        """Get status label"""
        if score >= 80:
            return "✅ Good"
        elif score >= 60:
            return "⚠️ Fair"
        elif score >= 40:
            return "🔶 Needs Work"
        else:
            return "❌ Critical"


def generate_report(
    analysis_data: Dict[str, Any],
    business_name: str = "Legrand Consulting",
    output_path: Optional[str] = None,
    client_name: Optional[str] = None
) -> str:
    """Convenience function to generate a report"""
    generator = SEOReportGenerator(business_name=business_name)
    return generator.generate(analysis_data, output_path, client_name)


if __name__ == "__main__":
    # Test report generation
    test_data = {
        "url": "https://example.com",
        "health_score": 72,
        "report_id": "TEST-001",
        "scores": {
            "technical": 82,
            "content": 68,
            "onpage": 75,
            "schema": 60,
            "performance": 45,
            "ai_readiness": 71,
            "images": 65
        },
        "findings": {
            "critical": [
                {"issue": "Missing meta description on 5 pages"},
                {"issue": "No SSL certificate detected"}
            ],
            "warnings": [
                {"issue": "Large image files not optimized"},
                {"issue": "H1 tag missing on homepage"}
            ],
            "opportunities": [
                {"issue": "Add schema markup for organization"},
                {"issue": "Implement lazy loading for images"}
            ]
        },
        "recommendations": [
            {"title": "Add meta descriptions to all pages", "priority": "High", "impact": "High"},
            {"title": "Optimize images for faster loading", "priority": "High", "impact": "Medium"},
            {"title": "Add Organization schema markup", "priority": "Medium", "impact": "Medium"},
            {"title": "Fix H1 tag on homepage", "priority": "Medium", "impact": "High"}
        ]
    }
    
    output = generate_report(test_data, business_name="Legrand Consulting")
    print(f"Report generated: {output}")
