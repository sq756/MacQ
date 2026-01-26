// MacQ 3D Quantum Simulator - Three.js Application
// WebGL-based 3D visualization

let scene, camera, renderer, blochSphere;
let circuit = [];
let currentQubits = 3;
let probChart;

// Initialize Three.js Scene
function init3D() {
    const canvas = document.getElementById('three-canvas');
    const container = document.getElementById('canvas-container');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e27);

    // Camera
    camera = new THREE.PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(3, 3, 5);
    camera.lookAt(0, 0, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x4A90E2, 1, 100);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);

    const pointLight2 = new THREE.PointLight(0xE24AE2, 0.5, 100);
    pointLight2.position.set(-10, -10, -10);
    scene.add(pointLight2);

    // Create Bloch Sphere
    createBlochSphere();

    // Create particle field
    createParticleField();

    // Animation loop
    animate();

    // Resize handler
    window.addEventListener('resize', onWindowResize);
}

function createBlochSphere() {
    const group = new THREE.Group();

    // Main sphere (transparent)
    const sphereGeometry = new THREE.SphereGeometry(2, 32, 32);
    const sphereMaterial = new THREE.MeshPhongMaterial({
        color: 0x4A90E2,
        transparent: true,
        opacity: 0.2,
        wireframe: false
    });
    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    group.add(sphere);

    // Wireframe
    const wireframeGeometry = new THREE.SphereGeometry(2.01, 16, 16);
    const wireframeMaterial = new THREE.MeshBasicMaterial({
        color: 0x667eea,
        wireframe: true,
        transparent: true,
        opacity: 0.3
    });
    const wireframe = new THREE.Mesh(wireframeGeometry, wireframeMaterial);
    group.add(wireframe);

    // Axes
    const axesMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });

    // X axis (red)
    const xGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-2.5, 0, 0),
        new THREE.Vector3(2.5, 0, 0)
    ]);
    const xAxis = new THREE.Line(xGeometry, new THREE.LineBasicMaterial({ color: 0xff6666 }));
    group.add(xAxis);

    // Y axis (green)
    const yGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, -2.5, 0),
        new THREE.Vector3(0, 2.5, 0)
    ]);
    const yAxis = new THREE.Line(yGeometry, new THREE.LineBasicMaterial({ color: 0x66ff66 }));
    group.add(yAxis);

    // Z axis (blue)
    const zGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, -2.5),
        new THREE.Vector3(0, 0, 2.5)
    ]);
    const zAxis = new THREE.Line(zGeometry, new THREE.LineBasicMaterial({ color: 0x6666ff }));
    group.add(zAxis);

    // State vector arrow
    const arrowHelper = new THREE.ArrowHelper(
        new THREE.Vector3(0, 0, 1),
        new THREE.Vector3(0, 0, 0),
        2,
        0xffd700,
        0.3,
        0.2
    );
    group.add(arrowHelper);
    group.userData.arrow = arrowHelper;

    // Labels
    createLabel('|0⟩', 0, 0, 2.8, 0x6666ff);
    createLabel('|1⟩', 0, 0, -2.8, 0xff6666);

    blochSphere = group;
    scene.add(group);
}

function createLabel(text, x, y, z, color) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 128;
    canvas.height = 64;

    context.fillStyle = `#${color.toString(16).padStart(6, '0')}`;
    context.font = 'Bold 40px Arial';
    context.textAlign = 'center';
    context.fillText(text, 64, 45);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(x, y, z);
    sprite.scale.set(1, 0.5, 1);

    blochSphere.add(sprite);
}

function createParticleField() {
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1000;

    const positions = new Float32Array(particlesCount * 3);
    const colors = new Float32Array(particlesCount * 3);

    for (let i = 0; i < particlesCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 20;
        positions[i + 1] = (Math.random() - 0.5) * 20;
        positions[i + 2] = (Math.random() - 0.5) * 20;

        colors[i] = Math.random() * 0.5 + 0.5;
        colors[i + 1] = Math.random() * 0.5 + 0.5;
        colors[i + 2] = 1;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.05,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });

    const particles = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particles);
    scene.userData.particles = particles;
}

