// ============================================
// SMART GRID DASHBOARD - MAIN SCRIPT
// ============================================

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const DATA_FETCH_INTERVAL = 3000; // 3 seconds
const STATUS_UPDATE_INTERVAL = 2000; // 2 seconds
const COST_PER_KWH = 25; // KES

// Chart Data
let labels = [];
let powerData = [];
let voltageData = [];
let currentData = [];

let totalEnergy = 0;

// Initialize Chart
const ctx = document.getElementById('chart');
if (!ctx) {
    console.error('Chart canvas not found');
} else {
    var chart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Power (W)',
                    data: powerData,
                    borderColor: '#2196f3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#2196f3',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Voltage (V)',
                    data: voltageData,
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#f44336',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Current (A)',
                    data: currentData,
                    borderColor: '#ff9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#ff9800',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                duration: 0 // Disable animation for smooth updates
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'white',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: 20
                    }
                },
                filler: {
                    propagate: true
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: 'white',
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    }
                },
                y: {
                    ticks: {
                        color: 'white',
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    }
                }
            }
        }
    });
}

// ============================================
// SOUND ALERT
// ============================================
function playBeep() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (err) {
        console.warn('Audio context not available:', err);
    }
}

// ============================================
// ALERT LOGIC
// ============================================
function checkAlerts(power, voltage, current, deviceOn) {
    let alerts = [];

    // Check for conditions
    if (voltage > 240) alerts.push("⚠️ High Voltage! (>240V)");
    if (voltage < 190) alerts.push("⚠️ Low Voltage! (<190V)");
    if (current > 5) alerts.push("⚠️ High Current! (>5A)");
    if (power > 500) alerts.push("⚠️ High Power Consumption! (>500W)");
    if (!deviceOn && power > 10) alerts.push("⚠️ Power flowing while device is OFF!");

    const alertBox = document.getElementById('alertBox');
    const alertMsg = document.getElementById('alertMessage');

    if (alerts.length > 0) {
        // Show alerts
        alertBox.style.display = 'block';
        alertBox.classList.remove('alert-safe');
        alertMsg.innerHTML = alerts.join('<br>');
        playBeep();
    } else {
        // System normal
        alertBox.style.display = 'block';
        alertBox.classList.add('alert-safe');
        alertMsg.innerHTML = '✅ System Normal - All Parameters OK';
    }
}

// ============================================
// FETCH REAL-TIME DATA
// ============================================
async function fetchData() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/data/all/?limit=1`);
        
        if (!res.ok) {
            throw new Error(`API Error: ${res.status}`);
        }

        const data = await res.json();

        if (data.length > 0) {
            const latest = data[0];

            // Format time
            const time = new Date(latest.timestamp).toLocaleTimeString();

            // Add to chart
            labels.push(time);
            powerData.push(latest.power);
            voltageData.push(latest.voltage);
            currentData.push(latest.current);

            // Update display
            document.getElementById('power').innerText = latest.power.toFixed(2);
            document.getElementById('voltage').innerText = latest.voltage.toFixed(2);
            document.getElementById('current').innerText = latest.current.toFixed(2);

            // Calculate energy (5 seconds interval = 5/3600 hours)
            totalEnergy += (latest.power / 1000) * (5 / 3600);
            document.getElementById('energy').innerText = totalEnergy.toFixed(4);

            // Calculate cost
            const cost = totalEnergy * COST_PER_KWH;
            document.getElementById('cost').innerText = cost.toFixed(2);

            // Keep only last 20 data points on chart
            if (labels.length > 20) {
                labels.shift();
                powerData.shift();
                voltageData.shift();
                currentData.shift();
            }

            // Update chart
            if (chart) {
                chart.data.labels = labels;
                chart.data.datasets[0].data = powerData;
                chart.data.datasets[1].data = voltageData;
                chart.data.datasets[2].data = currentData;
                chart.update();
            }

            // Get device status for alerts
            const statusRes = await fetch(`${API_BASE_URL}/api/device/status/`);
            const statusData = await statusRes.json();

            // Check alerts
            checkAlerts(latest.power, latest.voltage, latest.current, statusData.on);
        }
    } catch (err) {
        console.error('Error fetching data:', err);
        document.getElementById('power').innerText = 'Error';
        document.getElementById('voltage').innerText = 'Error';
        document.getElementById('current').innerText = 'Error';
    }
}

// ============================================
// DEVICE CONTROL
// ============================================
async function turnOn() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/device/on/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (res.ok) {
            console.log('Device turned ON');
            updateStatus();
        } else {
            console.error('Failed to turn on device');
        }
    } catch (err) {
        console.error('Error turning on device:', err);
    }
}

async function turnOff() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/device/off/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (res.ok) {
            console.log('Device turned OFF');
            updateStatus();
        } else {
            console.error('Failed to turn off device');
        }
    } catch (err) {
        console.error('Error turning off device:', err);
    }
}

// ============================================
// UPDATE STATUS
// ============================================
async function updateStatus() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/device/status/`);

        if (!res.ok) {
            throw new Error(`API Error: ${res.status}`);
        }

        const data = await res.json();
        const statusEl = document.getElementById('status');

        if (data.on) {
            statusEl.innerText = 'ON';
            statusEl.className = 'status-badge on-status';
        } else {
            statusEl.innerText = 'OFF';
            statusEl.className = 'status-badge off-status';
        }
    } catch (err) {
        console.error('Error updating status:', err);
        document.getElementById('status').innerText = 'Error';
    }
}

// ============================================
// INITIALIZATION
// ============================================
function init() {
    console.log('Dashboard initialized');
    console.log('API Base URL:', API_BASE_URL);

    // Initial calls
    updateStatus();
    fetchData();

    // Set intervals for continuous updates
    setInterval(fetchData, DATA_FETCH_INTERVAL);
    setInterval(updateStatus, STATUS_UPDATE_INTERVAL);
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}