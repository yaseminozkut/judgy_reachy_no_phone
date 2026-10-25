"""Text-to-speech and LLM response generation."""

import logging
import re

from .config import PERSONALITIES, get_random_personality

# Matches most emoji + pictographic ranges; used to strip emoji from small-LLM output.
_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F\U0001F100-\U0001F1FF]+",
    flags=re.UNICODE,
)

logger = logging.getLogger(__name__)


def _resolve_personality(personality: str) -> str:
    """Resolve 'mixtape' to a random concrete personality; otherwise return as-is."""
    if personality == "mixtape":
        return get_random_personality()
    return personality


def _build_shame_messages(personality: str, phone_count: int) -> tuple[str, str, str]:
    """Build (system_msg, user_msg, actual_personality) for a shame request.
    Shared by Groq and local MLX backends so they stay in sync."""
    actual_personality = _resolve_personality(personality)
    personality_data = PERSONALITIES.get(actual_personality, PERSONALITIES["angry_boss"])
    shame_data = personality_data["shame"]
    voice_desc = personality_data["voice"]
    avoid = personality_data.get("avoid", "")
    clean_name = personality_data["name"].split(maxsplit=1)[-1]

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

You ARE "{clean_name}". {voice_desc}

SCENE: You caught someone picking up their phone when they should be focusing on work. Call them out in your character's voice.

TONE: {shame_data['tone']}
STRUCTURE: {shame_data['structure']}
AVOID: {avoid}

EXAMPLES — these are just sample lines showing the character's voice.
You MAY use one of them verbatim, OR invent a completely new line in the same voice. Either path is correct — do NOT feel bound to the examples:
{chr(10).join('- ' + ex for ex in shame_data['examples'])}

RULES:
- Each call should feel fresh. Pick an example OR invent something new — your choice.
- 3-10 words. Must make sense and stay in character.
- Match the voice. Content is yours to decide.
- No emoji. No hashtags."""
    user_msg = f"Phone pickup {phone_count} times today. {context_hint}"
    return system_msg, user_msg, actual_personality


def _build_praise_messages(personality: str) -> tuple[str, str, str]:
    """Build (system_msg, user_msg, actual_personality) for a praise request."""
    actual_personality = _resolve_personality(personality)
    personality_data = PERSONALITIES.get(actual_personality, PERSONALITIES["angry_boss"])
    praise_data = personality_data["praise"]
    voice_desc = personality_data["voice"]
    clean_name = personality_data["name"].split(maxsplit=1)[-1]

    system_msg = f"""TASK: Generate a POSITIVE/APPROVING response because someone just put their phone down (GOOD behavior).

You ARE "{clean_name}". {voice_desc}

SCENE: They finally put their phone down after you called them out. React in character — acknowledge the win in your personality's style.

TONE: {praise_data['tone']}

EXAMPLES — these are just sample lines showing the character's voice.
You MAY use one of them verbatim, OR invent a completely new line in the same voice. Either path is correct — do NOT feel bound to the examples:
{chr(10).join('- ' + ex for ex in praise_data['examples'])}

