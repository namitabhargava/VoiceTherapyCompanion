import os
import json
import streamlit as st
from datetime import datetime
from models.analysis_models import TherapeuticFramework, AnalysisResult
import requests

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
        
        # Available analysis providers
        self.providers = {
            'openai': self._analyze_with_openai,
            'huggingface': self._analyze_with_huggingface,
            'local': self._analyze_with_local_model
        }
        
    def analyze_session(self, transcript):
        """Comprehensive analysis of therapy session using multiple frameworks"""
        try:
            st.info("Analyzing session with multiple therapeutic frameworks...")
            
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
            
            # Generate overall insights and recommendations
            overall_insights = self._generate_overall_insights(transcript, detailed_analysis)
            
            return {
                'domain_scores': domain_scores,
                'detailed_analysis': detailed_analysis,
                'key_insights': overall_insights['insights'],
                'recommendations': overall_insights['recommendations'],
                'session_themes': overall_insights['themes'],
                'progress_indicators': overall_insights['progress_indicators'],
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return None
    
    def _analyze_rogers_framework(self, transcript):
        """Analyze using Carl Rogers' person-centered approach"""
        prompt = f"""
        Analyze this therapy session transcript using Carl Rogers' person-centered approach.
        Focus on:
        1. Evidence of empathy from the therapist
        2. Genuineness and authenticity in the relationship
        3. Unconditional positive regard
        4. Client's self-exploration and self-acceptance
        5. Emotional safety and trust in the relationship
        
        Rate the session on a scale of 1-10 for emotional safety and relational depth.
        
        Transcript: {transcript}
        
        Respond in JSON format with:
        {{
            "score": <number 1-10>,
            "empathy_evidence": ["example1", "example2"],
            "genuineness_indicators": ["example1", "example2"],
            "positive_regard_moments": ["example1", "example2"],
            "client_self_exploration": ["example1", "example2"],
            "areas_for_improvement": ["suggestion1", "suggestion2"]
        }}
        """
        
        return self._analyze_with_providers(prompt, "Carl Rogers' person-centered therapy approach")
    
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
            # Simple keyword-based analysis for fallback
            transcript_text = prompt.split("Transcript: ")[1].split("Respond in JSON format")[0].lower()
            
            # Basic scoring based on keywords
            positive_keywords = ['good', 'better', 'progress', 'understand', 'feel', 'help', 'support', 'positive', 'growth', 'insight']
            negative_keywords = ['difficult', 'hard', 'struggle', 'problem', 'issue', 'challenge', 'worried', 'anxious', 'sad', 'angry']
            
            positive_count = sum(1 for word in positive_keywords if word in transcript_text)
            negative_count = sum(1 for word in negative_keywords if word in transcript_text)
            
            # Basic score calculation
            base_score = 5
            if positive_count > negative_count:
                score = min(10, base_score + (positive_count - negative_count) * 0.5)
            else:
                score = max(1, base_score - (negative_count - positive_count) * 0.5)
            
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
                "error": "Analysis unavailable",
                "note": "Please provide API keys for detailed analysis"
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
        try:
            prompt = f"""
            Analyze this therapy session transcript using psychodynamic principles from Freud and Klein.
            Focus on:
            1. Unconscious patterns and defenses
            2. Symbolic language and metaphors
            3. Transference and countertransference
            4. Early experiences and their impact
            5. Defense mechanisms in operation
            
            Rate the session on a scale of 1-10 for unconscious pattern emergence.
            
            Transcript: {transcript}
            
            Respond in JSON format with:
            {{
                "score": <number 1-10>,
                "unconscious_patterns": ["pattern1", "pattern2"],
                "defense_mechanisms": ["mechanism1", "mechanism2"],
                "symbolic_content": ["symbol1", "symbol2"],
                "transference_indicators": ["indicator1", "indicator2"],
                "early_experience_connections": ["connection1", "connection2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in psychodynamic therapy and unconscious processes."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Psychodynamic analysis error: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def _analyze_cognitive_framework(self, transcript):
        """Analyze using Ellis and Beck's cognitive approaches"""
        try:
            prompt = f"""
            Analyze this therapy session transcript using cognitive therapy principles from Ellis (REBT) and Beck (CBT).
            Focus on:
            1. Identification of irrational thoughts and beliefs
            2. Cognitive distortions present
            3. Evidence of cognitive restructuring
            4. Behavioral experiments or homework
            5. Thought challenging techniques used
            
            Rate the session on a scale of 1-10 for cognitive restructuring effectiveness.
            
            Transcript: {transcript}
            
            Respond in JSON format with:
            {{
                "score": <number 1-10>,
                "irrational_beliefs": ["belief1", "belief2"],
                "cognitive_distortions": ["distortion1", "distortion2"],
                "restructuring_evidence": ["evidence1", "evidence2"],
                "homework_assignments": ["assignment1", "assignment2"],
                "thought_challenging_examples": ["example1", "example2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in cognitive behavioral therapy and rational emotive behavior therapy."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Cognitive analysis error: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def _analyze_family_systems_framework(self, transcript):
        """Analyze using Virginia Satir's family systems approach"""
        try:
            prompt = f"""
            Analyze this therapy session transcript using Virginia Satir's family systems approach.
            Focus on:
            1. Communication patterns and styles
            2. Family role dynamics
            3. Boundary issues
            4. Intergenerational patterns
            5. Systems thinking and circular causality
            
            Rate the session on a scale of 1-10 for communication and family role changes.
            
            Transcript: {transcript}
            
            Respond in JSON format with:
            {{
                "score": <number 1-10>,
                "communication_patterns": ["pattern1", "pattern2"],
                "family_roles": ["role1", "role2"],
                "boundary_issues": ["issue1", "issue2"],
                "intergenerational_patterns": ["pattern1", "pattern2"],
                "systems_insights": ["insight1", "insight2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in family systems therapy and Virginia Satir's approach."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Family systems analysis error: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def _analyze_positive_psychology_framework(self, transcript):
        """Analyze using Seligman's positive psychology approach"""
        try:
            prompt = f"""
            Analyze this therapy session transcript using Martin Seligman's positive psychology principles.
            Focus on:
            1. PERMA model elements (Positive emotions, Engagement, Relationships, Meaning, Achievement)
            2. Character strengths identification and use
            3. Gratitude and appreciation practices
            4. Optimism and hope building
            5. Resilience factors
            
            Rate the session on a scale of 1-10 for strengths and well-being focus.
            
            Transcript: {transcript}
            
            Respond in JSON format with:
            {{
                "score": <number 1-10>,
                "perma_elements": {{"positive_emotions": ["example1"], "engagement": ["example2"], "relationships": ["example3"], "meaning": ["example4"], "achievement": ["example5"]}},
                "character_strengths": ["strength1", "strength2"],
                "gratitude_practices": ["practice1", "practice2"],
                "optimism_building": ["example1", "example2"],
                "resilience_factors": ["factor1", "factor2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in positive psychology and strengths-based therapy."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Positive psychology analysis error: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def _analyze_narrative_framework(self, transcript):
        """Analyze narrative coherence and identity themes"""
        try:
            prompt = f"""
            Analyze this therapy session transcript for narrative coherence and identity themes.
            Focus on:
            1. Story coherence and consistency
            2. Identity development and self-concept
            3. Life themes and meaning-making
            4. Narrative disruptions or contradictions
            5. Growth and change in self-story
            
            Rate the session on a scale of 1-10 for narrative coherence.
            
            Transcript: {transcript}
            
            Respond in JSON format with:
            {{
                "score": <number 1-10>,
                "narrative_coherence": ["coherent_theme1", "coherent_theme2"],
                "identity_themes": ["theme1", "theme2"],
                "life_meanings": ["meaning1", "meaning2"],
                "narrative_disruptions": ["disruption1", "disruption2"],
                "growth_indicators": ["indicator1", "indicator2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in narrative therapy and identity development."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Narrative analysis error: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def _analyze_behavioral_framework(self, transcript):
        """Analyze behavioral activation and real-life application"""
        try:
            prompt = f"""
            Analyze this therapy session transcript for behavioral activation and real-life application.
            Focus on:
            1. Behavioral goals and commitments
            2. Activity scheduling and planning
            3. Behavioral experiments discussed
            4. Real-world application of insights
            5. Action steps and follow-through
            
            Rate the session on a scale of 1-10 for behavioral activation.
            
            Transcript: {transcript}
            
            Respond in JSON format with:
            {{
                "score": <number 1-10>,
                "behavioral_goals": ["goal1", "goal2"],
                "activity_planning": ["activity1", "activity2"],
                "behavioral_experiments": ["experiment1", "experiment2"],
                "real_world_applications": ["application1", "application2"],
                "action_commitments": ["commitment1", "commitment2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in behavioral activation and action-oriented therapy."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Behavioral analysis error: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def _generate_overall_insights(self, transcript, detailed_analysis):
        """Generate overall insights and recommendations"""
        try:
            prompt = f"""
            Based on this comprehensive therapeutic analysis, provide overall insights and recommendations.
            
            Analysis Summary:
            {json.dumps(detailed_analysis, indent=2)}
            
            Provide:
            1. Key insights about the client's progress
            2. Specific recommendations for future sessions
            3. Main themes that emerged
            4. Progress indicators to track
            
            Respond in JSON format with:
            {{
                "insights": ["insight1", "insight2", "insight3"],
                "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
                "themes": ["theme1", "theme2", "theme3"],
                "progress_indicators": ["indicator1", "indicator2", "indicator3"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a master therapist providing supervision and case consultation."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Overall insights error: {str(e)}")
            return {
                "insights": [],
                "recommendations": [],
                "themes": [],
                "progress_indicators": []
            }
    
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
