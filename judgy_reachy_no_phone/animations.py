"""Robot animations for Judgy Reachy No Phone app."""

import time
import logging
import numpy as np

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

logger = logging.getLogger(__name__)


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
    """Gentle idle animation - kept short to avoid blocking events."""
    reachy.goto_target(antennas=[0.15, 0.15], duration=0.8, method="minjerk")
    time.sleep(0.8)
    reachy.goto_target(antennas=[0.05, 0.05], duration=0.8, method="minjerk")
    time.sleep(0.8)


def get_animation_for_count(count: int):
    """Get appropriate animation based on offense count."""
    if count <= 1:
        return curious_look
    elif count <= 3:
        return disappointed_shake
    else:
        return dramatic_sigh
