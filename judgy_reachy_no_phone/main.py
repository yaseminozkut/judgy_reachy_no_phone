"""
Phone Shame - Get off your phone! 📱🤖

A Reachy Mini app that detects when you pick up your phone
and shames you with snarky comments.

Stack (100% Free):
- Detection: YOLOv8 (local)
- LLM: Groq (free tier) or pre-written lines
- TTS: Edge TTS (free) or ElevenLabs (free tier)
"""

import time
import threading
import logging
import asyncio
import random
import os
from dataclasses import dataclass
from collections import deque
from typing import Optional
from pathlib import Path

import cv2
import numpy as np
import gradio as gr

from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class Config:
    # Detection settings
    PICKUP_THRESHOLD: int = 3          # Frames to confirm phone pickup
    PUTDOWN_THRESHOLD: int = 15        # Frames to confirm phone put down (~3 sec)
    DETECTION_CONFIDENCE: float = 0.5  # YOLO confidence threshold
    COOLDOWN_SECONDS: float = 30.0     # Min time between shames

    # API Keys (optional - leave empty for free defaults)
    GROQ_API_KEY: str = ""             # Get free at console.groq.com
    ELEVENLABS_API_KEY: str = ""       # Get free at elevenlabs.io

    # TTS settings
    EDGE_TTS_VOICE: str = "en-US-GuyNeural"  # Free voice
    ELEVENLABS_VOICE_ID: str = "JBFqnCBsd6RMkjVDRZzb"  # "George"


# =============================================================================
# Pre-written Snarky Lines (No API needed)
# =============================================================================

SNARKY_LINES = {
    1: [
        "The phone? Already?",
        "Oh, checking something important?",
        "And so it begins.",
        "First one of the day. Let's see how this goes.",
    ],
    2: [
        "Again?",
        "Twice now.",
        "Back to the phone I see.",
        "Round two.",
    ],
    3: [
        "Third time's the charm?",
        "Hat trick!",
        "Really? Three times?",
        "At this point I'm impressed.",
    ],
    "many": [
        "I've lost count.",
        "Phone addiction is real.",
        "Your screen time is weeping.",
        "At this point just glue it to your hand.",
        "Impressive dedication to distraction.",
        "The phone isn't going anywhere, you know.",
        "Do you even remember what you were doing?",
        "Your focus called. It's filing for divorce.",
    ]
}

PRAISE_LINES = [
    "Good. Back to work.",
    "There we go.",
    "Phone down. Respect.",
    "See? You can do it.",
    "Freedom!",
]


def get_prewritten_line(phone_count: int) -> str:
    """Get a random pre-written snarky line based on count."""
    if phone_count in SNARKY_LINES:
        return random.choice(SNARKY_LINES[phone_count])
    return random.choice(SNARKY_LINES["many"])


def get_praise_line() -> str:
    """Get a random praise line for putting phone down."""
    return random.choice(PRAISE_LINES)


# =============================================================================
# LLM Response (Groq - Free)
# =============================================================================

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


# =============================================================================
# Text-to-Speech (Edge TTS - Free, or ElevenLabs)
# =============================================================================

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
        import edge_tts

        communicate = edge_tts.Communicate(text, self.edge_voice)
        await communicate.save(output_path)

        logger.debug(f"Edge TTS: {len(text)} chars")
        return output_path


# =============================================================================
# Phone Detection (YOLO)
# =============================================================================

