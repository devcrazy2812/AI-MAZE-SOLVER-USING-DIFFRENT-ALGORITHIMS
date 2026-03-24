/**
 * Maze Solver AI — Web Frontend
 * ================================
 * Complete JavaScript implementation of maze generation,
 * BFS, DFS, A* pathfinding with canvas-based visualization.
 */

// ═══════════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════════
const state = {
    grid: null,
    rows: 0, cols: 0,
    start: null, end: null,
    algo: 'bfs',
    speed: 30,
    solving: false,
    animId: null,
    visited: new Set(),
    frontier: new Set(),
    current: null,
    path: new Set(),
    visitedOrder: new Map(),
    stepQueue: [],
    stepIndex: 0,
};

// ═══════════════════════════════════════════════════════════════
//  COLORS
// ═══════════════════════════════════════════════════════════════
const COLORS = {
    wall: '#15121e',
    open: '#2d3750',
    visited_early: '#193278',
    visited_late: '#508cdc',
    frontier: '#d4a017',
    current: '#f43f5e',
    solution: '#10b981',
    start: '#22c55e',
    end: '#ef4444',
    grid_line: '#141828',
};

// ═══════════════════════════════════════════════════════════════
//  DOM REFS
// ═══════════════════════════════════════════════════════════════
const canvas = document.getElementById('maze-canvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('canvas-overlay');
const wrapper = document.getElementById('canvas-wrapper');

const sizeSlider = document.getElementById('size-slider');
const sizeValue = document.getElementById('size-value');
const speedSlider = document.getElementById('speed-slider');
const speedValue = document.getElementById('speed-value');

const btnGenerate = document.getElementById('btn-generate');
const btnSolve = document.getElementById('btn-solve');
const btnReset = document.getElementById('btn-reset');
const btnScreenshot = document.getElementById('btn-screenshot');

const statPath = document.getElementById('stat-path');
const statNodes = document.getElementById('stat-nodes');
const statTime = document.getElementById('stat-time');
const statMemory = document.getElementById('stat-memory');

const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const statusCoords = document.getElementById('status-coords');
const badgeSize = document.getElementById('badge-size');
const badgeAlgo = document.getElementById('badge-algo');
const toastContainer = document.getElementById('toast-container');

const algoButtons = document.querySelectorAll('.algo-btn');

// ═══════════════════════════════════════════════════════════════
//  MAZE GENERATOR (Recursive Backtracking)
// ═══════════════════════════════════════════════════════════════
function generateMaze(rows, cols) {
    // Ensure odd dimensions
    rows = rows % 2 === 0 ? rows + 1 : rows;
    cols = cols % 2 === 0 ? cols + 1 : cols;

    // Fill with walls (0)
    const grid = Array.from({ length: rows }, () => new Uint8Array(cols));

    // Stack-based iterative backtracking
    const startR = 1, startC = 1;
    grid[startR][startC] = 1;
    const stack = [[startR, startC]];
    const dirs = [[0, 2], [2, 0], [0, -2], [-2, 0]];

    while (stack.length > 0) {
        const [cr, cc] = stack[stack.length - 1];
        // Shuffle directions
        const shuffled = dirs.slice().sort(() => Math.random() - 0.5);
        let found = false;

        for (const [dr, dc] of shuffled) {
            const nr = cr + dr, nc = cc + dc;
            if (nr > 0 && nr < rows - 1 && nc > 0 && nc < cols - 1 && grid[nr][nc] === 0) {
                grid[cr + dr / 2][cc + dc / 2] = 1; // wall between
                grid[nr][nc] = 1;
                stack.push([nr, nc]);
                found = true;
                break;
            }
        }
        if (!found) stack.pop();
    }

    // Create openings: top-left start, bottom-right end
    grid[0][1] = 1;
    grid[rows - 1][cols - 2] = 1;

    return { grid, rows, cols, start: [0, 1], end: [rows - 1, cols - 2] };
}

// ═══════════════════════════════════════════════════════════════
//  PATHFINDING ALGORITHMS
// ═══════════════════════════════════════════════════════════════

function getNeighbors(grid, r, c, rows, cols) {
    const n = [];
    for (const [dr, dc] of [[0, 1], [0, -1], [1, 0], [-1, 0]]) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] === 1) {
            n.push([nr, nc]);
        }
    }
    return n;
}

