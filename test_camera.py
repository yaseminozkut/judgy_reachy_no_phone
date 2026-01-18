"""
Standalone camera test - no robot/simulation needed
Tests phone detection at full speed
"""

import cv2
import time
import logging
from judgy_reachy_no_phone.main import PhoneDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Open webcam
    logger.info("Opening webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logger.error("Failed to open webcam!")
        return

    logger.info("Webcam opened successfully!")

    # Initialize detector
    detector = PhoneDetector(confidence=0.3)
    detector.initialize()

    # FPS tracking
    fps_counter = 0
    fps_start = time.time()
    current_fps = 0

    logger.info("Starting detection... Press 'Q' to quit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Run detection
            phone_detected = detector.detect_phone(frame)

            # Draw detection boxes
            frame_with_boxes = detector.draw_detections(frame)

            # Calculate FPS
            fps_counter += 1
            if time.time() - fps_start >= 1.0:
                current_fps = fps_counter
                logger.info(f"FPS: {current_fps} | Phone: {phone_detected}")
                fps_counter = 0
                fps_start = time.time()

            # Draw FPS and status
            cv2.putText(frame_with_boxes, f"FPS: {current_fps}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            status_text = "PHONE DETECTED!" if phone_detected else "No phone"
            status_color = (0, 255, 0) if phone_detected else (255, 255, 255)
            cv2.putText(frame_with_boxes, status_text, (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

            cv2.putText(frame_with_boxes, "Press 'Q' to quit", (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Show frame
            cv2.imshow("Phone Detection Test", frame_with_boxes)

            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Test completed")

if __name__ == "__main__":
    main()