class PhoneDetector:
    """Detect phone in camera frame using YOLOv8."""

    PHONE_CLASS_ID = 67  # "cell phone" in COCO dataset

    def __init__(self, confidence: float = 0.5):
        self.confidence = confidence
        self.model = None
        self._initialized = False

        # State tracking
        self.phone_visible = False
        self.consecutive_phone = 0
        self.consecutive_no_phone = 0
        self.phone_count = 0
        self.last_reaction_time = 0

        # History for robust detection
        self.history = deque(maxlen=30)  # ~6 seconds at 5fps

    def initialize(self):
        """Load YOLO model."""
        if self._initialized:
            return True

        try:
            from ultralytics import YOLO
            # Use nano model for speed
            self.model = YOLO("yolov8n.pt")
            self._initialized = True
            logger.info("YOLO model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")
            return False

    def detect_phone(self, frame: np.ndarray) -> bool:
        """Check if phone is in frame."""
        if not self._initialized:
            if not self.initialize():
                return False

        try:
            results = self.model(frame, verbose=False, conf=self.confidence)

            for result in results:
                for box in result.boxes:
                    if int(box.cls) == self.PHONE_CLASS_ID:
                        return True
            return False

        except Exception as e:
            logger.debug(f"Detection error: {e}")
            return False

    def process_frame(
        self,
        frame: np.ndarray,
        pickup_threshold: int = 3,
        putdown_threshold: int = 15,
        cooldown: float = 30.0
    ) -> Optional[str]:
        """
        Process a frame and track phone state.

        Returns:
            "picked_up" - Phone just picked up (trigger shame)
            "put_down" - Phone just put down (optional praise)
            None - No state change
        """
        phone_in_frame = self.detect_phone(frame)

        # Add to history
        self.history.append(phone_in_frame)

        # Update consecutive counters
        if phone_in_frame:
            self.consecutive_phone += 1
            self.consecutive_no_phone = 0
        else:
            self.consecutive_no_phone += 1
            # Don't reset consecutive_phone immediately (handles flickering)

        # Check for phone pickup (quick to detect)
        if self.consecutive_phone >= pickup_threshold and not self.phone_visible:
            self.phone_visible = True
            self.consecutive_no_phone = 0

            # Check cooldown
            now = time.time()
            if now - self.last_reaction_time >= cooldown:
                self.phone_count += 1
                self.last_reaction_time = now
                return "picked_up"

        # Check for phone put down (slow to confirm - avoids flickering)
        if self.consecutive_no_phone >= putdown_threshold and self.phone_visible:
            self.phone_visible = False
            self.consecutive_phone = 0
            return "put_down"

        return None

    def get_stats(self) -> dict:
        """Get detection statistics."""
        return {
            "phone_count": self.phone_count,
            "phone_visible": self.phone_visible,
            "history_size": len(self.history),
            "recent_detections": sum(self.history) if self.history else 0,
        }

    def reset_count(self):
        """Reset daily count."""
        self.phone_count = 0


# =============================================================================
# Robot Animations
# =============================================================================

def play_sound_safe(reachy: ReachyMini, sound_name: str):
    """Play a sound, catching any errors."""
    try:
        reachy.media.play_sound(sound_name)
    except Exception as e:
        logger.debug(f"Sound playback error: {e}")


def curious_look(reachy: ReachyMini):
    """Curious head tilt - first offense."""
    head = create_head_pose(z=5, roll=15, mm=True, degrees=True)
    reachy.goto_target(head=head, antennas=[0.4, 0.2], duration=0.4, method="minjerk")
    time.sleep(0.3)


def disappointed_shake(reachy: ReachyMini):
    """Disappointed head shake - repeat offense."""
    for _ in range(3):
        head = create_head_pose(roll=-15, mm=True, degrees=True)
        reachy.goto_target(head=head, antennas=[-0.1, -0.1], duration=0.15)
        time.sleep(0.15)
        head = create_head_pose(roll=15, mm=True, degrees=True)
        reachy.goto_target(head=head, antennas=[-0.1, -0.1], duration=0.15)
        time.sleep(0.15)

    # Return to neutral
    head = create_head_pose(roll=0, mm=True, degrees=True)
    reachy.goto_target(head=head, antennas=[0.0, 0.0], duration=0.3)


