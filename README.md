---
title: Judgy Reachy No Phone
emoji: 📱
colorFrom: red
colorTo: purple
sdk: static
pinned: false
license: apache-2.0
short_description: Robot shames you for phone addiction with AI vision
tags:
 - reachy_mini
 - reachy_mini_python_app
 - productivity
models:
 - onnx-community/yolo26m-ONNX
 - Ultralytics/YOLO26
 - meta-llama/Llama-3.1-8B
datasets:
 - pollen-robotics/reachy-mini-emotions-library
---

# 📱 Judgy Reachy No Phone 🤖 - Feel free to shame yourself and others!

**A Reachy Mini app that detects when you pick up your phone and shames you with snarky comments.**

Stop checking your phone and get back to work! This app uses computer vision to detect when you pick up your phone and makes Reachy Mini give you a judgmental, snarky comment to shame you back to productivity.

## Features

- 📱 **Phone Detection**: Uses YOLO26n to detect when you pick up your phone
- 🗣️ **Snarky Responses**: LLM-generated or pre-written judgmental comments
- 🔊 **Text-to-Speech**: Robot speaks the shame out loud with expressive voice
- 🤖 **Expressive Animations**: Different reactions based on offense count
- 📊 **Stats Tracking**: Pickup count, shame count, longest phone-free streak
- 🎮 **Web UI**: Gradio interface for monitoring and configuration

## How It Works

1. **Camera watches you** - Reachy Mini monitors the camera feed
2. **Phone detected** - YOLO26n detects when you pick up your phone
3. **Shame delivered** - Robot gives you a snarky comment via TTS
4. **Robot reacts** - Expressive animations get more dramatic with repeat offenses

## 100% Free Stack

| Component | Free Option | Premium Option |
|-----------|-------------|----------------|
| Detection | YOLO26n (local) | - |
| LLM | Pre-written lines | Groq (free tier using LLama 3.1-8b-instant) |
| TTS | Edge TTS (unlimited) | ElevenLabs (10k chars/month) |

## Prerequisites

Before installing this app, you need to set up Reachy Mini SDK:

1. **Install Reachy Mini SDK**: Follow the installation guide at:
   - [Reachy Mini Installation Guide](https://github.com/pollen-robotics/reachy_mini/blob/develop/docs/SDK/installation.md)
   - [Reachy Mini Quickstart](https://github.com/pollen-robotics/reachy_mini/blob/develop/docs/SDK/quickstart.md)

2. **Get the SDK**: Clone from [pollen-robotics/reachy_mini](https://github.com/pollen-robotics/reachy_mini)

## Installation

Once Reachy Mini SDK is installed:

```bash
# Clone this repository
git clone https://github.com/yaseminozkut/judgy_reachy_no_phone
cd judgy_reachy_no_phone

# Install the app
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

### Install Everything

```bash
pip install .[llm,premium-tts]
```

## Usage

### Start Reachy Mini Daemon

Make sure your reachy-mini-daemon is running please check [Reachy Mini Quickstart](https://github.com/pollen-robotics/reachy_mini/blob/develop/docs/SDK/quickstart.md) to know how to run:
- Simulation vs. Lite vs. Wireless
- MacOS vs. Windows/Linux

### Launch the App

The app will automatically detect if you're in simulation mode and use the appropriate camera:
- **Simulation mode**: Uses your laptop webcam
- **Real robot**: Uses robot's camera

Access the web UI at **http://localhost:8042**

## Configuration

### Settings (via Web UI)

- **Groq API Key**: Optional, for LLM-generated responses
- **ElevenLabs API Key**: Optional, for premium TTS voice
- **Cooldown**: Time between shames (10-120 seconds)
- **Praise Mode**: Enable/disable praise when phone is put down

### Pre-written Snarky Lines

The app includes 20+ pre-written responses with personalities that work without any API.

## Stats Tracked

- **Pickups Today**: Count of phone pickups in current session
- **Current Streak**: Current period without phone pickup
- **Best Streak**: Longest period without phone pickup

## Technical Details

- **Detection**: YOLO26 nano model for fast inference
- **Phone Class ID**: COCO dataset class 67 ("cell phone")
- **Camera Capture**: ~100 FPS max (0.01s sleep)
- **Detection Rate**: Every 3rd frame (~33 FPS)
- **Detection Threshold**: 3 consecutive frames to confirm pickup
- **Putdown Threshold**: 15 frames to confirm phone down (avoids flicker)

## Requirements

- Reachy Mini robot with camera
- Python 3.10+
- Internet connection (for first-time YOLO model download, LLM, and TTS)

## License

Apache 2.0

## Credits

Built by **Yasemin Ozkut** for [Reachy Mini](https://huggingface.co/spaces/pollen-robotics/Reachy_Mini) by Pollen Robotics & Hugging Face.
