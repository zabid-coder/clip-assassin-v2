"""
Clip Assassin AI Integration Module
Speech-to-text, auto-chapters, smart silence detection using OpenAI/Whisper
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import config
from exceptions import AIIntegrationError
from logger import get_logger

logger = get_logger(__name__)


class AIService:
    """AI service for transcription and smart editing features"""
    
    def __init__(self):
        self.enabled = config.AI_ENABLED
        self.openai_key = config.OPENAI_API_KEY
        self.whisper_model = config.WHISPER_MODEL
        
        # Initialize Whisper if available
        self.whisper = None
        if self.enabled and not self.openai_key:
            try:
                import whisper
                self.whisper = whisper.load_model(self.whisper_model)
                logger.info(f"Whisper model loaded: {self.whisper_model}")
            except ImportError:
                logger.warning("Whisper not installed. Install with: pip install openai-whisper")
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
        
        # Initialize OpenAI if key provided
        self.openai_client = None
        if self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
    
    def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """Transcribe audio file to text with timestamps"""
        if not self.enabled:
            raise AIIntegrationError("transcription", "AI services not enabled")
        
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise AIIntegrationError("transcription", f"Audio file not found: {audio_path}")
        
        try:
            if self.openai_client:
                # Use OpenAI Whisper API
                return self._transcribe_with_openai(audio_file, language)
            elif self.whisper:
                # Use local Whisper
                return self._transcribe_with_whisper(audio_file, language)
            else:
                raise AIIntegrationError(
                    "transcription",
                    "No transcription service available. Set OPENAI_API_KEY or install whisper"
                )
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise AIIntegrationError("transcription", str(e))
    
    def _transcribe_with_openai(self, audio_file: Path, language: str) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        with open(audio_file, "rb") as f:
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return {
            "text": transcript.text,
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in transcript.segments
            ],
            "language": transcript.language,
            "duration": transcript.duration
        }
    
    def _transcribe_with_whisper(self, audio_file: Path, language: str) -> Dict[str, Any]:
        """Transcribe using local Whisper model"""
        result = self.whisper.transcribe(str(audio_file), language=language)
        
        return {
            "text": result["text"],
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result.get("segments", [])
            ],
            "language": result.get("language", language),
            "duration": None  # Local whisper doesn't always provide duration
        }
    
    def generate_chapters(self, transcript: Dict[str, Any], max_chapters: int = 10) -> List[Dict[str, Any]]:
        """Generate chapter markers from transcript"""
        if not self.enabled:
            raise AIIntegrationError("chapters", "AI services not enabled")
        
        segments = transcript.get("segments", [])
        if not segments:
            return []
        
        # Simple chapter generation based on pauses and topic changes
        chapters = []
        segment_count = len(segments)
        chapter_interval = max(1, segment_count // max_chapters)
        
        for i in range(0, segment_count, chapter_interval):
            segment = segments[i]
            chapter_title = self._generate_chapter_title(segment["text"])
            
            chapters.append({
                "title": chapter_title,
                "start_time": segment["start"],
                "end_time": segments[min(i + chapter_interval - 1, segment_count - 1)]["end"],
                "summary": segment["text"][:100] + "..." if len(segment["text"]) > 100 else segment["text"]
            })
        
        # Refine chapters using OpenAI if available
        if self.openai_client:
            chapters = self._refine_chapters_with_ai(chapters, transcript["text"])
        
        return chapters
    
    def _generate_chapter_title(self, text: str, max_length: int = 50) -> str:
        """Generate a short chapter title from text"""
        # Simple heuristic: first sentence or first N words
        words = text.split()
        if len(words) <= 5:
            return text.strip()
        
        title = " ".join(words[:5])
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title
    
    def _refine_chapters_with_ai(self, chapters: List[Dict], full_text: str) -> List[Dict]:
        """Use OpenAI to refine chapter titles"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a video editor. Generate concise, engaging chapter titles."},
                    {"role": "user", "content": f"Refine these chapter titles:\n{json.dumps(chapters)}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            refined = json.loads(response.choices[0].message.content)
            return refined if isinstance(refined, list) else chapters
        except Exception as e:
            logger.warning(f"AI chapter refinement failed: {e}")
            return chapters
    
    def detect_smart_silence(
        self,
        audio_path: str,
        threshold_db: int = -40,
        min_silence_ms: int = 500
    ) -> List[Dict[str, Any]]:
        """Detect silence periods with context awareness"""
        if not self.enabled:
            raise AIIntegrationError("silence_detection", "AI services not enabled")
        
        # Transcribe first to get context
        transcript = self.transcribe_audio(audio_path)
        
        # Find gaps between segments (potential silence)
        silence_regions = []
        segments = transcript.get("segments", [])
        
        for i in range(len(segments) - 1):
            current_end = segments[i]["end"]
            next_start = segments[i + 1]["start"]
            gap_ms = (next_start - current_end) * 1000
            
            if gap_ms >= min_silence_ms:
                silence_regions.append({
                    "start": current_end,
                    "end": next_start,
                    "duration_ms": gap_ms,
                    "context_before": segments[i]["text"],
                    "context_after": segments[i + 1]["text"]
                })
        
        return silence_regions
    
    def suggest_markers(self, transcript: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest marker positions based on content analysis"""
        if not self.enabled:
            raise AIIntegrationError("markers", "AI services not enabled")
        
        segments = transcript.get("segments", [])
        markers = []
        
        # Look for natural break points
        for i, segment in enumerate(segments):
            text = segment["text"].lower()
            
            # Detect potential scene changes or important moments
            indicators = [
                "so ", "now ", "next ", "finally ", "importantly ",
                "let's ", "we'll ", "before we ", "after this "
            ]
            
            if any(ind in text for ind in indicators):
                markers.append({
                    "time": segment["start"],
                    "type": "content_change",
                    "description": segment["text"][:80],
                    "color": "Yellow"
                })
        
        return markers


# Global AI service instance
ai_service = AIService()


def get_ai_service() -> AIService:
    """Get the AI service instance"""
    return ai_service
