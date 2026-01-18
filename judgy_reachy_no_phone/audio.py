"""Text-to-speech and LLM response generation."""

import logging

from .config import get_prewritten_line, get_praise_line

logger = logging.getLogger(__name__)


class LLMResponder:
    """Generate snarky responses using Groq (free) or fallback to pre-written."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.client = None

        if api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=api_key)
                logger.info("Groq LLM initialized")
            except ImportError:
                logger.warning("groq package not installed, using pre-written lines")
            except Exception as e:
                logger.warning(f"Groq init failed: {e}, using pre-written lines")

    def get_response(self, phone_count: int, context: str = "") -> str:
        """Get a snarky response about phone usage."""

        # Fallback to pre-written if no API
        if not self.client:
            return get_prewritten_line(phone_count)

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=50,
                temperature=0.9,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a snarky desk robot watching someone work.
They just picked up their phone instead of working.
Be judgmental but funny. One short sentence only.
No emoji. No hashtags. Keep it under 15 words."""
                    },
                    {
                        "role": "user",
                        "content": f"Phone pickup #{phone_count} today. {context}"
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Groq API error: {e}, using fallback")
            return get_prewritten_line(phone_count)

    def get_praise(self) -> str:
        """Get praise for putting phone down."""

        if not self.client:
            return get_praise_line()

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=30,
                temperature=0.9,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a desk robot. User just put their phone down.
Give brief approval. One short sentence. No emoji."""
                    },
                    {
                        "role": "user",
                        "content": "User put their phone down."
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return get_praise_line()


class TextToSpeech:
    """Convert text to speech using Edge TTS (free) or ElevenLabs."""

    def __init__(self, elevenlabs_key: str = "", voice: str = "en-US-GuyNeural"):
        self.elevenlabs_key = elevenlabs_key
        self.edge_voice = voice
        self.eleven_client = None
        self.chars_used = 0
        self.MONTHLY_LIMIT = 9000  # Leave buffer under 10k

        if elevenlabs_key:
            try:
                from elevenlabs import ElevenLabs
                self.eleven_client = ElevenLabs(api_key=elevenlabs_key)
                logger.info("ElevenLabs TTS initialized")
            except ImportError:
                logger.warning("elevenlabs package not installed, using Edge TTS")
            except Exception as e:
                logger.warning(f"ElevenLabs init failed: {e}, using Edge TTS")

    async def synthesize(self, text: str, output_path: str = "/tmp/phone_shame_tts.mp3") -> str:
        """Convert text to speech, return path to audio file."""

        logger.info(f"TTS synthesize called with text: '{text}', output: {output_path}")

        # Try ElevenLabs first if available and under limit
        if self.eleven_client and (self.chars_used + len(text)) < self.MONTHLY_LIMIT:
            try:
                logger.info("Using ElevenLabs TTS")
                return await self._synthesize_elevenlabs(text, output_path)
            except Exception as e:
                logger.warning(f"ElevenLabs failed: {e}, falling back to Edge TTS")

        # Fallback to Edge TTS (always works, unlimited)
        logger.info("Using Edge TTS (free)")
        return await self._synthesize_edge(text, output_path)

    async def _synthesize_elevenlabs(self, text: str, output_path: str) -> str:
        """Use ElevenLabs for high-quality voice."""
        audio = self.eleven_client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # George - good for snarky
            model_id="eleven_turbo_v2_5",
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        self.chars_used += len(text)
        logger.debug(f"ElevenLabs TTS: {len(text)} chars, total: {self.chars_used}")
        return output_path

    async def _synthesize_edge(self, text: str, output_path: str) -> str:
        """Use Edge TTS (free, unlimited)."""
        try:
            import edge_tts
            logger.info(f"Edge TTS imported successfully, voice: {self.edge_voice}")
        except ImportError as e:
            logger.error(f"Failed to import edge_tts: {e}")
            raise

        logger.info(f"Creating Edge TTS communicate object for text: '{text}'")
        communicate = edge_tts.Communicate(text, self.edge_voice)

        logger.info(f"Saving audio to: {output_path}")
        await communicate.save(output_path)

        logger.info(f"Edge TTS complete: {len(text)} chars, file saved to {output_path}")
        return output_path
