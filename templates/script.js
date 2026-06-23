const canvas = document.getElementById("arcadeCanvas");
const ctx = canvas.getContext("2d");
const oscCanvas = document.getElementById("oscilloscopeCanvas");
const oscCtx = oscCanvas.getContext("2d");

let socket = null;
let signalHistory = [];
const maxTraceSamples = 120;
let globalCognitiveState = "RELAXED";

// --- FIXED STRAIGHT LINE HIGHWAY ENGINE ---
let car = { x: 177, y: 430, width: 46, height: 82, targetSpeed: 0, speed: 0, maxVelocity: 22 };
let score = 0;
let totalOdometer = 0;
let animatedLineOffset = 0;

function progressEngineTicks() {
    car.speed += (car.targetSpeed - car.speed) * 0.05;
    totalOdometer += car.speed;
    animatedLineOffset = (animatedLineOffset + car.speed) % 80;

    if (car.speed > 1) {
        score += Math.floor(car.speed * 0.1);
    }
    car.x = 177; 
}

function renderArcadeGraphics() {
    // Asphalt Track Base
    ctx.fillStyle = "#0e0e12";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Side Shoulders
    ctx.fillStyle = "#050507";
    ctx.fillRect(0, 0, 30, canvas.height);
    ctx.fillRect(canvas.width - 30, 0, 30, canvas.height);

    // Subtle dark curbing layout markers
    ctx.fillStyle = "#1c1c24"; 
    for(let y = (animatedLineOffset % 40) - 40; y < canvas.height; y += 40) {
        ctx.fillRect(25, y, 5, 20);
        ctx.fillRect(canvas.width - 30, y, 5, 20);
    }

    // Central lane dashed lines
    ctx.strokeStyle = "#3f3f46";
    ctx.lineWidth = 2;
    ctx.setLineDash([30, 50]);
    ctx.lineDashOffset = -animatedLineOffset;

    for (let x = 110; x < canvas.width - 100; x += 80) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    ctx.setLineDash([]); 

    // --- DRAW TOP-DOWN VEHICLE (No Glow) ---
    ctx.save();
    let colorAccent = (globalCognitiveState === "ATTENTIVE") ? lookupStyle('--accent-cyan') : lookupStyle('--accent-blue');
    
    // 1. Tires (4 corner wheels)
    ctx.fillStyle = "#18181b";
    ctx.fillRect(car.x - 3, car.y + 10, 5, 14); // Front Left
    ctx.fillRect(car.x + car.width - 2, car.y + 10, 5, 14); // Front Right
    ctx.fillRect(car.x - 3, car.y + car.height - 24, 5, 16); // Rear Left
    ctx.fillRect(car.x + car.width - 2, car.y + car.height - 24, 5, 16); // Rear Right

    // 2. Side Mirrors
    ctx.fillStyle = colorAccent;
    ctx.fillRect(car.x - 4, car.y + 24, 5, 4);
    ctx.fillRect(car.x + car.width - 1, car.y + 24, 5, 4);

    // 3. Main Chassis/Body (Tapered top-down blueprint)
    ctx.fillStyle = colorAccent;
    ctx.beginPath();
    ctx.moveTo(car.x + 8, car.y); // Front left hood
    ctx.lineTo(car.x + car.width - 8, car.y); // Front right hood
    ctx.lineTo(car.x + car.width, car.y + 16); // Front fender right
    ctx.lineTo(car.x + car.width, car.y + car.height - 8); // Rear right
    ctx.lineTo(car.x + car.width - 4, car.y + car.height); // Rear bumper right
    ctx.lineTo(car.x + 4, car.y + car.height); // Rear bumper left
    ctx.lineTo(car.x, car.y + car.height - 8); // Rear left
    ctx.lineTo(car.x, car.y + 16); // Front fender left
    ctx.closePath();
    ctx.fill();

    // 4. Windshield & Glass Greenhouse Canopy
    ctx.fillStyle = "#111115";
    ctx.beginPath();
    ctx.moveTo(car.x + 8, car.y + 22); // Windshield base left
    ctx.lineTo(car.x + car.width - 8, car.y + 22); // Windshield base right
    ctx.lineTo(car.x + car.width - 6, car.y + 36); // Side window right
    ctx.lineTo(car.x + car.width - 8, car.y + 54); // Rear window right
    ctx.lineTo(car.x + 8, car.y + 54); // Rear window left
    ctx.lineTo(car.x + 6, car.y + 36); // Side window left
    ctx.closePath();
    ctx.fill();

    // 5. Front Hood Detailing
    ctx.strokeStyle = "#050507";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(car.x + 12, car.y + 2);
    ctx.lineTo(car.x + 12, car.y + 16);
    ctx.moveTo(car.x + car.width - 12, car.y + 2);
    ctx.lineTo(car.x + car.width - 12, car.y + 16);
    ctx.stroke();

    // 6. Rear spoiler wing profile
    ctx.fillStyle = "#050507";
    ctx.fillRect(car.x + 2, car.y + car.height - 5, car.width - 4, 3);

    ctx.restore();

    // Dashboard Overlay fonts
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 16px monospace";
    ctx.fillText(`SCORE: ${score}`, 45, 45);
    ctx.font = "12px system-ui";
    ctx.fillStyle = lookupStyle('--text-muted');
    ctx.fillText(`SPEED: ${Math.round(car.speed * 12)} KM/H`, 45, 65);
}

