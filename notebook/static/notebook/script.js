
// Canvas setup
const drawingCanvas = document.getElementById('drawing-canvas');
const backgroundCanvas = document.getElementById('background-canvas');
const drawingCtx = drawingCanvas.getContext('2d');
const bgCtx = backgroundCanvas.getContext('2d');

// Set canvas dimensions (A4 size at 72 DPI)
const canvasWidth = 595;
const canvasHeight = 842;
drawingCanvas.width = canvasWidth;
drawingCanvas.height = canvasHeight;
backgroundCanvas.width = canvasWidth;
backgroundCanvas.height = canvasHeight;

// Tool elements
const penTool = document.getElementById('pen-tool');
const eraserTool = document.getElementById('eraser-tool');
const clearBtn = document.getElementById('clear-btn');
const downloadBtn = document.getElementById('download-btn');
const undoBtn = document.getElementById('undo-btn');
const penColor = document.getElementById('pen-color');
const penSize = document.getElementById('pen-size');
const sizeDisplay = document.getElementById('size-display');
const toolStatus = document.getElementById('tool-status');

// Drawing state
let isDrawing = false;
let currentTool = 'pen';
let lastX = 0;
let lastY = 0;
let drawingHistory = [];
let currentStep = -1;

// Initial setup
setupNotebookBackground();
saveDrawingState(); // Save the initial blank state

// Draw notebook lines background
function setupNotebookBackground() {
    bgCtx.fillStyle = 'white';
    bgCtx.fillRect(0, 0, canvasWidth, canvasHeight);
    
    // Draw horizontal lines
    bgCtx.strokeStyle = '#a0c0e8';
    bgCtx.lineWidth = 1;
    
    const lineSpacing = 25; // Spacing between lines
    
    // Draw horizontal lines
    for (let y = lineSpacing; y < canvasHeight; y += lineSpacing) {
        bgCtx.beginPath();
        bgCtx.moveTo(0, y);
        bgCtx.lineTo(canvasWidth, y);
        bgCtx.stroke();
    }
    
    // Draw vertical line (like a margin)
    bgCtx.strokeStyle = '#ff9999';
    bgCtx.beginPath();
    bgCtx.moveTo(50, 0);
    bgCtx.lineTo(50, canvasHeight);
    bgCtx.stroke();
}

// Event listeners for drawing
drawingCanvas.addEventListener('mousedown', startDrawing);
drawingCanvas.addEventListener('mousemove', draw);
drawingCanvas.addEventListener('mouseup', stopDrawing);
drawingCanvas.addEventListener('mouseout', stopDrawing);

// Tool selection
penTool.addEventListener('click', () => {
    setActiveTool('pen');
});

eraserTool.addEventListener('click', () => {
    setActiveTool('eraser');
});

clearBtn.addEventListener('click', clearCanvas);
downloadBtn.addEventListener('click', downloadCanvas);
undoBtn.addEventListener('click', undoLastAction);

// Tool options
penSize.addEventListener('input', () => {
    sizeDisplay.textContent = `${penSize.value}px`;
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'z') {
        e.preventDefault();
        undoLastAction();
    }
});

// Drawing functions
function startDrawing(e) {
    isDrawing = true;
    [lastX, lastY] = getMousePos(drawingCanvas, e);
    
    // Start a new path
    drawingCtx.beginPath();
    drawingCtx.moveTo(lastX, lastY);
    drawingCtx.lineTo(lastX, lastY);
    drawingCtx.stroke();
}

function draw(e) {
    if (!isDrawing) return;
    
    const [currentX, currentY] = getMousePos(drawingCanvas, e);
    
    drawingCtx.beginPath();
    drawingCtx.moveTo(lastX, lastY);
    drawingCtx.lineTo(currentX, currentY);
    
    if (currentTool === 'pen') {
        drawingCtx.strokeStyle = penColor.value;
        drawingCtx.lineWidth = parseInt(penSize.value);
        drawingCtx.lineCap = 'round';
        drawingCtx.lineJoin = 'round';
    } else if (currentTool === 'eraser') {
        drawingCtx.strokeStyle = 'white';
        drawingCtx.lineWidth = parseInt(penSize.value) * 2;
        drawingCtx.lineCap = 'round';
        drawingCtx.lineJoin = 'round';
    }
    
    drawingCtx.stroke();
    
    lastX = currentX;
    lastY = currentY;
}

function stopDrawing() {
    if (isDrawing) {
        isDrawing = false;
        saveDrawingState();
    }
}

function getMousePos(canvas, evt) {
    const rect = canvas.getBoundingClientRect();
    return [
        evt.clientX - rect.left,
        evt.clientY - rect.top
    ];
}

function setActiveTool(tool) {
    currentTool = tool;
    
    // Update UI
    penTool.classList.toggle('active', tool === 'pen');
    eraserTool.classList.toggle('active', tool === 'eraser');
    
    toolStatus.textContent = `Current tool: ${tool.charAt(0).toUpperCase() + tool.slice(1)}`;
}

function clearCanvas() {
    drawingCtx.clearRect(0, 0, canvasWidth, canvasHeight);
    saveDrawingState();
}

function downloadCanvas() {
    // Create a temporary canvas to combine both layers
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvasWidth;
    tempCanvas.height = canvasHeight;
    const tempCtx = tempCanvas.getContext('2d');
    
    // Draw background layer
    tempCtx.drawImage(backgroundCanvas, 0, 0);
    
    // Draw the drawing layer
    tempCtx.drawImage(drawingCanvas, 0, 0);
    
    // Create download link
    const link = document.createElement('a');
    link.download = 'notebook-drawing.png';
    link.href = tempCanvas.toDataURL('image/png');
    link.click();
}

function saveDrawingState() {
    // If we're not at the end of the history, remove everything after current step
    if (currentStep < drawingHistory.length - 1) {
        drawingHistory = drawingHistory.slice(0, currentStep + 1);
    }
    
    // Save current state
    drawingHistory.push(drawingCtx.getImageData(0, 0, canvasWidth, canvasHeight));
    currentStep = drawingHistory.length - 1;
}

function undoLastAction() {
    if (currentStep > 0) {
        currentStep--;
        drawingCtx.putImageData(drawingHistory[currentStep], 0, 0);
    } else if (currentStep === 0) {
        // Clear to initial state
        drawingCtx.clearRect(0, 0, canvasWidth, canvasHeight);
    }
}