function key(r, c) { return `${r},${c}`; }

/** BFS — returns array of steps */
function solveBFS(grid, start, end, rows, cols) {
    const steps = [];
    const visited = new Set();
    const parent = new Map();
    const queue = [start];
    visited.add(key(...start));

    while (queue.length > 0) {
        const [cr, cc] = queue.shift();
        const frontier = new Set(queue.map(([r, c]) => key(r, c)));
        steps.push({ current: [cr, cc], visited: new Set(visited), frontier });

        if (cr === end[0] && cc === end[1]) break;

        for (const [nr, nc] of getNeighbors(grid, cr, cc, rows, cols)) {
            const k = key(nr, nc);
            if (!visited.has(k)) {
                visited.add(k);
                parent.set(k, [cr, cc]);
                queue.push([nr, nc]);
            }
        }
    }

    // Reconstruct path
    const path = [];
    let cur = end;
    while (cur) {
        path.push(cur);
        cur = parent.get(key(...cur));
    }
    path.reverse();
    return { steps, path: path.length > 1 ? path : [], found: path.length > 1 };
}

/** DFS */
function solveDFS(grid, start, end, rows, cols) {
    const steps = [];
    const visited = new Set();
    const parent = new Map();
    const stack = [start];

    while (stack.length > 0) {
        const [cr, cc] = stack.pop();
        const k = key(cr, cc);
        if (visited.has(k)) continue;
        visited.add(k);

        const frontier = new Set(stack.map(([r, c]) => key(r, c)));
        steps.push({ current: [cr, cc], visited: new Set(visited), frontier });

        if (cr === end[0] && cc === end[1]) break;

        for (const [nr, nc] of getNeighbors(grid, cr, cc, rows, cols)) {
            const nk = key(nr, nc);
            if (!visited.has(nk)) {
                parent.set(nk, [cr, cc]);
                stack.push([nr, nc]);
            }
        }
    }

    const path = [];
    let cur = end;
    while (cur) {
        path.push(cur);
        cur = parent.get(key(...cur));
    }
    path.reverse();
    return { steps, path: path.length > 1 ? path : [], found: path.length > 1 };
}

/** A* */
function solveAStar(grid, start, end, rows, cols, heuristic = 'manhattan') {
    const steps = [];
    const hFn = heuristic === 'manhattan'
        ? (r, c) => Math.abs(r - end[0]) + Math.abs(c - end[1])
        : (r, c) => Math.sqrt((r - end[0]) ** 2 + (c - end[1]) ** 2);

    const gScore = new Map();
    const fScore = new Map();
    const parent = new Map();
    const openSet = []; // min-heap by fScore
    const closedSet = new Set();

    const sk = key(...start);
    gScore.set(sk, 0);
    fScore.set(sk, hFn(...start));
    openSet.push({ pos: start, f: fScore.get(sk) });

    while (openSet.length > 0) {
        // Find min f in open set
        openSet.sort((a, b) => a.f - b.f);
        const { pos: [cr, cc] } = openSet.shift();
        const ck = key(cr, cc);

        if (closedSet.has(ck)) continue;
        closedSet.add(ck);

        const frontier = new Set(openSet.map(o => key(...o.pos)));
        steps.push({ current: [cr, cc], visited: new Set(closedSet), frontier });

        if (cr === end[0] && cc === end[1]) break;

        const cg = gScore.get(ck) || 0;

        for (const [nr, nc] of getNeighbors(grid, cr, cc, rows, cols)) {
            const nk = key(nr, nc);
            if (closedSet.has(nk)) continue;

            const ng = cg + 1;
            if (ng < (gScore.get(nk) ?? Infinity)) {
                gScore.set(nk, ng);
                const nf = ng + hFn(nr, nc);
                fScore.set(nk, nf);
                parent.set(nk, [cr, cc]);
                openSet.push({ pos: [nr, nc], f: nf });
            }
        }
    }

    const path = [];
    let cur = end;
    while (cur) {
        path.push(cur);
        cur = parent.get(key(...cur));
    }
    path.reverse();
    return { steps, path: path.length > 1 ? path : [], found: path.length > 1 };
}

