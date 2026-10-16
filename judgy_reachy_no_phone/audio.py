"""Text-to-speech and LLM response generation."""

import logging

from .config import PERSONALITIES, get_random_personality

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

        print(f"\n=== LLM get_response called: personality={self.personality}, client={'YES' if self.client else 'NONE'} ===")

        # Fallback to personality-specific pre-written if no API
        if not self.client:
            print("  → No client, using prewritten shame")
            return self._get_prewritten_shame()

        try:
            # Get personality - if mixtape, randomly pick one
            if self.personality == "mixtape":
                actual_personality = get_random_personality()
            else:
                actual_personality = self.personality

            personality_data = PERSONALITIES.get(actual_personality, PERSONALITIES["angry_boss"])

            # Build personality prompt from structured data
            shame_data = personality_data["shame"]
            voice_desc = personality_data["voice"]
            avoid = personality_data.get("avoid", "")
            # Strip leading emoji from name (e.g. "😠 Angry Boss" → "Angry Boss")
            clean_name = personality_data["name"].split(maxsplit=1)[-1]

            # Construct prompt from structured data
            personality_prompt = f"""You ARE "{clean_name}". {voice_desc}

SCENE: You caught someone picking up their phone when they should be focusing on work. Call them out in your character's voice.

TONE: {shame_data['tone']}
STRUCTURE: {shame_data['structure']}
AVOID: {avoid}

EXAMPLES (you may use any of these or invent your own in the same voice):
{chr(10).join('- ' + ex for ex in shame_data['examples'])}"""

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

            system_msg = f"""TASK: Generate a NEGATIVE/SCOLDING response because someone just picked up their phone (BAD behavior).

{personality_prompt}

RULES:
- Vary your responses across calls — mix in the examples, your own fresh lines, or short combinations.
- 3-10 words. Must make sense and stay in character.
- Match the personality's voice. Invent specific content.
- No emoji. No hashtags."""
            user_msg = f"Phone pickup #{phone_count} today. {context_hint}"

            print(f"  → actual_personality: {actual_personality}")
            print(f"  → model: qwen/qwen3.8-27b, max_tokens=40, temperature=1.2")
            print(f"  → user: {user_msg}")
            print(f"  → system (first 200 chars): {system_msg[:200]}...")

            response = self.client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                max_tokens=40,
                temperature=1.2,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )

            print(f"  ← FULL response: {response}")
            print(f"  ← response.model_dump(): {response.model_dump() if hasattr(response, 'model_dump') else 'no model_dump'}")
            print(f"  ← choices[0].message: {response.choices[0].message}")
            print(f"  ← content: {response.choices[0].message.content!r}")
            if hasattr(response.choices[0].message, 'reasoning'):
                print(f"  ← reasoning field: {response.choices[0].message.reasoning!r}")
            if hasattr(response, "usage") and response.usage:
                print(f"  ← usage: prompt={response.usage.prompt_tokens} completion={response.usage.completion_tokens} total={response.usage.total_tokens}")

            text = (response.choices[0].message.content or "").strip()
            if not text:
                print("  ⚠️ empty content from LLM — falling back to prewritten")
                return self._get_prewritten_shame()
            return text
        except Exception as e:
            print(f"  ❌ Groq API error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            logger.warning(f"Groq API error: {e}, using fallback")
            return self._get_prewritten_shame()

    def get_praise(self) -> str:
        """Get praise for putting phone down."""

        print(f"\n=== LLM get_praise called: personality={self.personality}, client={'YES' if self.client else 'NONE'} ===")

        if not self.client:
            print("  → No client, using prewritten praise")
            return self._get_prewritten_praise()

        try:
            # Get personality - if mixtape, randomly pick one
            if self.personality == "mixtape":
                actual_personality = get_random_personality()
            else:
                actual_personality = self.personality

            personality_data = PERSONALITIES.get(actual_personality, PERSONALITIES["angry_boss"])

            # Build praise prompt from structured data
            praise_data = personality_data["praise"]
            voice_desc = personality_data["voice"]
            # Strip leading emoji from name (e.g. "😠 Angry Boss" → "Angry Boss")
            clean_name = personality_data["name"].split(maxsplit=1)[-1]

            # Construct prompt
            personality_prompt = f"""You ARE "{clean_name}". {voice_desc}

SCENE: They finally put their phone down after you called them out. React in character — acknowledge the win in your personality's style.

TONE: {praise_data['tone']}

EXAMPLES (you may use any of these or invent your own in the same voice):
{chr(10).join('- ' + ex for ex in praise_data['examples'])}"""

            system_msg = f"""TASK: Generate a POSITIVE/APPROVING response because someone just put their phone down (GOOD behavior).

{personality_prompt}

RULES:
- Vary your responses across calls — mix in the examples or invent your own.
- 2-6 words. Must make sense and stay in character.
- Match the personality's voice.
- No emoji."""
            user_msg = "Phone down."

            print(f"  → actual_personality: {actual_personality}")
            print(f"  → model: qwen/qwen3.8-27b, max_tokens=25, temperature=1.0")
            print(f"  → user: {user_msg}")
            print(f"  → system (first 200 chars): {system_msg[:200]}...")

            response = self.client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                max_tokens=25,
                temperature=1.0,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
            )

            print(f"  ← FULL response: {response}")
            print(f"  ← response.model_dump(): {response.model_dump() if hasattr(response, 'model_dump') else 'no model_dump'}")
            print(f"  ← choices[0].message: {response.choices[0].message}")
            print(f"  ← content: {response.choices[0].message.content!r}")
            if hasattr(response.choices[0].message, 'reasoning'):
                print(f"  ← reasoning field: {response.choices[0].message.reasoning!r}")
            if hasattr(response, "usage") and response.usage:
                print(f"  ← usage: prompt={response.usage.prompt_tokens} completion={response.usage.completion_tokens} total={response.usage.total_tokens}")

            text = (response.choices[0].message.content or "").strip()
            if not text:
                print("  ⚠️ empty content from LLM — falling back to prewritten")
                return self._get_prewritten_praise()
            return text
        except Exception as e:
            print(f"  ❌ Groq API error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return self._get_prewritten_praise()

    def _get_prewritten_shame(self) -> str:
        """Get personality-specific pre-written shame line."""
        import random

        # If mixtape, randomly pick a personality
        if self.personality == "mixtape":
            actual_personality = get_random_personality()
        else:
            actual_personality = self.personality

        personality_data = PERSONALITIES.get(actual_personality, PERSONALITIES["angry_boss"])
        prewritten = personality_data.get("prewritten_shame", [])
        return random.choice(prewritten)

    def _get_prewritten_praise(self) -> str:
        """Get personality-specific pre-written praise line."""
        import random

        # If mixtape, randomly pick a personality
        if self.personality == "mixtape":
            actual_personality = get_random_personality()
        else:
            actual_personality = self.personality

        personality_data = PERSONALITIES.get(actual_personality, PERSONALITIES["angry_boss"])
        prewritten = personality_data.get("prewritten_praise", [])
        return random.choice(prewritten)


class TextToSpeech:
    """Convert text to speech using Edge TTS (free) or ElevenLabs."""

    def __init__(self, elevenlabs_key: str = "", voice: str = "", eleven_voice_id: str = "", personality: str = "mixtape"):
        self.elevenlabs_key = elevenlabs_key
        self.user_edge_voice = voice  # User's custom Edge TTS voice (overrides personality default)
        self.user_eleven_voice = eleven_voice_id  # User's custom ElevenLabs voice (overrides personality default)
        self.personality = personality
        self.eleven_client = None
        self.chars_used = 0
        self.MONTHLY_LIMIT = 9000  # Leave buffer under 10k
        self.working_voice_cache = {}  # Cache of personality -> working voice ID

        if elevenlabs_key:
            try:
                from elevenlabs import ElevenLabs
                self.eleven_client = ElevenLabs(api_key=elevenlabs_key)
                logger.info(f"ElevenLabs TTS initialized (voices will be validated on first use)")
            except ImportError:
                logger.warning("elevenlabs package not installed, using Edge TTS")
            except Exception as e:
                logger.warning(f"ElevenLabs init failed: {e}, using Edge TTS")

    def _get_voice_for_personality(self):
        """Get the appropriate voice based on personality and user override."""
        personality_data = PERSONALITIES.get(self.personality, PERSONALITIES["mixtape"])

        # User override always wins for edge voice
        edge_voice = self.user_edge_voice if self.user_edge_voice else personality_data.get("default_voice", "en-US-AnaNeural")

        # For ElevenLabs voice, handle list of voices (try in order) or single voice (backward compatibility)
        if self.user_eleven_voice:
            # User specified a custom voice
            eleven_voices = [self.user_eleven_voice]
        else:
            # Get from personality config - handle both list and single voice
            eleven_voice_data = personality_data.get("default_eleven_voices", personality_data.get("default_eleven_voice", "21m00Tcm4TlvDq8ikWAM"))
            if isinstance(eleven_voice_data, list):
                eleven_voices = eleven_voice_data
            else:
                eleven_voices = [eleven_voice_data]

        return edge_voice, eleven_voices

    async def synthesize(self, text: str, output_path: str = "/tmp/judgy_reachy_tts.mp3") -> str:
        """Convert text to speech, return path to audio file."""

        # Get appropriate voices for current personality
        edge_voice, eleven_voices = self._get_voice_for_personality()

        # Try ElevenLabs first if available and under limit
        if self.eleven_client and (self.chars_used + len(text)) < self.MONTHLY_LIMIT:
            # Check cache first
            if self.personality in self.working_voice_cache:
                try:
                    cached_voice = self.working_voice_cache[self.personality]
                    logger.info(f"Using cached ElevenLabs voice: {cached_voice}")
                    return await self._synthesize_elevenlabs(text, output_path, cached_voice)
                except Exception as e:
                    logger.warning(f"Cached voice failed: {e}, trying other voices")
                    # Remove from cache if it failed
                    del self.working_voice_cache[self.personality]

            # Try each voice in the list until one works
            for voice_id in eleven_voices:
                try:
                    logger.info(f"Trying ElevenLabs voice: {voice_id}")
                    result = await self._synthesize_elevenlabs(text, output_path, voice_id)
                    # Success! Cache this voice for future use
                    self.working_voice_cache[self.personality] = voice_id
                    logger.info(f"✓ Voice {voice_id} works! Cached for {self.personality}")
                    return result
                except Exception as e:
                    logger.warning(f"Voice {voice_id} failed: {e}, trying next...")
                    continue

            # All voices failed
            logger.warning(f"All ElevenLabs voices failed for {self.personality}, falling back to Edge TTS")

        # Fallback to Edge TTS (always works, unlimited)
        logger.info(f"Using Edge TTS with voice: {edge_voice}")
        return await self._synthesize_edge(text, output_path, edge_voice)

    async def _synthesize_elevenlabs(self, text: str, output_path: str, voice_id: str) -> str:
        """Use ElevenLabs for high-quality voice."""
        audio = self.eleven_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",  # Good balance of emotion and speed
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        self.chars_used += len(text)
        logger.debug(f"ElevenLabs TTS: {len(text)} chars, total: {self.chars_used}")
        return output_path

    async def _synthesize_edge(self, text: str, output_path: str, voice: str) -> str:
        """Use Edge TTS (free, unlimited)."""
        import edge_tts

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

        logger.debug(f"Edge TTS: {len(text)} chars with voice {voice}")
        return output_path
