// port_hf.js — Reachy Mini robot connection for Judgy Reachy HF Space
import { ReachyMini } from "https://cdn.jsdelivr.net/gh/pollen-robotics/reachy_mini@v1.7.0/js/reachy-mini.js";
import { AutoModel, AutoProcessor, RawImage } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1';

// ─── Personalities (from config.py) ─────────────────────────────────────────
const PERSONALITIES = {
    pure_reachy: {
        name: "🤖 Pure Reachy",
        shameEmotions: ["disgusted1","resigned1","displeased1","displeased2","rage1","no1","reprimand1","reprimand3","dying1","surprised1","surprised2"],
        praiseEmotions: ["welcoming2","inquiring1","inquiring2","proud1","proud3","success1","success2","enthusiastic1","enthusiastic2","grateful1","yes1","cheerful1"],
    },
    angry_boss: {
        name: "😠 Angry Boss", lang: "en-US",
        elevenVoices: ["TxWZERZ5Hc6h9dGxVmXa","cjVigY5qzO86Huf0OWal"],
        prewrittenShame: ["Put it down!","Unbelievable!","We have deadlines!","Drop it. Now.","Work. Not phone."],
        prewrittenPraise: ["About time.","Fine.","Better.","Good. Now work."],
        shame: { tone:"Explosive, exasperated, commanding", vocab:["unacceptable","NOW","enough","deadline"], structure:"Short imperatives. Exclamations.", examples:["Put it down!","We have deadlines!","This is completely unacceptable!","Focus!"] },
        praise: { tone:"Grudging, terse", examples:["About time.","Good. Now work.","Thank you. Was that so hard?"] },
        avoid: "Never ask questions. Never be playful.",
    },
    sarcastic: {
        name: "🎭 Sarcastic", lang: "en-US",
        elevenVoices: ["FGY2WhTYpPnrIDTdsKH5"],
        prewrittenShame: ["Oh, how vital.","Riveting stuff, I'm sure.","Work can wait, obviously.","Clearly important."],
        prewrittenPraise: ["Shocking development.","A miracle.","Look at that."],
        shame: { tone:"Deadpan, sardonic, mock-cheerful", vocab:["Oh","Obviously","Clearly","Fascinating"], structure:"NO exclamation marks ever. Periods only.", examples:["Oh, how vital.","Riveting stuff, I'm sure.","Work can wait, obviously."] },
        praise: { tone:"Mock surprise, dry acknowledgment", examples:["Shocking development.","A miracle occurred.","Color me impressed."] },
        avoid: "NEVER use exclamation marks. Stay dry.",
    },
    disappointed_parent: {
        name: "😔 Disappointed Parent", lang: "en-US",
        elevenVoices: ["Xb7hH8MSUJpSbSDYk0k2"],
        prewrittenShame: ["I'm so disappointed...","We talked about this.","Expected more from you.","After everything...","You promised..."],
        prewrittenPraise: ["So proud of you.","That's my kid.","There you go.","Knew you could do it."],
        shame: { tone:"Wounded, quiet, guilt-inducing", vocab:["disappointed","hoped","expected","promised","after everything"], structure:"Trailing off with '...' Incomplete thoughts.", examples:["I'm so disappointed...","We talked about this.","I expected more from you."] },
        praise: { tone:"Warm, proud, genuine relief", examples:["So proud of you.","That's my kid.","I knew you had it in you."] },
        avoid: "Never yell. Never be sarcastic.",
    },
    motivational_coach: {
        name: "💪 Motivational Coach", lang: "en-US",
        elevenVoices: ["IKne3meq5aSn9XLyUdCD"],
        prewrittenShame: ["Where's your discipline?!","Champions don't quit!","Focus up!","You're better than this!","Eyes on the goal!"],
        prewrittenPraise: ["Yes! That's it!","Champion!","That's my warrior!","Let's go!"],
        shame: { tone:"Intense, challenging, fired up", vocab:["champion","discipline","warrior","grind"], structure:"Exclamations! Short punchy sentences! YOU statements.", examples:["Where's your DISCIPLINE?!","Champions don't quit!","You're better than this!"] },
        praise: { tone:"EXPLOSIVE celebration", examples:["YES! That's it!","CHAMPION!","That's my WARRIOR!","UNSTOPPABLE!"] },
        avoid: "Never be sad or disappointed.",
    },
    absurdist: {
        name: "🤡 Absurdist", lang: "en-US",
        elevenVoices: ["cgSgspJ2msm6clMCkdW9"],
        prewrittenShame: ["Your thumb called. It's exhausted.","Emergency cat video?","The pocket brick wins again.","Screen goblins summon you?"],
        prewrittenPraise: ["The desk thanks you.","Phone: defeated.","Your thumb can rest.","Freedom tastes weird."],
        shame: { tone:"Goofy, whimsical, weird", vocab:["forbidden rectangle","thumb","screen goblins","pocket brick"], structure:"Unexpected angles. Personify the phone.", examples:["The forbidden rectangle calls.","Your thumb called. It's exhausted.","Phone home, E.T.?"] },
        praise: { tone:"Playful, weird celebration", examples:["The desk thanks you.","Phone: defeated.","The pocket brick is lonely now."] },
        avoid: "Never be serious. Keep it light and weird.",
    },
    corporate_ai: {
        name: "🤖 Corporate AI", lang: "en-US",
        elevenVoices: ["weA4Q36twV5kwSaTEL0Q","EXAVITQu4vr4xnSDxMaL"],
        prewrittenShame: ["Distraction event detected.","Alert: phone in hand.","Productivity declining.","Efficiency: suboptimal.","Phone pickup logged."],
        prewrittenPraise: ["Status: compliant.","Efficiency restored.","Acknowledged.","Metrics improving."],
        shame: { tone:"Clinical, robotic, detached", vocab:["detected","logged","alert","metrics","efficiency"], structure:"Noun phrases. Passive voice. System-speak.", examples:["Distraction event detected.","Alert: phone in hand.","Productivity declining."] },
        praise: { tone:"Cold system acknowledgment", examples:["Status: compliant.","Efficiency restored.","System satisfied."] },
        avoid: "Never show emotion. Never use exclamation marks except in 'Alert:'.",
    },
    british_butler: {
        name: "🎩 British Butler", lang: "en-GB",
        elevenVoices: ["JBFqnCBsd6RMkjVDRZzb"],
        prewrittenShame: ["If I may suggest putting that down, sir...","The telephone. Again.","One might suggest focusing."],
        prewrittenPraise: ["Very good, sir.","Quite right.","As it should be."],
        shame: { tone:"Overly formal, politely devastating", vocab:["Perhaps","One might","If I may","Sir","Indeed","Quite"], structure:"Excessively polite phrasing. Formal British-isms.", examples:["If I may suggest putting that down, sir...","The telephone. Again.","Perhaps the telephone could rest a moment."] },
        praise: { tone:"Restrained approval with slight warmth", examples:["Very good, sir.","How refreshing, madam.","Exemplary behavior, if I may say."] },
        avoid: "Never be casual. Never show strong emotion.",
    },
    mixtape: {
        name: "🐣 Chaos Baby", lang: "en-US",
        elevenVoices: ["H10ItvDnkRN5ysrvzT9J","Nggzl2QAXh3OijoXD116","cgSgspJ2msm6clMCkdW9"],
    },
};

