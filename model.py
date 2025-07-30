import os
import re
import torch
import numpy as np
import pandas as pd
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
import timm
from time import time
from collections import defaultdict

# CONFIG
base_dir = "/content/Faces"
output_feature_dir = "/content/features"
label_csv_path = "/content/labels.csv"
model_path = "/content/efficientnetb2_rafdb_best.pth"
batch_size = 64
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(output_feature_dir, exist_ok=True)

# TRANSFORM
transform = transforms.Compose([
    transforms.Resize((260, 260)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def extract_video_id(filename):
    match = re.match(r'(NV_\d+|V_\d+)_mp4_f\d+_p\d+\.jpg', filename)
    return match.group(1) if match else None

# DATASET
class FaceDataset(Dataset):
    def _init_(self, base_dir, transform):
        self.items = []
        self.transform = transform
        for class_name in ['violent', 'non_violent']:
            label = 1 if class_name == 'violent' else 0
            folder = os.path.join(base_dir, class_name)
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    vid = extract_video_id(file)
                    if vid:
                        self.items.append((os.path.join(folder, file), vid, label))

    def _len_(self):
        return len(self.items)

    def _getitem_(self, idx):
        path, vid, label = self.items[idx]
        img = Image.open(path).convert("RGB")
        return self.transform(img), vid, label

# DATALOADER
dataset = FaceDataset(base_dir, transform)
loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=2)

# MODEL
model = timm.create_model('efficientnet_b2', pretrained=False, num_classes=7)
model.load_state_dict(torch.load(model_path))
model.reset_classifier(0, '')  # remove classification head
model.eval().to(device)

# EXTRACT & SAVE
labels_seen = {}
video_counts = defaultdict(int)
total_images = 0
start_time = time()

print("🚀 Extracting features...")
with torch.no_grad():
    for batch_idx, (images, video_ids, labels) in enumerate(loader):
        images = images.to(device)
        feats = model(images).cpu().numpy()

        for vid, feat, label in zip(video_ids, feats, labels):
            feat = np.expand_dims(feat, axis=0)
            path = os.path.join(output_feature_dir, f"{vid}.npy")

            if os.path.exists(path):
                existing = np.load(path)
                combined = np.vstack([existing, feat])
                np.save(path, combined)
            else:
                np.save(path, feat)

            labels_seen[vid] = int(label)
            video_counts[vid] += 1
            total_images += 1

        if (batch_idx + 1) % 10 == 0:
            print(f"🧪 Processed batch {batch_idx + 1}/{len(loader)}... Total images: {total_images}")

# SAVE LABELS CSV
df = pd.DataFrame([(vid, labels_seen[vid]) for vid in sorted(labels_seen)], columns=["video_id", "label"])
df.to_csv(label_csv_path, index=False)

# STATS
total_time = time() - start_time
print("\n✅ Feature extraction completed!")
print(f"📝 Labels saved to: {label_csv_path}")
print(f"📦 Feature .npy files saved to: {output_feature_dir}")
print(f"🧠 Total videos: {len(labels_seen)}")
print(f"🖼 Total face crops: {total_images}")
print(f"⏱ Total time: {total_time:.2f} seconds")