// ═══════════════════════════════════════════════════════════════
//  CANVAS RENDERING
// ═══════════════════════════════════════════════════════════════

function computeCellSize() {
    const pad = 16;
    const w = wrapper.clientWidth - pad * 2;
    const h = wrapper.clientHeight - pad * 2;
    const csW = Math.floor(w / state.cols);
    const csH = Math.floor(h / state.rows);
    return Math.max(3, Math.min(30, Math.min(csW, csH)));
}

function resizeCanvas() {
    if (!state.grid) return;
    const cs = computeCellSize();
    canvas.width = state.cols * cs;
    canvas.height = state.rows * cs;
    state.cellSize = cs;
}

function lerpColor(c1, c2, t) {
    t = Math.max(0, Math.min(1, t));
    const h = s => parseInt(s.slice(1), 16);
    const a = h(c1), b = h(c2);
    const r = ((a >> 16) + (((b >> 16) - (a >> 16)) * t)) & 0xff;
    const g = (((a >> 8) & 0xff) + ((((b >> 8) & 0xff) - ((a >> 8) & 0xff)) * t)) & 0xff;
    const bl = ((a & 0xff) + (((b & 0xff) - (a & 0xff)) * t)) & 0xff;
    return `rgb(${r},${g},${bl})`;
}

function drawMaze() {
    if (!state.grid) return;

    const cs = state.cellSize;
    const totalVisited = Math.max(1, state.visitedOrder.size);

    for (let r = 0; r < state.rows; r++) {
        for (let c = 0; c < state.cols; c++) {
            const x = c * cs, y = r * cs;
            const k = key(r, c);

            let color;
            if (state.grid[r][c] === 0) {
                color = COLORS.wall;
            } else if (state.path.has(k)) {
                color = COLORS.solution;
            } else if (state.current && state.current[0] === r && state.current[1] === c) {
                color = COLORS.current;
            } else if (state.frontier.has(k)) {
                color = COLORS.frontier;
            } else if (state.visited.has(k)) {
                const idx = state.visitedOrder.get(k) || 0;
                const t = idx / totalVisited;
                color = lerpColor(COLORS.visited_early, COLORS.visited_late, t);
            } else {
                color = COLORS.open;
            }

            ctx.fillStyle = color;
            ctx.fillRect(x, y, cs, cs);
        }
    }

    // Grid lines
    if (cs >= 8) {
        ctx.strokeStyle = COLORS.grid_line;
        ctx.lineWidth = 0.5;
        for (let r = 0; r <= state.rows; r++) {
            ctx.beginPath();
            ctx.moveTo(0, r * cs);
            ctx.lineTo(state.cols * cs, r * cs);
            ctx.stroke();
        }
        for (let c = 0; c <= state.cols; c++) {
            ctx.beginPath();
            ctx.moveTo(c * cs, 0);
            ctx.lineTo(c * cs, state.rows * cs);
            ctx.stroke();
        }
    }

    // Start / End markers
    if (state.start) drawMarker(state.start, COLORS.start, 'S');
    if (state.end) drawMarker(state.end, COLORS.end, 'E');
}