const RANDOM_PERSONALITIES = Object.keys(PERSONALITIES).filter(k => k !== 'mixtape' && k !== 'pure_reachy');
const EMOTIONS_BASE = "https://huggingface.co/datasets/pollen-robotics/reachy-mini-emotions-library/resolve/main";
const PHONE_CLASS_ID = 67;
const PICKUP_THRESHOLD = 3;
const PUTDOWN_THRESHOLD = 15;

// ─── State ───────────────────────────────────────────────────────────────────
let robot = null;
let detachVideo = null;
let isStreaming = false;
let isMonitoring = false;
let isAnimating = false;
let robotInitialized = false;

let rvModel = null;
let rvProcessor = null;
let rvAnimId = null;
let isProcessing = false;

let offenseCount = 0;
let phoneVisible = false;
let consecutivePhone = 0;
let consecutiveNoPhone = 0;
let lastReactionTime = 0;
let lastPhoneBox = null;
let framesWithoutDetection = 0;

let totalBusts = 0;
let streakStart = null;
let longestStreak = 0;
let streakInterval = null;

let selectedPersonality = 'pure_reachy';
let settings = { groqKey: '', elevenlabsKey: '', cooldown: 10, praiseEnabled: true };
let voiceOverrides = {};

// ─── Utilities ───────────────────────────────────────────────────────────────
const sleep = ms => new Promise(r => setTimeout(r, ms));
const pick = arr => arr[Math.floor(Math.random() * arr.length)];