def dramatic_sigh(reachy: ReachyMini):
    """Dramatic sigh and look away - many offenses."""
    # Look up (exasperated)
    head = create_head_pose(z=10, roll=0, mm=True, degrees=True)
    reachy.goto_target(head=head, antennas=[0.5, 0.5], duration=0.4)
    time.sleep(0.4)

    # Slump down
    head = create_head_pose(z=-5, roll=0, mm=True, degrees=True)
    reachy.goto_target(head=head, antennas=[-0.3, -0.3], duration=0.6)
    time.sleep(0.8)

    # Look away
    reachy.goto_target(body_yaw=np.deg2rad(30), duration=0.5)
    time.sleep(1.0)

    # Return
    head = create_head_pose(z=0, roll=0, mm=True, degrees=True)
    reachy.goto_target(head=head, antennas=[0.0, 0.0], body_yaw=0, duration=0.5)


def approving_nod(reachy: ReachyMini):
    """Approving nod - phone put down."""
    for _ in range(2):
        head = create_head_pose(z=-3, mm=True, degrees=True)
        reachy.goto_target(head=head, antennas=[0.2, 0.2], duration=0.2)
        time.sleep(0.2)
        head = create_head_pose(z=3, mm=True, degrees=True)
        reachy.goto_target(head=head, antennas=[0.2, 0.2], duration=0.2)
        time.sleep(0.2)

    # Return to neutral
    head = create_head_pose(z=0, mm=True, degrees=True)
    reachy.goto_target(head=head, antennas=[0.1, 0.1], duration=0.3)


def idle_breathing(reachy: ReachyMini):
    """Gentle idle animation."""
    reachy.goto_target(antennas=[0.15, 0.15], duration=1.5, method="minjerk")
    time.sleep(1.5)
    reachy.goto_target(antennas=[0.05, 0.05], duration=1.5, method="minjerk")
    time.sleep(1.5)


def get_animation_for_count(count: int):
    """Get appropriate animation based on offense count."""
    if count <= 1:
        return curious_look
    elif count <= 3:
        return disappointed_shake
    else:
        return dramatic_sigh


# =============================================================================
# Main App
# =============================================================================