RULES:
- Each call should feel fresh. Pick an example OR invent something new — your choice.
- 2-6 words. Must make sense and stay in character.
- Match the voice. Content is yours to decide.
- No emoji."""
    user_msg = "Phone down."
    return system_msg, user_msg, actual_personality


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

        print(f"\n=== Groq LLM get_response called: personality={self.personality}, client={'YES' if self.client else 'NONE'} ===")

        if not self.client:
            print("  → No client, using prewritten shame")
            return self._get_prewritten_shame()

        try:
            system_msg, user_msg, actual_personality = _build_shame_messages(self.personality, phone_count)

            print(f"  → actual_personality: {actual_personality}")
            print(f"  → model: qwen/qwen3.8-27b, max_tokens=40, temperature=1.2")
            print(f"  → user: {user_msg}")

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

        print(f"\n=== Groq LLM get_praise called: personality={self.personality}, client={'YES' if self.client else 'NONE'} ===")

        if not self.client:
            print("  → No client, using prewritten praise")
            return self._get_prewritten_praise()

        try:
            system_msg, user_msg, actual_personality = _build_praise_messages(self.personality)

            print(f"  → actual_personality: {actual_personality}")
            print(f"  → model: qwen/qwen3.8-27b, max_tokens=25, temperature=1.0")

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


class LocalLLMResponder:
    """Generate snarky responses using a local MLX-hosted small LLM (fully offline).

    Default model: mlx-community/Qwen2.5-3B-Instruct-4bit — same Qwen family as
    the Groq-hosted model, so the shared prompt helpers transfer directly.
    """

    DEFAULT_MODEL = "mlx-community/Qwen2.5-3B-Instruct-4bit"

    def __init__(self, personality: str = "mixtape", model_path: str = DEFAULT_MODEL):
        self.personality = personality
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._sampler_factory = None  # callable(temp) -> sampler, or None if unavailable

        try:
            from mlx_lm import load
            logger.info(f"Loading local MLX LLM: {model_path} (first run downloads weights, ~2GB)")
            self.model, self.tokenizer = load(model_path)
            try:
                from mlx_lm.sample_utils import make_sampler
                self._sampler_factory = make_sampler
            except Exception:
                self._sampler_factory = None
            logger.info(f"Local MLX LLM ready with personality: {PERSONALITIES.get(personality, {}).get('name', personality)}")
            # Warmup — first generation includes graph compilation (~1-2s). Run it now so
            # the first real shame/praise call feels snappy.
            try:
                self._generate("You are a test.", "say ok", max_tokens=4, temp=0.0)
                logger.info("Local MLX LLM warmed up")
            except Exception as e:
                logger.warning(f"MLX warmup failed (non-fatal): {e}")
        except ImportError:
            logger.warning("mlx-lm not installed — local LLM unavailable")
            raise
        except Exception as e:
            logger.warning(f"Local MLX LLM failed to load: {e}")
            raise

    @property
    def client(self):
        """Truthy if the local model is loaded. Mirrors LLMResponder.client API."""
        return self.model is not None

    # Markers after which the model is talking garbage — anything past them is cut.
    _STOP_MARKERS = ["<|im_end|>", "<|endoftext|>", "<|im_start|>", "$connector", "<|", "#afk", "#"]

    def _generate(self, system_msg: str, user_msg: str, max_tokens: int, temp: float) -> str:
        """Run one MLX generation call using the tokenizer's chat template."""
        from mlx_lm import generate
        prompt = self.tokenizer.apply_chat_template(
            [{"role": "system", "content": system_msg},
             {"role": "user", "content": user_msg}],
            add_generation_prompt=True,
            tokenize=False,
        )
        kwargs = {"prompt": prompt, "max_tokens": max_tokens, "verbose": False}
        if self._sampler_factory is not None:
            kwargs["sampler"] = self._sampler_factory(temp=temp)
        else:
            kwargs["temp"] = temp
        text = generate(self.model, self.tokenizer, **kwargs)
        # Strip anything after a stop marker (Qwen chat template leftovers / hallucinated tokens)
        for marker in self._STOP_MARKERS:
            if marker in text:
                text = text.split(marker)[0]
        # Strip emoji — 3B models don't reliably respect "no emoji" rule, and TTS can't speak them
        text = _EMOJI_RE.sub("", text)
        # Collapse any whitespace runs created by emoji removal
        text = re.sub(r"\s+", " ", text).strip()
        # Trim to the last completed sentence so TTS doesn't speak dangling fragments
        # ("...bandwidth of the universe, isn't it? Work can wait, obviously. The cosmos" → kills the trailing fragment)
        last_term = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
        if last_term >= 0 and last_term < len(text) - 1:
            text = text[:last_term + 1]
        return text

    def get_response(self, phone_count: int, context: str = "") -> str:
        print(f"\n=== Local MLX get_response called: personality={self.personality} ===")
        try:
            system_msg, user_msg, actual_personality = _build_shame_messages(self.personality, phone_count)
            # 3B needs lower temp than 27B — 1.0 is the sweet spot (0.9 too safe, 1.2 hallucinates).
            # max_tokens=25 keeps responses short so TTS stays snappy at the booth.
            print(f"  → actual_personality: {actual_personality}")
            print(f"  → model: {self.model_path}, max_tokens=25, temp=1.0")
            print(f"  → user: {user_msg}")

            text = self._generate(system_msg, user_msg, max_tokens=25, temp=1.0).strip()
            print(f"  ← content: {text!r}")
            if not text:
                print("  ⚠️ empty content from local LLM — falling back to prewritten")
                return self._get_prewritten_shame()
            return text
        except Exception as e:
            print(f"  ❌ Local MLX error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return self._get_prewritten_shame()

    def get_praise(self) -> str:
        print(f"\n=== Local MLX get_praise called: personality={self.personality} ===")
        try:
            system_msg, user_msg, actual_personality = _build_praise_messages(self.personality)
            print(f"  → actual_personality: {actual_personality}")
            print(f"  → model: {self.model_path}, max_tokens=25, temp=0.7")
            print(f"  → user: {user_msg}")

            text = self._generate(system_msg, user_msg, max_tokens=25, temp=0.7).strip()
            print(f"  ← content: {text!r}")
            if not text:
                print("  ⚠️ empty content from local LLM — falling back to prewritten")
                return self._get_prewritten_praise()
            return text
        except Exception as e:
            print(f"  ❌ Local MLX error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return self._get_prewritten_praise()

    # Reuse LLMResponder's prewritten helpers via composition
    def _get_prewritten_shame(self) -> str:
        return LLMResponder._get_prewritten_shame(self)

    def _get_prewritten_praise(self) -> str:
        return LLMResponder._get_prewritten_praise(self)


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
