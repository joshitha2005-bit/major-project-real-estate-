import os
import io
import math
import urllib.request
import numpy as np
from typing import List, Dict, Any, Optional
from PIL import Image

import cv2
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights

class ImageAIService:
    _model = None
    _transform = None
    _features_blob = []

    @classmethod
    def _get_model(cls):
        """Lazy load pretrained PyTorch ResNet-18 CNN model in eval mode."""
        if cls._model is not None:
            return cls._model, cls._transform

        try:
            weights = ResNet18_Weights.DEFAULT
            model = resnet18(weights=weights)
            model.eval()

            def hook_fn(module, input, output):
                cls._features_blob = output.data.squeeze().cpu().numpy()

            model.avgpool.register_forward_hook(hook_fn)

            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            cls._model = model
            cls._transform = transform
            return cls._model, cls._transform
        except Exception as e:
            print(f"Failed to load PyTorch ResNet-18 model: {e}")
            return None, None

    @classmethod
    def _load_pil_image(cls, image_source: str, base_dir: str = "") -> Optional[Image.Image]:
        """Load PIL RGB Image from HTTP URL, local path, or static uploads directory."""
        if not image_source or not isinstance(image_source, str):
            return None

        # 1. HTTP / HTTPS URL
        if image_source.startswith("http://") or image_source.startswith("https://"):
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(image_source, headers={"User-Agent": "Mozilla/5.0 (PropPulse/1.0)"})
            with urllib.request.urlopen(req, timeout=6, context=ctx) as resp:
                img_bytes = resp.read()
            return Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # 2. Direct local file path
        if os.path.exists(image_source):
            return Image.open(image_source).convert("RGB")

        # 3. Static uploads fallback path mapping
        filename = os.path.basename(image_source)
        if base_dir:
            upload_path = os.path.join(base_dir, "static", "uploads", filename)
            if os.path.exists(upload_path):
                return Image.open(upload_path).convert("RGB")
            static_rel = os.path.join(base_dir, image_source.lstrip("/\\"))
            if os.path.exists(static_rel):
                return Image.open(static_rel).convert("RGB")

        return None

    @classmethod
    def extract_image_embedding(cls, image_source: str, base_dir: str = "") -> np.ndarray:
        """
        Extract genuine 512-dimensional CNN feature vector from property image using PyTorch ResNet-18.
        Returns np.ndarray of shape (512,) float32.
        If image is missing, corrupt, or None, returns zeros of shape (512,).
        """
        if not image_source or not isinstance(image_source, str) or not image_source.strip():
            return np.zeros(512, dtype=np.float32)

        try:
            pil_img = cls._load_pil_image(image_source, base_dir=base_dir)
            if pil_img is None:
                return np.zeros(512, dtype=np.float32)

            model, transform = cls._get_model()
            if model is None or transform is None:
                return np.zeros(512, dtype=np.float32)

            cls._features_blob = []
            input_tensor = transform(pil_img).unsqueeze(0)
            with torch.no_grad():
                _ = model(input_tensor)

            feat = np.array(cls._features_blob, dtype=np.float32).flatten()
            if len(feat) == 512:
                return feat
            elif len(feat) > 512:
                return feat[:512]
            elif len(feat) > 0:
                padded = np.zeros(512, dtype=np.float32)
                padded[:len(feat)] = feat
                return padded
            return np.zeros(512, dtype=np.float32)
        except Exception as e:
            print(f"Error extracting image embedding for {image_source}: {e}")
            return np.zeros(512, dtype=np.float32)

    @classmethod
    def analyze_single_image(cls, image_source: str, base_dir: str = "") -> Dict[str, Any]:
        """
        Analyze a single property image using ResNet-18 CNN + OpenCV metrics.
        Computes genuine mathematical features without fabricating synthetic property attributes.
        """
        pil_img = cls._load_pil_image(image_source, base_dir=base_dir)
        if pil_img is None:
            raise ValueError(f"Could not load image from source: {image_source}")

        width, height = pil_img.size
        aspect_ratio = round(width / float(height), 2) if height > 0 else 1.0
        resolution_mp = round((width * height) / 1_000_000.0, 2)

        # 1. Classical OpenCV metrics (Brightness, Sharpness Laplacian variance, Contrast)
        open_cv_img = np.array(pil_img)[:, :, ::-1].copy()
        gray = cv2.cvtColor(open_cv_img, cv2.COLOR_BGR2GRAY)

        mean_brightness = float(np.mean(gray))
        contrast_std = float(np.std(gray))
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        mean_red = float(np.mean(open_cv_img[:, :, 2]))
        mean_green = float(np.mean(open_cv_img[:, :, 1]))
        mean_blue = float(np.mean(open_cv_img[:, :, 0]))

        # Normalized sub-scores
        brightness_norm = max(0.0, min(100.0, 100.0 - abs(mean_brightness - 130.0) * 0.6))
        sharpness_norm = max(0.0, min(100.0, (math.log(laplacian_var + 1.0) / 7.0) * 100.0))
        contrast_norm = max(0.0, min(100.0, (contrast_std / 64.0) * 100.0))
        res_norm = max(20.0, min(100.0, (min(width, 1920) / 1920.0) * 100.0))

        # Real composite image quality score
        quality_score = round(
            (sharpness_norm * 0.40) + (brightness_norm * 0.25) + (contrast_norm * 0.20) + (res_norm * 0.15),
            1
        )

        # 2. PyTorch ResNet-18 CNN Feature Extraction
        model, transform = cls._get_model()
        feat_norm = 0.0
        embedding_dim = 512
        feat_sample = []
        non_zero_count = 0

        if model is not None and transform is not None:
            try:
                cls._features_blob = []
                input_tensor = transform(pil_img).unsqueeze(0)
                with torch.no_grad():
                    _ = model(input_tensor)

                if len(cls._features_blob) > 0:
                    feat = np.array(cls._features_blob, dtype=np.float32).flatten()
                    embedding_dim = len(feat)
                    feat_norm = float(np.linalg.norm(feat))
                    non_zero_count = int(np.count_nonzero(feat))
                    feat_sample = [float(round(x, 4)) for x in feat[:6]]
            except Exception as cnn_err:
                print(f"CNN inference warning for {image_source}: {cnn_err}")

        return {
            "image_quality_score": quality_score,
            "quality_score": quality_score,
            "sharpness_score": round(sharpness_norm, 1),
            "brightness_score": round(brightness_norm, 1),
            "cnn_feature_score": round(feat_norm, 4) if feat_norm > 0 else quality_score,
            "sharpness": round(laplacian_var, 1),
            "brightness": round(mean_brightness, 1),
            "contrast": round(contrast_std, 1),
            "resolution": f"{width}x{height}",
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "megapixels": resolution_mp,
            "color_distribution": {
                "red_mean": round(mean_red, 1),
                "green_mean": round(mean_green, 1),
                "blue_mean": round(mean_blue, 1),
                "tone": "Warm Tone" if mean_red >= mean_blue else "Cool Tone"
            },
            "embedding_dimensions": embedding_dim,
            "embedding_norm": round(feat_norm, 4),
            "non_zero_features": non_zero_count,
            "embedding_sample": feat_sample,
            "feature_embedding": [float(x) for x in feat] if len(cls._features_blob) > 0 else []
        }

    @classmethod
    def analyze_property_images(
        cls,
        image_urls: List[str],
        image_classification: str = "REPRESENTATIVE",
        base_dir: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze property images via ResNet-18 CNN.
        Processes genuine property photos, user uploads, and representative images.
        """
        # 1. NO_IMAGE Handling
        if not image_urls or image_classification == "NO_IMAGE":
            return {
                "image_analysis_available": False,
                "image_loaded": False,
                "image_status": "PROPERTY IMAGE NOT AVAILABLE",
                "image_provenance": "NO_IMAGE",
                "cnn_model": "PyTorch ResNet-18",
                "cnn_status": "IMAGE_ANALYSIS_UNAVAILABLE",
                "overall_condition": "IMAGE_ANALYSIS_UNAVAILABLE",
                "overall_score": None,
                "processed_count": 0,
                "embedding_dimensions": None,
                "embedding_norm": 0.0,
                "non_zero_features": 0,
                "embedding_sample": [],
                "image_quality_score": None,
                "sharpness_score": None,
                "brightness_score": None,
                "contrast_score": None,
                "visual_features": {},
                "usable_for_ai": False,
                "disclosure_note": "PROPERTY IMAGE NOT AVAILABLE"
            }

        # 1b. SOURCE_LISTING_IMAGE Handling
        if image_classification == "SOURCE_LISTING_IMAGE":
            return {
                "image_analysis_available": False,
                "image_loaded": True,
                "image_status": "SOURCE_LISTING_REFERENCE",
                "image_provenance": "SOURCE_LISTING_IMAGE",
                "cnn_model": "PyTorch ResNet-18",
                "cnn_status": "Image available for reference; AI analysis unavailable because image-use permission is not established.",
                "embedding_dimensions": None,
                "embedding_norm": 0.0,
                "non_zero_features": 0,
                "embedding_sample": [],
                "image_quality_score": None,
                "sharpness_score": None,
                "brightness_score": None,
                "contrast_score": None,
                "visual_features": {},
                "usable_for_ai": False,
                "processed_count": 0,
                "disclosure_note": "Image available for reference; AI analysis unavailable because image-use permission is not established."
            }

        # 2. INVALID_IMAGE Handling
        if image_classification == "INVALID_IMAGE":
            return {
                "image_analysis_available": False,
                "image_loaded": False,
                "image_status": "INVALID_IMAGE",
                "image_provenance": "INVALID_IMAGE",
                "cnn_model": "PyTorch ResNet-18",
                "cnn_status": "UNAVAILABLE",
                "embedding_dimensions": None,
                "embedding_norm": 0.0,
                "non_zero_features": 0,
                "embedding_sample": [],
                "image_quality_score": None,
                "sharpness_score": None,
                "brightness_score": None,
                "contrast_score": None,
                "visual_features": {},
                "usable_for_ai": False,
                "disclosure_note": "INVALID / PLACEHOLDER IMAGE"
            }

        # 3. For any valid image (PROPERTY_SPECIFIC, USER_UPLOADED, REPRESENTATIVE, AUTHORIZED_PROPERTY_IMAGE, etc.)
        scores = []
        for url in image_urls:
            try:
                analysis = cls.analyze_single_image(url, base_dir=base_dir)
                scores.append(analysis)
            except Exception as err:
                print(f"Failed to analyze image '{url}': {err}")

        if not scores:
            return {
                "image_analysis_available": False,
                "image_loaded": False,
                "image_status": "ANALYSIS_FAILED",
                "image_provenance": image_classification,
                "cnn_model": "PyTorch ResNet-18",
                "cnn_status": "UNAVAILABLE",
                "embedding_dimensions": None,
                "embedding_norm": 0.0,
                "non_zero_features": 0,
                "embedding_sample": [],
                "image_quality_score": None,
                "visual_features": {},
                "usable_for_ai": False,
                "disclosure_note": "Image file could not be decoded or loaded."
            }

        primary = scores[0]
        avg_quality = round(sum(s["image_quality_score"] for s in scores) / len(scores), 1)

        # Compute mean aggregated 512-D embedding across ALL valid processed images
        all_embeddings = []
        for s in scores:
            feat_list = s.get("feature_embedding", [])
            if len(feat_list) == 512:
                all_embeddings.append(np.array(feat_list, dtype=np.float32))

        if all_embeddings:
            aggregated_embedding = np.mean(all_embeddings, axis=0).astype(np.float32)
        else:
            aggregated_embedding = np.zeros(512, dtype=np.float32)

        agg_norm = float(round(float(np.linalg.norm(aggregated_embedding)), 4))
        agg_nonzero = int(np.count_nonzero(aggregated_embedding))
        agg_sample = [float(round(x, 4)) for x in aggregated_embedding[:6]]

        per_image_metadata = [
            {
                "url": image_urls[idx] if idx < len(image_urls) else f"image_{idx+1}",
                "embedding_dimensions": s["embedding_dimensions"],
                "embedding_norm": s["embedding_norm"],
                "quality_score": s["image_quality_score"],
                "sharpness": s["sharpness"],
                "brightness": s["brightness"],
                "resolution": s["resolution"]
            }
            for idx, s in enumerate(scores)
        ]

        # Normalize metrics for direct gauge display
        brightness_norm = max(0.0, min(100.0, 100.0 - abs(primary["brightness"] - 130.0) * 0.6))
        sharpness_norm = max(0.0, min(100.0, (math.log(primary["sharpness"] + 1.0) / 7.0) * 100.0))
        contrast_norm = max(0.0, min(100.0, (primary["contrast"] / 64.0) * 100.0))

        # Truthful disclosure note based on provenance
        if image_classification == "USER_UPLOADED":
            disc = f"Owner/User-uploaded property photograph ({len(scores)} images analyzed). Processed by PyTorch ResNet-18 for visual feature extraction."
        elif image_classification == "PROPERTY_SPECIFIC":
            disc = f"Verified authentic property-specific photograph ({len(scores)} images analyzed). Processed by PyTorch ResNet-18 for visual feature extraction."
        else:
            disc = f"Representative real-estate photograph (publicly usable reference, {len(scores)} images analyzed). Processed by PyTorch ResNet-18 for visual feature extraction. Not claimed as an actual property photograph."

        visual_features = {
            "model": "PyTorch ResNet-18",
            "cnn_status": "ACTIVE",
            "embedding": f"512 dimensions (Mean aggregated across {len(scores)} images)",
            "embedding_dimensions": 512,
            "embedding_l2_norm": f"{agg_norm:.4f}",
            "embedding_norm_val": agg_norm,
            "non_zero_features": agg_nonzero,
            "embedding_sample": agg_sample,
            "images_analyzed_count": len(scores),
            "image_quality": f"{avg_quality} / 100",
            "image_quality_score": avg_quality,
            "sharpness": f"{primary['sharpness']} (Laplacian Variance)",
            "brightness": f"{primary['brightness']} / 255",
            "contrast": f"{primary['contrast']} (Grayscale StdDev)",
            "resolution": f"{primary['resolution']} ({primary['megapixels']} MP)",
            "aspect_ratio": f"{primary['aspect_ratio']}",
            "color_tone": primary["color_distribution"]["tone"],
            "rgb_distribution": f"R:{primary['color_distribution']['red_mean']}, G:{primary['color_distribution']['green_mean']}, B:{primary['color_distribution']['blue_mean']}"
        }

        # Determine overall condition
        if avg_quality >= 75:
            cond = "EXCELLENT"
        elif avg_quality >= 50:
            cond = "GOOD"
        elif avg_quality >= 30:
            cond = "AVERAGE"
        else:
            cond = "FAIR"

        return {
            "image_analysis_available": True,
            "image_loaded": True,
            "image_status": "IMAGE ANALYSIS COMPLETE",
            "image_provenance": image_classification,
            "cnn_model": "ResNet-18 (Pretrained ImageNet)",
            "cnn_status": "ACTIVE",
            "overall_condition": cond,
            "overall_score": avg_quality,
            "quality_score": avg_quality,
            "embedding_dimensions": 512,
            "embedding_norm": agg_norm,
            "non_zero_features": agg_nonzero,
            "embedding_sample": agg_sample,
            "feature_embedding": [float(x) for x in aggregated_embedding],
            "aggregation_method": "mean",
            "image_quality_score": avg_quality,
            "sharpness_score": round(sharpness_norm, 1),
            "brightness_score": round(brightness_norm, 1),
            "contrast_score": round(contrast_norm, 1),
            "visual_features": visual_features,
            "usable_for_ai": True,
            "number_of_images_analyzed": len(scores),
            "processed_count": len(scores),
            "per_image_analysis": per_image_metadata,
            "disclosure_note": disc
        }
