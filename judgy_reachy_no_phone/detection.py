"""Phone detection using YOLO."""

import time
import logging
from collections import deque
from typing import Optional, Dict, Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class PhoneDetector:
    """Detect phone in camera frame using YOLO."""

    PHONE_CLASS_ID = 67  # "cell phone" in COCO dataset

    # Adaptive confidence thresholds (like demo.js)
    DETECTION_CONFIDENCE = 0.5  # Initial detection threshold
    TRACKING_CONFIDENCE = 0.2   # Lower threshold when tracking existing phone
    TRACKING_PERSIST_FRAMES = 3  # Keep tracking for N frames after losing detection

    def __init__(self, confidence: float = 0.5, loading_callback=None):
        self.confidence = confidence  # Kept for backward compatibility
        self.yolo_model = None
        self._initialized = False
        self.loading_callback = loading_callback  # Callback to report loading progress

        # State tracking
        self.phone_visible = False
        self.consecutive_phone = 0
        self.consecutive_no_phone = 0
        self.phone_count = 0
        self.last_reaction_time = 0

        # History for robust detection
        self.history = deque(maxlen=30)

        # Tracking persistence (like demo.js)
        self.last_phone_box: Optional[Dict[str, Any]] = None
        self.frames_without_detection = 0

        # For visualization
        self.last_detections = []

        # Loading state (like demo.js)
        self.loading_status = "idle"  # idle, loading, ready, error
        self.loading_message = ""

    def initialize(self):
        """Load YOLO model with progress reporting."""
        if self._initialized:
            return True

        try:
            # Report loading start
            self.loading_status = "loading"
            self.loading_message = "Loading YOLO26m model..."
            if self.loading_callback:
                self.loading_callback("loading", "Loading YOLO26m model...")
            logger.info("Starting YOLO model initialization...")

            import torch
            from ultralytics import YOLO

            # Auto-detect best device (supports CUDA, MPS, and CPU)
            if torch.cuda.is_available():
                device = 'cuda'  # NVIDIA GPU
            elif torch.backends.mps.is_available():
                device = 'mps'   # Apple Silicon GPU
            else:
                device = 'cpu'   # Fallback to CPU

            self.loading_message = f"Loading YOLO26m on {device.upper()}..."
            if self.loading_callback:
                self.loading_callback("loading", f"Loading YOLO26m on {device.upper()}...")

            # Use pretrained YOLO26m model (better accuracy than 26n)
            self.yolo_model = YOLO("yolo26m.pt").to(device)

            # Report success
            self.loading_status = "ready"
            self.loading_message = f"Model ready on {device.upper()}"
            if self.loading_callback:
                self.loading_callback("ready", f"Model ready on {device.upper()}")

            self._initialized = True
            logger.info(f"YOLO26m model loaded on {device.upper()}")
            return True

        except Exception as e:
            # Report error
            self.loading_status = "error"
            self.loading_message = f"Failed to load model: {str(e)}"
            if self.loading_callback:
                self.loading_callback("error", f"Failed to load model: {str(e)}")
            logger.error(f"Failed to load YOLO: {e}")
            return False

    def detect_phone(self, frame: np.ndarray) -> bool:
        """
        Check if phone is in frame (backward compatible).

        For new tracking features, use detect_phone_with_tracking() instead.
        """
        detections = self.detect_phone_with_tracking(frame)
        return len(detections) > 0

    def detect_phone_with_tracking(self, frame: np.ndarray) -> list:
        """
        Detect phone with adaptive confidence and tracking persistence.

        Returns:
            List of detection dicts with keys: x1, y1, x2, y2, confidence, class_name
        """
        if not self._initialized:
            if not self.initialize():
                return []

        try:
            # Adaptive confidence: lower threshold when tracking existing phone
            confidence_threshold = (
                self.TRACKING_CONFIDENCE if self.last_phone_box
                else self.DETECTION_CONFIDENCE
            )

            # Run YOLO detection with adaptive threshold
            results = self.yolo_model(frame, verbose=False, conf=confidence_threshold)
            self.last_detections = results  # Save for visualization

            # Find best phone detection (highest confidence)
            best_phone = None
            best_score = 0.0

            for result in results:
                for box in result.boxes:
                    if int(box.cls) == self.PHONE_CLASS_ID:
                        conf = float(box.conf)

                        # Track the most confident phone
                        if conf > best_score:
                            best_score = conf
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            best_phone = {
                                'x1': x1,
                                'y1': y1,
                                'x2': x2,
                                'y2': y2,
                                'confidence': conf,
                                'class_name': 'cell phone'
                            }

            # Tracking persistence logic
            new_detections = []

            if best_phone:
                # Phone detected - update tracking
                self.last_phone_box = best_phone
                self.frames_without_detection = 0
                new_detections.append(best_phone)

            elif self.last_phone_box and self.frames_without_detection < self.TRACKING_PERSIST_FRAMES:
                # No detection but still tracking - persist last known box
                self.frames_without_detection += 1
                persisted_box = self.last_phone_box.copy()
                persisted_box['confidence'] *= 0.9  # Fade confidence
                new_detections.append(persisted_box)

            else:
                # Lost tracking completely
                self.last_phone_box = None
                self.frames_without_detection = 0

            return new_detections

        except Exception as e:
            logger.debug(f"YOLO detection error: {e}")
            return []

    def draw_detections(self, frame: np.ndarray) -> np.ndarray:
        """Draw detection boxes on frame."""
        if not self.last_detections:
            return frame

        frame_with_boxes = frame.copy()

        try:
            for result in self.last_detections:
                for box in result.boxes:
                    cls = int(box.cls)

                    # Only draw phones
                    if cls != self.PHONE_CLASS_ID:
                        continue

                    conf = float(box.conf)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Get class name from model
                    class_name = self.yolo_model.names[cls] if self.yolo_model else "phone"

                    # Draw green box for phone
                    cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    text = f"{class_name} {conf:.2f}"
                    cv2.putText(frame_with_boxes, text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        except Exception as e:
            logger.debug(f"Draw error: {e}")

        return frame_with_boxes

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
        # Use new tracking-enabled detection
        detections = self.detect_phone_with_tracking(frame)
        phone_in_frame = len(detections) > 0

        # Add to history
        self.history.append(phone_in_frame)

        # Update consecutive counters
        if phone_in_frame:
            self.consecutive_phone += 1
            self.consecutive_no_phone = 0
        else:
            self.consecutive_no_phone += 1

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

        # Periodic reactions while STILL holding phone (like demo.js)
        if self.phone_visible and phone_in_frame:
            now = time.time()
            if now - self.last_reaction_time >= cooldown:
                self.phone_count += 1
                self.last_reaction_time = now
                return "picked_up"  # Shame again!

        # Check for phone put down (slow to confirm - avoids flickering)
        if self.consecutive_no_phone >= putdown_threshold and self.phone_visible:
            self.phone_visible = False
            self.consecutive_phone = 0
            # Reset cooldown timer so next pickup can trigger immediately
            self.last_reaction_time = 0
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

    def reset_tracking(self):
        """Reset tracking state (useful when stopping/starting monitoring)."""
        self.phone_visible = False
        self.consecutive_phone = 0
        self.consecutive_no_phone = 0
        self.last_phone_box = None
        self.frames_without_detection = 0
        self.last_reaction_time = 0
        logger.debug("Tracking state reset")
