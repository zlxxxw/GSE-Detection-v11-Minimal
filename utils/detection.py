"""
Detection utilities for GSE Detection v11
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class GSEDetector:
    """
    Lightweight GSE Detection wrapper using YOLOv11
    """
    
    def __init__(self, model_path: str = config.MODEL_PATH, device: str = None):
        """
        Initialize detector
        
        Args:
            model_path: Path to YOLO model weights
            device: Device to use ('cuda', 'cpu', 'mps', or None for auto)
        """
        self.model_path = model_path
        self.device = device or config.DEVICE
        
        print(f"Loading model from: {model_path}")
        self.model = YOLO(model_path)
        
        if self.device:
            self.model.to(self.device)
        
        self.class_names = self.model.names
        print(f"Model loaded. Classes: {list(self.class_names.values())}")
    
    def detect(self, image, conf_threshold: float = None, iou_threshold: float = None):
        """
        Detect objects in image
        
        Args:
            image: Input image (numpy array or path)
            conf_threshold: Confidence threshold (default from config)
            iou_threshold: IoU threshold for NMS (default from config)
        
        Returns:
            results: YOLO detection results
        """
        conf = conf_threshold or config.CONFIDENCE_THRESHOLD
        iou = iou_threshold or config.IOU_THRESHOLD
        
        results = self.model(image, conf=conf, iou=iou, device=self.device)
        return results
    
    def detect_gse_only(self, image, conf_threshold: float = None):
        """
        Detect only GSE objects
        
        Args:
            image: Input image
            conf_threshold: Confidence threshold
        
        Returns:
            filtered_results: Detection results containing only GSE
        """
        results = self.detect(image, conf_threshold=conf_threshold)
        
        # Filter for GSE class only
        gse_class_id = config.GSE_CLASS_ID
        
        if len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                # Filter by class ID
                mask = result.boxes.cls == gse_class_id
                result.boxes = result.boxes[mask]
        
        return results
    
    def draw_detections(self, image, results, show_class_name: bool = True):
        """
        Draw detection boxes on image
        
        Args:
            image: Input image
            results: Detection results from model
            show_class_name: Whether to show class names
        
        Returns:
            annotated_image: Image with drawn boxes
        """
        annotated = image.copy()
        
        if len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for box, conf, cls_id in zip(
                    result.boxes.xyxy, 
                    result.boxes.conf, 
                    result.boxes.cls
                ):
                    x1, y1, x2, y2 = map(int, box)
                    cls_id = int(cls_id)
                    
                    # Get color
                    color = config.CLASS_COLORS.get(cls_id, (0, 255, 0))
                    
                    # Draw box
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label
                    label = f"{self.class_names[cls_id]} {conf:.2f}"
                    cv2.putText(
                        annotated, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )
        
        return annotated
    
    def get_detections_info(self, results):
        """
        Extract detection information from results
        
        Args:
            results: Detection results
        
        Returns:
            List of detection dictionaries with keys:
            - class_id, class_name, confidence, bbox (x1, y1, x2, y2)
        """
        detections = []
        
        if len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for box, conf, cls_id in zip(
                    result.boxes.xyxy,
                    result.boxes.conf,
                    result.boxes.cls
                ):
                    cls_id = int(cls_id)
                    detections.append({
                        'class_id': cls_id,
                        'class_name': self.class_names[cls_id],
                        'confidence': float(conf),
                        'bbox': [float(x) for x in box]
                    })
        
        return detections
