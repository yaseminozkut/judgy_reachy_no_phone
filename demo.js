// Judgy Reachy No Phone - Browser Demo
// Uses Transformers.js for YOLO detection in the browser

import { AutoModel, AutoProcessor, RawImage } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1';

// DOM Elements
const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d', { willReadFrequently: true });
const robotSvg = document.getElementById('robot-svg');
const cameraBtn = document.getElementById('camera-btn');
const cameraIcon = document.getElementById('camera-icon');
const cameraText = document.getElementById('camera-text');
const startBtn = document.getElementById('start-btn');
const btnIcon = document.getElementById('btn-icon');
const btnText = document.getElementById('btn-text');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const fpsEl = document.getElementById('fps');
const responseText = document.getElementById('response-text');
const loader = document.getElementById('loader');
const loaderText = document.getElementById('loader-text');

// Loader helpers
const showLoader = (text) => {
    loaderText.textContent = text;
    loader.classList.add('visible');
};

const hideLoader = () => {
    loader.classList.remove('visible');
};

// Demo defaults (hardcoded - Pure Reachy mode)
const DEMO_COOLDOWN = 10;  // 10 seconds cooldown
const DEMO_PRAISE_ENABLED = true;  // Enable praise sounds!

// State
let model = null;
let processor = null;
let isRunning = false;
let isMonitoring = false;
let isProcessing = false;  // Prevent overlapping detections
let animationId = null;
let stream = null;

// Detection state
let phoneVisible = false;
let consecutivePhone = 0;
let consecutiveNoPhone = 0;
let phoneCount = 0;
let lastReactionTime = 0;

// Tracking state
let lastPhoneBox = null;  // Last known phone position
let framesWithoutDetection = 0;  // Count frames without detection

// Offscreen canvas for processing
const offscreen = document.createElement('canvas');
const offscreenCtx = offscreen.getContext('2d', { willReadFrequently: true });

// Constants
const PHONE_CLASS_ID = 67;  // Cell phone in COCO dataset
const PICKUP_THRESHOLD = 3;
const PUTDOWN_THRESHOLD = 15;
const DETECTION_CONFIDENCE = 0.5;  // Initial detection: 0.1 (low) to 0.9 (high)
const TRACKING_CONFIDENCE = 0.2;  // Lower threshold when tracking existing phone
const TRACKING_PERSIST_FRAMES = 3;  // Keep tracking for N frames after losing detection

// Pure Reachy Mode - Robot emotion sounds from HuggingFace
const SHAME_EMOTIONS = [
    "disgusted1",
    "resigned1",
    "displeased1",
    "displeased2",
    "rage1",
    "no1",
    "reprimand1",
    "reprimand3",
    "dying1",
    "surprised1",
    "surprised2"
];

const PRAISE_EMOTIONS = [
    "welcoming2",
    "inquiring1",
    "inquiring2",
    "proud1",
    "proud3",
    "success1",
    "success2",
    "enthusiastic1",
    "enthusiastic2",
    "grateful1",
    "yes1",
    "cheerful1"
];

const EMOTIONS_BASE_URL = "https://huggingface.co/datasets/pollen-robotics/reachy-mini-emotions-library/resolve/main";

// Initialize
async function init() {
    try {
        // Disable buttons while loading
        cameraBtn.disabled = true;
        startBtn.disabled = true;

        // Show loader
        showLoader('Loading YOLO26m model...');
        statusText.textContent = 'Loading AI model...';
        statusIndicator.className = 'status-dot loading';

        // Load YOLO model
        model = await AutoModel.from_pretrained('onnx-community/yolo26m-ONNX', {
            device: 'webgpu',
            dtype: 'fp16'
        });

        showLoader('Loading processor...');
        processor = await AutoProcessor.from_pretrained('onnx-community/yolo26m-ONNX');

        // Hide loader
        hideLoader();
        statusText.textContent = 'Model ready! Open camera to begin';
        statusIndicator.className = 'status-dot ready';
        cameraBtn.disabled = false;

        console.log('YOLO model loaded successfully');
    } catch (error) {
        console.error('Failed to load model:', error);
        showLoader('Failed to load model: ' + error.message);
        statusText.textContent = 'Error loading model';
        statusIndicator.className = 'status-dot error';
    }
}

