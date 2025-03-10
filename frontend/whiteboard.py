import streamlit as st
import streamlit.components.v1 as components

def render_whiteboard():
    """Render the interactive whiteboard component"""
    st.markdown("""
    <style>
        .whiteboard-container {
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .whiteboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .whiteboard-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
        }
        .whiteboard-tools {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        .tool-button {
            padding: 0.5rem 1rem;
            border: 1px solid #D1D5DB;
            border-radius: 0.5rem;
            background: white;
            color: #374151;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tool-button:hover {
            background: #F3F4F6;
            border-color: #9CA3AF;
        }
        .tool-button.active {
            background: #1E88E5;
            color: white;
            border-color: #1E88E5;
        }
        .whiteboard-canvas {
            border: 1px solid #D1D5DB;
            border-radius: 0.5rem;
            background: white;
            width: 100%;
            height: 400px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="whiteboard-container">
        <div class="whiteboard-header">
            <h3 class="whiteboard-title">Interactive Whiteboard</h3>
            <div class="whiteboard-tools">
                <button class="tool-button" id="clear-btn">Clear</button>
                <button class="tool-button" id="save-btn">Save</button>
                <select class="tool-button" id="pen-color">
                    <option value="black">Black</option>
                    <option value="blue">Blue</option>
                    <option value="red">Red</option>
                    <option value="green">Green</option>
                </select>
                <select class="tool-button" id="pen-size">
                    <option value="2">Thin</option>
                    <option value="5">Medium</option>
                    <option value="10">Thick</option>
                </select>
            </div>
        </div>
        <canvas id="whiteboard" class="whiteboard-canvas"></canvas>
    </div>
    """, unsafe_allow_html=True)

    # Add JavaScript for whiteboard functionality
    components.html("""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const canvas = document.getElementById('whiteboard');
            const ctx = canvas.getContext('2d');
            const clearBtn = document.getElementById('clear-btn');
            const saveBtn = document.getElementById('save-btn');
            const penColor = document.getElementById('pen-color');
            const penSize = document.getElementById('pen-size');

            // Set canvas size
            function resizeCanvas() {
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
            }
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);

            let isDrawing = false;
            let lastX = 0;
            let lastY = 0;

            function startDrawing(e) {
                isDrawing = true;
                [lastX, lastY] = [e.offsetX, e.offsetY];
            }

            function stopDrawing() {
                isDrawing = false;
                ctx.beginPath();
            }

            function draw(e) {
                if (!isDrawing) return;

                ctx.beginPath();
                ctx.moveTo(lastX, lastY);
                ctx.lineTo(e.offsetX, e.offsetY);
                ctx.strokeStyle = penColor.value;
                ctx.lineWidth = parseInt(penSize.value);
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.stroke();

                [lastX, lastY] = [e.offsetX, e.offsetY];
            }

            // Event listeners
            canvas.addEventListener('mousedown', startDrawing);
            canvas.addEventListener('mousemove', draw);
            canvas.addEventListener('mouseup', stopDrawing);
            canvas.addEventListener('mouseout', stopDrawing);

            // Touch events for mobile
            canvas.addEventListener('touchstart', function(e) {
                e.preventDefault();
                const touch = e.touches[0];
                const rect = canvas.getBoundingClientRect();
                const x = touch.clientX - rect.left;
                const y = touch.clientY - rect.top;
                startDrawing({ offsetX: x, offsetY: y });
            });

            canvas.addEventListener('touchmove', function(e) {
                e.preventDefault();
                const touch = e.touches[0];
                const rect = canvas.getBoundingClientRect();
                const x = touch.clientX - rect.left;
                const y = touch.clientY - rect.top;
                draw({ offsetX: x, offsetY: y });
            });

            canvas.addEventListener('touchend', stopDrawing);

            // Clear button
            clearBtn.addEventListener('click', function() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            });

            // Save button
            saveBtn.addEventListener('click', function() {
                const dataURL = canvas.toDataURL('image/png');
                const a = document.createElement('a');
                a.href = dataURL;
                a.download = 'whiteboard.png';
                a.click();
            });
        });
    </script>
    """, height=0) 