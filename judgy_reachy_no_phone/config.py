"""Configuration and constants for Judgy Reachy No Phone app."""

import random
from dataclasses import dataclass


@dataclass
class Config:
    """App configuration."""
    # Detection settings
    PICKUP_THRESHOLD: int = 3          # Frames to confirm phone pickup
    PUTDOWN_THRESHOLD: int = 15        # Frames to confirm phone put down (~3 sec)
    DETECTION_CONFIDENCE: float = 0.3  # Higher = fewer false positives
    COOLDOWN_SECONDS: float = 10.0     # Min time between shames

    # API Keys (optional - leave empty for free defaults)
    GROQ_API_KEY: str = ""             # Get free at console.groq.com
    ELEVENLABS_API_KEY: str = ""       # Get free at elevenlabs.io

    # TTS settings
    EDGE_TTS_VOICE: str = "en-US-GuyNeural"  # Free voice
    ELEVENLABS_VOICE_ID: str = "JBFqnCBsd6RMkjVDRZzb"  # "George"


# Pre-written snarky lines (no API needed)
SNARKY_LINES = {
    1: [
        "The phone? Already?",
        #"Oh, checking something important?",
    ],
    2: [
        #"Again?",
        "Twice now.",
        #"Back to the phone I see.",
        #"Hey!",
        #"Focus!",
    ],
    3: [
        #"Third time's the charm?",
        #"Stop it!",
        "Really? Three times?",
        #"Put your phone down.",
    ],
    "many": [
        "I've lost count.",
        "I'm disappointed in you.",
        "Hey!",
        "Focus!",
        "Stop it!",
        "Put your phone down.",
        "Phone addiction is real.",
        "Your screen time is weeping.",
        "At this point just glue it to your hand.",
        "The phone isn't going anywhere, you know.",
        "Do you even remember what you were doing?",
    ]
}

PRAISE_LINES = [
    "Good. Back to work.",
    "There we go.",
    "Finally.",
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
