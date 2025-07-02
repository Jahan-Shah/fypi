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

app = Flask(__name__)

# ========== CONFIG ==========
device = 'cuda' if torch.cuda.is_available() else 'cpu'
max_frames = 30

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

    while cap.isOpened() and frame_count < max_frames:
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
    if len(features) < max_frames:
        pad_len = max_frames - len(features)
        features += [torch.zeros_like(features[0])] * pad_len
        faces_detected += [0] * pad_len
    else:
        features = features[:max_frames]
        faces_detected = faces_detected[:max_frames]

    return torch.stack(features).unsqueeze(0).to(device), faces_detected  # shape: [1, seq, 1280]

# ========== FLASK ROUTE ==========
@app.route('/predict', methods=['POST'])
def predict():
    # Get the video file from the request
    file = request.files.get('video')
    
    if not file:
        return jsonify({'error': 'No video file provided'}), 400

    video_path = f"./temp_video.mp4"
    file.save(video_path)  # Save the video file to a temporary location

    # Extract features from the video
    video_features, faces_detected = extract_video_features(video_path)

    if video_features is not None:
        with torch.no_grad():
            output = lstm_model(video_features)
            probs = F.softmax(output, dim=1) 
            pred = torch.argmax(probs, dim=1).item()
            violent_prob = probs[0][1].item() * 100
            non_violent_prob = probs[0][0].item() * 100

        label = "VIOLENT" if pred == 1 else "NON-VIOLENT"

        fig, ax = plt.subplots()
        ax.bar(range(len(faces_detected)), faces_detected)
        ax.set_xlabel("Frame")
        ax.set_ylabel("Face Detected (1=Yes, 0=No)")
        ax.set_title("Face Detection Per Frame")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return jsonify({
            'prediction': label,
            'violent_probability': f"{violent_prob:.2f}%",
            'non_violent_probability': f"{non_violent_prob:.2f}%",
            'faces_detected_per_frame': faces_detected,
            'visualization': image_base64
        })
    else:
        return jsonify({'error': 'No face detected or feature extraction failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)
