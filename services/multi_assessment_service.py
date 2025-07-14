"""
Multi-Assessment Service implementing evidence-based assessment techniques
Based on "Multiple Assessment Methods and Sources in Counseling: Ethical Considerations"
by Monica Leppma and Karyn Dayle Jones
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AssessmentMethod:
    """Represents a single assessment method with its strengths and limitations"""
    name: str
    method_type: str  # formal, informal, structured, unstructured
    strengths: List[str]
    weaknesses: List[str]
    reliability_score: float  # 1-10 scale
    validity_indicators: List[str]


@dataclass
class AssessmentSource:
    """Represents a source of assessment information"""
    source_type: str  # client, family, professional, documents
    reliability: float  # 1-10 scale
    perspective: str  # description of unique viewpoint
    limitations: List[str]


class MultiAssessmentService:
    """
    Implements multiple assessment methods and sources for therapeutic evaluation
    Based on best practices from counseling assessment literature
    """
    
    def __init__(self):
        self.assessment_methods = self._initialize_assessment_methods()
        self.assessment_sources = self._initialize_assessment_sources()
        
    def _initialize_assessment_methods(self) -> Dict[str, AssessmentMethod]:
        """Initialize the various assessment methods available"""
        return {
            "unstructured_interview": AssessmentMethod(
                name="Unstructured Clinical Interview",
                method_type="informal",
                strengths=[
                    "Fosters rapport building",
                    "Flexible; can tailor to clients", 
                    "Provides in-depth information",
                    "Holistic perspective",
                    "Time and cost effective",
                    "Face validity"
                ],
                weaknesses=[
                    "Reliance on counselor's judgment",
                    "Subject to counselor's bias",
                    "Not standardized; lack of reliability",
                    "Potential for misdiagnosis"
                ],
                reliability_score=6.0,
                validity_indicators=["rapport_quality", "depth_of_exploration", "client_openness"]
            ),
            
            "structured_interview": AssessmentMethod(
                name="Structured Interview",
                method_type="formal",
                strengths=[
                    "Improved reliability",
                    "Ensures collection of specific information",
                    "Little training needed",
                    "Standardized format"
                ],
                weaknesses=[
                    "Constrained to specific questions and format",
                    "May inhibit in-depth exploration"
                ],
                reliability_score=8.0,
                validity_indicators=["systematic_coverage", "consistency", "completeness"]
            ),
            
            "semi_structured_interview": AssessmentMethod(
                name="Semi-Structured Interview",
                method_type="mixed",
                strengths=[
                    "Better reliability than unstructured interview",
                    "Flexible guidelines",
                    "Can be tailored to client",
                    "Provides consistency of questions"
                ],
                weaknesses=[
                    "Not completely standardized",
                    "Subject to counselor bias",
                    "Wording of questions may influence responses",
                    "Dependent on skill of interviewer"
                ],
                reliability_score=7.5,
                validity_indicators=["structured_flexibility", "systematic_exploration", "response_quality"]
            ),
            
            "behavioral_observation": AssessmentMethod(
                name="Behavioral Observation",
                method_type="informal",
                strengths=[
                    "Provides perceptions of client's behavior",
                    "Real-time assessment",
                    "Non-verbal information"
                ],
                weaknesses=[
                    "Constrained by observer's relationship to client and setting",
                    "Observer bias",
                    "Context-dependent"
                ],
                reliability_score=6.5,
                validity_indicators=["behavioral_consistency", "contextual_relevance", "non_verbal_alignment"]
            ),
            
            "therapeutic_rating_scales": AssessmentMethod(
                name="Therapeutic Rating Scales",
                method_type="formal",
                strengths=[
                    "Quick and efficient",
                    "Quantifiable data",
                    "Standardized scoring"
                ],
                weaknesses=[
                    "Potential for rater bias",
                    "Validity issues",
                    "May miss nuanced information"
                ],
                reliability_score=7.0,
                validity_indicators=["score_consistency", "predictive_validity", "clinical_relevance"]
            )
        }
    
    def _initialize_assessment_sources(self) -> Dict[str, AssessmentSource]:
        """Initialize the various sources of assessment information"""
        return {
            "client_self_report": AssessmentSource(
                source_type="client",
                reliability=7.0,
                perspective="First-person subjective experience",
                limitations=["Self-report bias", "Limited self-awareness", "Social desirability"]
            ),
            
            "therapist_observation": AssessmentSource(
                source_type="professional",
                reliability=8.0,
                perspective="Professional clinical judgment",
                limitations=["Professional bias", "Limited context", "Theoretical orientation influence"]
            ),
            
            "session_transcript": AssessmentSource(
                source_type="documents",
                reliability=9.0,
                perspective="Objective record of interactions",
                limitations=["Lacks non-verbal cues", "Context-dependent interpretation"]
            ),
            
            "collateral_sources": AssessmentSource(
                source_type="family",
                reliability=6.5,
                perspective="External perspective on client functioning",
                limitations=["Relationship dynamics", "Limited clinical training", "Potential conflicts"]
            )
        }
    
    def conduct_comprehensive_assessment(self, transcript: str, additional_sources: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Conduct comprehensive assessment using multiple methods and sources
        Following best practices from counseling assessment literature
        """
        
        # Initialize results structure
        assessment_results = {
            "assessment_date": datetime.now().isoformat(),
            "methods_used": [],
            "sources_consulted": [],
            "convergent_findings": {},
            "divergent_findings": {},
            "reliability_assessment": {},
            "validity_indicators": {},
            "clinical_recommendations": [],
            "assessment_limitations": []
        }
        
        # 1. Unstructured Interview Analysis (primary method)
        unstructured_results = self._analyze_unstructured_interview(transcript)
        assessment_results["methods_used"].append("unstructured_interview")
        
        # 2. Structured Interview Elements (systematic coverage)
        structured_results = self._analyze_structured_elements(transcript)
        assessment_results["methods_used"].append("structured_interview")
        
        # 3. Behavioral Observation (from transcript)
        behavioral_results = self._analyze_behavioral_indicators(transcript)
        assessment_results["methods_used"].append("behavioral_observation")
        
        # 4. Therapeutic Rating Scales
        rating_results = self._apply_therapeutic_rating_scales(transcript)
        assessment_results["methods_used"].append("therapeutic_rating_scales")
        
        # 5. Cross-validate findings across methods (convergent validity)
        convergent_analysis = self._assess_convergent_validity(
            unstructured_results, structured_results, behavioral_results, rating_results
        )
        
        # 6. Integrate multiple sources if available
        if additional_sources:
            source_integration = self._integrate_multiple_sources(additional_sources)
            assessment_results["sources_consulted"] = list(additional_sources.keys())
        else:
            assessment_results["sources_consulted"] = ["session_transcript"]
        
        # 7. Compile comprehensive results
        assessment_results.update({
            "convergent_findings": convergent_analysis["convergent"],
            "divergent_findings": convergent_analysis["divergent"],
            "reliability_assessment": self._assess_overall_reliability(assessment_results["methods_used"]),
            "validity_indicators": self._assess_validity_indicators(transcript),
            "clinical_recommendations": self._generate_clinical_recommendations(convergent_analysis),
            "assessment_limitations": self._identify_assessment_limitations(assessment_results["methods_used"])
        })
        
        return assessment_results
    
    def _analyze_unstructured_interview(self, transcript: str) -> Dict[str, Any]:
        """Analyze transcript as unstructured clinical interview"""
        
        # Therapeutic relationship indicators
        rapport_indicators = self._assess_rapport_quality(transcript)
        depth_indicators = self._assess_exploration_depth(transcript)
        client_openness = self._assess_client_openness(transcript)
        
        return {
            "method": "unstructured_interview",
            "rapport_quality": rapport_indicators,
            "exploration_depth": depth_indicators,
            "client_openness": client_openness,
            "therapeutic_themes": self._identify_therapeutic_themes(transcript),
            "counselor_techniques": self._identify_counselor_techniques(transcript),
            "reliability_score": self.assessment_methods["unstructured_interview"].reliability_score
        }
    
    def _analyze_structured_elements(self, transcript: str) -> Dict[str, Any]:
        """Analyze transcript for structured interview elements"""
        
        # Systematic coverage areas
        coverage_areas = {
            "presenting_problem": self._assess_problem_presentation(transcript),
            "symptom_assessment": self._assess_symptom_coverage(transcript),
            "functional_impact": self._assess_functional_impact(transcript),
            "risk_assessment": self._assess_risk_factors(transcript),
            "strengths_assessment": self._assess_client_strengths(transcript),
            "treatment_goals": self._assess_goal_identification(transcript)
        }
        
        return {
            "method": "structured_interview",
            "systematic_coverage": coverage_areas,
            "completeness_score": self._calculate_completeness_score(coverage_areas),
            "reliability_score": self.assessment_methods["structured_interview"].reliability_score
        }
    
    def _analyze_behavioral_indicators(self, transcript: str) -> Dict[str, Any]:
        """Analyze behavioral indicators from transcript"""
        
        # Extract behavioral observations
        behavioral_patterns = {
            "engagement_level": self._assess_engagement_level(transcript),
            "emotional_regulation": self._assess_emotional_regulation(transcript),
            "communication_style": self._assess_communication_style(transcript),
            "defensive_behaviors": self._assess_defensive_behaviors(transcript),
            "therapeutic_alliance": self._assess_therapeutic_alliance(transcript)
        }
        
        return {
            "method": "behavioral_observation",
            "behavioral_patterns": behavioral_patterns,
            "consistency_indicators": self._assess_behavioral_consistency(transcript),
            "reliability_score": self.assessment_methods["behavioral_observation"].reliability_score
        }
    
    def _apply_therapeutic_rating_scales(self, transcript: str) -> Dict[str, Any]:
        """Apply therapeutic rating scales to session content"""
        
        # Therapeutic outcome scales
        scales = {
            "therapeutic_alliance_scale": self._rate_therapeutic_alliance(transcript),
            "session_impact_scale": self._rate_session_impact(transcript),
            "client_engagement_scale": self._rate_client_engagement(transcript),
            "therapist_competence_scale": self._rate_therapist_competence(transcript),
            "progress_indicators_scale": self._rate_progress_indicators(transcript)
        }
        
        return {
            "method": "therapeutic_rating_scales",
            "scale_scores": scales,
            "overall_rating": sum(scales.values()) / len(scales),
            "reliability_score": self.assessment_methods["therapeutic_rating_scales"].reliability_score
        }
    
    def _assess_convergent_validity(self, *method_results) -> Dict[str, Any]:
        """Assess convergent validity across multiple assessment methods"""
        
        convergent_themes = []
        divergent_findings = []
        
        # Extract key findings from each method
        all_findings = []
        for result in method_results:
            if isinstance(result, dict):
                all_findings.append(result)
        
        # Identify convergent patterns
        convergent_patterns = self._identify_convergent_patterns(all_findings)
        
        # Identify divergent findings
        divergent_patterns = self._identify_divergent_patterns(all_findings)
        
        return {
            "convergent": convergent_patterns,
            "divergent": divergent_patterns,
            "validity_strength": self._calculate_validity_strength(convergent_patterns, divergent_patterns)
        }
    
    # Helper methods for specific assessments
    def _assess_rapport_quality(self, transcript: str) -> Dict[str, Any]:
        """Assess quality of therapeutic rapport"""
        
        rapport_indicators = {
            "empathic_responses": len(re.findall(r'(understand|feel|hear you|that sounds|i can see)', transcript.lower())),
            "validation_statements": len(re.findall(r'(valid|understandable|makes sense|appreciate)', transcript.lower())),
            "collaborative_language": len(re.findall(r'(we|together|with you|our work)', transcript.lower())),
            "warmth_indicators": len(re.findall(r'(care|support|here for you|safe)', transcript.lower()))
        }
        
        rapport_score = min(10, sum(rapport_indicators.values()) * 0.5)
        
        return {
            "rapport_score": rapport_score,
            "indicators": rapport_indicators,
            "quality_level": "high" if rapport_score >= 7 else "moderate" if rapport_score >= 4 else "low"
        }
    
    def _assess_exploration_depth(self, transcript: str) -> Dict[str, Any]:
        """Assess depth of therapeutic exploration"""
        
        depth_indicators = {
            "open_ended_questions": len(re.findall(r'(how|what|tell me|describe|explain)', transcript.lower())),
            "emotion_exploration": len(re.findall(r'(feel|emotion|feeling|experience)', transcript.lower())),
            "pattern_exploration": len(re.findall(r'(pattern|usually|often|tend to)', transcript.lower())),
            "meaning_making": len(re.findall(r'(mean|significant|important|realize)', transcript.lower()))
        }
        
        depth_score = min(10, sum(depth_indicators.values()) * 0.3)
        
        return {
            "depth_score": depth_score,
            "indicators": depth_indicators,
            "exploration_level": "deep" if depth_score >= 7 else "moderate" if depth_score >= 4 else "superficial"
        }
    
    def _assess_client_openness(self, transcript: str) -> Dict[str, Any]:
        """Assess client's openness and engagement"""
        
        openness_indicators = {
            "self_disclosure": len(re.findall(r'(i feel|i think|i believe|i experience)', transcript.lower())),
            "vulnerability_sharing": len(re.findall(r'(difficult|hard|struggle|vulnerable)', transcript.lower())),
            "insight_expressions": len(re.findall(r'(realize|understand|see now|learned)', transcript.lower())),
            "emotional_expression": len(re.findall(r'(sad|happy|angry|anxious|excited|frustrated)', transcript.lower()))
        }
        
        openness_score = min(10, sum(openness_indicators.values()) * 0.4)
        
        return {
            "openness_score": openness_score,
            "indicators": openness_indicators,
            "engagement_level": "high" if openness_score >= 7 else "moderate" if openness_score >= 4 else "low"
        }
    
    def _identify_therapeutic_themes(self, transcript: str) -> List[str]:
        """Identify major therapeutic themes in the session"""
        
        themes = []
        
        # Common therapeutic themes
        theme_patterns = {
            "relationship_issues": r'(relationship|partner|family|friend|connect)',
            "emotional_regulation": r'(emotion|feeling|regulate|control|manage)',
            "trauma_processing": r'(trauma|abuse|hurt|pain|past)',
            "self_esteem": r'(self|worth|value|confidence|esteem)',
            "anxiety_depression": r'(anxious|worried|sad|depressed|down)',
            "coping_skills": r'(cope|manage|deal with|handle|strategy)',
            "life_transitions": r'(change|transition|new|different|moving)',
            "identity_issues": r'(identity|who am i|purpose|meaning|role)'
        }
        
        for theme, pattern in theme_patterns.items():
            if re.search(pattern, transcript.lower()):
                themes.append(theme)
        
        return themes
    
    def _identify_counselor_techniques(self, transcript: str) -> List[str]:
        """Identify counselor techniques used in session"""
        
        techniques = []
        
        # Common therapeutic techniques
        technique_patterns = {
            "active_listening": r'(i hear|sounds like|what i\'m hearing)',
            "reflection": r'(reflect|mirror|seems like you)',
            "reframing": r'(another way|different perspective|reframe)',
            "summarizing": r'(so what i\'m hearing|to summarize|let me recap)',
            "questioning": r'(what|how|when|where|why|tell me more)',
            "validation": r'(valid|understandable|makes sense|normal)',
            "interpretation": r'(seems like|appears that|wonder if)',
            "psychoeducation": r'(education|explain|information|learn about)'
        }
        
        for technique, pattern in technique_patterns.items():
            if re.search(pattern, transcript.lower()):
                techniques.append(technique)
        
        return techniques
    
    def _assess_problem_presentation(self, transcript: str) -> Dict[str, Any]:
        """Assess how well the presenting problem is covered"""
        
        problem_elements = {
            "problem_description": bool(re.search(r'(problem|issue|concern|difficult)', transcript.lower())),
            "symptom_details": bool(re.search(r'(symptom|experience|feel|happen)', transcript.lower())),
            "onset_timing": bool(re.search(r'(when|started|began|first time)', transcript.lower())),
            "severity_impact": bool(re.search(r'(severe|mild|impact|affect|interfere)', transcript.lower())),
            "frequency_duration": bool(re.search(r'(often|frequency|how long|duration)', transcript.lower()))
        }
        
        coverage_score = sum(problem_elements.values()) / len(problem_elements) * 10
        
        return {
            "coverage_score": coverage_score,
            "elements_covered": problem_elements,
            "completeness": "comprehensive" if coverage_score >= 8 else "adequate" if coverage_score >= 6 else "limited"
        }
    
    def _assess_symptom_coverage(self, transcript: str) -> Dict[str, Any]:
        """Assess systematic coverage of symptoms"""
        
        symptom_domains = {
            "cognitive_symptoms": bool(re.search(r'(think|thought|memory|concentrate)', transcript.lower())),
            "emotional_symptoms": bool(re.search(r'(feel|emotion|mood|affect)', transcript.lower())),
            "behavioral_symptoms": bool(re.search(r'(do|behave|action|activity)', transcript.lower())),
            "somatic_symptoms": bool(re.search(r'(body|physical|sleep|eat|energy)', transcript.lower())),
            "interpersonal_symptoms": bool(re.search(r'(relationship|social|interact|people)', transcript.lower()))
        }
        
        coverage_score = sum(symptom_domains.values()) / len(symptom_domains) * 10
        
        return {
            "coverage_score": coverage_score,
            "domains_covered": symptom_domains,
            "systematic_assessment": "thorough" if coverage_score >= 8 else "adequate" if coverage_score >= 6 else "limited"
        }
    
    def _assess_functional_impact(self, transcript: str) -> Dict[str, Any]:
        """Assess impact on client's functioning"""
        
        functional_areas = {
            "work_functioning": bool(re.search(r'(work|job|career|employment)', transcript.lower())),
            "relationship_functioning": bool(re.search(r'(relationship|family|friend|social)', transcript.lower())),
            "self_care": bool(re.search(r'(self care|hygiene|health|eating)', transcript.lower())),
            "daily_activities": bool(re.search(r'(daily|routine|activities|function)', transcript.lower())),
            "recreational_activities": bool(re.search(r'(hobbies|fun|recreation|enjoy)', transcript.lower()))
        }
        
        impact_score = sum(functional_areas.values()) / len(functional_areas) * 10
        
        return {
            "impact_score": impact_score,
            "areas_assessed": functional_areas,
            "functional_assessment": "comprehensive" if impact_score >= 8 else "adequate" if impact_score >= 6 else "limited"
        }
    
    def _assess_risk_factors(self, transcript: str) -> Dict[str, Any]:
        """Assess risk factors and safety concerns"""
        
        risk_indicators = {
            "self_harm_risk": bool(re.search(r'(hurt myself|self harm|suicide|die)', transcript.lower())),
            "substance_use": bool(re.search(r'(alcohol|drug|substance|drinking)', transcript.lower())),
            "violence_risk": bool(re.search(r'(violent|hurt others|anger|rage)', transcript.lower())),
            "impulsivity": bool(re.search(r'(impulsive|reckless|dangerous|risky)', transcript.lower())),
            "social_support": bool(re.search(r'(support|family|friends|help)', transcript.lower()))
        }
        
        risk_score = sum(risk_indicators.values()) / len(risk_indicators) * 10
        
        return {
            "risk_score": risk_score,
            "risk_indicators": risk_indicators,
            "safety_assessment": "comprehensive" if risk_score >= 8 else "adequate" if risk_score >= 6 else "limited"
        }
    
    def _assess_client_strengths(self, transcript: str) -> Dict[str, Any]:
        """Assess client strengths and resources"""
        
        strength_indicators = {
            "coping_skills": bool(re.search(r'(cope|manage|handle|strategy)', transcript.lower())),
            "resilience": bool(re.search(r'(resilient|strong|overcome|survive)', transcript.lower())),
            "insight": bool(re.search(r'(understand|realize|aware|insight)', transcript.lower())),
            "motivation": bool(re.search(r'(motivated|want to|goal|change)', transcript.lower())),
            "social_support": bool(re.search(r'(support|family|friends|help)', transcript.lower()))
        }
        
        strength_score = sum(strength_indicators.values()) / len(strength_indicators) * 10
        
        return {
            "strength_score": strength_score,
            "strengths_identified": strength_indicators,
            "strength_assessment": "comprehensive" if strength_score >= 8 else "adequate" if strength_score >= 6 else "limited"
        }
    
    def _assess_goal_identification(self, transcript: str) -> Dict[str, Any]:
        """Assess treatment goal identification"""
        
        goal_elements = {
            "goals_discussed": bool(re.search(r'(goal|objective|want to|hope to)', transcript.lower())),
            "specific_targets": bool(re.search(r'(specific|particular|focus on)', transcript.lower())),
            "measurable_outcomes": bool(re.search(r'(measure|track|progress|improve)', transcript.lower())),
            "realistic_expectations": bool(re.search(r'(realistic|achievable|possible)', transcript.lower())),
            "client_motivation": bool(re.search(r'(motivated|committed|ready)', transcript.lower()))
        }
        
        goal_score = sum(goal_elements.values()) / len(goal_elements) * 10
        
        return {
            "goal_score": goal_score,
            "goal_elements": goal_elements,
            "goal_setting": "comprehensive" if goal_score >= 8 else "adequate" if goal_score >= 6 else "limited"
        }
    
    def _calculate_completeness_score(self, coverage_areas: Dict[str, Any]) -> float:
        """Calculate overall completeness score for structured assessment"""
        
        total_score = 0
        count = 0
        
        for area, data in coverage_areas.items():
            if isinstance(data, dict) and 'coverage_score' in data:
                total_score += data['coverage_score']
                count += 1
        
        return total_score / count if count > 0 else 0
    
    def _assess_engagement_level(self, transcript: str) -> Dict[str, Any]:
        """Assess client's engagement level"""
        
        engagement_indicators = {
            "response_length": len(transcript.split()) > 100,
            "emotional_expression": bool(re.search(r'(feel|emotion|excited|sad|happy)', transcript.lower())),
            "question_asking": bool(re.search(r'(what|how|why|can you|do you think)', transcript.lower())),
            "active_participation": bool(re.search(r'(yes|right|exactly|that\'s true)', transcript.lower())),
            "personal_sharing": bool(re.search(r'(i|me|my|personally)', transcript.lower()))
        }
        
        engagement_score = sum(engagement_indicators.values()) / len(engagement_indicators) * 10
        
        return {
            "engagement_score": engagement_score,
            "indicators": engagement_indicators,
            "engagement_level": "high" if engagement_score >= 7 else "moderate" if engagement_score >= 4 else "low"
        }
    
    def _assess_emotional_regulation(self, transcript: str) -> Dict[str, Any]:
        """Assess emotional regulation patterns"""
        
        regulation_indicators = {
            "emotion_awareness": bool(re.search(r'(feel|emotion|aware of|notice)', transcript.lower())),
            "regulation_strategies": bool(re.search(r'(cope|manage|control|regulate)', transcript.lower())),
            "emotional_stability": not bool(re.search(r'(overwhelmed|out of control|intense)', transcript.lower())),
            "adaptive_responses": bool(re.search(r'(healthy|positive|adaptive|helpful)', transcript.lower())),
            "emotional_expression": bool(re.search(r'(express|share|communicate|tell)', transcript.lower()))
        }
        
        regulation_score = sum(regulation_indicators.values()) / len(regulation_indicators) * 10
        
        return {
            "regulation_score": regulation_score,
            "indicators": regulation_indicators,
            "regulation_level": "good" if regulation_score >= 7 else "moderate" if regulation_score >= 4 else "poor"
        }
    
    def _assess_communication_style(self, transcript: str) -> Dict[str, Any]:
        """Assess communication patterns"""
        
        communication_indicators = {
            "clear_expression": bool(re.search(r'(clear|understand|explain|describe)', transcript.lower())),
            "assertiveness": bool(re.search(r'(i need|i want|i think|i believe)', transcript.lower())),
            "active_listening": bool(re.search(r'(i hear|understand|listening)', transcript.lower())),
            "nonverbal_awareness": bool(re.search(r'(body|gesture|tone|expression)', transcript.lower())),
            "empathy": bool(re.search(r'(understand|feel|empathy|compassion)', transcript.lower()))
        }
        
        communication_score = sum(communication_indicators.values()) / len(communication_indicators) * 10
        
        return {
            "communication_score": communication_score,
            "indicators": communication_indicators,
            "communication_style": "effective" if communication_score >= 7 else "adequate" if communication_score >= 4 else "limited"
        }
    
    def _assess_defensive_behaviors(self, transcript: str) -> Dict[str, Any]:
        """Assess defensive behaviors and resistance"""
        
        defensive_indicators = {
            "denial": bool(re.search(r'(not really|not true|don\'t think so)', transcript.lower())),
            "minimization": bool(re.search(r'(not that bad|minor|small|just)', transcript.lower())),
            "deflection": bool(re.search(r'(change topic|anyway|whatever|but)', transcript.lower())),
            "intellectualization": bool(re.search(r'(theory|research|generally|typically)', transcript.lower())),
            "resistance": bool(re.search(r'(don\'t want|won\'t|refuse|can\'t)', transcript.lower()))
        }
        
        defensive_score = sum(defensive_indicators.values()) / len(defensive_indicators) * 10
        
        return {
            "defensive_score": defensive_score,
            "indicators": defensive_indicators,
            "defensiveness_level": "high" if defensive_score >= 7 else "moderate" if defensive_score >= 4 else "low"
        }
    
    def _assess_therapeutic_alliance(self, transcript: str) -> Dict[str, Any]:
        """Assess therapeutic alliance quality"""
        
        alliance_indicators = {
            "collaboration": bool(re.search(r'(together|we|our|work with)', transcript.lower())),
            "trust": bool(re.search(r'(trust|safe|comfortable|open)', transcript.lower())),
            "agreement": bool(re.search(r'(agree|yes|right|exactly)', transcript.lower())),
            "respect": bool(re.search(r'(respect|appreciate|value)', transcript.lower())),
            "connection": bool(re.search(r'(connect|understand|relate|feel)', transcript.lower()))
        }
        
        alliance_score = sum(alliance_indicators.values()) / len(alliance_indicators) * 10
        
        return {
            "alliance_score": alliance_score,
            "indicators": alliance_indicators,
            "alliance_quality": "strong" if alliance_score >= 7 else "moderate" if alliance_score >= 4 else "weak"
        }
    
    def _assess_behavioral_consistency(self, transcript: str) -> Dict[str, Any]:
        """Assess consistency of behavioral patterns"""
        
        # This would require more sophisticated analysis in a real implementation
        # For now, we'll provide a basic assessment
        
        consistency_score = 7.0  # Default moderate consistency
        
        return {
            "consistency_score": consistency_score,
            "patterns_identified": ["engagement", "emotional_expression", "communication_style"],
            "consistency_level": "moderate"
        }
    
    def _rate_therapeutic_alliance(self, transcript: str) -> float:
        """Rate therapeutic alliance on 1-10 scale"""
        alliance_data = self._assess_therapeutic_alliance(transcript)
        return alliance_data["alliance_score"]
    
    def _rate_session_impact(self, transcript: str) -> float:
        """Rate session impact on 1-10 scale"""
        
        impact_indicators = {
            "insight_gained": bool(re.search(r'(realize|understand|see now|learned)', transcript.lower())),
            "emotional_processing": bool(re.search(r'(feel better|relief|process|work through)', transcript.lower())),
            "new_perspective": bool(re.search(r'(different|new way|perspective|angle)', transcript.lower())),
            "motivation_increased": bool(re.search(r'(motivated|encouraged|hopeful)', transcript.lower())),
            "skills_learned": bool(re.search(r'(skill|strategy|technique|tool)', transcript.lower()))
        }
        
        impact_score = sum(impact_indicators.values()) / len(impact_indicators) * 10
        return impact_score
    
    def _rate_client_engagement(self, transcript: str) -> float:
        """Rate client engagement on 1-10 scale"""
        engagement_data = self._assess_engagement_level(transcript)
        return engagement_data["engagement_score"]
    
    def _rate_therapist_competence(self, transcript: str) -> float:
        """Rate therapist competence on 1-10 scale"""
        
        competence_indicators = {
            "appropriate_techniques": bool(re.search(r'(reflect|summarize|explore|validate)', transcript.lower())),
            "professional_boundaries": not bool(re.search(r'(personal|my life|i do this)', transcript.lower())),
            "empathic_responses": bool(re.search(r'(understand|feel|hear|see)', transcript.lower())),
            "clinical_judgment": bool(re.search(r'(assess|evaluate|consider|important)', transcript.lower())),
            "ethical_practice": not bool(re.search(r'(inappropriate|boundary|ethical)', transcript.lower()))
        }
        
        competence_score = sum(competence_indicators.values()) / len(competence_indicators) * 10
        return competence_score
    
    def _rate_progress_indicators(self, transcript: str) -> float:
        """Rate progress indicators on 1-10 scale"""
        
        progress_indicators = {
            "symptom_improvement": bool(re.search(r'(better|improve|less|reduced)', transcript.lower())),
            "increased_insight": bool(re.search(r'(realize|understand|aware|see)', transcript.lower())),
            "behavioral_changes": bool(re.search(r'(change|different|new|started)', transcript.lower())),
            "emotional_regulation": bool(re.search(r'(manage|control|cope|regulate)', transcript.lower())),
            "functional_improvement": bool(re.search(r'(work|function|daily|better)', transcript.lower()))
        }
        
        progress_score = sum(progress_indicators.values()) / len(progress_indicators) * 10
        return progress_score
    
    def _identify_convergent_patterns(self, all_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify patterns that converge across multiple assessment methods"""
        
        convergent_patterns = {
            "therapeutic_alliance": [],
            "client_engagement": [],
            "emotional_processing": [],
            "behavioral_patterns": [],
            "treatment_progress": []
        }
        
        # This would require more sophisticated pattern matching
        # For now, we'll provide a basic structure
        
        for finding in all_findings:
            if "rapport_quality" in finding:
                convergent_patterns["therapeutic_alliance"].append(finding["rapport_quality"])
            if "engagement_level" in finding:
                convergent_patterns["client_engagement"].append(finding["engagement_level"])
        
        return convergent_patterns
    
    def _identify_divergent_patterns(self, all_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify patterns that diverge across assessment methods"""
        
        # This would require sophisticated analysis to identify actual divergences
        # For now, we'll return an empty list
        
        return []
    
    def _calculate_validity_strength(self, convergent_patterns: Dict[str, Any], divergent_patterns: List[Dict[str, Any]]) -> float:
        """Calculate overall validity strength based on convergent/divergent patterns"""
        
        convergent_count = sum(len(patterns) for patterns in convergent_patterns.values())
        divergent_count = len(divergent_patterns)
        
        if convergent_count + divergent_count == 0:
            return 5.0  # Default moderate validity
        
        validity_strength = (convergent_count / (convergent_count + divergent_count)) * 10
        return min(10, validity_strength)
    
    def _integrate_multiple_sources(self, additional_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate information from multiple sources"""
        
        # This would integrate information from family, other professionals, etc.
        # For now, we'll provide a basic structure
        
        return {
            "sources_integrated": list(additional_sources.keys()),
            "source_reliability": {source: self.assessment_sources.get(source, {}).get("reliability", 7.0) 
                                 for source in additional_sources.keys()},
            "integration_quality": "good"
        }
    
    def _assess_overall_reliability(self, methods_used: List[str]) -> Dict[str, Any]:
        """Assess overall reliability of the assessment"""
        
        reliability_scores = []
        for method in methods_used:
            if method in self.assessment_methods:
                reliability_scores.append(self.assessment_methods[method].reliability_score)
        
        if not reliability_scores:
            return {"overall_reliability": 5.0, "reliability_level": "moderate"}
        
        overall_reliability = sum(reliability_scores) / len(reliability_scores)
        reliability_level = "high" if overall_reliability >= 7.5 else "moderate" if overall_reliability >= 5.0 else "low"
        
        return {
            "overall_reliability": overall_reliability,
            "reliability_level": reliability_level,
            "method_reliabilities": {method: self.assessment_methods[method].reliability_score 
                                   for method in methods_used if method in self.assessment_methods}
        }
    
    def _assess_validity_indicators(self, transcript: str) -> Dict[str, Any]:
        """Assess validity indicators for the assessment"""
        
        validity_indicators = {
            "content_validity": self._assess_content_validity(transcript),
            "construct_validity": self._assess_construct_validity(transcript),
            "criterion_validity": self._assess_criterion_validity(transcript),
            "face_validity": self._assess_face_validity(transcript)
        }
        
        overall_validity = sum(validity_indicators.values()) / len(validity_indicators)
        validity_level = "high" if overall_validity >= 7.5 else "moderate" if overall_validity >= 5.0 else "low"
        
        return {
            "overall_validity": overall_validity,
            "validity_level": validity_level,
            "validity_indicators": validity_indicators
        }
    
    def _assess_content_validity(self, transcript: str) -> float:
        """Assess content validity of the assessment"""
        
        # Check if assessment covers relevant therapeutic content
        content_areas = {
            "presenting_problem": bool(re.search(r'(problem|issue|concern)', transcript.lower())),
            "emotional_content": bool(re.search(r'(feel|emotion|mood)', transcript.lower())),
            "behavioral_content": bool(re.search(r'(do|behave|action)', transcript.lower())),
            "cognitive_content": bool(re.search(r'(think|thought|believe)', transcript.lower())),
            "interpersonal_content": bool(re.search(r'(relationship|social|people)', transcript.lower()))
        }
        
        content_validity = sum(content_areas.values()) / len(content_areas) * 10
        return content_validity
    
    def _assess_construct_validity(self, transcript: str) -> float:
        """Assess construct validity of the assessment"""
        
        # Check if assessment measures intended therapeutic constructs
        construct_indicators = {
            "therapeutic_alliance": bool(re.search(r'(alliance|rapport|connection)', transcript.lower())),
            "symptom_assessment": bool(re.search(r'(symptom|problem|difficulty)', transcript.lower())),
            "functional_assessment": bool(re.search(r'(function|daily|work|social)', transcript.lower())),
            "progress_assessment": bool(re.search(r'(progress|change|improvement)', transcript.lower())),
            "insight_assessment": bool(re.search(r'(insight|understand|realize)', transcript.lower()))
        }
        
        construct_validity = sum(construct_indicators.values()) / len(construct_indicators) * 10
        return construct_validity
    
    def _assess_criterion_validity(self, transcript: str) -> float:
        """Assess criterion validity of the assessment"""
        
        # This would require external criteria for validation
        # For now, we'll provide a moderate score
        return 7.0
    
    def _assess_face_validity(self, transcript: str) -> float:
        """Assess face validity of the assessment"""
        
        # Check if assessment appears to measure what it claims to measure
        face_validity_indicators = {
            "therapeutic_content": bool(re.search(r'(therapy|counseling|treatment)', transcript.lower())),
            "clinical_language": bool(re.search(r'(assess|evaluate|clinical|therapeutic)', transcript.lower())),
            "professional_interaction": bool(re.search(r'(professional|counselor|therapist)', transcript.lower())),
            "therapeutic_goals": bool(re.search(r'(goal|objective|outcome)', transcript.lower()))
        }
        
        face_validity = sum(face_validity_indicators.values()) / len(face_validity_indicators) * 10
        return face_validity
    
    def _generate_clinical_recommendations(self, convergent_analysis: Dict[str, Any]) -> List[str]:
        """Generate clinical recommendations based on assessment findings"""
        
        recommendations = []
        
        # Base recommendations on convergent findings
        validity_strength = convergent_analysis.get("validity_strength", 5.0)
        
        if validity_strength >= 8.0:
            recommendations.append("Assessment findings show strong convergent validity - high confidence in results")
            recommendations.append("Continue with current therapeutic approach based on reliable assessment data")
        elif validity_strength >= 6.0:
            recommendations.append("Assessment findings show moderate convergent validity - reasonable confidence in results")
            recommendations.append("Consider additional assessment methods to strengthen validity")
        else:
            recommendations.append("Assessment findings show limited convergent validity - use caution in interpretation")
            recommendations.append("Recommend comprehensive re-assessment using multiple methods and sources")
        
        # Add method-specific recommendations
        recommendations.append("Consider integrating multiple assessment sources for comprehensive evaluation")
        recommendations.append("Regular reassessment recommended to track therapeutic progress")
        recommendations.append("Document assessment limitations and reliability considerations")
        
        return recommendations
    
    def _identify_assessment_limitations(self, methods_used: List[str]) -> List[str]:
        """Identify limitations of the assessment approach"""
        
        limitations = []
        
        # General limitations
        limitations.append("Assessment based on single session transcript - limited temporal scope")
        limitations.append("Lack of collateral sources limits comprehensive evaluation")
        limitations.append("Observer bias may influence interpretation of findings")
        
        # Method-specific limitations
        for method in methods_used:
            if method in self.assessment_methods:
                method_obj = self.assessment_methods[method]
                limitations.extend([f"{method_obj.name}: {weakness}" for weakness in method_obj.weaknesses[:2]])
        
        return limitations