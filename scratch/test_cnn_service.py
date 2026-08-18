import os
import io
import math
import urllib.request
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
import cv2

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

# Test image URL
TEST_URLS = [
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
]

# Load ResNet-18
weights = ResNet18_Weights.DEFAULT
model = resnet18(weights=weights)
model.eval()

# Hooks to extract average pooling features
features_blobs = []
def hook_feature(module, input, output):
    features_blobs.append(output.data.squeeze().cpu().numpy())

model.avgpool.register_forward_hook(hook_feature)

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

for idx, url in enumerate(TEST_URLS):
    print(f"\n--- Testing Image #{idx+1}: {url[:60]}... ---")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            img_bytes = resp.read()

        pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        print(f"Loaded image size: {pil_img.size}")

        # OpenCV conversion for brightness & Laplacian blur
        open_cv_img = np.array(pil_img)[:, :, ::-1].copy()
        gray = cv2.cvtColor(open_cv_img, cv2.COLOR_BGR2GRAY)

        # 1. Brightness
        mean_brightness = float(np.mean(gray))
        brightness_score = max(0.0, min(100.0, 100.0 - abs(mean_brightness - 135.0) * 0.65))

        # 2. Sharpness (Laplacian Variance)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharpness_score = max(0.0, min(100.0, (math.log(laplacian_var + 1.0) / 7.0) * 100.0))

        # 3. ResNet-18 Deep Feature Extraction
        features_blobs.clear()
        input_tensor = transform(pil_img).unsqueeze(0)
        with torch.no_grad():
            output = model(input_tensor)

        if features_blobs:
            feat = features_blobs[-1]
            feat_norm = float(np.linalg.norm(feat))
            feat_std = float(np.std(feat))
            # Normalize CNN feature score to 0-100 scale
            cnn_feature_score = max(0.0, min(100.0, (feat_norm / 25.0) * 100.0))
        else:
            cnn_feature_score = 80.0

        # Quality & Condition calculations
        quality_score = round((brightness_score * 0.25) + (sharpness_score * 0.35) + (cnn_feature_score * 0.40), 1)
        interior_condition = round(min(100.0, quality_score * 1.02), 1)
        exterior_condition = round(min(100.0, quality_score * 0.98), 1)
        overall_score = round((quality_score + interior_condition + exterior_condition) / 3.0, 1)

        print(f"Brightness Score: {brightness_score:.1f}")
        print(f"Sharpness Score: {sharpness_score:.1f}")
        print(f"CNN Feature Score: {cnn_feature_score:.1f}")
        print(f"Quality Score: {quality_score}")
        print(f"Overall Score: {overall_score}")

    except Exception as e:
        print(f"Error processing image: {e}")
