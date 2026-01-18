"""
Judgy Reachy No Phone - Get off your phone! 📱🤖

A Reachy Mini app that detects when you pick up your phone
and shames you with snarky comments.
"""

import time
import threading
import logging
import asyncio
import base64

import cv2

from reachy_mini import ReachyMini, ReachyMiniApp
from pydantic import BaseModel

from .config import Config
from .detection import PhoneDetector
from .audio import LLMResponder, TextToSpeech
from .animations import (
    play_sound_safe,
    get_animation_for_count,
    disappointed_shake,
    approving_nod,
    idle_breathing
)

logger = logging.getLogger(__name__)


class JudgyReachyNoPhone(ReachyMiniApp):
    """Judgy Reachy No Phone - Get off your phone! 📱🤖"""

    custom_app_url: str | None = "http://0.0.0.0:8042"
    dont_start_webserver: bool = False
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
        self.has_previous_session = False  # Track if there's data to continue from
        self._lock = threading.Lock()

        # Stats
        self.session_start = None
        self.total_shames = 0
        self.longest_streak = 0
        self.current_streak_start = None
        self.frozen_streak = 0  # Stores streak when monitoring is stopped
        self.frozen_phone_count = 0  # Store phone count when stopped

        # Camera thread state
        self.latest_frame = None
        self.latest_frame_jpeg = None  # JPEG encoded frame for web display
        self.camera_running = False
        self.camera_fps = 0
        self.detection_event_queue = []

    def _camera_thread(self, webcam, stop_event: threading.Event):
        """Fast camera capture and encoding thread."""
        fps_counter = 0
        fps_start = time.time()
        detection_skip = 0

        logger.info("Camera thread started")

        try:
            while not stop_event.is_set() and self.camera_running:
                ret, frame = webcam.read()
                if not ret:
                    time.sleep(0.01)
                    continue

                # Store frame for detection
                self.latest_frame = frame.copy()

                # Calculate FPS
                fps_counter += 1
                if time.time() - fps_start >= 1.0:
                    self.camera_fps = fps_counter
                    fps_counter = 0
                    fps_start = time.time()

                # Run detection every 3rd frame
                if self.is_monitoring and (detection_skip % 3 == 0):
                    try:
                        event = self.detector.process_frame(
                            frame,
                            pickup_threshold=self.config.PICKUP_THRESHOLD,
                            putdown_threshold=self.config.PUTDOWN_THRESHOLD,
                            cooldown=self.config.COOLDOWN_SECONDS
                        )
                        # Store event for main thread to handle
                        if event:
                            self.detection_event_queue.append(event)
                    except Exception as e:
                        logger.error(f"Detection error: {e}")

                detection_skip += 1

                # Draw detection boxes
                frame_with_boxes = self.detector.draw_detections(frame)

                # Draw FPS
                cv2.putText(frame_with_boxes, f"FPS: {self.camera_fps}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Draw model name
                cv2.putText(frame_with_boxes, "Model: YOLO", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                status = "📱 MONITORING" if self.is_monitoring else "⏸️ PAUSED"
                cv2.putText(frame_with_boxes, status, (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                # Encode as JPEG for web display
                _, buffer = cv2.imencode('.jpg', frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 85])
                self.latest_frame_jpeg = base64.b64encode(buffer).decode('utf-8')

                time.sleep(0.01)  # ~100 FPS max

        finally:
            logger.info("Camera thread stopped")

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

        # For testing: Use Mac webcam instead of robot camera
        USE_WEBCAM = True  # Set to False to use robot camera
        webcam = None
        if USE_WEBCAM:
            logger.info("Opening Mac webcam for testing...")
            webcam = cv2.VideoCapture(0)
            if not webcam.isOpened():
                logger.error("Failed to open webcam!")
                webcam = None
            else:
                logger.info("Webcam opened successfully!")
                self.camera_running = True

                # Start fast camera thread
                camera_thread = threading.Thread(
                    target=self._camera_thread,
                    args=(webcam, stop_event),
                    daemon=True
                )
                camera_thread.start()

        # Detection and robot control loop (separate from camera display)
        breath_counter = 0
        BREATH_INTERVAL = 8
        last_tick = time.time()

        try:
            while not stop_event.is_set():
                current_time = time.time()
                delta = current_time - last_tick
                last_tick = current_time

                # Process detection events from camera thread
                while self.detection_event_queue:
                    event = self.detection_event_queue.pop(0)
                    try:
                        if event == "picked_up":
                            self._handle_phone_pickup(reachy_mini)
                        elif event == "put_down" and self.praise_enabled:
                            self._handle_phone_putdown(reachy_mini)
                    except Exception as e:
                        logger.error(f"Event handling error: {e}")

                # Idle breathing when not reacting - only if no pending events
                breath_counter += delta
                if breath_counter >= BREATH_INTERVAL:
                    breath_counter = 0
                    # Only do idle breathing if no events pending (to avoid blocking)
                    if self.is_monitoring and not self.detector.phone_visible and len(self.detection_event_queue) == 0:
                        try:
                            idle_breathing(reachy_mini)
                        except:
                            pass

                # Faster loop for responsive event processing
                time.sleep(0.05)  # 20 FPS = 50ms max delay

        finally:
            # Stop camera thread
            self.camera_running = False
            if webcam is not None:
                webcam.release()
                logger.info("Webcam released")

        # Cleanup
        self.is_monitoring = False

    def _handle_phone_pickup(self, reachy: ReachyMini):
        """Handle phone pickup event."""
        start_time = time.time()
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
        llm_start = time.time()
        text = self.llm.get_response(count)
        logger.info(f"Response: {text} (LLM took {time.time() - llm_start:.2f}s)")

        # Generate and play audio
        try:
            tts_start = time.time()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_path = loop.run_until_complete(self.tts.synthesize(text))
            loop.close()
            logger.info(f"TTS took {time.time() - tts_start:.2f}s")

            # Play audio
            audio_start = time.time()
            reachy.media.play_sound(audio_path)
            logger.info(f"Audio playback took {time.time() - audio_start:.2f}s")

            # Animate based on offense count
            animation = get_animation_for_count(count)
            animation(reachy)

            logger.info(f"Total pickup handling: {time.time() - start_time:.2f}s")

        except Exception as e:
            logger.error(f"Shame response error: {e}")
            # Fallback: just animate
            play_sound_safe(reachy, "confused1.wav")
            disappointed_shake(reachy)

    def _handle_phone_putdown(self, reachy: ReachyMini):
        """Handle phone put down event."""
        start_time = time.time()
        logger.info("Phone put down!")

        # Start new streak
        self.current_streak_start = time.time()

        # Get praise
        llm_start = time.time()
        text = self.llm.get_praise()
        logger.info(f"Praise: {text} (LLM took {time.time() - llm_start:.2f}s)")

        try:
            tts_start = time.time()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_path = loop.run_until_complete(self.tts.synthesize(text))
            loop.close()
            logger.info(f"TTS took {time.time() - tts_start:.2f}s")

            audio_start = time.time()
            reachy.media.play_sound(audio_path)
            logger.info(f"Audio playback took {time.time() - audio_start:.2f}s")

            approving_nod(reachy)
            logger.info(f"Total putdown handling: {time.time() - start_time:.2f}s")

        except Exception as e:
            logger.debug(f"Praise error: {e}")
            approving_nod(reachy)

    def _run_ui(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        """Setup FastAPI routes for the UI."""

        # API models
        class ToggleRequest(BaseModel):
            groq_key: str = ""
            eleven_key: str = ""
            cooldown: int = 30
            praise: bool = True
            reset: bool = False  # If True, reset all stats (Start Fresh)

        # API endpoint: Get video frame
        @self.settings_app.get("/api/video-frame")
        def get_video_frame():
            if self.latest_frame_jpeg:
                return {"frame": self.latest_frame_jpeg, "fps": self.camera_fps}
            return {"frame": None, "fps": 0}

        # API endpoint: Get status
        @self.settings_app.get("/api/status")
        def get_status():
            stats = self.detector.get_stats()

            # Calculate streak
            if self.is_monitoring:
                if self.current_streak_start:
                    current_streak = time.time() - self.current_streak_start
                else:
                    current_streak = 0
            else:
                current_streak = self.frozen_streak

            current_streak_display = self._format_duration(current_streak)
            longest_streak_display = self._format_duration(self.longest_streak)

            # Status text
            if not self.is_monitoring:
                status_text = "Not monitoring"
            elif stats["phone_visible"]:
                status_text = "📱 PHONE DETECTED!"
            else:
                status_text = "✅ Phone-free"

            mode_text = f"YOLO | {'LLM + TTS' if self.llm.client else 'Pre-written lines'} → {'ElevenLabs' if self.tts.eleven_client else 'Edge TTS'}"

            # Determine button text
            if self.is_monitoring:
                button_text = "🛑 Stop Monitoring"
            elif self.has_previous_session:
                button_text = "▶️ Continue Monitoring"
            else:
                button_text = "▶️ Start Monitoring"

            return {
                "status_text": status_text,
                "phone_count": stats['phone_count'],
                "total_shames": self.total_shames,
                "current_streak": current_streak_display,
                "longest_streak": longest_streak_display,
                "mode": mode_text,
                "is_monitoring": self.is_monitoring,
                "button_text": button_text,
                "has_previous_session": self.has_previous_session
            }

        # API endpoint: Toggle monitoring
        @self.settings_app.post("/api/toggle")
        def toggle_monitoring(req: ToggleRequest):
            if self.is_monitoring:
                # Stop monitoring - save current state
                if self.current_streak_start:
                    self.frozen_streak = time.time() - self.current_streak_start
                else:
                    self.frozen_streak = 0

                self.frozen_phone_count = self.detector.phone_count
                self.has_previous_session = True
                self.is_monitoring = False

                # Return appropriate button text based on whether there's data
                button_text = "▶️ Continue Monitoring" if self.has_previous_session else "▶️ Start Monitoring"
                return {"button_text": button_text}
            else:
                # Start or Continue monitoring
                if req.groq_key:
                    self.llm = LLMResponder(api_key=req.groq_key)
                if req.eleven_key:
                    self.tts = TextToSpeech(elevenlabs_key=req.eleven_key)

                self.config.COOLDOWN_SECONDS = req.cooldown
                self.praise_enabled = req.praise

                self.is_monitoring = True
                self.session_start = time.time()

                if req.reset or not self.has_previous_session:
                    # Start Fresh - reset everything
                    self.detector.reset_count()
                    self.total_shames = 0
                    self.longest_streak = 0
                    self.current_streak_start = time.time()
                    self.frozen_streak = 0
                    self.frozen_phone_count = 0
                    self.has_previous_session = False
                else:
                    # Continue - restore previous state
                    self.detector.phone_count = self.frozen_phone_count
                    self.current_streak_start = time.time() - self.frozen_streak if self.frozen_streak > 0 else time.time()

                return {"button_text": "🛑 Stop Monitoring"}

        # API endpoint: Reset all stats
        @self.settings_app.post("/api/reset")
        def reset_stats():
            """Reset all statistics and start fresh."""
            self.detector.reset_count()
            self.total_shames = 0
            self.longest_streak = 0
            self.current_streak_start = None
            self.frozen_streak = 0
            self.frozen_phone_count = 0
            self.has_previous_session = False
            return {
                "success": True,
                "button_text": "▶️ Start Monitoring"
            }

        # API endpoint: Test shame
        @self.settings_app.post("/api/test")
        def test_shame():
            if not self.is_monitoring:
                self.is_monitoring = True
            self.detector.phone_count += 1
            self._handle_phone_pickup(reachy_mini)
            return {"success": True}

        # Keep thread alive
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = JudgyReachyNoPhone()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
