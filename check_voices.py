#!/usr/bin/env python3
"""
Check which ElevenLabs voices are available to you.
Run this with: python check_voices.py YOUR_API_KEY
"""
import sys
from elevenlabs import ElevenLabs

if len(sys.argv) < 2:
    print("Usage: python check_voices.py YOUR_ELEVENLABS_API_KEY")
    sys.exit(1)

api_key = sys.argv[1]
client = ElevenLabs(api_key=api_key)

print("\n=== Available Voices in Your Account ===\n")

try:
    voices = client.voices.get_all()

    print(f"Total voices available: {len(voices.voices)}\n")

    for voice in voices.voices:
        # Check if it's likely a premade/stock voice
        is_premade = hasattr(voice, 'category') and voice.category == 'premade'
        voice_type = "STOCK" if is_premade else "CUSTOM"

        print(f"  [{voice_type}] {voice.name}")
        print(f"           ID: {voice.voice_id}")
        if hasattr(voice, 'labels'):
            labels = ', '.join([f"{k}: {v}" for k, v in voice.labels.items()])
            print(f"           Labels: {labels}")
        print()

    print("\n=== Checking voices in your config.py ===\n")

    config_voices = {
        "mixtape": "H10ItvDnkRN5ysrvzT9J",
        "angry_boss": "TxWZERZ5Hc6h9dGxVmXa",
        "sarcastic": "FGY2WhTYpPnrIDTdsKH5",
        "disappointed_parent": "Xb7hH8MSUJpSbSDYk0k2",
        "motivational_coach": "IKne3meq5aSn9XLyUdCD",
        "absurdist": "cgSgspJ2msm6clMCkdW9",
        "corporate_ai": "weA4Q36twV5kwSaTEL0Q",
        "british_butler": "JBFqnCBsd6RMkjVDRZzb"
    }

    all_voice_ids = [v.voice_id for v in voices.voices]

    problems_found = False
    for personality, vid in config_voices.items():
        if vid in all_voice_ids:
            voice = next(v for v in voices.voices if v.voice_id == vid)
            print(f"  ✓ {personality}: {voice.name} ({vid})")
        else:
            print(f"  ✗ {personality}: {vid} - NOT AVAILABLE!")
            problems_found = True

    if problems_found:
        print("\n⚠️  Some voices in your config are NOT available to your account.")
        print("    You need to replace them with voices you have access to.")
        print("    Use the voice IDs from the list above.")
    else:
        print("\n✓ All config voices are available!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
