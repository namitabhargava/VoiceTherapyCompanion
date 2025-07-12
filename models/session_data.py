from datetime import datetime
from typing import Dict, Any, Optional
import json

class SessionData:
    """Data model for therapy session information"""
    
    def __init__(self, file_path: str, transcript: str, analysis: Dict[str, Any], 
                 timestamp: datetime = None):
        self.file_path = file_path
        self.transcript = transcript
        self.analysis = analysis
        self.timestamp = timestamp or datetime.now()
        
        # Optional attributes
        self.id: Optional[str] = None
        self.platform: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        self.duration: Optional[float] = None
        self.file_size: Optional[int] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'transcript': self.transcript,
            'analysis': self.analysis,
            'timestamp': self.timestamp.isoformat(),
            'platform': self.platform,
            'metadata': self.metadata,
            'duration': self.duration,
            'file_size': self.file_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create instance from dictionary"""
        session = cls(
            file_path=data['file_path'],
            transcript=data['transcript'],
            analysis=data['analysis'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
        
        session.id = data.get('id')
        session.platform = data.get('platform')
        session.metadata = data.get('metadata', {})
        session.duration = data.get('duration')
        session.file_size = data.get('file_size')
        
        return session
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SessionData':
        """Create instance from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary information"""
        domain_scores = self.analysis.get('domain_scores', {})
        
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'platform': self.platform,
            'overall_score': sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0,
            'domain_count': len(domain_scores),
            'has_transcript': bool(self.transcript),
            'duration': self.duration,
            'file_size': self.file_size,
            'key_themes': self.analysis.get('session_themes', [])[:3]  # Top 3 themes
        }
    
    def get_domain_score(self, domain: str) -> float:
        """Get score for specific domain"""
        return self.analysis.get('domain_scores', {}).get(domain, 0)
    
    def get_progress_since(self, previous_session: 'SessionData') -> Dict[str, float]:
        """Compare progress with previous session"""
        if not previous_session:
            return {}
        
        current_scores = self.analysis.get('domain_scores', {})
        previous_scores = previous_session.analysis.get('domain_scores', {})
        
        progress = {}
        for domain in current_scores:
            if domain in previous_scores:
                progress[domain] = current_scores[domain] - previous_scores[domain]
        
        return progress
    
    def __str__(self) -> str:
        return f"SessionData(id={self.id}, timestamp={self.timestamp}, platform={self.platform})"
    
    def __repr__(self) -> str:
        return self.__str__()