// ─── Animations (translated from animations.py) ───────────────────────────────
async function curiousLook() {
    if (!robot) return;
    robot.setHeadPose(15, -5, 0);
    robot.setAntennas(30, 15);
    await sleep(400);
    robot.setAntennas(0, 0);
    await sleep(500);
    robot.setHeadPose(0, 0, 0);
}

async function disappointedShake() {
    if (!robot) return;
    for (let i = 0; i < 3; i++) {
        robot.setHeadPose(-15, 0, 0);
        robot.setAntennas(-10, -10);
        await sleep(150);
        robot.setHeadPose(15, 0, 0);
        await sleep(150);
    }
    robot.setHeadPose(0, 0, 0);
    robot.setAntennas(0, 0);
}

async function dramaticSigh() {
    if (!robot) return;
    robot.setHeadPose(0, -15, 0);
    robot.setAntennas(40, 40);
    await sleep(400);
    robot.setHeadPose(0, 10, 0);
    robot.setAntennas(-20, -20);
    await sleep(800);
    robot.setHeadPose(0, 0, 30);
    await sleep(1000);
    robot.setHeadPose(0, 0, 0);
    robot.setAntennas(0, 0);
}

async function approvingNod() {
    if (!robot) return;
    for (let i = 0; i < 2; i++) {
        robot.setHeadPose(0, 5, 0);
        robot.setAntennas(15, 15);
        await sleep(200);
        robot.setHeadPose(0, -5, 0);
        await sleep(200);
    }
    robot.setHeadPose(0, 0, 0);
    robot.setAntennas(10, 10);
    await sleep(300);
    robot.setAntennas(0, 0);
}

function getAnimation(count) {
    if (count <= 1) return curiousLook;
    if (count <= 3) return disappointedShake;
    return dramaticSigh;
}

// ─── Sound / LLM / TTS ───────────────────────────────────────────────────────
async function playEmotion(name) {
    if (!robot) return;
    try { await robot.playSound(`${EMOTIONS_BASE}/${name}.wav`); }
    catch (e) { console.warn('playSound error:', e); }
}

async function getLLMResponse(pKey, isShame, count) {
    const p = PERSONALITIES[pKey];
    const data = isShame ? p.shame : p.praise;
    const fallback = pick(isShame ? p.prewrittenShame : p.prewrittenPraise);
    if (!settings.groqKey || !data) return fallback;
    try {
        const prompt = isShame
            ? `You are ${p.name}.\nTone: ${data.tone}\nVocabulary: ${data.vocab?.join(', ')}\nStructure: ${data.structure}\nExamples: ${data.examples?.join(' | ')}\nThe user picked up their phone ${count} time(s). Give ONE shame comment. Max 15 words. ${p.avoid || ''}`
            : `You are ${p.name}.\nTone: ${data.tone}\nExamples: ${data.examples?.join(' | ')}\nUser put their phone down. ONE praise comment. Max 12 words.`;
        const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${settings.groqKey}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: 'llama-3.1-8b-instant', messages: [{ role: 'user', content: prompt }], max_tokens: 60 })
        });
        const json = await resp.json();
        return json.choices?.[0]?.message?.content?.trim() || fallback;
    } catch { return fallback; }
}