class JudgyReachyNoPhone(ReachyMiniApp):
    """Phone Shame - Get off your phone! 📱🤖"""

    custom_app_url: str | None = "http://localhost:7863"
    dont_start_webserver: bool = True
    request_media_backend: str | None = "default"

    def __init__(self):
        super().__init__()
        self.config = Config()

        # Components
        self.detector = PhoneDetector(confidence=self.config.DETECTION_CONFIDENCE)
        self.llm = LLMResponder(api_key=self.config.GROQ_API_KEY)
        self.tts = TextToSpeech(
            elevenlabs_key=self.config.ELEVENLABS_API_KEY,
            voice=self.config.EDGE_TTS_VOICE
        )

        # State
        self.is_running = False
        self.is_monitoring = False
        self.praise_enabled = True
        self._lock = threading.Lock()

        # Stats
        self.session_start = None
        self.total_shames = 0
        self.longest_streak = 0
        self.current_streak_start = None
        self.frozen_streak = 0  # Stores streak when monitoring is stopped

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        """Main loop."""

        # Start UI
        ui_thread = threading.Thread(
            target=self._run_ui,
            args=(reachy_mini, stop_event),
            daemon=True
        )
        ui_thread.start()

        # Initialize detector
        self.detector.initialize()

        # Main loop
        breath_counter = 0
        BREATH_INTERVAL = 8
        last_tick = time.time()

        while not stop_event.is_set():
            current_time = time.time()
            delta = current_time - last_tick
            last_tick = current_time

            if self.is_monitoring:
                try:
                    # Get frame from robot camera
                    frame = reachy_mini.media.get_frame()

                    if frame is not None:
                        # Process frame
                        event = self.detector.process_frame(
                            frame,
                            pickup_threshold=self.config.PICKUP_THRESHOLD,
                            putdown_threshold=self.config.PUTDOWN_THRESHOLD,
                            cooldown=self.config.COOLDOWN_SECONDS
                        )

                        if event == "picked_up":
                            self._handle_phone_pickup(reachy_mini)
                        elif event == "put_down" and self.praise_enabled:
                            self._handle_phone_putdown(reachy_mini)

                except Exception as e:
                    logger.debug(f"Frame processing error: {e}")

                # Idle breathing when not reacting
                breath_counter += delta
                if breath_counter >= BREATH_INTERVAL:
                    breath_counter = 0
                    if self.is_monitoring and not self.detector.phone_visible:
                        try:
                            idle_breathing(reachy_mini)
                        except:
                            pass

            time.sleep(0.2)  # 5 Hz

        # Cleanup
        self.is_monitoring = False

    def _handle_phone_pickup(self, reachy: ReachyMini):
        """Handle phone pickup event."""
        count = self.detector.phone_count
        self.total_shames += 1

        # Reset streak
        if self.current_streak_start:
            streak_duration = time.time() - self.current_streak_start
            if streak_duration > self.longest_streak:
                self.longest_streak = streak_duration
        self.current_streak_start = None

        logger.info(f"Phone pickup #{count}!")

        # Get snarky response
        text = self.llm.get_response(count)
        logger.info(f"Response: {text}")

        # Generate and play audio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_path = loop.run_until_complete(self.tts.synthesize(text))
            loop.close()

            # Play audio
            reachy.media.play(audio_path)

            # Animate based on offense count
            animation = get_animation_for_count(count)
            animation(reachy)

        except Exception as e:
            logger.error(f"Shame response error: {e}")
            # Fallback: just animate
            play_sound_safe(reachy, "confused1.wav")
            disappointed_shake(reachy)

    def _handle_phone_putdown(self, reachy: ReachyMini):
        """Handle phone put down event."""
        logger.info("Phone put down!")

        # Start new streak
        self.current_streak_start = time.time()

        # Get praise
        text = self.llm.get_praise()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_path = loop.run_until_complete(self.tts.synthesize(text))
            loop.close()

            reachy.media.play(audio_path)
            approving_nod(reachy)

        except Exception as e:
            logger.debug(f"Praise error: {e}")
            approving_nod(reachy)

    def _run_ui(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        """Run Gradio UI."""

        def start_monitoring(groq_key, eleven_key, cooldown, praise):
            # Update config
            if groq_key:
                self.llm = LLMResponder(api_key=groq_key)
            if eleven_key:
                self.tts = TextToSpeech(elevenlabs_key=eleven_key)

            self.config.COOLDOWN_SECONDS = cooldown
            self.praise_enabled = praise

            self.is_monitoring = True
            self.session_start = time.time()
            self.detector.reset_count()
            self.current_streak_start = time.time()
            self.frozen_streak = 0  # Reset frozen streak when starting

            return get_status(), "🛑 Stop Monitoring", gr.update(interactive=True)

        def stop_monitoring():
            # Freeze the current streak at the moment of stopping
            if self.current_streak_start:
                self.frozen_streak = time.time() - self.current_streak_start
            else:
                self.frozen_streak = 0

            self.is_monitoring = False
            return get_status(), "▶️ Start Monitoring", gr.update(interactive=True)

        def toggle_monitoring(groq_key, eleven_key, cooldown, praise):
            if self.is_monitoring:
                return stop_monitoring()
            else:
                return start_monitoring(groq_key, eleven_key, cooldown, praise)

        def get_status():
            stats = self.detector.get_stats()

            # Calculate streak
            if self.is_monitoring:
                # When monitoring, calculate in real-time
                if self.current_streak_start:
                    current_streak = time.time() - self.current_streak_start
                else:
                    current_streak = 0
            else:
                # When not monitoring, use the frozen streak
                current_streak = self.frozen_streak

            streak_display = self._format_duration(max(current_streak, self.longest_streak))

            # Status color
            if not self.is_monitoring:
                status_color = "#6b7280"
                status_text = "Not monitoring"
            elif stats["phone_visible"]:
                status_color = "#ef4444"
                status_text = "📱 PHONE DETECTED!"
            else:
                status_color = "#22c55e"
                status_text = "✅ Phone-free"

            return f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 48px; margin-bottom: 10px;">📱🤖</div>
                    <div style="font-size: 18px; font-weight: 600; color: {status_color};">
                        {status_text}
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                    <div style="background: #fef2f2; padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 32px; font-weight: 700; color: #ef4444;">
                            {stats['phone_count']}
                        </div>
                        <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">
                            Pickups Today
                        </div>
                    </div>

                    <div style="background: #f0fdf4; padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 32px; font-weight: 700; color: #22c55e;">
                            {self.total_shames}
                        </div>
                        <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">
                            Total Shames
                        </div>
                    </div>

                    <div style="background: #eff6ff; padding: 15px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 32px; font-weight: 700; color: #3b82f6;">
                            {streak_display}
                        </div>
                        <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">
                            Best Streak
                        </div>
                    </div>
                </div>

                <div style="background: #f3f4f6; padding: 12px; border-radius: 8px; margin-top: 15px;">
                    <div style="font-size: 13px; color: #6b7280;">
                        <strong>Mode:</strong>
                        {"LLM + TTS" if self.llm.client else "Pre-written lines"}
                        → {"ElevenLabs" if self.tts.eleven_client else "Edge TTS"}
                    </div>
                </div>
            </div>
            """

        def test_shame():
            """Test the shame response."""
            if not self.is_monitoring:
                self.is_monitoring = True  # Temporarily enable

            self.detector.phone_count += 1
            self._handle_phone_pickup(reachy_mini)

            return get_status()

        # Build UI
        with gr.Blocks(
            title="Phone Shame",
            css="""
                .gradio-container { max-width: 500px !important; margin: auto; }
                footer { display: none !important; }
            """
        ) as demo:

            gr.HTML("""
            <div style="background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
                        color: white; padding: 20px; text-align: center;
                        border-radius: 12px; margin-bottom: 15px;">
                <h1 style="margin: 0; font-size: 24px;">📱 Phone Shame 🤖</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">
                    Get off your phone!
                </p>
            </div>
            """)

            status_html = gr.HTML(value=get_status())

            with gr.Accordion("⚙️ Settings", open=False):
                groq_key = gr.Textbox(
                    label="Groq API Key (optional)",
                    placeholder="Get free at console.groq.com",
                    type="password"
                )
                eleven_key = gr.Textbox(
                    label="ElevenLabs API Key (optional)",
                    placeholder="Get free at elevenlabs.io",
                    type="password"
                )
                cooldown = gr.Slider(
                    minimum=10, maximum=120, value=30, step=5,
                    label="Cooldown between shames (seconds)"
                )
                praise_toggle = gr.Checkbox(
                    value=True,
                    label="Praise when phone is put down"
                )

            with gr.Row():
                toggle_btn = gr.Button(
                    "▶️ Start Monitoring",
                    variant="primary",
                    size="lg",
                    scale=2
                )
                test_btn = gr.Button(
                    "🧪 Test",
                    size="lg",
                    scale=1
                )

            # Auto-refresh
            timer = gr.Timer(value=0.5)
            timer.tick(fn=get_status, outputs=[status_html])

            # Handlers
            toggle_btn.click(
                fn=toggle_monitoring,
                inputs=[groq_key, eleven_key, cooldown, praise_toggle],
                outputs=[status_html, toggle_btn, toggle_btn]
            )
            test_btn.click(fn=test_shame, outputs=[status_html])

        demo.launch(server_port=7863, quiet=True, prevent_thread_lock=True)

        while not stop_event.is_set():
            time.sleep(1)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            return f"{mins}m"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h{mins}m"


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = JudgyReachyNoPhone()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
