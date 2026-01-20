"""Phone detection using YOLO."""

import time
import logging
from collections import deque
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class PhoneDetector:
    """Detect phone in camera frame using YOLO."""

    PHONE_CLASS_ID = 67  # "cell phone" in COCO dataset

    def __init__(self, confidence: float = 0.5):
        self.confidence = confidence
        self.yolo_model = None
        self._initialized = False

        # State tracking
        self.phone_visible = False
        self.consecutive_phone = 0
        self.consecutive_no_phone = 0
        self.phone_count = 0
        self.last_reaction_time = 0

        # History for robust detection
        self.history = deque(maxlen=30)

        # For visualization
        self.last_detections = []

    def initialize(self):
        """Load YOLO model."""
        if self._initialized:
            return True

        try:
            from ultralytics import YOLO
            self.yolo_model = YOLO("yolo26n.pt")
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
            results = self.yolo_model(frame, verbose=False, conf=self.confidence)
            self.last_detections = results  # Save for visualization

            for result in results:
                for box in result.boxes:
                    if int(box.cls) == self.PHONE_CLASS_ID:
                        return True
            return False
        except Exception as e:
            logger.debug(f"YOLO detection error: {e}")
            return False

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

                    # Draw green box for phone
                    cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    text = f"cell phone {conf:.2f}"
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
        phone_in_frame = self.detect_phone(frame)

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