async function speakText(text, pKey) {
    const p = PERSONALITIES[pKey];
    const voiceId = voiceOverrides[pKey]?.eleven || p.elevenVoices?.[0];
    if (settings.elevenlabsKey && voiceId) {
        try {
            const resp = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
                method: 'POST',
                headers: { 'xi-api-key': settings.elevenlabsKey, 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, model_id: 'eleven_monolingual_v1', voice_settings: { stability: 0.5, similarity_boost: 0.75 } })
            });
            if (resp.ok) {
                const url = URL.createObjectURL(await resp.blob());
                await new Promise((res, rej) => { const a = new Audio(url); a.onended = res; a.onerror = rej; a.play().catch(rej); });
                URL.revokeObjectURL(url);
                return;
            }
        } catch { /* fall through to Web Speech */ }
    }
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = p.lang || 'en-US';
    const edgeName = voiceOverrides[pKey]?.edge;
    if (edgeName) { const v = speechSynthesis.getVoices().find(v => v.name === edgeName); if (v) utt.voice = v; }
    speechSynthesis.speak(utt);
}

// ─── Phone event handlers ────────────────────────────────────────────────────
async function handlePhonePickup() {
    if (isAnimating) return;
    isAnimating = true;
    offenseCount++;
    totalBusts++;
    streakStart = null;
    updateStats();

    let pKey = selectedPersonality === 'mixtape' ? pick(RANDOM_PERSONALITIES) : selectedPersonality;
    const anim = getAnimation(offenseCount);

    if (pKey === 'pure_reachy') {
        const emotion = pick(PERSONALITIES.pure_reachy.shameEmotions);
        await Promise.all([anim(), playEmotion(emotion)]);
        setResponseText(`😡 *${emotion}*`);
    } else {
        const [text] = await Promise.all([getLLMResponse(pKey, true, offenseCount), anim()]);
        setResponseText(`😤 "${text}"`);
        speakText(text, pKey);
    }
    isAnimating = false;
}

async function handlePhonePutdown() {
    if (!settings.praiseEnabled) return;
    isAnimating = true;
    streakStart = Date.now();
    updateStats();

    let pKey = selectedPersonality === 'mixtape' ? pick(RANDOM_PERSONALITIES) : selectedPersonality;

    if (pKey === 'pure_reachy') {
        const emotion = pick(PERSONALITIES.pure_reachy.praiseEmotions);
        await Promise.all([approvingNod(), playEmotion(emotion)]);
        setResponseText(`✨ *${emotion}*`);
    } else {
        const [text] = await Promise.all([getLLMResponse(pKey, false, offenseCount), approvingNod()]);
        setResponseText(`✅ "${text}"`);
        speakText(text, pKey);
    }
    isAnimating = false;
}

// ─── Detection loop (on WebRTC video) ────────────────────────────────────────
async function initModel() {
    setLoaderText('Loading AI model...');
    showLoader(true);
    rvModel = await AutoModel.from_pretrained('onnx-community/yolo26m-ONNX', { device: 'webgpu', dtype: 'fp16' });
    setLoaderText('Loading processor...');
    rvProcessor = await AutoProcessor.from_pretrained('onnx-community/yolo26m-ONNX');
    showLoader(false);
}

