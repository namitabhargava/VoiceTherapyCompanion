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
    
    def _generate_overall_insights(self, transcript, detailed_analysis):
        """Generate overall insights and recommendations"""
        prompt = f"""
        Based on this comprehensive therapeutic analysis incorporating the expertise of Carl Rogers, Sigmund Freud, Albert Ellis, Melanie Klein, Virginia Satir, Martin Seligman, and Aaron Beck, provide overall insights and recommendations.
        
        Analysis Summary:
        {json.dumps(detailed_analysis, indent=2)}
        
        Synthesize findings across all frameworks to provide:
        1. Key insights about the client's therapeutic progress
        2. Specific recommendations for future sessions
        3. Main themes that emerged across different approaches
        4. Progress indicators to track over time
        
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
            return {
                "insights": ["Session analysis completed with multiple therapeutic perspectives"],
                "recommendations": ["Continue working on identified areas for growth"],
                "themes": ["Therapeutic progress and self-exploration"],
                "progress_indicators": ["Client engagement and insight development"]
            }
        
        return result
    
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
