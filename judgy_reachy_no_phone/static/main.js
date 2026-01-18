// State
let isMonitoring = false;
let startTime = null;
let frozenStreak = 0;

// Format duration helper
function formatDuration(seconds) {
    if (seconds < 60) return Math.floor(seconds) + 's';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm';
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return hours + 'h' + mins + 'm';
}

// Update display from API data
async function updateDisplay() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update status text and color
        const statusEl = document.getElementById('status-text');
        statusEl.textContent = data.status_text;
        statusEl.className = '';
        if (data.status_text.includes('PHONE DETECTED')) {
            statusEl.classList.add('detected');
        } else if (data.status_text.includes('Phone-free')) {
            statusEl.classList.add('monitoring');
        }

        // Update stats - only change text content, not DOM structure
        document.getElementById('phone-count').textContent = data.phone_count;
        document.getElementById('total-shames').textContent = data.total_shames;
        document.getElementById('streak-display').textContent = data.streak;
        document.getElementById('mode-text').innerHTML = '<strong>Mode:</strong> ' + data.mode;

        // Track monitoring state
        isMonitoring = data.is_monitoring;

    } catch (e) {
        console.error('Update failed:', e);
    }
}

// Toggle monitoring
async function toggleMonitoring() {
    const groqKey = document.getElementById('groq-key').value;
    const elevenKey = document.getElementById('eleven-key').value;
    const cooldown = document.getElementById('cooldown').value;
    const praise = document.getElementById('praise-toggle').checked;

    try {
        const response = await fetch('/api/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                groq_key: groqKey,
                eleven_key: elevenKey,
                cooldown: parseInt(cooldown),
                praise: praise
            })
        });

        const data = await response.json();

        // Update button text
        const btn = document.getElementById('toggle-btn');
        btn.textContent = data.button_text;

        // Update display immediately
        await updateDisplay();

    } catch (e) {
        console.error('Toggle failed:', e);
    }
}

// Test shame response
async function testShame() {
    try {
        await fetch('/api/test', { method: 'POST' });
        // Update display after test
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

// Auto-update every 500ms - only updates text content, no DOM manipulation
setInterval(updateDisplay, 500);

// Initial update
updateDisplay();