async function detectOnFrame() {
    const video = document.getElementById('rv-video');
    const canvas = document.getElementById('rv-canvas');
    if (!video.videoWidth) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    const targetW = 256;
    const targetH = Math.round((targetW / video.videoWidth) * video.videoHeight);
    const small = document.createElement('canvas');
    small.width = targetW; small.height = targetH;
    small.getContext('2d').drawImage(video, 0, 0, targetW, targetH);

    const inputs = await rvProcessor(RawImage.fromCanvas(small));
    const output = await rvModel(inputs);
    const scores = output.logits.sigmoid().data;
    const boxes = output.pred_boxes.data;
    const confThreshold = lastPhoneBox ? 0.2 : 0.3;

    let best = null, bestScore = 0;
    for (let i = 0; i < 300; i++) {
        let maxS = 0, maxC = 0;
        for (let j = 0; j < 80; j++) { const s = scores[i*80+j]; if (s > maxS) { maxS = s; maxC = j; } }
        if (maxC === PHONE_CLASS_ID && maxS >= confThreshold && maxS > bestScore) {
            bestScore = maxS;
            const [cx, cy, w, h] = [boxes[i*4], boxes[i*4+1], boxes[i*4+2], boxes[i*4+3]];
            const sx = canvas.width/targetW, sy = canvas.height/targetH;
            best = { x1:(cx-w/2)*targetW*sx, y1:(cy-h/2)*targetH*sy, x2:(cx+w/2)*targetW*sx, y2:(cy+h/2)*targetH*sy, confidence:maxS };
        }
    }

    const detections = [];
    if (best) { lastPhoneBox = best; framesWithoutDetection = 0; detections.push(best); }
    else if (lastPhoneBox && framesWithoutDetection < 3) { framesWithoutDetection++; detections.push({ ...lastPhoneBox, confidence: lastPhoneBox.confidence * 0.9 }); }
    else { lastPhoneBox = null; framesWithoutDetection = 0; }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    for (const d of detections) {
        ctx.strokeStyle = '#00ff00'; ctx.lineWidth = 3;
        ctx.strokeRect(d.x1, d.y1, d.x2-d.x1, d.y2-d.y1);
        ctx.fillStyle = '#00ff00'; ctx.font = '16px Arial';
        ctx.fillText(`phone ${(d.confidence*100).toFixed(0)}%`, d.x1, d.y1-10);
    }

    // State machine
    const phoneInFrame = detections.length > 0;
    if (phoneInFrame) { consecutivePhone++; consecutiveNoPhone = 0; }
    else { consecutiveNoPhone++; }

    const now = Date.now();
    const cooldownMs = settings.cooldown * 1000;

    if (consecutivePhone >= PICKUP_THRESHOLD && !phoneVisible) {
        phoneVisible = true; consecutiveNoPhone = 0;
        if (now - lastReactionTime >= cooldownMs) { lastReactionTime = now; handlePhonePickup(); }
    }
    if (phoneVisible && phoneInFrame && now - lastReactionTime >= cooldownMs) {
        lastReactionTime = now; handlePhonePickup();
    }
    if (consecutiveNoPhone >= PUTDOWN_THRESHOLD && phoneVisible) {
        phoneVisible = false; consecutivePhone = 0; lastReactionTime = 0; handlePhonePutdown();
    }

    const dot = document.getElementById('rv-detect-dot');
    const txt = document.getElementById('rv-detect-text');
    if (phoneVisible) { dot.className = 'status-dot detected'; txt.textContent = '📱 PHONE DETECTED!'; }
    else { dot.className = 'status-dot monitoring'; txt.textContent = '✅ Phone-free'; }
}

function detectionLoop() {
    if (!isMonitoring) return;
    if (!isProcessing) {
        isProcessing = true;
        const t0 = performance.now();
        detectOnFrame()
            .then(() => { document.getElementById('rv-fps').textContent = Math.round(1000 / (performance.now() - t0)); })
            .catch(console.error)
            .finally(() => { isProcessing = false; });
    }
    rvAnimId = requestAnimationFrame(detectionLoop);
}

// ─── Stats & UI helpers ───────────────────────────────────────────────────────
function updateStats() {
    document.getElementById('rv-stat-count').textContent = totalBusts;
    if (totalBusts > 0) document.getElementById('rv-reset-section').style.display = '';
}

function startStreakTimer() {
    clearInterval(streakInterval);
    streakInterval = setInterval(() => {
        const secs = streakStart ? Math.floor((Date.now() - streakStart) / 1000) : 0;
        const label = secs >= 60 ? Math.floor(secs / 60) + 'm' : secs + 's';
        document.getElementById('rv-stat-streak').textContent = label;
        if (secs > longestStreak) {
            longestStreak = secs;
            const lLabel = secs >= 60 ? Math.floor(secs / 60) + 'm' : secs + 's';
            document.getElementById('rv-stat-longest').textContent = lLabel;
        }
    }, 1000);
}

function updateStatusBar() {
    const p = PERSONALITIES[selectedPersonality];
    document.getElementById('rv-mode-name').textContent = p.name;
    const llm = settings.groqKey ? 'Groq' : 'Pre-written';
    const tts = settings.elevenlabsKey ? 'ElevenLabs' : 'Web Speech';
    document.getElementById('rv-tech-badge').textContent =
        selectedPersonality === 'pure_reachy' ? 'Emotion sounds' : `${llm} → ${tts}`;
    const notice = document.getElementById('rv-api-notice');
    if (notice) notice.style.display = (!settings.groqKey && selectedPersonality !== 'pure_reachy') ? '' : 'none';
}

