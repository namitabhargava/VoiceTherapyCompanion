import os
import json
from datetime import datetime
import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2E86AB'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#A23B72'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            bulletIndent=10,
            textColor=HexColor('#555555')
        ))
    
    def generate_report(self, session_data, report_type="Single Session Report", 
                       include_transcript=False, include_recommendations=True,
                       include_visualizations=True):
        """Generate comprehensive PDF report"""
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"therapeutic_report_{timestamp}.pdf"
            filepath = f"reports/{filename}"
            
            # Create directory if it doesn't exist
            os.makedirs('reports', exist_ok=True)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build story (content)
            story = []
            
            # Title page
            story.extend(self._create_title_page(session_data, report_type))
            
            # Executive summary
            story.extend(self._create_executive_summary(session_data))
            
            # Domain analysis
            story.extend(self._create_domain_analysis(session_data))
            
            # Visualizations
            if include_visualizations:
                story.extend(self._create_visualizations(session_data))
            
            # Detailed insights
            story.extend(self._create_detailed_insights(session_data))
            
            # Recommendations
            if include_recommendations:
                story.extend(self._create_recommendations(session_data))
            
            # Transcript
            if include_transcript:
                story.extend(self._create_transcript_section(session_data))
            
            # Footer
            story.extend(self._create_footer())
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            st.error(f"PDF generation error: {str(e)}")
            return None
    
    def _create_title_page(self, session_data, report_type):
        """Create title page"""
        story = []
        
        # Title
        title = Paragraph("Therapeutic Assessment Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Report type
        report_type_p = Paragraph(f"<b>{report_type}</b>", self.styles['CustomHeading'])
        story.append(report_type_p)
        story.append(Spacer(1, 0.3*inch))
        
        # Session info
        session_info = [
            ['Session Date:', session_data.timestamp.strftime("%B %d, %Y")],
            ['Session Time:', session_data.timestamp.strftime("%I:%M %p")],
            ['Report Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ['Analysis Version:', '1.0']
        ]
        
        info_table = Table(session_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<b>Confidentiality Notice:</b> This report contains confidential therapeutic information. "
            "It is intended solely for the use of the client and authorized healthcare providers. "
            "Any unauthorized disclosure or distribution is strictly prohibited.",
            self.styles['CustomBody']
        )
        story.append(disclaimer)
        
        story.append(PageBreak())
        
        return story
    
    def _create_executive_summary(self, session_data):
        """Create executive summary section"""
        story = []
        
        # Section title
        title = Paragraph("Executive Summary", self.styles['CustomHeading'])
        story.append(title)
        
        # Overall assessment
        analysis = session_data.analysis
        domain_scores = analysis.get('domain_scores', {})
        
        # Calculate overall score
        overall_score = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0
        
        summary_text = f"""
        This therapeutic assessment analyzed the session using multiple evidence-based frameworks. 
        The overall session rating is <b>{overall_score:.1f}/10</b>, indicating 
        {'excellent' if overall_score >= 8 else 'good' if overall_score >= 6 else 'moderate' if overall_score >= 4 else 'needs attention'} 
        therapeutic progress across measured domains.
        """
        
        story.append(Paragraph(summary_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key highlights
        key_insights = analysis.get('key_insights', [])
        if key_insights:
            story.append(Paragraph("<b>Key Highlights:</b>", self.styles['CustomBody']))
            for insight in key_insights[:3]:  # Top 3 insights
                story.append(Paragraph(f"• {insight}", self.styles['CustomBullet']))
        
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_domain_analysis(self, session_data):
        """Create detailed domain analysis"""
        story = []
        
        # Section title
        title = Paragraph("Therapeutic Domain Analysis", self.styles['CustomHeading'])
        story.append(title)
        
        analysis = session_data.analysis
        domain_scores = analysis.get('domain_scores', {})
        
        # Domain descriptions
        domain_descriptions = {
            'emotional_safety': 'Emotional Safety & Relational Depth (Rogers)',
            'unconscious_patterns': 'Unconscious Pattern Emergence (Freud, Klein)',
            'cognitive_restructuring': 'Cognitive Restructuring (Ellis, Beck)',
            'communication_changes': 'Communication/Family Role Changes (Satir)',
            'strengths_wellbeing': 'Strengths and Well-being (Seligman)',
            'narrative_coherence': 'Narrative/Identity Coherence',
            'behavioral_activation': 'Behavioral Activation in Real Life'
        }
        
        # Create table for domain scores
        domain_data = [['Domain', 'Score', 'Assessment']]
        
        for domain, score in domain_scores.items():
            description = domain_descriptions.get(domain, domain.replace('_', ' ').title())
            assessment = self._get_score_assessment(score)
            domain_data.append([description, f"{score}/10", assessment])
        
        domain_table = Table(domain_data, colWidths=[3*inch, 0.8*inch, 1.5*inch])
        domain_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#F8F9FA'), HexColor('#FFFFFF')])
        ]))
        
        story.append(domain_table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_visualizations(self, session_data):
        """Create visualization section"""
        story = []
        
        # Section title
        title = Paragraph("Visual Analysis", self.styles['CustomHeading'])
        story.append(title)
        
        # Create radar chart
        chart_path = self._create_radar_chart(session_data)
        if chart_path:
            # Add chart to PDF
            story.append(Image(chart_path, width=4*inch, height=3*inch))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_detailed_insights(self, session_data):
        """Create detailed insights section"""
        story = []
        
        # Section title
        title = Paragraph("Detailed Insights", self.styles['CustomHeading'])
        story.append(title)
        
        analysis = session_data.analysis
        
        # Session themes
        themes = analysis.get('session_themes', [])
        if themes:
            story.append(Paragraph("<b>Session Themes:</b>", self.styles['CustomBody']))
            for theme in themes:
                story.append(Paragraph(f"• {theme}", self.styles['CustomBullet']))
            story.append(Spacer(1, 0.2*inch))
        
        # Progress indicators
        progress_indicators = analysis.get('progress_indicators', [])
        if progress_indicators:
            story.append(Paragraph("<b>Progress Indicators:</b>", self.styles['CustomBody']))
            for indicator in progress_indicators:
                story.append(Paragraph(f"• {indicator}", self.styles['CustomBullet']))
            story.append(Spacer(1, 0.2*inch))
        
        # Detailed analysis by framework
        detailed_analysis = analysis.get('detailed_analysis', {})
        
        framework_names = {
            'rogers': 'Person-Centered Approach (Rogers)',
            'psychodynamic': 'Psychodynamic Approach (Freud, Klein)',
            'cognitive': 'Cognitive Behavioral Approach (Ellis, Beck)',
            'family_systems': 'Family Systems Approach (Satir)',
            'positive_psychology': 'Positive Psychology Approach (Seligman)',
            'narrative': 'Narrative Therapy Approach',
            'behavioral': 'Behavioral Activation Approach'
        }
        
        for framework, data in detailed_analysis.items():
            if isinstance(data, dict) and 'score' in data:
                framework_name = framework_names.get(framework, framework.replace('_', ' ').title())
                story.append(Paragraph(f"<b>{framework_name}:</b>", self.styles['CustomBody']))
                
                # Add specific insights from this framework
                for key, value in data.items():
                    if key != 'score' and isinstance(value, list) and value:
                        key_name = key.replace('_', ' ').title()
                        story.append(Paragraph(f"<i>{key_name}:</i>", self.styles['CustomBody']))
                        for item in value[:3]:  # Limit to top 3 items
                            story.append(Paragraph(f"• {item}", self.styles['CustomBullet']))
                
                story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_recommendations(self, session_data):
        """Create recommendations section"""
        story = []
        
        # Section title
        title = Paragraph("Recommendations", self.styles['CustomHeading'])
        story.append(title)
        
        analysis = session_data.analysis
        recommendations = analysis.get('recommendations', [])
        
        if recommendations:
            story.append(Paragraph(
                "Based on the therapeutic analysis, the following recommendations are suggested:",
                self.styles['CustomBody']
            ))
            story.append(Spacer(1, 0.1*inch))
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
                story.append(Spacer(1, 0.05*inch))
        else:
            story.append(Paragraph(
                "No specific recommendations were generated for this session.",
                self.styles['CustomBody']
            ))
        
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_transcript_section(self, session_data):
        """Create transcript section"""
        story = []
        
        # Section title
        title = Paragraph("Session Transcript", self.styles['CustomHeading'])
        story.append(title)
        
        # Transcript text
        transcript = session_data.transcript
        if transcript:
            # Split transcript into paragraphs for better formatting
            paragraphs = transcript.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No transcript available.", self.styles['CustomBody']))
        
        return story
    
    def _create_footer(self):
        """Create footer section"""
        story = []
        
        story.append(PageBreak())
        story.append(Spacer(1, 1*inch))
        
        footer_text = f"""
        <b>Report Information:</b><br/>
        This report was generated using AI-powered therapeutic analysis tools.<br/>
        Analysis Date: {datetime.now().strftime("%B %d, %Y")}<br/>
        Version: 1.0<br/><br/>
        
        <b>Disclaimer:</b><br/>
        This analysis is intended as a supplementary tool for therapeutic reflection and should not 
        replace professional clinical judgment. All therapeutic decisions should be made in consultation 
        with qualified mental health professionals.
        """
        
        story.append(Paragraph(footer_text, self.styles['CustomBody']))
        
        return story
    
    def _get_score_assessment(self, score):
        """Get text assessment for numeric score"""
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Moderate"
        else:
            return "Needs Attention"
    
    def _create_radar_chart(self, session_data):
        """Create radar chart for domain scores"""
        try:
            analysis = session_data.analysis
            domain_scores = analysis.get('domain_scores', {})
            
            if not domain_scores:
                return None
            
            # Prepare data
            categories = list(domain_scores.keys())
            values = list(domain_scores.values())
            
            # Create radar chart
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
            
            # Set up angles for each category
            angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
            angles += angles[:1]  # Complete the circle
            
            # Add values
            values += values[:1]  # Complete the circle
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, label='Current Session')
            ax.fill(angles, values, alpha=0.25)
            
            # Add labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([cat.replace('_', ' ').title() for cat in categories])
            ax.set_ylim(0, 10)
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'])
            ax.grid(True)
            
            plt.title('Therapeutic Domain Scores', size=14, fontweight='bold', pad=20)
            plt.tight_layout()
            
            # Save chart
            chart_path = f"temp_radar_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            st.error(f"Chart creation error: {str(e)}")
            return None
