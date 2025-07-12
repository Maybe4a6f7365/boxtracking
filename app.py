import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import threading
import time
from collections import deque
import json
from box_tracker import BoxTracker

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 100 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

processing_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video(input_path, output_path, job_id, settings=None):
    """Process video with box tracking effects"""
    try:
        processing_status[job_id] = {'status': 'processing', 'progress': 0}
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            processing_status[job_id] = {'status': 'error', 'message': 'Could not open video'}
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        tracker = BoxTracker(settings=settings)
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            result_frame = tracker.process_frame(frame, frame_idx)
            
            out.write(result_frame)
            
            progress = int((frame_idx / total_frames) * 100)
            processing_status[job_id] = {'status': 'processing', 'progress': progress}
            
            frame_idx += 1
        
        cap.release()
        out.release()
        
        processing_status[job_id] = {'status': 'completed', 'progress': 100}
        
    except Exception as e:
        processing_status[job_id] = {'status': 'error', 'message': str(e)}

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start processing"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    settings = None
    if 'settings' in request.form:
        try:
            settings = json.loads(request.form['settings'])
        except:
            settings = None
    
    job_id = str(uuid.uuid4())
    
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_{filename}")
    output_path = os.path.join(OUTPUT_FOLDER, f"{job_id}_processed.mp4")
    
    file.save(input_path)
    
    thread = threading.Thread(target=process_video, args=(input_path, output_path, job_id, settings))
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'uploaded'})

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get processing status"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_status[job_id])

@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download processed video"""
    if job_id not in processing_status:
        return jsonify({'error': 'Job not found'}), 404
    
    if processing_status[job_id]['status'] != 'completed':
        return jsonify({'error': 'Video not ready'}), 400
    
    output_path = os.path.join(OUTPUT_FOLDER, f"{job_id}_processed.mp4")
    if not os.path.exists(output_path):
        return jsonify({'error': 'Processed video not found'}), 404
    
    return send_file(output_path, as_attachment=True, 
                    download_name=f"tracked_video_{job_id}.mp4")

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with usage instructions"""
    return '''
    <html>
    <head><title>BoxTracker API</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>🎯 BoxTracker API is Running!</h1>
        <p>The backend is working correctly. To use BoxTracker:</p>
        <ol>
            <li><strong>Open the frontend:</strong> Open <code>index.html</code> in your browser</li>
            <li><strong>Upload a video:</strong> Use the drag-and-drop interface</li>
            <li><strong>Configure settings:</strong> Choose colors, effects, and trail options</li>
            <li><strong>Download result:</strong> Get your video with professional motion tracking</li>
        </ol>
        <h2>API Endpoints:</h2>
        <ul>
            <li><code>POST /api/upload</code> - Upload video</li>
            <li><code>GET /api/status/&lt;job_id&gt;</code> - Check processing status</li>
            <li><code>GET /api/download/&lt;job_id&gt;</code> - Download processed video</li>
            <li><code>GET /api/health</code> - Health check</li>
        </ul>
        <p><strong>Frontend URL:</strong> <code>file:///path/to/index.html</code></p>
        <p><strong>Backend URL:</strong> <code>http://localhost:5000</code></p>
    </body>
    </html>
    '''

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'BoxTracker API is running'})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 