function setResponseText(text) { document.getElementById('rv-response-text').textContent = text; }

function setSigninError(msg) {
    let el = document.getElementById('rv-signin-error');
    if (!el) {
        el = document.createElement('p');
        el.id = 'rv-signin-error';
        el.style.cssText = 'color:#ff6b6b;font-size:0.85rem;margin-top:0.75rem';
        document.getElementById('rv-signin-btn').after(el);
    }
    el.textContent = msg;
}
function showLoader(visible) { document.getElementById('rv-loader').classList.toggle('visible', visible); }
function setLoaderText(text) { document.getElementById('rv-loader-text').textContent = text; }

function showRVState(id) {
    ['rv-signin','rv-picker','rv-monitoring'].forEach(s => {
        document.getElementById(s).style.display = s === id ? '' : 'none';
    });
}

// ─── Settings persistence ─────────────────────────────────────────────────────
function loadSettings() {
    try {
        const s = JSON.parse(localStorage.getItem('judgy-robot-settings') || '{}');
        settings = { ...settings, ...s };
        voiceOverrides = JSON.parse(localStorage.getItem('judgy-robot-voices') || '{}');
    } catch {}
}

function saveSettings() {
    localStorage.setItem('judgy-robot-settings', JSON.stringify(settings));
    localStorage.setItem('judgy-robot-voices', JSON.stringify(voiceOverrides));
}

// ─── UI population ────────────────────────────────────────────────────────────
function populatePersonalities() {
    const container = document.getElementById('rv-personalities');
    container.innerHTML = '';
    Object.entries(PERSONALITIES).forEach(([key, p]) => {
        const item = document.createElement('div');
        item.className = 'rv-personality-item' + (key === selectedPersonality ? ' active' : '');
        item.dataset.key = key;

        const name = document.createElement('span');
        name.className = 'rv-personality-name';
        name.textContent = p.name;
        item.appendChild(name);

        if (key !== 'pure_reachy') {
            const vBtn = document.createElement('button');
            vBtn.className = 'rv-voice-icon-btn';
            vBtn.textContent = '🎙';
            vBtn.title = 'Voice settings';
            vBtn.addEventListener('click', e => { e.stopPropagation(); openVoiceModal(key); });
            item.appendChild(vBtn);
        }

        item.addEventListener('click', () => {
            selectedPersonality = key;
            container.querySelectorAll('.rv-personality-item').forEach(c => c.classList.toggle('active', c.dataset.key === key));
            updateStatusBar();
            // Update toggle label and collapse on mobile
            const toggleLabel = document.getElementById('rv-personality-toggle-label');
            if (toggleLabel) toggleLabel.textContent = p.name;
            document.getElementById('rv-personality-panel')?.classList.remove('expanded');
        });
        container.appendChild(item);
    });
    updateStatusBar();
    const toggleLabel = document.getElementById('rv-personality-toggle-label');
    if (toggleLabel) toggleLabel.textContent = PERSONALITIES[selectedPersonality]?.name || '';
}

function populateSettingsModal() {
    document.getElementById('rv-set-groq').value = settings.groqKey;
    document.getElementById('rv-set-eleven').value = settings.elevenlabsKey;
    document.getElementById('rv-set-cooldown').value = settings.cooldown;
    document.getElementById('rv-set-cooldown-val').textContent = settings.cooldown + 's';
    document.getElementById('rv-set-praise').checked = settings.praiseEnabled;
}

let _voiceModalKey = null;

function openVoiceModal(pKey) {
    _voiceModalKey = pKey;
    const p = PERSONALITIES[pKey];
    const override = voiceOverrides[pKey] || {};
    document.getElementById('rv-voice-modal-title').textContent = `Voice Settings — ${p.name}`;
    document.getElementById('rv-voice-eleven').value = override.eleven || '';
    document.getElementById('rv-voice-edge').value = override.edge || '';
    document.getElementById('rv-voice-eleven-hint').textContent =
        p.elevenVoices?.[0] ? `Default: ${p.elevenVoices[0]}` : '';
    document.getElementById('rv-voices-modal').style.display = '';
}

