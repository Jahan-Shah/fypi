import os
import time
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, WeightedRandomSampler
import timm
from tqdm import tqdm
from collections import Counter

# ============ CONFIGURATION ============
data_dir = '/content/DF/Data/DATASET'
model_save_path = '/content/Model/efficientnetb0_rafdb_best.pth'
batch_size = 32
num_classes = 7
epochs = 20
learning_rate = 1e-4
weight_decay = 1e-5
patience = 3  # early stopping patience
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ============ CREATE SAVE DIRECTORY ============
os.makedirs('/content/Model', exist_ok=True)

# ============ IMAGE TRANSFORMS ============
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.RandomRotation(15),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# ============ LOAD DATA ============
train_data = datasets.ImageFolder(f'{data_dir}/train', transform=train_transform)
val_data = datasets.ImageFolder(f'{data_dir}/test', transform=val_transform)

# ============ OPTIONAL: BALANCE SAMPLER ============
labels = [label for _, label in train_data.samples]
class_counts = Counter(labels)
weights = [1.0 / class_counts[label] for label in labels]
sampler = WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)

train_loader = DataLoader(train_data, batch_size=batch_size, sampler=sampler)
val_loader = DataLoader(val_data, batch_size=batch_size)

# ============ MODEL ============
model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=num_classes, drop_rate=0.3)
model.to(device)

# ============ LOSS AND OPTIMIZER ============
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)

# ============ TRAINING LOOP ============
best_val_acc = 0.0
early_stop_counter = 0

for epoch in range(1, epochs + 1):
    model.train()
    start_time = time.time()
    total_loss = 0.0
    correct = 0
    total = 0

    loop = tqdm(enumerate(train_loader), total=len(train_loader),
                desc=f"Epoch {epoch}/{epochs}", ncols=100)

    for batch_idx, (images, labels) in loop:
        images, labels = images.to(device), labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

        acc = correct / total
        avg_loss = total_loss / (batch_idx + 1)
        loop.set_postfix(acc=f"{acc:.3f}", loss=f"{avg_loss:.4f}")

    train_acc = correct / total
    print(f"📈 Epoch [{epoch}] - Train Accuracy: {train_acc:.4f}")

    # ============ VALIDATION ============
    model.eval()
    val_loss = 0.0
    correct_val = 0
    total_val = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            val_loss += loss.item()
            _, predicted = outputs.max(1)
            correct_val += predicted.eq(labels).sum().item()
            total_val += labels.size(0)

    val_loss /= len(val_loader)
    val_acc = correct_val / total_val

    print(f"📘 Validation - Accuracy: {val_acc:.4f}, Loss: {val_loss:.4f}, Time: {time.time() - start_time:.1f}s")

    # ============ EARLY STOPPING + SAVE ============
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        early_stop_counter = 0
        torch.save(model.state_dict(), model_save_path)
        print(f"✔  Best model saved with val accuracy: {best_val_acc:.4f}")
    else:
        early_stop_counter += 1
        if early_stop_counter >= patience:
            print(f"⛔ Early stopping at epoch {epoch} — no improvement for {patience} epochs.")
            break