function drawMarker(pos, color, label) {
    const cs = state.cellSize;
    const cx = pos[1] * cs + cs / 2;
    const cy = pos[0] * cs + cs / 2;
    const r = Math.max(cs / 3, 3);

    // Glow
    ctx.beginPath();
    ctx.arc(cx, cy, r + 3, 0, Math.PI * 2);
    ctx.fillStyle = color + '44';
    ctx.fill();

    // Circle
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();

    // Label
    if (cs >= 14) {
        ctx.fillStyle = '#fff';
        ctx.font = `bold ${Math.max(cs / 2, 9)}px Inter, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(label, cx, cy + 1);
    }
}

// ═══════════════════════════════════════════════════════════════
//  ANIMATION ENGINE
// ═══════════════════════════════════════════════════════════════

function startAnimation(result) {
    state.solving = true;
    state.stepQueue = result.steps;
    state.stepIndex = 0;
    state.visitedOrder = new Map();
    statusDot.classList.add('solving');
    setStatus('Solving...', 'solving');

    const startTime = performance.now();

    function tick() {
        if (!state.solving) return;

        const idx = state.stepIndex;
        if (idx >= state.stepQueue.length) {
            // Done
            const elapsed = performance.now() - startTime;
            finishSolve(result, elapsed);
            return;
        }

        const step = state.stepQueue[idx];
        state.current = step.current;
        state.visited = step.visited;
        state.frontier = step.frontier;

        // Track order
        for (const k of step.visited) {
            if (!state.visitedOrder.has(k)) {
                state.visitedOrder.set(k, state.visitedOrder.size);
            }
        }

        // Update real-time stats
        statNodes.textContent = step.visited.size;
        const elapsed = performance.now() - startTime;
        statTime.textContent = elapsed.toFixed(1) + ' ms';

        drawMaze();
        state.stepIndex++;
        state.animId = setTimeout(tick, state.speed);
    }

    tick();
}

function finishSolve(result, elapsed) {
    state.solving = false;
    state.current = null;
    state.frontier = new Set();
    statusDot.classList.remove('solving');

    if (result.found) {
        state.path = new Set(result.path.map(([r, c]) => key(r, c)));
        drawMaze();

        statPath.textContent = result.path.length;
        statNodes.textContent = result.steps.length;
        statTime.textContent = elapsed.toFixed(2) + ' ms';
        statMemory.textContent = (result.steps.length * 0.05).toFixed(1) + ' KB';

        setStatus(`Path found! Length: ${result.path.length} | Explored: ${result.steps.length} | Time: ${elapsed.toFixed(1)}ms`);
        showToast('Path found!', 'success');
    } else {
        setStatus('No path exists in this maze!');
        showToast('No path exists!', 'error');
    }
}

function stopAnimation() {
    state.solving = false;
    if (state.animId) clearTimeout(state.animId);
    statusDot.classList.remove('solving');
}

// ═══════════════════════════════════════════════════════════════
//  UI HELPERS
// ═══════════════════════════════════════════════════════════════

function setStatus(text) {
    statusText.textContent = text;
}

function clearStats() {
    statPath.textContent = '--';
    statNodes.textContent = '--';
    statTime.textContent = '--';
    statMemory.textContent = '--';
}

function showToast(msg, type = 'info') {
    const el = document.createElement('div');
    el.className = 'toast';
    if (type === 'success') el.style.borderColor = '#10b981';
    else if (type === 'error') el.style.borderColor = '#f43f5e';
    el.textContent = msg;
    toastContainer.appendChild(el);
    setTimeout(() => el.remove(), 2600);
}

function clearAnimation() {
    state.visited = new Set();
    state.frontier = new Set();
    state.current = null;
    state.path = new Set();
    state.visitedOrder = new Map();
}

// ═══════════════════════════════════════════════════════════════
//  EVENT HANDLERS
// ═══════════════════════════════════════════════════════════════

// Generate
btnGenerate.addEventListener('click', () => {
    if (state.solving) return;
    const size = parseInt(sizeSlider.value);
    const maze = generateMaze(size, size);
    state.grid = maze.grid;
    state.rows = maze.rows;
    state.cols = maze.cols;
    state.start = maze.start;
    state.end = maze.end;
    clearAnimation();
    clearStats();
    resizeCanvas();
    drawMaze();
    overlay.classList.add('hidden');
    badgeSize.textContent = `${maze.rows}x${maze.cols}`;

    const open = maze.grid.flat().reduce((a, b) => a + b, 0);
    setStatus(`Maze generated: ${maze.rows}x${maze.cols} | ${open} open cells`);
    showToast(`${maze.rows}x${maze.cols} maze generated!`, 'success');
});

// Solve
btnSolve.addEventListener('click', () => {
    if (!state.grid) { showToast('Generate a maze first!', 'error'); return; }
    if (state.solving) return;
    clearAnimation();
    clearStats();

    let result;
    if (state.algo === 'bfs') {
        result = solveBFS(state.grid, state.start, state.end, state.rows, state.cols);
    } else if (state.algo === 'dfs') {
        result = solveDFS(state.grid, state.start, state.end, state.rows, state.cols);
    } else if (state.algo === 'astar-m') {
        result = solveAStar(state.grid, state.start, state.end, state.rows, state.cols, 'manhattan');
    } else {
        result = solveAStar(state.grid, state.start, state.end, state.rows, state.cols, 'euclidean');
    }

    const algoNames = { bfs: 'BFS', dfs: 'DFS', 'astar-m': 'A* Manhattan', 'astar-e': 'A* Euclidean' };
    showToast(`Solving with ${algoNames[state.algo]}...`);
    startAnimation(result);
});

// Reset
btnReset.addEventListener('click', () => {
    stopAnimation();
    clearAnimation();
    clearStats();
    if (state.grid) drawMaze();
    setStatus('Reset - Ready to solve');
    showToast('Reset complete');
});

// Screenshot
btnScreenshot.addEventListener('click', () => {
    if (!state.grid) return;
    const link = document.createElement('a');
    link.download = `maze_screenshot_${Date.now()}.png`;
    link.href = canvas.toDataURL();
    link.click();
    showToast('Screenshot saved!', 'success');
});

// Algorithm buttons
algoButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        algoButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.algo = btn.dataset.algo;
        const names = { bfs: 'BFS', dfs: 'DFS', 'astar-m': 'A* Man.', 'astar-e': 'A* Euc.' };
        badgeAlgo.textContent = names[state.algo];
    });
});

// Sliders
sizeSlider.addEventListener('input', () => { sizeValue.textContent = sizeSlider.value; });
speedSlider.addEventListener('input', () => {
    speedValue.textContent = speedSlider.value;
    state.speed = parseInt(speedSlider.value);
});

// Click on canvas to set start/end
canvas.addEventListener('click', (e) => {
    if (!state.grid || state.solving) return;
    const rect = canvas.getBoundingClientRect();
    const c = Math.floor((e.clientX - rect.left) / state.cellSize);
    const r = Math.floor((e.clientY - rect.top) / state.cellSize);
    if (r >= 0 && r < state.rows && c >= 0 && c < state.cols && state.grid[r][c] === 1) {
        state.start = [r, c];
        clearAnimation();
        drawMaze();
        showToast(`Start: (${r},${c})`);
    }
});

canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    if (!state.grid || state.solving) return;
    const rect = canvas.getBoundingClientRect();
    const c = Math.floor((e.clientX - rect.left) / state.cellSize);
    const r = Math.floor((e.clientY - rect.top) / state.cellSize);
    if (r >= 0 && r < state.rows && c >= 0 && c < state.cols && state.grid[r][c] === 1) {
        state.end = [r, c];
        clearAnimation();
        drawMaze();
        showToast(`End: (${r},${c})`);
    }
});

// Mouse coords display
canvas.addEventListener('mousemove', (e) => {
    if (!state.grid) return;
    const rect = canvas.getBoundingClientRect();
    const c = Math.floor((e.clientX - rect.left) / state.cellSize);
    const r = Math.floor((e.clientY - rect.top) / state.cellSize);
    if (r >= 0 && r < state.rows && c >= 0 && c < state.cols) {
        statusCoords.textContent = `(${r}, ${c})`;
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (k === 'r') btnGenerate.click();
    else if (k === ' ') { e.preventDefault(); btnSolve.click(); }
    else if (k === 'c') btnReset.click();
    else if (k === '1') document.getElementById('btn-bfs').click();
    else if (k === '2') document.getElementById('btn-dfs').click();
    else if (k === '3') document.getElementById('btn-astar-m').click();
    else if (k === '4') document.getElementById('btn-astar-e').click();
    else if (k === 'arrowup') {
        speedSlider.value = Math.max(1, parseInt(speedSlider.value) - 5);
        speedSlider.dispatchEvent(new Event('input'));
    }
    else if (k === 'arrowdown') {
        speedSlider.value = Math.min(200, parseInt(speedSlider.value) + 5);
        speedSlider.dispatchEvent(new Event('input'));
    }
    else if (k === 'escape') { stopAnimation(); setStatus('Cancelled'); }
});

// Window resize
window.addEventListener('resize', () => {
    if (state.grid) {
        resizeCanvas();
        drawMaze();
    }
});

// Init
setStatus('Ready - Click Generate or press R');