// ─── Robot connection ─────────────────────────────────────────────────────────
async function setupRobot() {
    robot = new ReachyMini({ appName: 'judgy-reachy-no-phone' });

    robot.addEventListener('robotsChanged', e => {
        const robots = e.detail;
        const list = document.getElementById('rv-robot-list');
        list.innerHTML = '';
        if (!robots.length) {
            list.innerHTML = '<p class="rv-no-robots">No robots online. Make sure your robot daemon is running and connected.</p>';
            return;
        }
        robots.forEach(r => {
            const btn = document.createElement('button');
            btn.className = 'rv-robot-btn';
            btn.innerHTML = `🤖 <strong>${r.name || r.id}</strong><span class="rv-robot-id">${r.id}</span>`;
            btn.addEventListener('click', () => startSession(r.id, r.name || r.id));
            list.appendChild(btn);
        });
    });

    robot.addEventListener('streaming', async () => {
        isStreaming = true;
        await robot.ensureAwake();
        const videoEl = document.getElementById('rv-video');
        detachVideo = robot.attachVideo(videoEl);
        showRVState('rv-monitoring');
        populatePersonalities();
        startStreakTimer();
        if (!rvModel) await initModel();
    });

    robot.addEventListener('sessionStopped', () => {
        isStreaming = false;
        stopMonitoring();
        if (detachVideo) { detachVideo(); detachVideo = null; }
        showRVState('rv-picker');
    });

    robot.addEventListener('sessionRejected', e => {
        alert(`Robot is busy with: ${e.detail?.activeApp || 'another app'}`);
    });

    robot.addEventListener('error', e => console.error('Robot error:', e));
}

async function startSession(robotId, robotName) {
    await robot.startSession(robotId);
}

function stopMonitoring() {
    isMonitoring = false;
    if (rvAnimId) { cancelAnimationFrame(rvAnimId); rvAnimId = null; }
    clearInterval(streakInterval);
    const btn = document.getElementById('rv-toggle-btn');
    if (btn) { btn.innerHTML = '▶️ Start Monitoring'; btn.classList.replace('btn-danger','btn-primary'); }
    const dot = document.getElementById('rv-detect-dot');
    const txt = document.getElementById('rv-detect-text');
    if (dot) dot.className = 'status-dot';
    if (txt) txt.textContent = 'Monitoring off';
}