// Start webcam
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: 640,
                height: 480,
                facingMode: 'user'
            }
        });

        video.srcObject = stream;
        await video.play();

        // Show video and canvas
        video.style.display = 'block';
        canvas.style.display = 'block';

        canvas.width = offscreen.width = video.videoWidth;
        canvas.height = offscreen.height = video.videoHeight;

        isRunning = true;
        loop();  // Start the loop

        statusIndicator.className = isMonitoring ? 'status-dot monitoring' : 'status-dot ready';

    } catch (error) {
        console.error('Camera error:', error);
        alert('Could not access webcam. Please allow camera permissions.');
    }
}

// Stop webcam
function stopCamera() {
    isRunning = false;

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    if (animationId) {
        cancelAnimationFrame(animationId);
    }

    // Clear and hide video/canvas when closed
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    video.style.display = 'none';
    canvas.style.display = 'none';
}

// Main loop (like YOLO26-WebGPU)
function loop() {
    if (!isRunning) return;

    if (!isMonitoring) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
      }

    // Run detection if ready (non-blocking)
    if (isMonitoring && !isProcessing) {
        isProcessing = true;
        const startTime = performance.now();
        detectAndProcess()
            .then(() => {
                fpsEl.textContent = Math.round(1000 / (performance.now() - startTime));
            })
            .finally(() => {
                isProcessing = false;
            });
    }

    if (isRunning) animationId = requestAnimationFrame(loop);
}

// Combined detection and processing
async function detectAndProcess() {
    // Detect phone and get results
    const detections = await detectPhoneAndGetBoxes();

    // Process state machine
    const phoneInFrame = detections.length > 0;

    // Update consecutive counters
    if (phoneInFrame) {
        consecutivePhone++;
        consecutiveNoPhone = 0;
    } else {
        consecutiveNoPhone++;
    }

    // Check for phone pickup (3 frames)
    if (consecutivePhone >= PICKUP_THRESHOLD && !phoneVisible) {
        phoneVisible = true;
        consecutiveNoPhone = 0;

        const now = Date.now();
        const cooldown = DEMO_COOLDOWN * 1000;

        if (now - lastReactionTime >= cooldown) {
            phoneCount++;
            lastReactionTime = now;
            handlePhonePickup();
        }
    }

    // Check for periodic reaction while STILL holding phone
    if (phoneVisible && phoneInFrame) {
        const now = Date.now();
        const cooldown = DEMO_COOLDOWN * 1000;

        if (now - lastReactionTime >= cooldown) {
            phoneCount++;
            lastReactionTime = now;
            handlePhonePickup();
        }
    }

    // Check for putdown (15 frames)
    if (consecutiveNoPhone >= PUTDOWN_THRESHOLD && phoneVisible) {
        phoneVisible = false;
        consecutivePhone = 0;
        lastReactionTime = 0;

        // No praise in demo (keeps it simple)
        if (DEMO_PRAISE_ENABLED) {
            handlePhonePutdown();
        }
    }

    // Update status (only if still monitoring)
    if (isMonitoring) {
        if (phoneVisible) {
            statusText.textContent = '📱 PHONE DETECTED!';
            statusIndicator.className = 'status-dot detected';
        } else {
            statusText.textContent = '✅ Phone-free';
            statusIndicator.className = 'status-dot monitoring';
        }

        // Draw (only when monitoring)
        draw(detections);
    }
}

