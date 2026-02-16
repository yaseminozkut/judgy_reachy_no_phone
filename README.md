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

# 📱 Judgy Reachy No Phone 🤖

**A Reachy Mini app that uses NVIDIA-accelerated computer vision to detect phone usage and deliver personalized robot interventions through 8 distinct AI personalities.**

Built for the **NVIDIA GTC 2026 Golden Ticket Contest** in partnership with Pollen Robotics & Hugging Face.

[![Demo Video](https://img.shields.io/badge/Watch-Demo-red?style=for-the-badge&logo=youtube)](https://www.linkedin.com/feed/update/urn:li:activity:7420180578961907712/)
[![Try it Live](https://img.shields.io/badge/Try-Live%20Demo-blue?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/yozkut/judgy_reachy_no_phone)
[![Tech Stack](https://img.shields.io/badge/NVIDIA%20%2B%20Partners-Tech%20Stack-green?style=for-the-badge&logo=nvidia)](#-nvidia-and-partner-technologies-integration)

<div align="center">

<img src="quick_demo.gif" alt="Judgy Reachy No Phone Demo" width="700">

*Real-time phone detection with YOLO26m + TensorRT, 8 AI personalities, and expressive robot reactions*

</div>

---

## ⚡ Quick Start

**Want to try it right now?**
- 🌐 **[Try Web Demo](https://huggingface.co/spaces/yozkut/judgy_reachy_no_phone#demo)** - No installation, runs in browser (Transformers.js + ONNX)
- 🚀 **[Install Locally](#️-installation)** - Full experience with all 8 personalities (multiple install options)

📖 **[Usage Instructions](#-usage)** • ⚙️ **[Configuration](#️-configuration)**

---

## 🎯 The Problem

Phone addiction is a growing productivity killer. Traditional app blockers fail because they're easy to bypass or disable. What if a physical robot could intervene with personalized, funny, and emotionally engaging feedback?

## 💡 The Solution

Judgy Reachy No Phone combines **NVIDIA-accelerated computer vision**, **LLM-generated responses**, and **expressive robotics** to create a physical productivity guardian that:
- **Detects** phone pickups in real-time using YOLO26m with TensorRT optimization
- **Tracks** your behavior patterns with ByteTrack persistent object tracking
- **Responds** with personality-matched interventions via 8 distinct AI personalities
- **Adapts** its reactions based on your offense count and streak performance

---

## 🚀 Key Features

- **NVIDIA GPU Acceleration**: TensorRT optimization for 2-3x faster inference
- **Advanced Object Tracking**: ByteTrack algorithm with adaptive confidence thresholds
- **8 AI Personalities**: From Angry Boss to Pure Reachy (robot sounds only)
- **Multi-Voice TTS**: ElevenLabs premium or Edge TTS free tier
- **Smart Detection**: Robust phone pickup/putdown with anti-flicker
- **Behavior Tracking**: Streaks, pickup counts, session stats
- **Expressive Animations**: Personality-matched robot reactions
- **100% Free Tier**: Works without any API keys or NVIDIA GPU

---

## 🌐 Accessibility - Multiple Ways to Try It

This app is designed to be **100% accessible** regardless of your hardware or budget:

### 💰 **100% Free Tier** (No API Keys Required)
- **Responses**: Pre-written personality lines (no LLM needed)
- **Voice**: Edge TTS (unlimited, free forever)
- **Cost**: $0 - Works completely offline for responses

### ⚡ **Optional Premium Tier** (Free APIs Available)
- **LLM Responses**: Groq API - Llama 3.1-8B (free tier available)
- **Premium Voice**: ElevenLabs API - 10k chars/month free
- **Dynamic**: AI-generated responses that adapt to context
- **Cost**: $0 with free API tiers

### 🖥️ **Hardware Flexibility** (GPU Optional)
- **NVIDIA GPU**: TensorRT acceleration (2-3x faster)
- **Apple Silicon**: MPS GPU support
- **CPU Only**: Full functionality, slightly slower inference
- **Auto-detection**: Automatically uses best available hardware

### 🤖 **Robot Options** (Physical Robot Optional)
- **[Try it NOW - Web Demo](https://huggingface.co/spaces/yozkut/judgy_reachy_no_phone#demo)**: No robot needed! Runs in your browser using **[Transformers.js](https://huggingface.co/docs/transformers.js/en/index)** from Hugging Face + **[ONNX YOLO](https://huggingface.co/onnx-community/yolo26m-ONNX)** (Pure Reachy mode only)
- **Simulation Mode**: Full app with laptop webcam (all 8 personalities, no physical robot)
- **Reachy Mini Lite**: Complete experience with wired robot connection
- **Reachy Mini Wireless**: Full wireless robot experience

### 🎨 **Engaging UX**
- **8 personalities** make intervention fun, not annoying
- **Customizable**: Add your own personalities, voices, animations
- **Extensible**: Easy to modify and adapt to your needs

**→ Anyone can try this right now, for free, without any hardware, API keys, or setup!**

---

## 🤝 NVIDIA and Partner Technologies Integration

This project leverages the full stack of contest technologies:

### ⚡ NVIDIA GPU Acceleration

**TensorRT & CUDA:**
- **2-3x performance boost** with automatic TensorRT optimization
- **Auto-detection** of NVIDIA GPUs with CUDA support
- **FP16 precision** for faster inference
- **Automatic fallback** to CPU/MPS when GPU unavailable

**→ Detailed technical explanation in [NVIDIA GPU Acceleration](#-nvidia-gpu-acceleration) section below**

### 🤗 Hugging Face Ecosystem

**Model Hub & Inference:**
- **[ONNX YOLO](https://huggingface.co/onnx-community/yolo26m-ONNX)** - Used in web demo via Transformers.js
- **[Transformers.js](https://huggingface.co/docs/transformers.js)** - Browser-based ML inference (no server needed!)

**Dataset:**
- **[reachy-mini-emotions-library](https://huggingface.co/datasets/pollen-robotics/reachy-mini-emotions-library)** - Pre-recorded robot emotions for Pure Reachy mode

**Deployment:**
- **[HF Spaces](https://huggingface.co/spaces/yozkut/judgy_reachy_no_phone)** - Web demo hosting with instant deployment
- **GitHub Actions → HF Sync** - Automatic synchronization using [custom fork](https://github.com/yaseminozkut/huggingface-sync-action)

### 🤖 Reachy Mini (Pollen Robotics)

**SDK Integration:**
- Full integration with [Reachy Mini SDK](https://github.com/pollen-robotics/reachy_mini)
- Supports **Simulation**, **Lite**, and **Wireless** modes
- Multi-platform installation (macOS, Windows, Linux)

**Robot Capabilities:**
- **Expressive animations** - Head movements, antenna gestures
- **Emotion library** - Access to 20+ pre-recorded emotional reactions
- **Multiple deployment options** - SDK app store, Desktop app, or pip install

**App Store Integration:**
- One-click install via Reachy Mini dashboard (localhost:8000)
- Available in [Reachy Mini Desktop App](https://github.com/pollen-robotics/reachy-mini-desktop-app)
- Community apps distribution

---

## 🎮 NVIDIA GPU Acceleration

### **TensorRT Optimization** (2-3x Speed Boost!)
- **Auto-detection** of NVIDIA GPUs with CUDA support
- **One-time export** to TensorRT engine for maximum performance
- **Automatic fallback** to PyTorch/CPU if NVIDIA GPU unavailable
- **FP16 precision** for faster inference without accuracy loss

```python
# Automatic TensorRT optimization on NVIDIA GPUs
if torch.cuda.is_available():
    device = 'cuda'
    # Export YOLO to TensorRT (one-time, ~1-2 min)
    model.export(format='engine', device=0, half=True, workspace=4)
    # Inference is now 2-3x faster! 🚀
```

---

## 👁️ Computer Vision & Object Tracking

### **YOLO26m Object Detection**
- Latest YOLO model from Ultralytics (2026 release)
- Trained on COCO dataset (class 67: "cell phone")
- Optimized for edge deployment (runs faster on NVIDIA hardware with TensorRT)
- Links: [Ultralytics/YOLO26](https://huggingface.co/Ultralytics/YOLO26), [ONNX version](https://huggingface.co/onnx-community/yolo26m-ONNX)

### **ByteTrack Object Tracking**
- Industry-standard multi-object tracking with persistent IDs
- **Adaptive Confidence Thresholds**: 0.5 for initial detection, 0.2 when tracking existing objects
- **Robust to Occlusion**: Maintains track IDs even when phone temporarily hidden
- **Real-time Performance**: ~100 FPS camera capture, ~33 FPS detection rate

---

## 🤖 AI-Powered Personality System

**8 Distinct Robot Personalities** powered by Meta's **Llama 3.1-8B-instant** (via [Groq](https://console.groq.com) - free API), each with carefully selected Edge TTS and ElevenLabs voices:

| Personality | Example Shame | Example Praise |
|------------|---------------|----------------|
| 🤖 **Pure Reachy** | *disgusted1.wav* (robot sound) | *success1.wav* (robot sound) |
| 😠 **Angry Boss** | "We have deadlines!" | "About time." |
| 🎭 **Sarcastic** | "Work can wait, obviously." | "Shocking development." |
| 😔 **Disappointed Parent** | "Expected more from you." | "So proud of you." |
| 💪 **Motivational Coach** | "Champions don't quit!" | "YES! That's it!" |
| 🤡 **Absurdist** | "Screen goblins summon you?" | "The desk thanks you." |
| 🤖 **Corporate AI** | "Productivity declining." | "Status: compliant." |
| 🎩 **British Butler** | "If I may suggest..." | "Very good, sir." |
| 🐣 **Chaos Baby** | *Random personality each time* | *Unpredictable!* |

**Pure Reachy Mode**: Uses [pollen-robotics/reachy-mini-emotions-library](https://huggingface.co/datasets/pollen-robotics/reachy-mini-emotions-library) dataset for emotion-based interactions without text-to-speech.

### 🎨 Expressive Robot Animations

**TTS Personalities** (Angry Boss, Sarcastic, etc.):
- **Curious Look** (1st offense): Gentle head tilt with antenna twitch
- **Disappointed Shake** (2-3 offenses): Triple head shake with drooping antennas
- **Dramatic Sigh** (4+ offenses): Exasperated look-up, slump, and turn away
- **Approving Nod** (phone down): Enthusiastic double-nod celebration
- **Idle Breathing** (monitoring): Gentle antenna movements while watching

**Pure Reachy Mode**:
- Uses pre-recorded emotion animations from [pollen-robotics/reachy-mini-emotions-library](https://huggingface.co/datasets/pollen-robotics/reachy-mini-emotions-library)
- **Shame emotions**: disgusted1, resigned1, displeased1/2, rage1, no1, reprimand1/3, dying1, surprised1/2
- **Praise emotions**: welcoming2, inquiring1/2, proud1/3, success1/2, enthusiastic1/2, grateful1, yes1, cheerful1
- Each emotion includes synchronized sound + animation

### 📊 Smart Behavior Tracking

- **Phone Pickup Counter**: Total pickups in current session
- **Shame Counter**: How many times robot intervened
- **Current Streak**: Time since last phone pickup
- **Best Streak**: Longest phone-free period achieved
- **Continue/Pause**: Preserve stats when stopping monitoring

### 🔊 Multi-Voice TTS System

Each personality has carefully selected voices that match their speaking style and tone:

**Free Tier (Unlimited) - Edge TTS**:
- 🤖 **Pure Reachy**: Robot sounds only (no TTS)
- 😠 **Angry Boss**: `en-US-EricNeural` (deep, stern male)
- 🎭 **Sarcastic**: `en-US-AvaMultilingualNeural` (dry wit)
- 😔 **Disappointed Parent**: `en-US-AvaNeural` (soft, empathetic)
- 💪 **Motivational Coach**: `en-US-GuyNeural` (energetic male)
- 🤡 **Absurdist**: `en-US-AriaNeural` (playful, expressive)
- 🤖 **Corporate AI**: `en-US-MichelleNeural` (neutral, professional)
- 🎩 **British Butler**: `en-GB-RyanNeural` (polite British male)
- 🐣 **Chaos Baby**: `en-US-AnaNeural` (versatile)

**Premium Tier (Optional) - ElevenLabs**:
- 🤖 **Pure Reachy**: Robot sounds only (no ElevenLabs)
- 😠 **Angry Boss**: Jerry B. (Gruff Commander) → Eric (Smooth, Trustworthy)
- 🎭 **Sarcastic**: Laura (Enthusiast, Quirky Attitude)
- 😔 **Disappointed Parent**: Alice (Clear, Engaging)
- 💪 **Motivational Coach**: Charlie (Deep, Confident, Energetic)
- 🤡 **Absurdist**: Jessica (Playful, Bright, Warm)
- 🤖 **Corporate AI**: Eva (Futuristic Robot Helper) → Sarah (Mature, Reassuring)
- 🎩 **British Butler**: George (Warm, Captivating Storyteller)
- 🐣 **Chaos Baby**: Custom Voice → Candy (Young and Sweet) → Jessica (Playful)

*Note: Multiple voices per personality ensure fallback if one is unavailable. System tries voices in order.*
- Voice validation with automatic fallback to Edge TTS
- 10k characters/month free tier → **[Get free API key](https://elevenlabs.io)**

### 🎯 Detection Features

- **Smart Pickup Detection**: 3 consecutive frames to confirm (avoids false positives)
- **Smart Putdown Detection**: 15 frames to confirm (avoids flicker)
- **Adaptive Cooldown**: Configurable time between interventions (10-120s)
- **Periodic Reminders**: Continuous shaming while phone in hand
- **Praise Mode**: Optional celebration when phone is put down

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  NVIDIA GPU (CUDA + TensorRT)                               │
│  ├─ YOLO26m Detection (30-60 FPS)                           │
│  ├─ ByteTrack Tracking (Persistent IDs)                     │
│  └─ Adaptive Confidence Thresholds                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Behavior Analysis Engine                                   │
│  ├─ Pickup/Putdown State Machine                            │
│  ├─ Streak Tracking                                         │
│  └─ Cooldown Management                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LLM Response Generation (Groq / Prewritten)                │
│  ├─ Llama 3.1-8B-instant (Groq API)                         │
│  ├─ Personality-matched prompts                             │
│  └─ Context-aware shame/praise                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Text-to-Speech (ElevenLabs / Edge TTS)                     │
│  ├─ Voice validation & fallback                             │
│  ├─ Personality-matched voices                              │
│  └─ Emotion library (Pure Reachy mode)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Reachy Mini Robot                                          │
│  ├─ Expressive Animations (head, antennas, body)            │
│  ├─ Synchronized Audio Playback                             │
│  └─ Real-time Camera Feed                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Technical Details

### Performance & Design Parameters

| Component | Configuration | Notes |
|-----------|--------------|-------|
| **Camera Capture** | Laptop/Robot Camera | Max ~100 FPS (0.01s sleep) |
| **Detection Rate** | Every 3rd frame | Max ~33 FPS detection |
| **TensorRT Speedup** | NVIDIA GPU optimization | **2-3x faster vs PyTorch** |
| **Pickup Detection** | 3 consecutive frames | Fast response (~90ms at 33 FPS) |
| **Putdown Detection** | 15 consecutive frames | Anti-flicker delay (~450ms) |
| **LLM Response** | Groq (Llama 3.1-8B) | Varies by API load |
| **TTS Generation** | Edge TTS / ElevenLabs | Varies by text length |

*Note: Actual FPS depends on hardware (camera quality, CPU/GPU), lighting conditions, and system load.*

### NVIDIA GPU Support

**Automatic Device Detection**:
```python
if torch.cuda.is_available():
    device = 'cuda'  # NVIDIA GPU → TensorRT
elif torch.backends.mps.is_available():
    device = 'mps'   # Apple Silicon GPU
else:
    device = 'cpu'   # Fallback to CPU
```

**TensorRT Export** (one-time setup):
```python
# Export PyTorch model to TensorRT engine
model.export(
    format='engine',
    device=0,           # GPU 0
    half=True,          # FP16 precision
    workspace=4         # 4GB workspace
)
# Result: yolo26m.engine (2-3x faster inference!)
```

### ByteTrack Object Tracking

```python
# YOLO's built-in ByteTrack integration
results = model.track(
    frame,
    persist=True,                  # Maintain track IDs across frames
    conf=adaptive_confidence,      # 0.5 initial, 0.2 tracking
    tracker="bytetrack.yaml",      # ByteTrack algorithm
    classes=[67]                   # Phone class only
)
```

---

## 🛠️ Installation

### Choose Your Installation Method

There are **multiple ways** to install and run this app:

#### **Option 1: Clone from GitHub** (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/yaseminozkut/judgy_reachy_no_phone
cd judgy_reachy_no_phone

# Install base (free tier)
pip install .

# OR install everything (LLM + Premium TTS)
pip install .[llm,premium-tts]
```

#### **Option 2: Clone from Hugging Face**

```bash
# Clone from Hugging Face Spaces
git clone https://huggingface.co/spaces/yozkut/judgy_reachy_no_phone
cd judgy_reachy_no_phone

# Install (same as GitHub)
pip install .

# OR install everything (LLM + Premium TTS)
pip install .[llm,premium-tts]
```

> **Note:** GitHub and Hugging Face repositories are automatically synced via GitHub Actions using a [custom fork](https://github.com/yaseminozkut/huggingface-sync-action) of [huggingface-sync-action](https://github.com/alozowski/huggingface-sync-action). Both sources are always up to date!

#### **Option 3: Install via Reachy Mini SDK App Store** (Easiest!)

1. Start Reachy Mini daemon ([see guide](https://github.com/pollen-robotics/reachy_mini?tab=readme-ov-file#user-guides))
2. Go to **http://localhost:8000** (Reachy Mini dashboard)
3. Check **"Community Apps"** box
4. Find **"Judgy Reachy No Phone"**
5. Click **Install**
6. Toggle **ON** to start
7. Access at **http://localhost:8042**

#### **Option 4: Install via Reachy Mini Desktop App**

1. Download [Reachy Mini Desktop App](https://github.com/pollen-robotics/reachy-mini-desktop-app)
2. Open the app and go to **App Store**
3. Find **"Judgy Reachy No Phone"**
4. Click **Install**
5. Start the app
6. Access at **http://localhost:8042**

### Prerequisites (for Options 1 & 2)

1. **Reachy Mini SDK**: [Installation Guide](https://github.com/pollen-robotics/reachy_mini/blob/develop/docs/SDK/installation.md)
2. **Python 3.10+**
3. **(Optional) NVIDIA GPU with CUDA** for TensorRT acceleration

### Optional: Get Free API Keys

- **Groq** (LLM): [console.groq.com](https://console.groq.com) - Free Llama 3.1-8B access
- **ElevenLabs** (Premium TTS): [elevenlabs.io](https://elevenlabs.io) - 10k chars/month free

---

## 🎮 Usage

### 1. Start Reachy Mini Daemon

See [Reachy Mini Quickstart](https://github.com/pollen-robotics/reachy_mini/blob/develop/docs/SDK/quickstart.md) for:
- **Simulation** vs. **Lite** vs. **Wireless** mode
- **macOS** vs. **Windows/Linux** setup

### 2. Launch the App

```bash
# App auto-detects simulation mode and uses appropriate camera:
# - Simulation: Laptop webcam
# - Real robot: Robot's camera
```

### 3. Access Web UI

Open **http://localhost:8042** in your browser

### 4. Configure & Start

1. **(Optional)** Enter API keys for LLM/Premium TTS
2. **Select personality** (Pure Reachy, Angry Boss, Sarcastic, etc.)
3. **Adjust cooldown** (10-120 seconds between shames)
4. **Enable/disable praise** for putting phone down
5. **Click "Start Monitoring"**

### 5. Get Judged!

Pick up your phone and watch Reachy react! 📱🤖

---

## 🎛️ Configuration

### Web UI Settings

| Setting | Options | Default |
|---------|---------|---------|
| **Personality** | 8 personalities + Pure Reachy | Pure Reachy |
| **Cooldown** | 10-120 seconds | 30s |
| **Praise Mode** | On/Off | On |
| **Groq API Key** | Optional (for LLM) | - |
| **ElevenLabs API Key** | Optional (premium TTS) | - |
| **Edge Voice** | Custom voice ID | Personality default |
| **ElevenLabs Voice** | Custom voice ID | Personality default |

### Advanced: Custom Personalities

Edit `config.py` to add your own personalities:

```python
PERSONALITIES = {
    "your_personality": {
        "name": "🎨 Your Personality",
        "voice": "Description of speaking style...",
        "default_voice": "en-US-VoiceName",
        "default_eleven_voices": ["voice_id_1", "voice_id_2"],
        "prewritten_shame": ["Line 1", "Line 2", ...],
        "shame": {
            "tone": "Description...",
            "examples": ["Example 1", ...]
        },
        # ... see config.py for full schema
    }
}
```

---

## 📈 How It Works (Technical Deep Dive)

### 1. **Camera Thread** (100 FPS)
```python
while not stop_event.is_set():
    frame = webcam.read()  # or reachy.media.get_frame()
    latest_frame = frame.copy()

    # Detection every 3rd frame (~33 FPS)
    if frame_count % 3 == 0:
        event = detector.process_frame(frame)

    # Encode as JPEG for web UI
    latest_frame_jpeg = encode_jpeg(frame)
    time.sleep(0.01)  # ~100 FPS
```

### 2. **Phone Detection** (YOLO26m + TensorRT)
```python
# Auto-detect NVIDIA GPU and use TensorRT
if cuda_available:
    model = YOLO("yolo26m.engine")  # TensorRT (2-3x faster!)
else:
    model = YOLO("yolo26m.pt")      # PyTorch fallback

# ByteTrack for persistent tracking
results = model.track(
    frame,
    persist=True,
    conf=adaptive_threshold,  # 0.5 → 0.2 when tracking
    tracker="bytetrack.yaml"
)
```

### 3. **State Machine** (Pickup/Putdown)
```python
# Pickup detection (fast: 3 frames)
if consecutive_phone >= 3 and not phone_visible:
    phone_visible = True
    return "picked_up"  # Trigger shame!

# Putdown detection (slow: 15 frames, anti-flicker)
if consecutive_no_phone >= 15 and phone_visible:
    phone_visible = False
    return "put_down"  # Trigger praise!
```

### 4. **LLM Response** (Groq + Llama 3.1-8B)
```python
response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    max_tokens=20,
    temperature=1.1,  # High creativity
    messages=[
        {"role": "system", "content": personality_prompt},
        {"role": "user", "content": f"Phone pickup #{count}"}
    ]
)
```

### 5. **Text-to-Speech** (Multi-Voice)
```python
# Try ElevenLabs first (if API key + under quota)
for voice_id in eleven_voices:
    try:
        audio = eleven.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2"
        )
        return audio  # Success!
    except:
        continue  # Try next voice

# Fallback to Edge TTS (always works, unlimited)
audio = edge_tts.Communicate(text, edge_voice).save()
```

### 6. **Robot Animation** (Synchronized)
```python
# Play audio
reachy.media.play_sound(audio_path)

# Animate based on offense count
if count == 1:
    curious_look(reachy)          # Gentle tilt
elif count <= 3:
    disappointed_shake(reachy)     # Head shake
else:
    dramatic_sigh(reachy)          # Full-body exasperation
```

---

## 🎯 Impact & Use Cases

### 🏢 **Productivity Enhancement**
- **Home office / Private workspace**: Stay focused during work sessions
- **Study sessions**: Break the phone-checking habit while studying
- **Personal accountability**: Physical reminder to stay off your phone

### 🏥 **Behavior Modification**
- **Digital wellness**: Reduce screen time naturally
- **Habit formation**: Build phone-free streaks
- **Mindfulness**: Awareness of unconscious phone checks

### 🎓 **Education & Research**
- **Human-Robot Interaction**: Study emotional engagement with robots
- **Behavior Psychology**: Test intervention effectiveness with different personalities
- **Computer Vision**: Real-time object detection demos
- **AI Ethics**: Explore persuasive technology boundaries

### 🤖 **Robotics Applications**
- **Social Robotics**: Emotional feedback systems
- **Assistive Technology**: Habit coaching robots
- **Edge AI**: Real-time vision on consumer hardware

---

## 🔧 Requirements

### Hardware
- Reachy Mini robot with camera
- **(Optional)** NVIDIA GPU with CUDA for TensorRT acceleration

### Software
- Python 3.10+
- Reachy Mini SDK
- Internet connection (first-time model download, LLM/TTS APIs)

### Dependencies

**Core** (always required):
```
reachy_mini
ultralytics
opencv-python
torch
numpy
edge-tts
fastapi
uvicorn
pydantic
```

**Optional - LLM**:
```
groq
```

**Optional - Premium TTS**:
```
elevenlabs
```

---

## 📝 Project Structure

```
judgy_reachy_no_phone/
├── judgy_reachy_no_phone/
│   ├── __init__.py
│   ├── main.py              # Main app loop, UI endpoints
│   ├── detection.py         # YOLO + TensorRT + ByteTrack
│   ├── audio.py             # LLM + TTS (Groq, ElevenLabs, Edge)
│   ├── animations.py        # Robot movements
│   └── config.py            # Personalities, settings
├── README.md                # This file
├── pyproject.toml           # Package config
└── .github/
    └── workflows/
        └── sync-hf-space.yml  # Auto-sync to Hugging Face
```

---

## 🤝 Contributing

This project was built for the **NVIDIA GTC 2026 Golden Ticket Contest**. Contributions welcome after contest ends!

### Ideas for Future Enhancements
- [ ] Multi-person tracking (shame multiple people!)
- [ ] Gesture recognition (phone in pocket vs. actively using)
- [ ] Dashboard analytics (daily/weekly reports)
- [ ] Mobile app integration (sync with phone screen-time data)
- [ ] Custom shame schedules (stricter during work hours)
- [ ] Gamification (achievements, leaderboards)
- [ ] Voice recognition (personalized responses per user)
- [ ] Integration with productivity tools (Slack, Calendar)

---

## 📜 License

**Apache 2.0** - Feel free to use, modify, and distribute!

---

## 🙏 Acknowledgments

### Technologies
- **NVIDIA**: CUDA, TensorRT optimization
- **Ultralytics**: YOLO26m object detection model
- **ByteTrack**: Multi-object tracking algorithm
- **Groq**: Free Llama 3.1-8B-instant API
- **Meta**: Llama 3.1-8B model
- **ElevenLabs**: High-quality TTS voices
- **Microsoft**: Edge TTS (free tier)

### Datasets & Models
- **Hugging Face**: [pollen-robotics/reachy-mini-emotions-library](https://huggingface.co/datasets/pollen-robotics/reachy-mini-emotions-library)
- **Ultralytics**: [YOLO26](https://huggingface.co/Ultralytics/YOLO26)
- **ONNX Community**: [yolo26m-ONNX](https://huggingface.co/onnx-community/yolo26m-ONNX)

### Partners
- **Pollen Robotics**: Reachy Mini robot platform
- **Hugging Face**: Hosting & model distribution
- **NVIDIA**: GTC Golden Ticket Contest sponsor

---

## 👤 Author

**Yasemin Ozkut**

Built for the **NVIDIA GTC 2026 Golden Ticket Contest** (Jan 27 - Feb 15, 2026)

Partnership: **Pollen Robotics Reachy Mini x Hugging Face x NVIDIA**

---

## 🎥 Demo

**[Watch Demo Video →](https://your-demo-link)**

**[Try Live Demo on Hugging Face →](https://huggingface.co/spaces/pollen-robotics/Reachy_Mini)**

---

## 📧 Contact & Links

- **GitHub**: [yaseminozkut/judgy_reachy_no_phone](https://github.com/yaseminozkut/judgy_reachy_no_phone)
- **Hugging Face**: [@yaseminozkut](https://huggingface.co/yaseminozkut)
- **Contest**: [NVIDIA GTC Golden Ticket](https://www.nvidia.com/gtc)

---

<div align="center">

**Built with ❤️ using NVIDIA TensorRT, YOLO26m, Llama 3.1, and Reachy Mini**

*Get off your phone and get back to work! 📱→🤖→💪*

</div>
