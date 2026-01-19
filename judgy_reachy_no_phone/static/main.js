// State
let selectedPersonality = 'mixtape';

// Update UI based on API keys (without starting monitoring)
async function updateUIForAPIKeys() {
    const groqKey = document.getElementById('groq-key').value;
    const elevenKey = document.getElementById('eleven-key').value;
    const elevenVoice = document.getElementById('eleven-voice').value;
    const edgeVoice = document.getElementById('edge-voice').value;
    const cooldown = document.getElementById('cooldown').value;
    const praise = document.getElementById('praise-toggle').checked;

    // If no keys, just update UI
    if (!groqKey && !elevenKey) {
        document.getElementById('mode-text').textContent = 'YOLO | Pre-written lines → Edge TTS';
        document.getElementById('api-notice').classList.remove('hidden');
        return;
    }

    try {
        // Validate keys with backend
        const response = await fetch('/api/validate-keys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                groq_key: groqKey,
                eleven_key: elevenKey,
                eleven_voice: elevenVoice,
                edge_voice: edgeVoice,
                cooldown: parseInt(cooldown),
                praise: praise,
                reset: false,
                personality: selectedPersonality
            })
        });

        const data = await response.json();

        // Update tech badge
        document.getElementById('mode-text').textContent = data.mode;

        // Show/hide API notice
        const apiNotice = document.getElementById('api-notice');
        if (data.groq_valid) {
            apiNotice.classList.add('hidden');
        } else {
            apiNotice.classList.remove('hidden');
        }

        // Show validation feedback with detailed errors
        if (data.errors && data.errors.length > 0) {
            alert('Validation errors:\n\n' + data.errors.join('\n'));
        }

    } catch (e) {
        console.error('Key validation failed:', e);
    }
}

// Personality card selection
document.querySelectorAll('.personality-card').forEach(card => {
    card.addEventListener('click', () => {
        // Remove active from all
        document.querySelectorAll('.personality-card').forEach(c => c.classList.remove('active'));
        // Add active to clicked
        card.classList.add('active');
        // Store selection
        selectedPersonality = card.dataset.personality;
    });
});

// Settings modal
const settingsModal = document.getElementById('settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const closeSettings = document.getElementById('close-settings');
const doneSettings = document.getElementById('done-settings');

settingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('active');
});

closeSettings.addEventListener('click', () => {
    settingsModal.classList.remove('active');
});

doneSettings.addEventListener('click', () => {
    settingsModal.classList.remove('active');
    // Update UI immediately based on API keys
    updateUIForAPIKeys();
});

// Close modal on backdrop click
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.classList.remove('active');
    }
});

// Update video feed
async function updateVideo() {
    try {
        const response = await fetch('/api/video-frame');
        const data = await response.json();

        const videoFeed = document.getElementById('video-feed');
        const placeholder = document.getElementById('video-placeholder');
        const standbyBadge = document.querySelector('.standby-badge');

        if (data.frame) {
            videoFeed.src = 'data:image/jpeg;base64,' + data.frame;
            videoFeed.classList.add('active');
            placeholder.classList.add('hidden');
            standbyBadge.style.display = 'none';
        } else {
            videoFeed.classList.remove('active');
            placeholder.classList.remove('hidden');
            standbyBadge.style.display = 'flex';
        }
    } catch (e) {
        console.error('Video update failed:', e);
    }
}