// Detect phone and return detection boxes (like YOLO26-WebGPU)
async function detectPhoneAndGetBoxes() {
    try {
        // Resize for faster inference (trade accuracy for speed)
        const targetWidth = 320;  // Smaller = faster (try 320, 416, or 640)
        const targetHeight = Math.round((targetWidth / offscreen.width) * offscreen.height);
        console.log(`Detection resolution: ${targetWidth}x${targetHeight}`);

        // Create smaller canvas for YOLO
        const smallCanvas = document.createElement('canvas');
        smallCanvas.width = targetWidth;
        smallCanvas.height = targetHeight;
        const smallCtx = smallCanvas.getContext('2d');

        // Draw resized image
        offscreenCtx.drawImage(video, 0, 0);
        smallCtx.drawImage(offscreen, 0, 0, targetWidth, targetHeight);

        const image = RawImage.fromCanvas(smallCanvas);

        // Run YOLO detection
        const inputs = await processor(image);
        const output = await model(inputs);

        // Process detections - YOLO26 format
        const scores = output.logits.sigmoid().data;
        const boxes = output.pred_boxes.data;

        // Adaptive confidence: lower threshold when tracking existing phone
        const confidenceThreshold = lastPhoneBox ? TRACKING_CONFIDENCE : DETECTION_CONFIDENCE;

        // Collect new detections
        const newDetections = [];
        let bestPhone = null;
        let bestScore = 0;

        // Check 300 detections
        for (let i = 0; i < 300; i++) {
            let maxScore = 0, maxClass = 0;

            // Find max class and score
            for (let j = 0; j < 80; j++) {
                const score = scores[i * 80 + j];
                if (score > maxScore) {
                    maxScore = score;
                    maxClass = j;
                }
            }

            // Check if it's a phone with adaptive confidence
            if (maxClass === PHONE_CLASS_ID && maxScore >= confidenceThreshold) {
                // Get box coordinates (cx, cy, w, h) - normalized 0-1
                const cx = boxes[i * 4];
                const cy = boxes[i * 4 + 1];
                const w = boxes[i * 4 + 2];
                const h = boxes[i * 4 + 3];

                // Convert to x1, y1, x2, y2 and scale to original canvas size
                const scaleX = canvas.width / targetWidth;
                const scaleY = canvas.height / targetHeight;

                const x1 = (cx - w / 2) * targetWidth * scaleX;
                const y1 = (cy - h / 2) * targetHeight * scaleY;
                const x2 = (cx + w / 2) * targetWidth * scaleX;
                const y2 = (cy + h / 2) * targetHeight * scaleY;

                const detection = {
                    x1, y1, x2, y2,
                    confidence: maxScore,
                    class: 'cell phone'
                };

                // Keep track of best detection
                if (maxScore > bestScore) {
                    bestScore = maxScore;
                    bestPhone = detection;
                }
            }
        }

        // Tracking logic: smooth and persist
        if (bestPhone) {
            // Phone detected - update tracking
            lastPhoneBox = bestPhone;
            framesWithoutDetection = 0;
            newDetections.push(bestPhone);
        } if (lastPhoneBox && framesWithoutDetection < TRACKING_PERSIST_FRAMES) {
            // No detection but still tracking - persist last known box
            framesWithoutDetection++;
            newDetections.push({
                ...lastPhoneBox,
                confidence: lastPhoneBox.confidence * 0.9  // Fade confidence
            });
        } else {
            // Lost tracking completely
            lastPhoneBox = null;
            framesWithoutDetection = 0;
        }

        // Return detections array
        return newDetections;

    } catch (error) {
        console.error('Detection error:', error);
        return [];
    }
}

// Draw (like YOLO26-WebGPU - clear and redraw every time)
function draw(detections) {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw video
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Draw detection boxes
    for (const det of detections) {
        // Draw green box for phone
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        ctx.strokeRect(det.x1, det.y1, det.x2 - det.x1, det.y2 - det.y1);

        // Draw label
        ctx.fillStyle = '#00ff00';
        ctx.font = '16px Arial';
        const text = `${det.class} ${(det.confidence * 100).toFixed(0)}%`;
        ctx.fillText(text, det.x1, det.y1 - 10);
    }
}

