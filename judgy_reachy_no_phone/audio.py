"""Text-to-speech and LLM response generation."""

import logging

from .config import get_prewritten_line, get_praise_line, PERSONALITIES

logger = logging.getLogger(__name__)


class LLMResponder:
    """Generate snarky responses using Groq (free) or fallback to pre-written."""

    def __init__(self, api_key: str = "", personality: str = "mixtape"):
        self.api_key = api_key
        self.client = None
        self.personality = personality

        if api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=api_key)
                logger.info(f"Groq LLM initialized with personality: {PERSONALITIES.get(personality, {}).get('name', personality)}")
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
            # Get personality
            personality_data = PERSONALITIES.get(self.personality, PERSONALITIES["mixtape"])
            personality_prompt = personality_data["shame"]

            # Build context based on count
            if phone_count == 1:
                context_hint = "First time today."
            elif phone_count == 2:
                context_hint = "Second time."
            elif phone_count == 3:
                context_hint = "Third time."
            elif phone_count <= 5:
                context_hint = f"{phone_count} times now."
            else:
                context_hint = f"{phone_count} times today!"

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=20,
                temperature=1.2,  # Higher for more creativity
                messages=[
                    {
                        "role": "system",
                        "content": f"""TASK: Generate a NEGATIVE/SCOLDING response because someone just picked up their phone (BAD behavior).

PERSONALITY: {personality_prompt}

RULES:
- Maximum 8 words. Prefer 3-5 words.
- You can mention the count or not - be creative.
- Be CRITICAL/NEGATIVE about picking up the phone.
- No emoji. No hashtags."""
                    },
                    {
                        "role": "user",
                        "content": f"Phone pickup #{phone_count} today. {context_hint}"
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
            # Get personality
            personality_data = PERSONALITIES.get(self.personality, PERSONALITIES["mixtape"])
            personality_prompt = personality_data["praise"]

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=15,
                temperature=1.1,  # Higher for variety
                messages=[
                    {
                        "role": "system",
                        "content": f"""TASK: Generate a POSITIVE/APPROVING response because someone just put their phone down (GOOD behavior).

PERSONALITY: {personality_prompt}

RULES:
- Maximum 5 words. Prefer 2-3 words.
- Be POSITIVE/APPROVING about putting the phone down.
- No emoji."""
                    },
                    {
                        "role": "user",
                        "content": "Phone down."
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return get_praise_line()


class TextToSpeech:
    """Convert text to speech using Edge TTS (free) or ElevenLabs."""

    def __init__(self, elevenlabs_key: str = "", voice: str = "en-US-AnaNeural"):
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

    async def synthesize(self, text: str, output_path: str = "/tmp/judgy_reachy_tts.mp3") -> str:
        """Convert text to speech, return path to audio file."""

        # Try ElevenLabs first if available and under limit
        if self.eleven_client and (self.chars_used + len(text)) < self.MONTHLY_LIMIT:
            try:
                return await self._synthesize_elevenlabs(text, output_path)
            except Exception as e:
                logger.warning(f"ElevenLabs failed: {e}, falling back to Edge TTS")

        # Fallback to Edge TTS (always works, unlimited)
        return await self._synthesize_edge(text, output_path)

    async def _synthesize_elevenlabs(self, text: str, output_path: str) -> str:
        """Use ElevenLabs for high-quality voice."""
        audio = self.eleven_client.text_to_speech.convert(
            text=text,
            voice_id="Nggzl2QAXh3OijoXD116",  # cute voice H10ItvDnkRN5ysrvzT9J
            model_id="eleven_multilingual_v2",  # Good balance of emotion and speed
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        self.chars_used += len(text)
        logger.debug(f"ElevenLabs TTS: {len(text)} chars, total: {self.chars_used}")
        return output_path

    async def _synthesize_edge(self, text: str, output_path: str) -> str:
        """Use Edge TTS (free, unlimited)."""
        import edge_tts

        communicate = edge_tts.Communicate(text, self.edge_voice)
        await communicate.save(output_path)

        logger.debug(f"Edge TTS: {len(text)} chars")
        return output_path