// Update display from API data
async function updateDisplay() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update status badge
        const statusBadge = document.querySelector('.status-badge');
        const statusText = document.getElementById('status-text');

        statusBadge.classList.remove('monitoring', 'detected');

        if (data.status_text.includes('PHONE DETECTED')) {
            statusBadge.classList.add('detected');
            statusText.textContent = 'Phone Detected';
        } else if (data.status_text.includes('Phone-free')) {
            statusBadge.classList.add('monitoring');
            statusText.textContent = 'Monitoring';
        } else {
            statusText.textContent = 'Not Monitoring';
        }

        // Update stats
        document.getElementById('phone-count').textContent = data.phone_count;
        document.getElementById('current-streak').textContent = data.current_streak;
        document.getElementById('longest-streak').textContent = data.longest_streak;

        // Update mode name
        document.getElementById('mode-name').textContent = selectedPersonality.charAt(0).toUpperCase() + selectedPersonality.slice(1).replace('_', ' ');

        // Update tech info (only if monitoring, otherwise keep user's entered keys)
        if (data.is_monitoring) {
            document.getElementById('mode-text').textContent = data.mode;

            // Show/hide API notice based on whether LLM is active
            const apiNotice = document.getElementById('api-notice');
            if (data.mode.includes('LLM + TTS')) {
                apiNotice.classList.add('hidden');
            } else {
                apiNotice.classList.remove('hidden');
            }
        }

        // Update button
        const toggleBtn = document.getElementById('toggle-btn');
        const btnIcon = toggleBtn.querySelector('.btn-icon');
        const btnText = toggleBtn.querySelector('.btn-text');

        if (data.button_text.includes('Stop')) {
            btnIcon.textContent = '⏹';
            btnText.textContent = 'Stop Monitoring';
            toggleBtn.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
        } else if (data.button_text.includes('Continue')) {
            btnIcon.textContent = '▶';
            btnText.textContent = 'Continue Monitoring';
            toggleBtn.style.background = 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)';
        } else {
            btnIcon.textContent = '▶';
            btnText.textContent = 'Start Monitoring';
            toggleBtn.style.background = 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)';
        }

        // Show/hide reset button
        const resetSection = document.getElementById('reset-section');
        if (data.has_previous_session && !data.is_monitoring) {
            resetSection.style.display = 'block';
        } else {
            resetSection.style.display = 'none';
        }

    } catch (e) {
        console.error('Update failed:', e);
    }
}

// Toggle monitoring
async function toggleMonitoring() {
    const groqKey = document.getElementById('groq-key').value;
    const elevenKey = document.getElementById('eleven-key').value;
    const elevenVoice = document.getElementById('eleven-voice').value;
    const edgeVoice = document.getElementById('edge-voice').value;
    const cooldown = document.getElementById('cooldown').value;
    const praise = document.getElementById('praise-toggle').checked;

    try {
        await fetch('/api/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                groq_key: groqKey,
                eleven_key: elevenKey,
                eleven_voice: elevenVoice,
                edge_voice: edgeVoice,
                cooldown: parseInt(cooldown),
                praise: praise,
                reset: false,
                personality: selectedPersonality
            })
        });

        // Update display immediately
        await updateDisplay();

    } catch (e) {
        console.error('Toggle failed:', e);
    }
}

// Reset all stats
async function resetStats() {
    if (!confirm('Reset all statistics? This will clear your phone count, shames, and streaks.')) {
        return;
    }

    try {
        await fetch('/api/reset', { method: 'POST' });
        await updateDisplay();
    } catch (e) {
        console.error('Reset failed:', e);
    }
}

// Test shame response
async function testShame() {
    const groqKey = document.getElementById('groq-key').value;
    const elevenKey = document.getElementById('eleven-key').value;
    const elevenVoice = document.getElementById('eleven-voice').value;
    const edgeVoice = document.getElementById('edge-voice').value;
    const cooldown = document.getElementById('cooldown').value;
    const praise = document.getElementById('praise-toggle').checked;

    try {
        await fetch('/api/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                groq_key: groqKey,
                eleven_key: elevenKey,
                eleven_voice: elevenVoice,
                edge_voice: edgeVoice,
                cooldown: parseInt(cooldown),
                praise: praise,
                reset: false,
                personality: selectedPersonality
            })
        });
        await updateDisplay();
    } catch (e) {
        console.error('Test failed:', e);
    }
}

// Update cooldown value display
document.getElementById('cooldown').addEventListener('input', (e) => {
    document.getElementById('cooldown-value').textContent = e.target.value;
});

// Button handlers
document.getElementById('toggle-btn').addEventListener('click', toggleMonitoring);
document.getElementById('test-btn').addEventListener('click', testShame);
document.getElementById('reset-btn').addEventListener('click', resetStats);

// Auto-update every 100ms for smooth video
setInterval(() => {
    updateVideo();
    updateDisplay();
}, 100);

// Initial update
updateDisplay();
updateVideo();
updateUIForAPIKeys();