// Play Reachy emotion sound (Pure Reachy mode)
async function playReachyEmotion(emotionList) {
    // Pick random emotion from list
    const emotionName = emotionList[Math.floor(Math.random() * emotionList.length)];
    const audioUrl = `${EMOTIONS_BASE_URL}/${emotionName}.wav`;

    try {
        const audio = new Audio(audioUrl);
        await audio.play();
        return emotionName;
    } catch (error) {
        console.warn(`Failed to play emotion ${emotionName}:`, error);
        return null;
    }
}

// Handle phone pickup - Pure Reachy mode
async function handlePhonePickup() {
    // Change to KO/shame robot
    robotSvg.setAttribute('data', 'reachy-mad.svg');
    robotSvg.classList.add('shaking');

    // Play random shame emotion sound
    const emotionName = await playReachyEmotion(SHAME_EMOTIONS);

    // Show which emotion played
    if (emotionName) {
        responseText.textContent = `😡 *${emotionName}*`;
    }

    // Return to normal after animation
    setTimeout(() => {
        robotSvg.classList.remove('shaking');
    }, 2000);
}

// Handle phone putdown - Pure Reachy mode
async function handlePhonePutdown() {
    // Trigger robot praise animation (stays happy)
    robotSvg.classList.add('nodding');
    robotSvg.setAttribute('data', 'reachy-happy.svg');

    // Play random praise emotion sound
    const emotionName = await playReachyEmotion(PRAISE_EMOTIONS);

    // Show which emotion played
    if (emotionName) {
        responseText.textContent = `✨ *${emotionName}*`;
    }

    // Return to normal after animation
    setTimeout(() => {
        robotSvg.classList.remove('nodding');
    }, 1500);
}

// Removed - stats not needed for demo

// Event handlers
cameraBtn.addEventListener('click', async () => {
    if (!isRunning) {
        // Open camera
        await startCamera();
        cameraIcon.textContent = '🎥';
        cameraText.textContent = 'Close Camera';
        startBtn.disabled = false;
        isMonitoring = true;
        btnIcon.textContent = '🛑';
        btnText.textContent = 'Stop Monitoring';
        statusIndicator.className = 'status-dot monitoring';

    } else {
        // Close camera
        isMonitoring = false;
        stopCamera();
        cameraIcon.textContent = '📹';
        cameraText.textContent = 'Open Camera';
        startBtn.disabled = true;
        btnIcon.textContent = '▶️';
        btnText.textContent = 'Start Monitoring';
        statusText.textContent = 'Camera closed';
        statusIndicator.className = 'status-dot ready';
        robotSvg.setAttribute('data', 'reachy-happy.svg');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Reset tracking
        phoneVisible = false;
        consecutivePhone = 0;
        consecutiveNoPhone = 0;
        lastPhoneBox = null;
        framesWithoutDetection = 0;
        lastReactionTime = 0;
    }
});

startBtn.addEventListener('click', async () => {
    isMonitoring = !isMonitoring;
    if (isMonitoring) {
        btnIcon.textContent = '🛑';
        btnText.textContent = 'Stop Monitoring';
        statusIndicator.className = 'status-dot monitoring';

    } else {
        btnIcon.textContent = '▶️';
        btnText.textContent = 'Start Monitoring';
        statusText.textContent = 'Paused';
        statusIndicator.className = 'status-dot ready';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        robotSvg.setAttribute('data', 'reachy-happy.svg');

        // Reset tracking
        phoneVisible = false;
        consecutivePhone = 0;
        consecutiveNoPhone = 0;
        lastPhoneBox = null;
        framesWithoutDetection = 0;
        lastReactionTime = 0;
    }
});

// Initialize on load
init();