function animate() {
    requestAnimationFrame(animate);

    // Rotate Bloch sphere
    if (blochSphere) {
        blochSphere.rotation.y += 0.005;
    }

    // Rotate particles
    if (scene.userData.particles) {
        scene.userData.particles.rotation.y += 0.001;
    }

    renderer.render(scene, camera);
}

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// Update Bloch sphere based on quantum state
function updateBlochSphere(theta, phi) {
    if (!blochSphere || !blochSphere.userData.arrow) return;

    const x = Math.sin(theta) * Math.cos(phi);
    const y = Math.sin(theta) * Math.sin(phi);
    const z = Math.cos(theta);

    const direction = new THREE.Vector3(x, y, z);
    blochSphere.userData.arrow.setDirection(direction);
}

// Circuit Management
function addGateToCircuit(gate, qubit) {
    circuit.push({ gate, qubit, id: Date.now() });
    updateCircuitDisplay();
}

function updateCircuitDisplay() {
    const display = document.getElementById('circuit-display');
    if (circuit.length === 0) {
        display.innerHTML = '<p style="color: #666;">电路为空。拖拽门到这里...</p>';
        return;
    }

    let html = '<div style="font-family: monospace; font-size: 12px;">';
    for (let i = 0; i < currentQubits; i++) {
        html += `<div style="margin: 5px 0;">q[${i}]: `;

        const gatesOnQubit = circuit.filter(g => g.qubit === i);
        gatesOnQubit.forEach(g => {
            html += `<span style="background: linear-gradient(135deg, #667eea, #764ba2); 
                     padding: 3px 8px; border-radius: 4px; margin: 0 2px;">${g.gate}</span>`;
        });

        html += '</div>';
    }
    html += '</div>';
    display.innerHTML = html;
}

function clearCircuit() {
    circuit = [];
    updateCircuitDisplay();
    updateProbabilityChart([]);
    document.getElementById('status-text').textContent = '电路已清空';
}

async function runCircuit() {
    if (circuit.length === 0) {
        document.getElementById('status-text').textContent = '电路为空';
        return;
    }

    document.getElementById('status-text').textContent = '正在执行电路...';

    try {
        // Call Python backend
        const response = await fetch('http://localhost:5000/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                num_qubits: currentQubits,
                gates: circuit
            })
        });

        const result = await response.json();

        // Update visualizations
        updateProbabilityChart(result.probabilities);

        // Update Bloch sphere for single qubit
        if (currentQubits === 1 && result.bloch) {
            updateBlochSphere(result.bloch.theta, result.bloch.phi);
        }

        document.getElementById('status-text').textContent = '执行完成 ✓';
    } catch (error) {
        console.error('执行错误:', error);
        document.getElementById('status-text').textContent = '执行失败 - 请确保后端服务器运行中';
    }
}

// Probability Chart
function initProbabilityChart() {
    const ctx = document.getElementById('prob-chart').getContext('2d');
    probChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '概率',
                data: [],
                backgroundColor: 'rgba(74, 144, 226, 0.8)',
                borderColor: 'rgba(74, 144, 226, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#B0B0B0' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#B0B0B0' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function updateProbabilityChart(probabilities) {
    if (!probChart) return;

    const labels = probabilities.map((_, i) => {
        return `|${i.toString(2).padStart(currentQubits, '0')}⟩`;
    });

    probChart.data.labels = labels;
    probChart.data.datasets[0].data = probabilities;
    probChart.update();
}

// Drag and Drop
document.addEventListener('DOMContentLoaded', () => {
    init3D();
    initProbabilityChart();

    const gates = document.querySelectorAll('.gate-btn');
    const circuitOverlay = document.getElementById('circuit-overlay');

    gates.forEach(gate => {
        gate.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('gate', gate.dataset.gate);
        });
    });

    circuitOverlay.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    circuitOverlay.addEventListener('drop', (e) => {
        e.preventDefault();
        const gateName = e.dataTransfer.getData('gate');

        // Simple: add to qubit 0, can be enhanced
        const qubit = Math.floor(Math.random() * currentQubits);
        addGateToCircuit(gateName, qubit);

        document.getElementById('status-text').textContent = `已添加 ${gateName} 门`;
    });

    // Qubit count change
    document.getElementById('qubit-count').addEventListener('change', (e) => {
        currentQubits = parseInt(e.target.value);
        clearCircuit();
    });
});
