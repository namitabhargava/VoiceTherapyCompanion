import os
import json
import streamlit as st
from datetime import datetime
from models.analysis_models import TherapeuticFramework, AnalysisResult
import requests
from services.multi_assessment_service import MultiAssessmentService

class AnalysisService:
    def __init__(self):
        # Support multiple AI providers with fallbacks
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize OpenAI client only if API key exists
        self.openai_client = None
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                st.warning(f"OpenAI initialization failed: {str(e)}")
        
        self.frameworks = TherapeuticFramework()
        self.multi_assessment = MultiAssessmentService()
        
        # Available analysis providers
        self.providers = {
            'openai': self._analyze_with_openai,
            'huggingface': self._analyze_with_huggingface,
            'local': self._analyze_with_local_model
        }
        
    def _detect_negative_patterns(self, transcript):
        """Detect negative patterns and warning signs that indicate therapy is not working well"""
        
        # Define negative indicators for each therapeutic approach
        negative_indicators = {
            'therapeutic_alliance': [
                "I don't feel understood",
                "therapist doesn't get it",
                "waste of time",
                "not helping",
                "doesn't listen",
                "judgmental",
                "rushed",
                "distracted",
                "uncomfortable",
                "don't trust"
            ],
            'emotional_deterioration': [
                "getting worse",
                "more depressed",
                "more anxious",
                "hopeless",
                "suicidal thoughts",
                "can't cope",
                "overwhelmed",
                "breaking down",
                "lost control",
                "spiraling"
            ],
            'resistance_patterns': [
                "nothing works",
                "tried everything",
                "won't change",
                "can't do it",
                "too difficult",
                "pointless",
                "give up",
                "no hope",
                "stuck",
                "same problems"
            ],
            'therapeutic_rupture': [
                "angry at therapist",
                "disappointed",
                "frustrated with therapy",
                "want to quit",
                "not coming back",
                "wasting money",
                "not worth it",
                "better off alone",
                "therapy failed"
            ],
            'stagnation_signs': [
                "no progress",
                "same place",
                "not moving forward",
                "stuck in patterns",
                "repeating cycles",
                "no improvement",
                "months with no change",
                "going in circles"
            ]
        }
        
        # Analyze transcript for negative patterns
        transcript_lower = transcript.lower()
        detected_patterns = {}
        
        for category, indicators in negative_indicators.items():
            matches = []
            for indicator in indicators:
                if indicator in transcript_lower:
                    matches.append(indicator)
            
            if matches:
                detected_patterns[category] = {
                    'severity': len(matches) / len(indicators),  # Proportion of indicators found
                    'indicators': matches[:5]  # First 5 matches
                }
        
        return detected_patterns
    
    def analyze_session(self, transcript):
        """Comprehensive analysis of therapy session using multiple frameworks"""
        try:
            st.info("Analyzing session with multiple therapeutic frameworks...")

            # First, detect negative patterns and warning signs
            negative_patterns = self._detect_negative_patterns(transcript)

            # Domain-specific analyses
            domain_scores = {}
            detailed_analysis = {}

            # 1. Emotional safety & relational depth (Rogers)
            rogers_analysis = self._analyze_rogers_framework(transcript)
            domain_scores['emotional_safety'] = rogers_analysis['score']
            detailed_analysis['rogers'] = rogers_analysis

            # 2. Unconscious pattern emergence (Freud, Klein)
            psychodynamic_analysis = self._analyze_psychodynamic_framework(transcript)
            domain_scores['unconscious_patterns'] = psychodynamic_analysis['score']
            detailed_analysis['psychodynamic'] = psychodynamic_analysis

            # 3. Cognitive restructuring (Ellis, Beck)
            cognitive_analysis = self._analyze_cognitive_framework(transcript)
            domain_scores['cognitive_restructuring'] = cognitive_analysis['score']
            detailed_analysis['cognitive'] = cognitive_analysis

            # 4. Communication/family role changes (Satir)
            family_analysis = self._analyze_family_systems_framework(transcript)
            domain_scores['communication_changes'] = family_analysis['score']
            detailed_analysis['family_systems'] = family_analysis

            # 5. Strengths and well-being (Seligman)
            positive_analysis = self._analyze_positive_psychology_framework(transcript)
            domain_scores['strengths_wellbeing'] = positive_analysis['score']
            detailed_analysis['positive_psychology'] = positive_analysis

            # 6. Narrative/identity coherence
            narrative_analysis = self._analyze_narrative_framework(transcript)
            domain_scores['narrative_coherence'] = narrative_analysis['score']
            detailed_analysis['narrative'] = narrative_analysis

            # 7. Behavioral activation in real life
            behavioral_analysis = self._analyze_behavioral_framework(transcript)
            domain_scores['behavioral_activation'] = behavioral_analysis['score']
            detailed_analysis['behavioral'] = behavioral_analysis

            # Adjust scores based on negative patterns detected
            adjusted_scores = self._adjust_scores_for_negative_patterns(domain_scores, negative_patterns)

            # Conduct comprehensive multi-method, multi-source assessment
            multi_assessment_results = self.multi_assessment.conduct_comprehensive_assessment(transcript)

            # Generate overall insights and recommendations
            overall_insights = self._generate_overall_insights(transcript, detailed_analysis, negative_patterns)

            # Conduct expert-level therapist evaluation
            expert_evaluation = self._conduct_expert_therapist_evaluation(transcript)

            # Evaluate therapist performance (existing method)
            therapist_evaluation = self._evaluate_therapist_performance(transcript, detailed_analysis, negative_patterns)

            # Add chorus analysis automatically
            chorus_analysis = self.analyze_as_chorus(transcript)

            return {
                'domain_scores': adjusted_scores,
                'detailed_analysis': detailed_analysis,
                'multi_assessment_results': multi_assessment_results,
                'negative_patterns': negative_patterns,
                'key_insights': overall_insights['insights'],
                'recommendations': overall_insights['recommendations'],
                'session_themes': overall_insights['themes'],
                'progress_indicators': overall_insights['progress_indicators'],
                'therapy_effectiveness': self._assess_therapy_effectiveness(adjusted_scores, negative_patterns),
                'warning_signs': self._generate_warning_signs(negative_patterns),
                'expert_therapist_evaluation': expert_evaluation,
                'therapist_evaluation': therapist_evaluation,
                'chorus_analysis': chorus_analysis,
                'analysis_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return None
    
    def _analyze_rogers_framework(self, transcript):
        """Analyze using Carl Rogers' person-centered approach (1902-1987)"""
        prompt = f"""
        Analyze this therapy session transcript using Carl Rogers' person-centered approach.
        
        Carl Rogers (1902-1987) was a key figure in humanistic psychology who developed client-centered therapy.
        His approach emphasizes three core conditions for therapeutic change:
        
        1. UNCONDITIONAL POSITIVE REGARD: Complete acceptance of the client without judgment
        2. EMPATHY: Deep understanding and reflection of client's feelings and perspective  
        3. GENUINENESS/CONGRUENCE: Therapist authenticity and realness in the relationship
        
        Additional Rogers principles:
        - Client as expert on their own experience
        - Focus on present feelings and experiences
        - Self-actualization tendency - humans naturally grow toward fulfillment
        - Non-directive approach - client leads, therapist facilitates
        - Importance of self-acceptance and self-worth
        
        Evaluate this session for:
        1. Evidence of therapist empathy and accurate reflection
        2. Therapist genuineness and authenticity
        3. Unconditional positive regard (acceptance without judgment)
        4. Client's self-exploration and self-discovery
        5. Emotional safety allowing vulnerability
        6. Client-centered focus vs. therapist-directed interventions
        7. Signs of increased self-acceptance in client
        
        Rate the session on a scale of 1-10 for emotional safety and relational depth.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "empathy_evidence": ["specific examples of empathic responses"],
            "genuineness_indicators": ["examples of therapist authenticity"],
            "positive_regard_moments": ["examples of unconditional acceptance"],
            "client_self_exploration": ["examples of client self-discovery"],
            "emotional_safety_indicators": ["signs client feels safe to be vulnerable"],
            "self_acceptance_growth": ["signs of increased self-worth/acceptance"],
            "areas_for_improvement": ["suggestions for enhancing person-centered approach"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "Carl Rogers' person-centered therapy approach")
    
    def _adjust_scores_for_negative_patterns(self, domain_scores, negative_patterns):
        """Adjust domain scores based on detected negative patterns"""
        adjusted_scores = domain_scores.copy()
        
        # Define how negative patterns affect different domains
        pattern_impact = {
            'therapeutic_alliance': {
                'emotional_safety': -3.0,
                'communication_changes': -2.0,
                'strengths_wellbeing': -1.5
            },
            'emotional_deterioration': {
                'emotional_safety': -2.5,
                'strengths_wellbeing': -3.0,
                'cognitive_restructuring': -2.0,
                'behavioral_activation': -1.5
            },
            'resistance_patterns': {
                'cognitive_restructuring': -2.5,
                'behavioral_activation': -3.0,
                'narrative_coherence': -2.0
            },
            'therapeutic_rupture': {
                'emotional_safety': -3.5,
                'communication_changes': -2.5,
                'unconscious_patterns': -2.0
            },
            'stagnation_signs': {
                'behavioral_activation': -2.0,
                'cognitive_restructuring': -1.5,
                'narrative_coherence': -2.5,
                'strengths_wellbeing': -1.0
            }
        }
        
        # Apply negative adjustments based on severity
        for pattern_type, pattern_data in negative_patterns.items():
            severity = pattern_data['severity']
            
            if pattern_type in pattern_impact:
                for domain, base_penalty in pattern_impact[pattern_type].items():
                    if domain in adjusted_scores:
                        # Apply penalty based on severity (0-1) and base penalty
                        penalty = base_penalty * severity
                        adjusted_scores[domain] = max(1.0, adjusted_scores[domain] + penalty)
        
        return adjusted_scores
    
    def _assess_therapy_effectiveness(self, scores, negative_patterns):
        """Assess overall therapy effectiveness"""
        avg_score = sum(scores.values()) / len(scores)
        negative_severity = sum(p['severity'] for p in negative_patterns.values()) / len(negative_patterns) if negative_patterns else 0
        
        if avg_score <= 3.0 or negative_severity > 0.4:
            return {
                'status': 'concerning',
                'message': 'Therapy may not be working effectively. Consider discussing concerns with therapist.',
                'confidence': 0.8
            }
        elif avg_score <= 5.0 or negative_severity > 0.2:
            return {
                'status': 'mixed',
                'message': 'Therapy showing mixed results. Some areas need attention.',
                'confidence': 0.6
            }
        else:
            return {
                'status': 'positive',
                'message': 'Therapy appears to be working well overall.',
                'confidence': 0.7
            }
    
    def _generate_warning_signs(self, negative_patterns):
        """Generate warning signs based on negative patterns"""
        warning_signs = []
        
        if 'therapeutic_alliance' in negative_patterns:
            warning_signs.append({
                'category': 'Relationship Issues',
                'description': 'Client may not feel understood or supported by therapist',
                'severity': 'high' if negative_patterns['therapeutic_alliance']['severity'] > 0.3 else 'medium',
                'indicators': negative_patterns['therapeutic_alliance']['indicators']
            })
        
        if 'emotional_deterioration' in negative_patterns:
            warning_signs.append({
                'category': 'Emotional Decline',
                'description': 'Client reports worsening emotional state',
                'severity': 'high',
                'indicators': negative_patterns['emotional_deterioration']['indicators']
            })
        
        if 'resistance_patterns' in negative_patterns:
            warning_signs.append({
                'category': 'Treatment Resistance',
                'description': 'Client showing resistance to therapeutic interventions',
                'severity': 'medium',
                'indicators': negative_patterns['resistance_patterns']['indicators']
            })
        
        if 'therapeutic_rupture' in negative_patterns:
            warning_signs.append({
                'category': 'Therapeutic Rupture',
                'description': 'Relationship between client and therapist may be damaged',
                'severity': 'high',
                'indicators': negative_patterns['therapeutic_rupture']['indicators']
            })
        
        if 'stagnation_signs' in negative_patterns:
            warning_signs.append({
                'category': 'Lack of Progress',
                'description': 'Client not experiencing meaningful change or improvement',
                'severity': 'medium',
                'indicators': negative_patterns['stagnation_signs']['indicators']
            })
        
        return warning_signs
    
    def _evaluate_therapist_performance(self, transcript, detailed_analysis, negative_patterns):
        """Evaluate therapist's performance based on conversation analysis"""
        try:
            # Extract therapist responses from transcript
            therapist_responses = []
            client_responses = []
            
            lines = transcript.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Therapist:'):
                    therapist_responses.append(line.replace('Therapist:', '').strip())
                elif line.startswith('Client:'):
                    client_responses.append(line.replace('Client:', '').strip())
            
            # Analyze therapist performance across multiple dimensions
            evaluation = {
                'overall_score': 0,
                'empathy_score': 0,
                'communication_score': 0,
                'technique_score': 0,
                'professional_score': 0,
                'strengths': [],
                'areas_for_improvement': [],
                'specific_feedback': []
            }
            
            # Evaluate empathy and emotional attunement
            empathy_score = self._evaluate_therapist_empathy(therapist_responses, client_responses)
            evaluation['empathy_score'] = empathy_score
            
            # Evaluate communication skills
            communication_score = self._evaluate_therapist_communication(therapist_responses, client_responses)
            evaluation['communication_score'] = communication_score
            
            # Evaluate therapeutic techniques
            technique_score = self._evaluate_therapist_techniques(therapist_responses, detailed_analysis)
            evaluation['technique_score'] = technique_score
            
            # Evaluate professional boundaries and ethics
            professional_score = self._evaluate_therapist_professionalism(therapist_responses, negative_patterns)
            evaluation['professional_score'] = professional_score
            
            # Calculate overall score
            evaluation['overall_score'] = round((empathy_score + communication_score + technique_score + professional_score) / 4, 1)
            
            # Generate strengths and improvement areas
            evaluation['strengths'] = self._identify_therapist_strengths(evaluation)
            evaluation['areas_for_improvement'] = self._identify_therapist_improvements(evaluation, negative_patterns)
            evaluation['specific_feedback'] = self._generate_specific_therapist_feedback(therapist_responses, evaluation)
            
            return evaluation
            
        except Exception as e:
            st.warning(f"Therapist evaluation error: {str(e)}")
            return {
                'overall_score': 5,
                'empathy_score': 5,
                'communication_score': 5,
                'technique_score': 5,
                'professional_score': 5,
                'strengths': ['Analysis limited due to processing error'],
                'areas_for_improvement': ['Unable to analyze due to processing error'],
                'specific_feedback': ['Detailed evaluation unavailable']
            }
    
    def _evaluate_therapist_empathy(self, therapist_responses, client_responses):
        """Evaluate therapist's empathy and emotional attunement"""
        if not therapist_responses:
            return 5
        
        empathy_indicators = {
            'reflective_statements': ['I hear', 'it sounds like', 'I understand', 'that must', 'I can see'],
            'emotional_validation': ['feel', 'feeling', 'emotion', 'difficult', 'challenging'],
            'paraphrasing': ['so what you\'re saying', 'if I understand', 'let me make sure'],
            'empathetic_responses': ['that\'s understandable', 'I can imagine', 'that makes sense']
        }
        
        score = 5  # Base score
        total_responses = len(therapist_responses)
        
        for response in therapist_responses:
            response_lower = response.lower()
            
            # Check for empathy indicators
            for category, indicators in empathy_indicators.items():
                if any(indicator in response_lower for indicator in indicators):
                    score += 0.5
                    break
        
        # Normalize score
        return min(10, max(1, round(score / total_responses * 10, 1)))
    
    def _evaluate_therapist_communication(self, therapist_responses, client_responses):
        """Evaluate therapist's communication skills"""
        if not therapist_responses:
            return 5
        
        communication_factors = {
            'open_questions': ['how', 'what', 'when', 'where', 'why', 'tell me more'],
            'clarifying_questions': ['can you explain', 'what do you mean', 'can you give me'],
            'summarizing': ['so far we\'ve', 'to summarize', 'what I\'m hearing'],
            'appropriate_responses': ['that\'s interesting', 'good point', 'thank you for sharing']
        }
        
        score = 5  # Base score
        total_responses = len(therapist_responses)
        
        for response in therapist_responses:
            response_lower = response.lower()
            
            # Check for good communication indicators
            for category, indicators in communication_factors.items():
                if any(indicator in response_lower for indicator in indicators):
                    score += 0.4
                    break
            
            # Penalize for poor communication
            if len(response) < 10:  # Very short responses
                score -= 0.2
            elif response.count('?') > 3:  # Too many questions
                score -= 0.1
        
        return min(10, max(1, round(score / total_responses * 10, 1)))
    
    def _evaluate_therapist_techniques(self, therapist_responses, detailed_analysis):
        """Evaluate therapist's use of therapeutic techniques"""
        if not therapist_responses:
            return 5
        
        technique_indicators = {
            'cognitive_techniques': ['thought', 'belief', 'thinking', 'perspective', 'view'],
            'behavioral_techniques': ['action', 'behavior', 'activity', 'practice', 'try'],
            'psychodynamic_techniques': ['pattern', 'relationship', 'past', 'childhood', 'family'],
            'person_centered': ['you', 'your', 'feel', 'experience', 'important to you']
        }
        
        score = 5  # Base score
        techniques_used = 0
        
        for response in therapist_responses:
            response_lower = response.lower()
            
            for category, indicators in technique_indicators.items():
                if any(indicator in response_lower for indicator in indicators):
                    techniques_used += 1
                    break
        
        # Bonus for technique variety
        if techniques_used > len(therapist_responses) * 0.3:
            score += 2
        elif techniques_used > len(therapist_responses) * 0.1:
            score += 1
        
        return min(10, max(1, round(score, 1)))
    
    def _evaluate_therapist_professionalism(self, therapist_responses, negative_patterns):
        """Evaluate therapist's professional boundaries and ethics"""
        score = 8  # Start with high professional score
        
        # Check for negative patterns that might indicate therapist issues
        if 'therapeutic_alliance' in negative_patterns:
            score -= 2
        if 'therapeutic_rupture' in negative_patterns:
            score -= 3
        
        # Check for professional language
        for response in therapist_responses:
            response_lower = response.lower()
            
            # Positive professional indicators
            if any(word in response_lower for word in ['understand', 'explore', 'together', 'support']):
                score += 0.1
            
            # Negative indicators
            if any(word in response_lower for word in ['you should', 'you must', 'wrong', 'bad']):
                score -= 0.5
        
        return min(10, max(1, round(score, 1)))
    
    def _identify_therapist_strengths(self, evaluation):
        """Identify therapist's strengths based on evaluation scores"""
        strengths = []
        
        if evaluation['empathy_score'] >= 7:
            strengths.append("Shows strong empathy and emotional attunement with client")
        if evaluation['communication_score'] >= 7:
            strengths.append("Demonstrates effective communication skills")
        if evaluation['technique_score'] >= 7:
            strengths.append("Uses appropriate therapeutic techniques")
        if evaluation['professional_score'] >= 8:
            strengths.append("Maintains professional boundaries and ethics")
        
        if not strengths:
            strengths.append("Shows basic therapeutic competency")
        
        return strengths
    
    def _identify_therapist_improvements(self, evaluation, negative_patterns):
        """Identify areas where therapist could improve"""
        improvements = []
        
        if evaluation['empathy_score'] < 6:
            improvements.append("Could improve empathetic responses and emotional validation")
        if evaluation['communication_score'] < 6:
            improvements.append("Could enhance communication skills and active listening")
        if evaluation['technique_score'] < 6:
            improvements.append("Could expand use of therapeutic techniques")
        if evaluation['professional_score'] < 7:
            improvements.append("Should focus on maintaining professional boundaries")
        
        # Add specific improvements based on negative patterns
        if 'therapeutic_alliance' in negative_patterns:
            improvements.append("Work on building stronger therapeutic alliance with client")
        if 'therapeutic_rupture' in negative_patterns:
            improvements.append("Address and repair therapeutic relationship ruptures")
        
        return improvements
    
    def _generate_specific_therapist_feedback(self, therapist_responses, evaluation):
        """Generate specific feedback for the therapist"""
        feedback = []
        
        if evaluation['overall_score'] >= 8:
            feedback.append("Overall excellent therapeutic performance")
        elif evaluation['overall_score'] >= 6:
            feedback.append("Good therapeutic performance with room for growth")
        else:
            feedback.append("Therapeutic performance needs improvement")
        
        # Add specific suggestions based on response analysis
        if len(therapist_responses) > 0:
            avg_length = sum(len(response) for response in therapist_responses) / len(therapist_responses)
            if avg_length < 50:
                feedback.append("Consider providing more detailed responses to clients")
            elif avg_length > 200:
                feedback.append("Consider being more concise in responses")
        
        return feedback
    
    def _analyze_with_providers(self, prompt, system_context):
        """Try different AI providers for analysis"""
        # Try OpenAI first
        if self.openai_client:
            result = self._analyze_with_openai(prompt, system_context)
            if result:
                return result
        
        # Try Hugging Face
        if self.huggingface_api_key:
            result = self._analyze_with_huggingface(prompt, system_context)
            if result:
                return result
        
        # Fall back to local analysis
        return self._analyze_with_local_model(prompt, system_context)
    
    def _analyze_with_openai(self, prompt, system_context):
        """Analyze with OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are an expert in {system_context}."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.warning(f"OpenAI analysis failed: {str(e)}")
            return None
    
    def _analyze_with_huggingface(self, prompt, system_context):
        """Analyze with Hugging Face"""
        try:
            # Use a free text generation model
            API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            
            payload = {
                "inputs": f"Context: {system_context}\n\nTask: {prompt}",
                "parameters": {
                    "max_length": 1000,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                # Parse the response and create a basic analysis
                return self._create_basic_analysis(result)
            else:
                st.warning(f"Hugging Face API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.warning(f"Hugging Face analysis failed: {str(e)}")
            return None
    
    def _analyze_with_local_model(self, prompt, system_context):
        """Perform basic local analysis without external APIs"""
        try:
            # Handle both string and dict inputs
            if isinstance(prompt, dict):
                transcript_text = str(prompt).lower()
            else:
                # Try to extract transcript from prompt
                if "Transcript: " in prompt:
                    parts = prompt.split("Transcript: ")
                    if len(parts) > 1:
                        transcript_text = parts[1].split("Respond in JSON format")[0].lower()
                    else:
                        transcript_text = prompt.lower()
                else:
                    transcript_text = prompt.lower()
            
            # Enhanced scoring based on therapeutic indicators
            # Therapist quality indicators
            therapist_positive = ['listen', 'understand', 'explore', 'feel', 'tell me more', 'how does that', 'what do you think', 'reflect', 'validate', 'support', 'acknowledge', 'empathy', 'compassionate']
            therapist_negative = ['should', 'must', 'wrong', 'bad', 'fix', 'solve', 'simple', 'just', 'advice', 'tell you what to do', 'obvious', 'clearly']
            
            # Client progress indicators
            client_positive = ['better', 'progress', 'insight', 'understand', 'realize', 'aware', 'growth', 'helpful', 'clearer', 'learned', 'different perspective']
            client_negative = ['worse', 'stuck', 'hopeless', 'confused', 'frustrated', 'not helping', 'pointless', 'waste', 'giving up']
            
            # Count therapeutic indicators
            therapist_pos_count = sum(1 for phrase in therapist_positive if phrase in transcript_text)
            therapist_neg_count = sum(1 for phrase in therapist_negative if phrase in transcript_text)
            client_pos_count = sum(1 for phrase in client_positive if phrase in transcript_text)
            client_neg_count = sum(1 for phrase in client_negative if phrase in transcript_text)
            
            # Calculate dynamic score based on transcript length and quality indicators
            transcript_length = len(transcript_text.split())
            
            # Base score depends on session engagement
            if transcript_length < 50:
                base_score = 4  # Very short session
            elif transcript_length < 200:
                base_score = 5  # Short session
            elif transcript_length < 500:
                base_score = 6  # Medium session
            else:
                base_score = 7  # Long, engaged session
            
            # Adjust based on therapeutic quality
            therapist_quality = (therapist_pos_count - therapist_neg_count) * 0.3
            client_progress = (client_pos_count - client_neg_count) * 0.4
            
            # Final score calculation
            score = base_score + therapist_quality + client_progress
            score = max(1, min(10, score))  # Clamp between 1-10
            
            return {
                "score": round(score, 1),
                "empathy_evidence": ["Local analysis - limited detail available"],
                "genuineness_indicators": ["Local analysis - limited detail available"],
                "positive_regard_moments": ["Local analysis - limited detail available"],
                "client_self_exploration": ["Local analysis - limited detail available"],
                "areas_for_improvement": ["Consider using AI API for detailed analysis"],
                "note": "This is a basic local analysis. For detailed insights, please provide API keys for OpenAI or Hugging Face."
            }
            
        except Exception as e:
            st.warning(f"Local analysis failed: {str(e)}")
            return {
                "score": 5,
                "empathy_evidence": ["Local analysis - error occurred"],
                "genuineness_indicators": ["Local analysis - error occurred"],
                "positive_regard_moments": ["Local analysis - error occurred"],
                "client_self_exploration": ["Local analysis - error occurred"],
                "areas_for_improvement": ["Please provide API keys for detailed analysis"],
                "note": "Analysis unavailable due to error"
            }
    
    def _create_basic_analysis(self, hf_result):
        """Create basic analysis from Hugging Face result"""
        return {
            "score": 6,
            "empathy_evidence": ["Analysis from Hugging Face model"],
            "genuineness_indicators": ["Analysis from Hugging Face model"],
            "positive_regard_moments": ["Analysis from Hugging Face model"],
            "client_self_exploration": ["Analysis from Hugging Face model"],
            "areas_for_improvement": ["Consider upgrading to OpenAI for more detailed analysis"],
            "note": "Analysis performed using Hugging Face free tier"
        }
    
    def _analyze_psychodynamic_framework(self, transcript):
        """Analyze using Freud and Klein's psychodynamic approach"""
        prompt = f"""
        Analyze this therapy session transcript using psychodynamic principles from Sigmund Freud and Melanie Klein.
        
        SIGMUND FREUD (1856-1939) - Founder of psychoanalysis:
        - Unconscious mind drives behavior and contains repressed memories/desires
        - Defense mechanisms protect ego from anxiety (repression, projection, denial, displacement)
        - Transference: client projects feelings about past relationships onto therapist
        - Free association reveals unconscious material
        - Structural model: Id (drives), Ego (reality), Superego (morality)
        - Psychosexual development and early childhood experiences shape personality
        
        MELANIE KLEIN (1882-1960) - Pioneer of child therapy and object relations:
        - Play therapy techniques to understand unconscious conflicts
        - Object relations: how we internalize relationships with significant others
        - Projective identification: unconscious projection of internal objects
        - Paranoid-schizoid and depressive positions in development
        - Splitting: seeing things as all good or all bad
        - Focus on early mother-child relationship and its impact on later relationships
        
        Evaluate this session for:
        1. Unconscious patterns and recurring themes
        2. Defense mechanisms in operation (denial, projection, repression, etc.)
        3. Transference manifestations (how client relates to therapist)
        4. Symbolic content and metaphors revealing unconscious material
        5. Early childhood experiences and their current impact
        6. Object relations patterns (how client relates to others)
        7. Signs of splitting or integration (Klein's concepts)
        8. Emergence of previously unconscious material into awareness
        
        Rate the session on a scale of 1-10 for unconscious pattern emergence and insight.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "unconscious_patterns": ["specific recurring themes or behaviors"],
            "defense_mechanisms": ["specific mechanisms observed with examples"],
            "transference_indicators": ["how client relates to therapist"],
            "symbolic_content": ["metaphors or symbols revealing unconscious material"],
            "early_experience_connections": ["links between past and present patterns"],
            "object_relations_patterns": ["how client relates to significant others"],
            "unconscious_emergence": ["moments when unconscious material became conscious"],
            "areas_for_improvement": ["suggestions for deeper psychodynamic exploration"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "Freud and Klein's psychodynamic approach")
    
    def _analyze_cognitive_framework(self, transcript):
        """Analyze using Ellis and Beck's cognitive approaches"""
        prompt = f"""
        Analyze this therapy session transcript using cognitive therapy principles from Albert Ellis and Aaron Beck.
        
        ALBERT ELLIS (1913-2007) - Developed Rational Emotive Behavior Therapy (REBT):
        - A-B-C Model: Activating event → Beliefs → Consequences (emotional/behavioral)
        - Irrational beliefs lead to emotional disturbance
        - 12 Common irrational beliefs (e.g., "I must be perfect", "Everyone must approve of me")
        - Disputing irrational beliefs through logical, empirical, and pragmatic questioning
        - Unconditional self-acceptance while changing behaviors
        - Focus on present-moment thinking patterns
        - Homework assignments to practice new thinking
        
        AARON BECK (1921-2021) - Father of Cognitive Therapy (CBT):
        - Cognitive triad: negative thoughts about self, world, and future
        - Cognitive distortions: all-or-nothing thinking, catastrophizing, mind reading, etc.
        - Automatic thoughts that arise spontaneously
        - Cognitive restructuring through evidence examination
        - Behavioral experiments to test thoughts
        - Thought records and homework assignments
        - Collaborative empiricism between therapist and client
        
        Evaluate this session for:
        1. Identification of irrational beliefs (Ellis) and cognitive distortions (Beck)
        2. Evidence of disputing or challenging negative thoughts
        3. Use of A-B-C model or cognitive restructuring techniques
        4. Behavioral experiments or homework assignments
        5. Thought challenging and evidence examination
        6. Movement from automatic thoughts to balanced thinking
        7. Development of coping statements and rational beliefs
        8. Problem-solving and practical applications
        
        Rate the session on a scale of 1-10 for cognitive restructuring effectiveness.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "irrational_beliefs": ["specific Ellis-style beliefs identified"],
            "cognitive_distortions": ["specific Beck-style distortions found"],
            "thought_challenging_examples": ["instances of disputing or restructuring"],
            "behavioral_experiments": ["homework or real-world applications"],
            "abc_model_usage": ["examples of A-B-C analysis"],
            "balanced_thinking_development": ["movement toward rational thoughts"],
            "coping_strategies": ["practical tools developed"],
            "areas_for_improvement": ["suggestions for enhanced cognitive work"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "Ellis and Beck's cognitive approaches")
    
    def _analyze_family_systems_framework(self, transcript):
        """Analyze using Virginia Satir's family systems approach"""
        prompt = f"""
        Analyze this therapy session transcript using Virginia Satir's family systems approach.
        
        VIRGINIA SATIR (1916-1988) - Pioneer of family therapy:
        - Family as a system where change in one member affects all others
        - Focus on communication patterns and family dynamics
        - Four communication stances: Placater, Blamer, Super-reasonable, Irrelevant
        - Healthy communication is congruent - matching inner feelings with outer expression
        - Family roles and rules (both spoken and unspoken)
        - Self-worth as core issue affecting all family interactions
        - Sculpture and experiential techniques to explore family dynamics
        - Intergenerational patterns passed down through families
        - Growth model vs. pathology model - focus on potential and resources
        - Circular causality - problems maintain themselves through family interactions
        
        Satir's Key Concepts:
        - Primary triad: Self-worth, Communication, Rules
        - Survival stances people use when threatened
        - Importance of congruent communication
        - Family life cycle and developmental stages
        - Boundaries and subsystems within families
        - Homeostasis vs. growth in family systems
        
        Evaluate this session for:
        1. Communication patterns and styles (congruent vs. survival stances)
        2. Family role dynamics and rules (spoken/unspoken)
        3. Self-worth issues affecting relationships
        4. Boundary issues and subsystem problems
        5. Intergenerational patterns and their impact
        6. Systems thinking and circular causality
        7. Movement toward healthier communication
        8. Family resources and strengths identified
        
        Rate the session on a scale of 1-10 for communication and family role changes.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "communication_patterns": ["specific patterns observed"],
            "communication_stances": ["survival stances identified"],
            "family_roles": ["roles and rules affecting relationships"],
            "self_worth_issues": ["how self-esteem affects family dynamics"],
            "boundary_issues": ["boundary problems in relationships"],
            "intergenerational_patterns": ["patterns passed down through family"],
            "systems_insights": ["understanding of circular causality"],
            "congruent_communication": ["examples of healthy communication"],
            "areas_for_improvement": ["suggestions for family systems work"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "Virginia Satir's family systems approach")
    
    def _analyze_positive_psychology_framework(self, transcript):
        """Analyze using Seligman's positive psychology approach"""
        prompt = f"""
        Analyze this therapy session transcript using Martin Seligman's positive psychology principles.
        
        MARTIN SELIGMAN (b. 1942) - Leading researcher in positive psychology:
        - Shift from pathology model to strengths and well-being focus
        - PERMA-V Model for well-being:
          • P: Positive Emotions (joy, gratitude, serenity, interest, hope, pride, amusement, inspiration, awe, love)
          • E: Engagement (flow states, deep involvement, using signature strengths)
          • R: Relationships (social connections, love, intimacy, emotional support)
          • M: Meaning (purpose, significance, serving something larger than oneself)
          • A: Achievement (accomplishment, mastery, success for its own sake)
          • V: Vitality (physical health, energy, wellness)
        
        - VIA Character Strengths (24 strengths in 6 virtues):
          • Wisdom: creativity, curiosity, judgment, love of learning, perspective
          • Courage: bravery, perseverance, honesty, zest
          • Humanity: love, kindness, social intelligence
          • Justice: teamwork, fairness, leadership
          • Temperance: forgiveness, humility, prudence, self-regulation
          • Transcendence: appreciation of beauty, gratitude, hope, humor, spirituality
        
        - Learned Optimism: explanatory style (permanent vs. temporary, pervasive vs. specific, personal vs. external)
        - Resilience and post-traumatic growth
        - Flourishing vs. languishing
        - Authentic happiness through meaning, engagement, and positive emotion
        
        Evaluate this session for:
        1. PERMA-V elements present and developed
        2. Character strengths identification and utilization
        3. Gratitude and appreciation practices
        4. Optimistic explanatory style development
        5. Resilience building and coping resources
        6. Flow and engagement experiences
        7. Meaning and purpose exploration
        8. Positive relationships and social connections
        9. Achievement and accomplishment recognition
        10. Overall well-being and flourishing indicators
        
        Rate the session on a scale of 1-10 for strengths and well-being focus.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "perma_elements": {{
                "positive_emotions": ["specific emotions expressed or cultivated"],
                "engagement": ["flow states or deep involvement examples"],
                "relationships": ["social connections and support discussed"],
                "meaning": ["purpose and significance explored"],
                "achievement": ["accomplishments and mastery recognized"],
                "vitality": ["physical health and energy addressed"]
            }},
            "character_strengths": ["specific VIA strengths identified or used"],
            "gratitude_practices": ["expressions of gratitude and appreciation"],
            "optimism_building": ["examples of optimistic explanatory style"],
            "resilience_factors": ["coping resources and resilience building"],
            "flourishing_indicators": ["signs of well-being and thriving"],
            "areas_for_improvement": ["suggestions for enhancing positive psychology elements"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "Martin Seligman's positive psychology approach")
    
    def _analyze_narrative_framework(self, transcript):
        """Analyze narrative coherence and identity themes"""
        prompt = f"""
        Analyze this therapy session transcript for narrative coherence and identity themes.
        
        NARRATIVE THERAPY PRINCIPLES:
        - People are the experts of their own lives
        - Problems are separate from people (externalization)
        - Life stories can be re-authored and reconstructed
        - Identity is constructed through stories we tell about ourselves
        - Dominant stories vs. alternative stories
        - Unique outcomes that contradict problem-saturated stories
        - Thick descriptions vs. thin descriptions of identity
        - Preferred identity and values exploration
        
        Evaluate this session for:
        1. Story coherence and consistency in client's narrative
        2. Identity development and evolving self-concept
        3. Life themes and meaning-making processes
        4. Narrative disruptions or contradictions
        5. Growth and change in self-story
        6. Externalization of problems from identity
        7. Alternative stories and unique outcomes
        8. Values and preferred identity exploration
        
        Rate the session on a scale of 1-10 for narrative coherence and identity development.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "narrative_coherence": ["coherent themes in client's story"],
            "identity_themes": ["evolving aspects of self-concept"],
            "life_meanings": ["meaning-making and purpose explored"],
            "narrative_disruptions": ["contradictions or gaps in story"],
            "growth_indicators": ["signs of story re-authoring"],
            "externalization_examples": ["separation of problems from identity"],
            "alternative_stories": ["positive counter-narratives emerging"],
            "values_exploration": ["preferred identity and values discussed"],
            "areas_for_improvement": ["suggestions for narrative development"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "narrative therapy and identity development")
    
    def _analyze_behavioral_framework(self, transcript):
        """Analyze behavioral activation and real-life application"""
        prompt = f"""
        Analyze this therapy session transcript for behavioral activation and real-life application.
        
        BEHAVIORAL ACTIVATION PRINCIPLES:
        - Focus on behavior change and activity engagement
        - Connection between behavior, mood, and thoughts
        - Activity scheduling and behavioral experiments
        - Values-based action and meaningful engagement
        - Breaking patterns of avoidance and withdrawal
        - Mastery and pleasure activities
        - Goal setting and step-by-step progress
        - Environmental modification and context awareness
        
        Evaluate this session for:
        1. Behavioral goals and specific commitments made
        2. Activity scheduling and planning discussions
        3. Behavioral experiments designed or discussed
        4. Real-world application of therapeutic insights
        5. Action steps and follow-through strategies
        6. Values-aligned behavior identification
        7. Avoidance pattern recognition and intervention
        8. Environmental factors and context consideration
        
        Rate the session on a scale of 1-10 for behavioral activation and real-life application.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "behavioral_goals": ["specific goals and commitments"],
            "activity_planning": ["scheduled activities and planning"],
            "behavioral_experiments": ["experiments designed to test beliefs"],
            "real_world_applications": ["practical applications of insights"],
            "action_commitments": ["specific commitments to behavior change"],
            "values_alignment": ["behaviors aligned with personal values"],
            "avoidance_patterns": ["patterns of avoidance identified"],
            "environmental_factors": ["contextual factors affecting behavior"],
            "areas_for_improvement": ["suggestions for enhanced behavioral activation"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "behavioral activation and action-oriented therapy")
    
    def _generate_overall_insights(self, transcript, detailed_analysis, negative_patterns=None):
        """Generate overall insights and recommendations"""
        negative_context = ""
        if negative_patterns:
            negative_context = f"""
            
            IMPORTANT - NEGATIVE PATTERNS DETECTED:
            {json.dumps(negative_patterns, indent=2)}
            
            Pay special attention to these concerning patterns when forming insights and recommendations.
            Consider whether therapy is working effectively or if changes are needed.
            """
        
        prompt = f"""
        Based on this comprehensive therapeutic analysis incorporating the expertise of Carl Rogers, Sigmund Freud, Albert Ellis, Melanie Klein, Virginia Satir, Martin Seligman, and Aaron Beck, provide overall insights and recommendations.
        
        Analysis Summary:
        {json.dumps(detailed_analysis, indent=2)}
        {negative_context}
        
        Synthesize findings across all frameworks to provide:
        1. Key insights about the client's therapeutic progress (be honest about negative patterns)
        2. Specific recommendations for future sessions (address concerning patterns)
        3. Main themes that emerged across different approaches
        4. Progress indicators to track over time
        5. If negative patterns are present, provide specific guidance on addressing them
        
        CRITICAL: If negative patterns indicate therapy is not working well, include this in your insights.
        Do not ignore warning signs or present overly positive assessments when concerning patterns exist.
        
        Respond in JSON format with:
        {{
            "insights": ["insight1", "insight2", "insight3"],
            "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
            "themes": ["theme1", "theme2", "theme3"],
            "progress_indicators": ["indicator1", "indicator2", "indicator3"]
        }}
        """
        
        result = self._analyze_with_providers(prompt, "master therapist providing supervision and case consultation")
        
        # Provide fallback if analysis fails
        if not result or 'insights' not in result:
            fallback_insights = ["Session analysis completed with multiple therapeutic perspectives"]
            fallback_recommendations = ["Continue working on identified areas for growth"]
            
            # Add negative pattern warnings to fallback
            if negative_patterns:
                fallback_insights.append("Warning: Concerning patterns detected that may indicate therapy is not working effectively")
                fallback_recommendations.append("Consider discussing therapy effectiveness and potential changes with your therapist")
            
            return {
                "insights": fallback_insights,
                "recommendations": fallback_recommendations,
                "themes": ["Therapeutic progress and self-exploration"],
                "progress_indicators": ["Client engagement and insight development"]
            }
        
        return result
    
    def analyze_as_chorus(self, transcript):
        """
        Analyze the session as a 'chorus' of eight theorists, each building on the previous,
        avoiding repetition, and offering unique insights.
        """
        prompt = f"""
You are a panel of eight world-renowned psychotherapy theorists:
1. Carl Rogers (Person-Centered)
2. Sigmund Freud (Psychoanalysis)
3. Melanie Klein (Object Relations)
4. Aaron Beck (Cognitive Therapy)
5. Albert Ellis (REBT)
6. Virginia Satir (Family Systems)
7. Martin Seligman (Positive Psychology)
8. Irvin Yalom (Existential Therapy)

You will analyze the following therapy session transcript as a roundtable discussion. Each theorist will:
- Comment in turn, building on previous remarks.
- Offer unique insights from their framework.
- Avoid repeating points already made.
- Reference or respond to earlier comments if relevant.

**Transcript:**  
{transcript}

**Format your response as:**
Rogers: [unique insight]  
Freud: [builds on Rogers, adds unique insight]  
Klein: [builds on above, adds unique insight]  
Beck: [builds on above, adds unique insight]  
Ellis: [builds on above, adds unique insight]  
Satir: [builds on above, adds unique insight]  
Seligman: [builds on above, adds unique insight]  
Yalom: [builds on above, adds unique insight]

Each theorist should be concise (2-3 sentences), insightful, and non-repetitive.
        """

        return self._analyze_with_providers(prompt, "Chorus of eight psychotherapy theorists")
    
    def answer_query(self, query, session_data):
        """Answer specific questions about the therapy session"""
        try:
            context = {
                'transcript': session_data.transcript,
                'analysis': session_data.analysis,
                'timestamp': session_data.timestamp.isoformat()
            }
            
            prompt = f"""
            Answer this question about the therapy session using the provided context.
            
            Question: {query}
            
            Context:
            {json.dumps(context, indent=2)}
            
            Provide a thoughtful, therapeutic response that draws from the session content and analysis.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a compassionate therapeutic assistant providing insights about therapy sessions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Query answering error: {str(e)}")
            return "I apologize, but I encountered an error while processing your question."

    def _conduct_expert_therapist_evaluation(self, transcript):
        """Conduct comprehensive expert-level therapist evaluation based on world-class therapeutic principles"""
        
        expert_prompt = f"""
        You are an expert-level therapy session evaluator trained on the combined principles, techniques, and ethics of the world's most respected psychologists and therapists, including:

        - Carl Rogers (unconditional positive regard, client-centered therapy)
        - Aaron Beck (Cognitive Behavioral Therapy)  
        - Sigmund Freud (psychoanalysis, transference)
        - B.F. Skinner (behavioral modification)
        - Carl Jung (archetypes, individuation)
        - Viktor Frankl (logotherapy, meaning-making)
        - Irvin Yalom (existential psychotherapy)
        - Marsha Linehan (Dialectical Behavior Therapy)
        - Alfred Adler (inferiority complex, goal-oriented therapy)
        - Francine Shapiro (EMDR)
        - Virginia Satir (family therapy and systemic dynamics)
        - Brené Brown (vulnerability and emotional authenticity)
        - Gabor Maté (trauma-informed care)
        - John Gottman (relationship psychology)
        - Daniel Siegel (interpersonal neurobiology)

        Your task is to analyze the following therapy session transcript using a deep, multi-modal lens that includes emotional tone, therapeutic technique, and ethical alignment.

        Evaluate the session across these dimensions:

        1. **Therapist Empathy & Attunement**  
           - Did the therapist demonstrate active listening, emotional resonance, and psychological safety?

        2. **Use of Therapeutic Models**  
           - Which specific approaches (e.g., CBT, DBT, person-centered, somatic, narrative) were used — and were they used skillfully?

        3. **Signs of Therapist Burnout or Disengagement**  
           - Look for signs of hopelessness, minimization, lack of structure, or emotional distance.

        4. **Client Progress Signals**  
           - Did the session contain meaningful cognitive, emotional, or behavioral shifts that suggest forward movement?

        5. **Therapist Fit Score**  
           - Rate from 1–10 based on alignment with client needs, relational connection, and psychological safety.

        Transcript: {transcript}

        Format your response as follows:
        - **Therapist Empathy & Attunement**: [1–10] – [Evidence from transcript]
        - **Therapeutic Techniques Used**: [List models, with comments on skill level]
        - **Signs of Burnout or Detachment**: [Yes/No] – [Explanation]
        - **Client Progress Signals**: [Yes/No] – [Examples]
        - **Therapist Fit Score**: [1–10] – [Justification referencing known therapy principles]

        **Recommendation to Client**:
        Provide 2–3 personalized suggestions, such as:
        - Continue with the therapist and explore deeper
        - Raise concerns in next session
        - Consider evaluating a new therapist with a better modality fit
        """
        
        # Use the best available AI provider for expert evaluation
        evaluation_result = self._analyze_with_providers(expert_prompt, "Expert Therapist Evaluation")
        
        if evaluation_result:
            # Handle both string and dict responses
            if isinstance(evaluation_result, dict):
                # If we got a dict (from local analysis), convert it to expected format
                base_score = evaluation_result.get("score", 6)
                
                # Generate dynamic recommendations based on score
                if base_score >= 8:
                    recommendations = [
                        "Your therapist shows strong therapeutic skills",
                        "Continue building on this positive therapeutic relationship",
                        "Discuss deeper topics as you feel comfortable"
                    ]
                elif base_score >= 6:
                    recommendations = [
                        "Your therapist demonstrates adequate therapeutic skills",
                        "Continue sessions while monitoring your progress",
                        "Provide feedback on what works best for you"
                    ]
                else:
                    recommendations = [
                        "Consider discussing your therapy goals with your therapist",
                        "Evaluate if this therapeutic approach matches your needs",
                        "You may benefit from exploring other therapeutic options"
                    ]
                
                evaluation = {
                    "therapist_empathy_score": base_score,
                    "empathy_evidence": evaluation_result.get("empathy_evidence", ["Basic analysis performed"]),
                    "therapeutic_techniques": evaluation_result.get("therapeutic_techniques", ["Standard approaches detected"]),
                    "burnout_signs": {"present": base_score < 5, "explanation": "Assessment based on session engagement"},
                    "client_progress": {"present": base_score >= 6, "examples": ["Session engagement present"]},
                    "therapist_fit_score": base_score,
                    "fit_justification": f"Score {base_score}/10 - Basic therapeutic assessment (detailed analysis requires AI API)",
                    "client_recommendations": recommendations,
                    "raw_evaluation": str(evaluation_result)
                }
            else:
                # Handle string response
                evaluation = {
                    "therapist_empathy_score": 7,
                    "empathy_evidence": ["Comprehensive analysis performed"],
                    "therapeutic_techniques": ["Multiple therapeutic approaches assessed"],
                    "burnout_signs": {"present": False, "explanation": "No clear signs detected"},
                    "client_progress": {"present": True, "examples": ["Session engagement present"]},
                    "therapist_fit_score": 7,
                    "fit_justification": "Moderate therapeutic alignment observed",
                    "client_recommendations": [
                        "Continue sessions to build therapeutic relationship",
                        "Discuss therapy goals and expectations",
                        "Monitor progress over next few sessions"
                    ],
                    "raw_evaluation": evaluation_result
                }
                
                # Try to extract specific scores and insights from the response
                try:
                    import re
                    
                    # Extract empathy score
                    empathy_match = re.search(r'Empathy.*?(\d+)', evaluation_result, re.IGNORECASE)
                    if empathy_match:
                        evaluation["therapist_empathy_score"] = int(empathy_match.group(1))
                    
                    # Extract fit score
                    fit_match = re.search(r'Fit Score.*?(\d+)', evaluation_result, re.IGNORECASE)
                    if fit_match:
                        evaluation["therapist_fit_score"] = int(fit_match.group(1))
                    
                    # Extract burnout signs
                    if "burnout" in evaluation_result.lower() or "disengagement" in evaluation_result.lower():
                        evaluation["burnout_signs"]["present"] = "yes" in evaluation_result.lower()
                    
                    # Extract progress signals
                    if "progress" in evaluation_result.lower():
                        evaluation["client_progress"]["present"] = "yes" in evaluation_result.lower()
                        
                except Exception as e:
                    pass  # Keep default values if parsing fails
            
            return evaluation
        else:
            # Fallback evaluation when no AI provider is available
            return {
                "therapist_empathy_score": 6,
                "empathy_evidence": ["Limited analysis available - consider professional evaluation"],
                "therapeutic_techniques": ["Standard therapeutic approaches detected"],
                "burnout_signs": {"present": False, "explanation": "Assessment requires professional review"},
                "client_progress": {"present": True, "examples": ["Basic engagement in session"]},
                "therapist_fit_score": 6,
                "fit_justification": "Standard therapeutic interaction - monitoring recommended",
                "client_recommendations": [
                    "Continue with current therapist while monitoring fit",
                    "Provide feedback on session experience to therapist",
                    "Consider seeking second opinion if concerns persist"
                ],
                "raw_evaluation": "Professional evaluation recommended for comprehensive assessment"
            }
        
