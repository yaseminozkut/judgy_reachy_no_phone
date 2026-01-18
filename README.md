---
title: Judgy Reachy No Phone
emoji: 📱
colorFrom: red
colorTo: orange
sdk: static
pinned: false
short_description: Get off your phone! Reachy Mini shames you with snarky comments
tags:
 - reachy_mini
 - reachy_mini_python_app
---

# 📱 Judgy Reachy No Phone 🤖

**A Reachy Mini app that detects when you pick up your phone and shames you with snarky comments.**

Stop checking your phone and get back to work! This app uses computer vision to detect when you pick up your phone and makes Reachy Mini give you a judgmental, snarky comment to shame you back to productivity.

## Features

- 📱 **Phone Detection**: Uses YOLOv8 to detect when you pick up your phone
- 🗣️ **Snarky Responses**: LLM-generated or pre-written judgmental comments
- 🔊 **Text-to-Speech**: Robot speaks the shame out loud with expressive voice
- 🤖 **Expressive Animations**: Different reactions based on offense count
- 📊 **Stats Tracking**: Pickup count, shame count, longest phone-free streak
- 🎮 **Web UI**: Gradio interface for monitoring and configuration

## How It Works

1. **Camera watches you** - Reachy Mini monitors the camera feed
2. **Phone detected** - YOLOv8 detects when you pick up your phone
3. **Shame delivered** - Robot gives you a snarky comment via TTS
4. **Robot reacts** - Expressive animations get more dramatic with repeat offenses

### Robot Reactions

| Offense Count | Animation | Reaction |
|---------------|-----------|----------|
| 1st pickup | Curious head tilt | "The phone? Already?" |
| 2-3 pickups | Disappointed head shake | "Again?" |
| 4+ pickups | Dramatic sigh, looks away | "I've lost count." |
| Phone down | Approving nod | "Good. Back to work." |

## 100% Free Stack

| Component | Free Option | Premium Option |
|-----------|-------------|----------------|
| Detection | YOLOv8 (local) | - |
| LLM | Pre-written lines | Groq (free tier) |
| TTS | Edge TTS (unlimited) | ElevenLabs (10k chars/month) |

## Installation

```bash
pip install .
```

### Optional: Enable LLM Responses

```bash
pip install .[llm]
```

Get free API key at [console.groq.com](https://console.groq.com)

### Optional: Enable Premium Voice

```bash
pip install .[premium-tts]
```

Get free API key at [elevenlabs.io](https://elevenlabs.io)

## Usage

Run the app:
```bash
reachy-mini-daemon
```

Then install and start the app from the Reachy Mini dashboard, or run directly:
```python
from judgy_reachy_no_phone.main import JudgyReachyNoPhone

app = JudgyReachyNoPhone()
app.wrapped_run()
```

The web UI will be available at http://localhost:7863

## Configuration

### Settings (via Web UI)

- **Groq API Key**: Optional, for LLM-generated responses
- **ElevenLabs API Key**: Optional, for premium TTS voice
- **Cooldown**: Time between shames (10-120 seconds)
- **Praise Mode**: Enable/disable praise when phone is put down

### Pre-written Snarky Lines

The app includes 20+ pre-written responses that work without any API:

- **1st offense**: "The phone? Already?", "And so it begins."
- **2nd-3rd**: "Again?", "Back to the phone I see."
- **4+ offenses**: "I've lost count.", "Phone addiction is real."

## Stats Tracked

- **Pickups Today**: Count of phone pickups in current session
- **Total Shames**: Total number of shaming events
- **Best Streak**: Longest period without phone pickup

## Technical Details

- **Detection**: YOLOv8 nano model for fast inference
- **Phone Class ID**: COCO dataset class 67 ("cell phone")
- **Detection Threshold**: 3 consecutive frames to confirm pickup
- **Putdown Threshold**: 15 frames to confirm phone down (avoids flicker)
- **Frame Rate**: 5 Hz for efficient processing

## Requirements

- Reachy Mini robot with camera
- Python 3.10+
- Internet connection (for first-time YOLO model download and TTS)

## License

MIT - Feel free to shame yourself and others!

## Credits

Built for [Reachy Mini](https://huggingface.co/spaces/pollen-robotics/Reachy_Mini) by Pollen Robotics & Hugging Face.
