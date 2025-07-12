from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DomainScore:
    """Individual domain score with details"""
    domain: str
    score: float
    evidence: List[str]
    areas_for_improvement: List[str]
    
class TherapeuticFramework:
    """Therapeutic analysis frameworks and scoring"""
    
    def __init__(self):
        self.domains = {
            'emotional_safety': {
                'name': 'Emotional Safety & Relational Depth',
                'theorist': 'Carl Rogers',
                'description': 'Empathy, genuineness, and unconditional positive regard',
                'indicators': [
                    'Therapist empathy evidence',
                    'Genuineness and authenticity',
                    'Unconditional positive regard',
                    'Client self-exploration',
                    'Emotional safety and trust'
                ]
            },
            'unconscious_patterns': {
                'name': 'Unconscious Pattern Emergence',
                'theorist': 'Freud & Klein',
                'description': 'Unconscious material and symbolic processing',
                'indicators': [
                    'Unconscious patterns identified',
                    'Defense mechanisms',
                    'Symbolic content',
                    'Transference indicators',
                    'Early experience connections'
                ]
            },
            'cognitive_restructuring': {
                'name': 'Cognitive Restructuring',
                'theorist': 'Ellis & Beck',
                'description': 'Irrational thought detection and belief reframing',
                'indicators': [
                    'Irrational beliefs identified',
                    'Cognitive distortions',
                    'Restructuring evidence',
                    'Homework assignments',
                    'Thought challenging'
                ]
            },
            'communication_changes': {
                'name': 'Communication/Family Role Changes',
                'theorist': 'Virginia Satir',
                'description': 'Family dynamics and communication patterns',
                'indicators': [
                    'Communication patterns',
                    'Family role dynamics',
                    'Boundary issues',
                    'Intergenerational patterns',
                    'Systems insights'
                ]
            },
            'strengths_wellbeing': {
                'name': 'Strengths and Well-being',
                'theorist': 'Martin Seligman',
                'description': 'Positive psychology and PERMA model',
                'indicators': [
                    'PERMA elements',
                    'Character strengths',
                    'Gratitude practices',
                    'Optimism building',
                    'Resilience factors'
                ]
            },
            'narrative_coherence': {
                'name': 'Narrative/Identity Coherence',
                'theorist': 'Narrative Therapy',
                'description': 'Life story coherence and identity development',
                'indicators': [
                    'Story coherence',
                    'Identity themes',
                    'Life meanings',
                    'Narrative disruptions',
                    'Growth indicators'
                ]
            },
            'behavioral_activation': {
                'name': 'Behavioral Activation in Real Life',
                'theorist': 'Behavioral Therapy',
                'description': 'Real-world application and behavior change',
                'indicators': [
                    'Behavioral goals',
                    'Activity planning',
                    'Behavioral experiments',
                    'Real-world applications',
                    'Action commitments'
                ]
            }
        }
    
    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get information about a specific domain"""
        return self.domains.get(domain, {})
    
    def get_all_domains(self) -> List[str]:
        """Get list of all domain names"""
        return list(self.domains.keys())
    
    def get_domain_indicators(self, domain: str) -> List[str]:
        """Get indicators for a specific domain"""
        return self.domains.get(domain, {}).get('indicators', [])

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    session_id: str
    timestamp: datetime
    domain_scores: Dict[str, float]
    detailed_analysis: Dict[str, Any]
    key_insights: List[str]
    recommendations: List[str]
    session_themes: List[str]
    progress_indicators: List[str]
    
    def get_overall_score(self) -> float:
        """Calculate overall session score"""
        if not self.domain_scores:
            return 0.0
        return sum(self.domain_scores.values()) / len(self.domain_scores)
    
    def get_strongest_domains(self, count: int = 3) -> List[str]:
        """Get domains with highest scores"""
        sorted_domains = sorted(
            self.domain_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [domain for domain, score in sorted_domains[:count]]
    
    def get_weakest_domains(self, count: int = 3) -> List[str]:
        """Get domains with lowest scores"""
        sorted_domains = sorted(
            self.domain_scores.items(), 
            key=lambda x: x[1]
        )
        return [domain for domain, score in sorted_domains[:count]]
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary"""
        return {
            'overall_score': self.get_overall_score(),
            'strongest_domains': self.get_strongest_domains(),
            'weakest_domains': self.get_weakest_domains(),
            'key_themes': self.session_themes[:3],
            'primary_recommendations': self.recommendations[:3]
        }

class ProgressTracker:
    """Track progress across multiple sessions"""
    
    def __init__(self):
        self.sessions: List[AnalysisResult] = []
    
    def add_session(self, analysis_result: AnalysisResult):
        """Add a new session analysis"""
        self.sessions.append(analysis_result)
        self.sessions.sort(key=lambda x: x.timestamp)
    
    def get_progress_trend(self, domain: str) -> List[float]:
        """Get progress trend for a specific domain"""
        return [
            session.domain_scores.get(domain, 0) 
            for session in self.sessions
        ]
    
    def get_overall_progress_trend(self) -> List[float]:
        """Get overall progress trend"""
        return [session.get_overall_score() for session in self.sessions]
    
    def calculate_improvement_rate(self, domain: str) -> float:
        """Calculate improvement rate for a domain"""
        if len(self.sessions) < 2:
            return 0.0
        
        first_score = self.sessions[0].domain_scores.get(domain, 0)
        last_score = self.sessions[-1].domain_scores.get(domain, 0)
        
        return last_score - first_score
    
    def get_session_comparison(self, session1_idx: int, session2_idx: int) -> Dict[str, float]:
        """Compare two sessions"""
        if session1_idx >= len(self.sessions) or session2_idx >= len(self.sessions):
            return {}
        
        session1 = self.sessions[session1_idx]
        session2 = self.sessions[session2_idx]
        
        comparison = {}
        for domain in session1.domain_scores:
            if domain in session2.domain_scores:
                comparison[domain] = session2.domain_scores[domain] - session1.domain_scores[domain]
        
        return comparison
    
    def get_insights_evolution(self) -> List[str]:
        """Get evolution of insights across sessions"""
        all_insights = []
        for session in self.sessions:
            all_insights.extend(session.key_insights)
        
        # Return unique insights to show evolution
        return list(set(all_insights))
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        if not self.sessions:
            return {}
        
        report = {
            'total_sessions': len(self.sessions),
            'date_range': {
                'start': self.sessions[0].timestamp.isoformat(),
                'end': self.sessions[-1].timestamp.isoformat()
            },
            'overall_improvement': self.get_overall_progress_trend()[-1] - self.get_overall_progress_trend()[0],
            'domain_improvements': {},
            'consistent_themes': [],
            'key_recommendations': []
        }
        
        # Calculate domain improvements
        for domain in self.sessions[0].domain_scores:
            report['domain_improvements'][domain] = self.calculate_improvement_rate(domain)
        
        # Find consistent themes
        theme_counts = {}
        for session in self.sessions:
            for theme in session.session_themes:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Themes that appear in multiple sessions
        report['consistent_themes'] = [
            theme for theme, count in theme_counts.items() 
            if count > 1
        ]
        
        # Collect all unique recommendations
        all_recommendations = []
        for session in self.sessions:
            all_recommendations.extend(session.recommendations)
        
        report['key_recommendations'] = list(set(all_recommendations))[:5]
        
        return report