// --- PIPELINE WEBSOCKET CORE HANDSHAKE ---
function connectPipeline(streamMode) {
    document.getElementById('btn-hardware').disabled = true;
    document.getElementById('btn-simulation').disabled = true;
    
    car.speed = 0; car.targetSpeed = 0; score = 0; totalOdometer = 0;

    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${wsScheme}://${window.location.host}/pipeline_stream`);

    socket.onopen = function() {
        socket.send(JSON.stringify({ "command": "START", "mode": streamMode }));
    };

    socket.onmessage = function(event) {
        const packet = JSON.parse(event.data);
        
        globalCognitiveState = packet.state;
        
        const elementState = document.getElementById('val-state');
        elementState.innerText = packet.state;
        elementState.className = "tile-value " + (packet.state === "ATTENTIVE" ? "status-attentive" : "status-relaxed");

        document.getElementById('val-action').innerText = packet.action === "ACCELERATE" ? "THROTTLE ON" : "OFF (BRAKING)";
        document.getElementById('val-signal').innerText = packet.signal ? Number(packet.signal).toFixed(0) : "---";

        if (packet.signal !== undefined) {
            signalHistory.push(Number(packet.signal));
            if (signalHistory.length > maxTraceSamples) signalHistory.shift();
        }

        if (packet.action === "ACCELERATE") {
            car.targetSpeed = car.maxVelocity;
        } else {
            car.targetSpeed = 1;
        }
    };

    socket.onclose = function() {
        document.getElementById('btn-hardware').disabled = false;
        document.getElementById('btn-simulation').disabled = false;
    };
}

function lookupStyle(property) { 
    return getComputedStyle(document.documentElement).getPropertyValue(property).trim(); 
}

function scaleTraceViewport() {
    oscCanvas.width = oscCanvas.parentElement.clientWidth;
    oscCanvas.height = oscCanvas.parentElement.clientHeight;
}
window.addEventListener('resize', scaleTraceViewport);
scaleTraceViewport();

function renderOscilloscope() {
    oscCtx.clearRect(0, 0, oscCanvas.width, oscCanvas.height);
    oscCtx.strokeStyle = "#161622";
    oscCtx.lineWidth = 1;
    for(let i = 1; i < 4; i++) {
        let currentY = (oscCanvas.height / 4) * i;
        oscCtx.beginPath(); oscCtx.moveTo(0, currentY); oscCtx.lineTo(oscCanvas.width, currentY); oscCtx.stroke();
    }
    if (signalHistory.length < 2) return;
    
    oscCtx.beginPath();
    oscCtx.strokeStyle = globalCognitiveState === "ATTENTIVE" ? lookupStyle('--accent-cyan') : lookupStyle('--accent-blue');
    oscCtx.lineWidth = 1.5;
    for (let i = 0; i < signalHistory.length; i++) {
        const targetX = (oscCanvas.width / (maxTraceSamples - 1)) * i;
        const targetY = oscCanvas.height - ((signalHistory[i] / 1023) * oscCanvas.height);
        if (i === 0) oscCtx.moveTo(targetX, targetY); else oscCtx.lineTo(targetX, targetY);
    }
    oscCtx.stroke();
}

function processingLoop() {
    progressEngineTicks();
    renderArcadeGraphics();
    renderOscilloscope();
    requestAnimationFrame(processingLoop);
}
processingLoop();