"""
Transcription service for converting voice to text.
Supports OpenAI Whisper and Deepgram.

This is the first step in the pipeline:
Voice Audio → Transcription → Quote Generation
"""

import os
import tempfile
from typing import Optional
from pathlib import Path
import httpx

from ..config import settings


class TranscriptionService:
    """
    Handles voice-to-text transcription.
    Currently supports OpenAI Whisper API.
    """

    def __init__(self):
        self.provider = settings.transcription_provider
        self.openai_key = settings.openai_api_key
        self.deepgram_key = settings.deepgram_api_key

    async def transcribe(
        self,
        audio_file_path: str,
        language: str = "en"
    ) -> dict:
        """
        Transcribe an audio file to text.

        Args:
            audio_file_path: Path to the audio file
            language: Language code (default: English)

        Returns:
            dict with:
                - text: The transcribed text
                - confidence: Confidence score (if available)
                - duration: Audio duration in seconds
        """
        if self.provider == "openai":
            return await self._transcribe_openai(audio_file_path, language)
        elif self.provider == "deepgram":
            return await self._transcribe_deepgram(audio_file_path, language)
        else:
            raise ValueError(f"Unknown transcription provider: {self.provider}")

    async def _transcribe_openai(
        self,
        audio_file_path: str,
        language: str
    ) -> dict:
        """
        Transcribe using OpenAI Whisper API.
        Cost: ~$0.006 per minute of audio.
        """
        if not self.openai_key:
            raise ValueError("OpenAI API key not configured")

        url = "https://api.openai.com/v1/audio/transcriptions"

        # Read the audio file
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Prepare the request
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(audio_path, "rb") as audio_file:
                files = {
                    "file": (audio_path.name, audio_file, "audio/mpeg"),
                }
                data = {
                    "model": "whisper-1",
                    "language": language,
                    "response_format": "verbose_json",
                }
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                }

                response = await client.post(
                    url,
                    files=files,
                    data=data,
                    headers=headers,
                )

                if response.status_code != 200:
                    raise Exception(f"Transcription failed: {response.text}")

                result = response.json()

                return {
                    "text": result.get("text", ""),
                    "duration": result.get("duration", 0),
                    "language": result.get("language", language),
                    "segments": result.get("segments", []),
                }

    async def _transcribe_deepgram(
        self,
        audio_file_path: str,
        language: str
    ) -> dict:
        """
        Transcribe using Deepgram Nova API.
        Cost: ~$0.0043 per minute (batch), good accuracy.
        """
        if not self.deepgram_key:
            raise ValueError("Deepgram API key not configured")

        url = "https://api.deepgram.com/v1/listen"
        params = {
            "model": "nova-2",
            "language": language,
            "smart_format": "true",
            "punctuate": "true",
            "diarize": "false",  # Speaker detection off for single speaker
        }

        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Determine content type
        suffix = audio_path.suffix.lower()
        content_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".m4a": "audio/mp4",
            ".webm": "audio/webm",
            ".ogg": "audio/ogg",
        }
        content_type = content_types.get(suffix, "audio/mpeg")

        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(audio_path, "rb") as audio_file:
                headers = {
                    "Authorization": f"Token {self.deepgram_key}",
                    "Content-Type": content_type,
                }

                response = await client.post(
                    url,
                    params=params,
                    content=audio_file.read(),
                    headers=headers,
                )

                if response.status_code != 200:
                    raise Exception(f"Transcription failed: {response.text}")

                result = response.json()
                channel = result.get("results", {}).get("channels", [{}])[0]
                alternative = channel.get("alternatives", [{}])[0]

                return {
                    "text": alternative.get("transcript", ""),
                    "confidence": alternative.get("confidence", 0),
                    "duration": result.get("metadata", {}).get("duration", 0),
                    "words": alternative.get("words", []),
                }

    async def transcribe_from_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.mp3",
        language: str = "en"
    ) -> dict:
        """
        Transcribe from audio bytes (for direct uploads).
        Saves to temp file, transcribes, then cleans up.
        """
        # Save to temp file
        suffix = Path(filename).suffix or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            # Transcribe
            result = await self.transcribe(tmp_path, language)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get the transcription service singleton."""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
