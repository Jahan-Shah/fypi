import os
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision import models
from insightface.app import FaceAnalysis
from PIL import Image
from flask import Flask, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import threading  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, origins=["http://localhost:5173"])
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173", async_mode='threading')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}

# ========== CONFIG ==========
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# Processing entire video without frame limit

# Path to your models
effnet_ckpt = "best_model.pth"   # Update to your actual model path
lstm_ckpt = "retrained_lstm_model.pt"  # Update to your actual LSTM model path

# ========== FACE DETECTOR ==========
face_detector = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
face_detector.prepare(ctx_id=0)

# ========== TRANSFORM ==========
transform = transforms.Compose([
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ========== LOAD FULL EFFICIENTNET ==========
effnet = models.efficientnet_b0()
effnet.classifier[1] = torch.nn.Linear(1280, 7)  # Match RAF-DB 7-class classifier
effnet.load_state_dict(torch.load(effnet_ckpt, map_location=device))
effnet = effnet.to(device).eval()

# Hook to extract pre-classifier features
features_list = []
def extract_hook(module, input, output):
    features_list.append(output)

effnet.avgpool.register_forward_hook(extract_hook)

# ========== LSTM CLASS ==========
class ViolenceClassifier(nn.Module):
    def __init__(self, input_size=1280, hidden_size=256, num_layers=1, num_classes=2):
        super(ViolenceClassifier, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)  # (batch, seq, hidden)
        return self.fc(out[:, -1, :])  # Last time step

# ========== LOAD LSTM ==========
lstm_model = ViolenceClassifier()
lstm_model.load_state_dict(torch.load(lstm_ckpt, map_location=device))
lstm_model = lstm_model.to(device).eval()

# ========== FEATURE EXTRACTION ==========
def extract_video_features(video_path):
    cap = cv2.VideoCapture(video_path)
    features = []
    frame_count = 0
    faces_detected = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        faces = face_detector.get(frame)
        faces_detected.append(1 if faces else 0)
        if faces:
            bbox = faces[0].bbox.astype(int)
            x1, y1, x2, y2 = bbox
            face_crop = frame[y1:y2, x1:x2]
            if face_crop.size == 0:
                continue
            face_pil = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
            face_tensor = transform(face_pil).unsqueeze(0).to(device)

            with torch.no_grad():
                features_list.clear()  # reset
                _ = effnet(face_tensor)
                feat = features_list[0].squeeze()  # shape: [1280]
            features.append(feat.cpu())
            frame_count += 1

    cap.release()

    if not features:
        return None

    return torch.stack(features).unsqueeze(0).to(device), faces_detected  # shape: [1, seq, 1280]

# ========== FLASK ROUTE ==========
@app.route('/predict', methods=['POST'])
def predict():
    # Get the video file from the request
    file = request.files.get('video')
    session_id = request.form.get('session_id')
    
    if not file or not allowed_file(file.filename) or not session_id:
        return jsonify({'error': 'Invalid request'}), 400

    video_path = f"./temp_video.mp4"
    file.save(video_path)  # Save the video file to a temporary location

    # Use threading instead of socketio background task for better real-time performance
    thread = threading.Thread(target=process_video, args=(video_path, session_id))
    thread.daemon = True
    thread.start()

    return jsonify({'message': 'Processing started'}), 200


def process_video(video_path, session_id):
    print(f"Processing video: {video_path} for session: {session_id}")
    cap = cv2.VideoCapture(video_path)
    
    # Optimize video capture for speed
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
    
    features = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Skip frame processing for speed optimization
    process_every_nth_frame = 2  # Process every 2nd frame for speed
    frame_skip_counter = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        frame_skip_counter += 1
        
        # Resize frame for faster processing while maintaining aspect ratio
        height, width = frame.shape[:2]
        if width > 640:  # Resize large frames for speed
            scale = 640 / width
            new_width = 640
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))

        faces = face_detector.get(frame)
        face_data = []
        
        # Process face detection and feature extraction for ALL faces
        # Only extract features every nth frame for speed
        extract_features = frame_skip_counter % process_every_nth_frame == 0
        
        if faces:
            # Draw bounding boxes for all detected faces
            for i, face in enumerate(faces):
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                
                # Draw bounding box on the frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(frame, f'Face {i+1}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Store face data for the first face (for backward compatibility with frontend)
                if i == 0:
                    face_data = [int(x1), int(y1), int(x2), int(y2)]
            
            # Extract features from the first/primary face for ML processing (less frequently)
            if extract_features:
                primary_face = faces[0]
                bbox = primary_face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                face_crop = frame[y1:y2, x1:x2]
                if face_crop.size > 0:
                    face_pil = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
                    face_tensor = transform(face_pil).unsqueeze(0).to(device)

                    with torch.no_grad():
                        features_list.clear()
                        _ = effnet(face_tensor)
                        feat = features_list[0].squeeze()
                    features.append(feat.cpu())

        # Encode frame for transmission with lower quality for speed
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])  # Reduced quality for speed
        img_bytes = jpeg.tobytes()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        print(f"Sending frame {frame_count}/{total_frames} to session {session_id}")
        
        # Emit frame data immediately
        with app.app_context():
            socketio.emit('frame', {
                'frame_idx': frame_count,
                'total_frames': total_frames,
                'face': face_data,
                'frame_img': img_b64
            }, to=session_id)
        
        # Minimal delay for 30fps target - adjust based on processing speed
        time.sleep(0.01)  # Very small delay to prevent overwhelming

    cap.release()

    if not features:
        with app.app_context():
            socketio.emit('result', {'error': 'No face detected'}, to=session_id)
        return

    # LSTM prediction - handle variable sequence lengths
    if len(features) == 0:
        with app.app_context():
            socketio.emit('result', {'error': 'No face detected'}, to=session_id)
        return
    
    video_features = torch.stack(features).unsqueeze(0).to(device)  # shape: [1, seq_len, 1280]
    with torch.no_grad():
        output = lstm_model(video_features)
        pred = torch.argmax(output, dim=1).item()
        label = "VIOLENT" if pred == 1 else "NON-VIOLENT"

    # Send final result
    print(label)
    with app.app_context():
        socketio.emit('result', {'prediction': label}, to=session_id)


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'session_id': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
