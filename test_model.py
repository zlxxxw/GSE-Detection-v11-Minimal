#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for GSE Detection v11
"""

import sys
from pathlib import Path
import numpy as np

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.detection import GSEDetector
import config


def test_model_loading():
    """Test if model loads correctly"""
    print("🧪 Testing Model Loading...")
    print("="*70)
    
    try:
        detector = GSEDetector()
        print(f"✅ Model loaded successfully")
        print(f"   Model path: {config.MODEL_PATH}")
        print(f"   Device: {detector.device or 'auto-detected'}")
        print(f"   Input size: {config.INPUT_SIZE}")
        print(f"   Classes: {list(detector.class_names.values())}")
        return True
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False


def test_inference_dummy():
    """Test inference with dummy image"""
    print("\n🧪 Testing Inference (Dummy Image)...")
    print("="*70)
    
    try:
        detector = GSEDetector()
        
        # Create dummy image (640x640 RGB)
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        print(f"📷 Created dummy image: {dummy_image.shape}")
        print(f"🔍 Running inference...")
        
        results = detector.detect(dummy_image)
        detections = detector.get_detections_info(results)
        
        print(f"✅ Inference successful")
        print(f"   Detections: {len(detections)}")
        if detections:
            print(f"   First detection: {detections[0]['class_name']} ({detections[0]['confidence']:.3f})")
        
        return True
    except Exception as e:
        print(f"❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration"""
    print("\n🧪 Testing Configuration...")
    print("="*70)
    
    print(f"✅ Configuration loaded:")
    print(f"   Model path: {config.MODEL_PATH}")
    print(f"   Confidence threshold: {config.CONFIDENCE_THRESHOLD}")
    print(f"   IoU threshold: {config.IOU_THRESHOLD}")
    print(f"   Input size: {config.INPUT_SIZE}")
    print(f"   GSE class ID: {config.GSE_CLASS_ID}")
    print(f"   Classes: {config.CLASS_NAMES}")
    
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "GSE Detection v11 - Self Test" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Config": test_config(),
        "Model Loading": test_model_loading(),
        "Inference": test_inference_dummy(),
    }
    
    print("\n" + "="*70)
    print("📊 Test Summary:")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed."))
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