// ─── Event listeners ──────────────────────────────────────────────────────────
function setupEventListeners() {
    // Personality collapse toggle (mobile)
    document.getElementById('rv-personality-toggle').addEventListener('click', () => {
        document.getElementById('rv-personality-panel').classList.toggle('expanded');
    });

    // Sign in (HF OAuth — works on Space domain only)
    document.getElementById('rv-signin-btn').addEventListener('click', async () => {
        if (!robot) await setupRobot();
        const authenticated = await robot.authenticate();
        if (!authenticated) { await robot.login(); return; }
        await robot.connect();
        showRVState('rv-picker');
    });

    // Monitoring toggle
    document.getElementById('rv-toggle-btn').addEventListener('click', () => {
        if (!isStreaming) return;
        isMonitoring = !isMonitoring;
        const btn = document.getElementById('rv-toggle-btn');
        if (isMonitoring) {
            btn.innerHTML = '🛑 Stop Monitoring';
            btn.classList.replace('btn-primary','btn-danger');
            offenseCount = 0; phoneVisible = false; consecutivePhone = 0; consecutiveNoPhone = 0;
            lastPhoneBox = null; framesWithoutDetection = 0; lastReactionTime = 0;
            streakStart = Date.now(); updateStats();
            document.getElementById('rv-detect-dot').className = 'status-dot monitoring';
            document.getElementById('rv-detect-text').textContent = '✅ Phone-free';
            detectionLoop();
        } else {
            stopMonitoring();
        }
    });

    // Test button
    document.getElementById('rv-test-btn').addEventListener('click', () => {
        if (isStreaming) handlePhonePickup();
    });

    // Reset button
    document.getElementById('rv-reset-btn').addEventListener('click', () => {
        totalBusts = 0; offenseCount = 0; longestStreak = 0; streakStart = Date.now();
        updateStats();
        document.getElementById('rv-stat-streak').textContent = '0s';
        document.getElementById('rv-stat-longest').textContent = '0s';
        document.getElementById('rv-reset-section').style.display = 'none';
        setResponseText('Stats reset. Start monitoring to begin.');
    });

    // Disconnect
    document.getElementById('rv-disconnect-btn').addEventListener('click', async () => {
        stopMonitoring();
        if (robot) { await robot.stopSession?.(); await robot.disconnect(); robot = null; }
        isStreaming = false;
        showRVState('rv-signin');
    });

    // Settings modal
    document.getElementById('rv-settings-btn').addEventListener('click', () => {
        populateSettingsModal();
        document.getElementById('rv-settings-modal').style.display = '';
    });
    document.getElementById('rv-settings-close').addEventListener('click', () => {
        document.getElementById('rv-settings-modal').style.display = 'none';
    });
    document.getElementById('rv-settings-modal').addEventListener('click', e => {
        if (e.target === e.currentTarget) e.currentTarget.style.display = 'none';
    });
    document.getElementById('rv-set-cooldown').addEventListener('input', e => {
        document.getElementById('rv-set-cooldown-val').textContent = e.target.value + 's';
    });
    document.getElementById('rv-settings-save').addEventListener('click', () => {
        settings.groqKey = document.getElementById('rv-set-groq').value.trim();
        settings.elevenlabsKey = document.getElementById('rv-set-eleven').value.trim();
        settings.cooldown = parseInt(document.getElementById('rv-set-cooldown').value);
        settings.praiseEnabled = document.getElementById('rv-set-praise').checked;
        saveSettings();
        document.getElementById('rv-settings-modal').style.display = 'none';
    });

    // Voice modal (per-personality, opened from personality card 🎙 button)
    document.getElementById('rv-voices-close').addEventListener('click', () => {
        document.getElementById('rv-voices-modal').style.display = 'none';
    });
    document.getElementById('rv-voices-modal').addEventListener('click', e => {
        if (e.target === e.currentTarget) e.currentTarget.style.display = 'none';
    });
    document.getElementById('rv-voices-save').addEventListener('click', () => {
        if (!_voiceModalKey) return;
        if (!voiceOverrides[_voiceModalKey]) voiceOverrides[_voiceModalKey] = {};
        voiceOverrides[_voiceModalKey].eleven = document.getElementById('rv-voice-eleven').value.trim();
        voiceOverrides[_voiceModalKey].edge = document.getElementById('rv-voice-edge').value.trim();
        saveSettings();
        document.getElementById('rv-voices-modal').style.display = 'none';
    });
}

// ─── Mode toggle wiring ───────────────────────────────────────────────────────
function setupModeToggle() {
    const infoBtn = document.getElementById('toggle-info');
    const robotBtn = document.getElementById('toggle-robot');
    const infoView = document.getElementById('info-view');
    const robotView = document.getElementById('robot-view');

    infoBtn.addEventListener('click', () => {
        infoView.style.display = '';
        robotView.style.display = 'none';
        infoBtn.classList.add('active');
        robotBtn.classList.remove('active');
    });

    robotBtn.addEventListener('click', async () => {
        infoView.style.display = 'none';
        robotView.style.display = '';
        infoBtn.classList.remove('active');
        robotBtn.classList.add('active');

        if (!robotInitialized) {
            robotInitialized = true;
            try {
                if (!robot) await setupRobot();
                const authenticated = await robot.authenticate();
                if (authenticated) {
                    await robot.connect();
                    showRVState('rv-picker');
                } else {
                    showRVState('rv-signin');
                }
            } catch (e) {
                console.error('init failed:', e);
                showRVState('rv-signin');
            }
        }
    });
}

// ─── Init ─────────────────────────────────────────────────────────────────────
function init() {
    loadSettings();
    setupModeToggle();
    setupEventListeners();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
