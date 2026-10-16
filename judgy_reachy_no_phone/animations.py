"""Robot animations for Judgy Reachy No Phone app."""

import time
import logging
import threading
import numpy as np

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from reachy_mini.reachy_mini import INIT_HEAD_POSE

logger = logging.getLogger(__name__)

IDLE_SWAY_LOOP_HZ = 50
IDLE_ANTENNA_AMP_DEG = 15.0
IDLE_ANTENNA_FREQ_HZ = 0.3
IDLE_HEAD_SMOOTHING = 0.04


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


def antenna_sway_loop(
    reachy: ReachyMini,
    stop_event: threading.Event,
    playing_move: threading.Event,
):
    """Continuous sinusoidal antenna sway. Pauses while `playing_move` is set
    so shame/praise animations can take over without fighting for the antennas.
    """
    t0 = time.time()
    dt = 1.0 / IDLE_SWAY_LOOP_HZ
    amp_rad = np.deg2rad(IDLE_ANTENNA_AMP_DEG)
    pose = INIT_HEAD_POSE.copy()

    while not stop_event.is_set():
        if playing_move.is_set():
            pose = INIT_HEAD_POSE.copy()
            time.sleep(dt)
            continue
        t = time.time() - t0
        a = amp_rad * np.sin(2.0 * np.pi * IDLE_ANTENNA_FREQ_HZ * t)
        pose = (1.0 - IDLE_HEAD_SMOOTHING) * pose + IDLE_HEAD_SMOOTHING * INIT_HEAD_POSE
        try:
            reachy.set_target(head=pose, antennas=[a, -a])
        except Exception as e:
            logger.debug(f"Sway tick error: {e}")
        time.sleep(dt)


def get_animation_for_count(count: int):
    """Get appropriate animation based on offense count."""
    if count <= 1:
        return curious_look
    elif count <= 3:
        return disappointed_shake
    else:
        return dramatic_sigh
