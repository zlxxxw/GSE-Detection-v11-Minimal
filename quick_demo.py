#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick inference demo for GSE Detection v11
机场GSE检测 v11 快速推理演示
"""

import cv2
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.detection import GSEDetector
import config


def detect_image(image_path: str):
    """
    Detect objects in a single image
    
    Args:
        image_path: Path to input image
    """
    print(f"\n{'='*70}")
    print(f"GSE Detection v11 - Image Detection Demo")
    print(f"{'='*70}\n")
    
    # Initialize detector
    detector = GSEDetector()
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return
    
    print(f"📷 Loaded image: {image_path}")
    print(f"   Size: {image.shape}")
    
    # Detect
    print("\n🔍 Running detection...")
    results = detector.detect(image)
    
    # Print results
    detections = detector.get_detections_info(results)
    print(f"✅ Found {len(detections)} objects:")
    
    for i, det in enumerate(detections):
        print(f"\n   [{i+1}] {det['class_name']}")
        print(f"       Confidence: {det['confidence']:.3f}")
        print(f"       BBox: {[f'{x:.1f}' for x in det['bbox']]}")
    
    # Draw and save
    annotated = detector.draw_detections(image, results)
    output_path = image_path.replace('.', '_detected.')
    cv2.imwrite(output_path, annotated)
    print(f"\n💾 Saved to: {output_path}")


def detect_video(video_path: str, output_path: str = None, skip_frames: int = 1):
    """
    Detect objects in video
    
    Args:
        video_path: Path to input video
        output_path: Path for output video (optional)
        skip_frames: Skip N frames between detections (for speed)
    """
    print(f"\n{'='*70}")
    print(f"GSE Detection v11 - Video Detection Demo")
    print(f"{'='*70}\n")
    
    # Initialize detector
    detector = GSEDetector()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Failed to open video: {video_path}")
        return
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Loaded video: {video_path}")
    print(f"   Frames: {frame_count} | FPS: {fps:.1f} | Size: {width}x{height}")
    print(f"   Processing every {skip_frames} frame(s)")
    
    # Setup output if requested
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"📝 Output will be saved to: {output_path}")
    
    # Process video
    frame_idx = 0
    detected_count = 0
    
    print("\n🔍 Processing video...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every Nth frame
        if frame_idx % skip_frames == 0:
            results = detector.detect(frame)
            detections = detector.get_detections_info(results)
            detected_count += len(detections)
            
            # Draw on frame
            frame = detector.draw_detections(frame, results)
            
            # Print progress
            if frame_idx % (skip_frames * 30) == 0:
                print(f"   Frame {frame_idx}/{frame_count} | Objects: {detected_count}")
        
        # Write frame
        if writer:
            writer.write(frame)
        
        frame_idx += 1
    
    # Cleanup
    cap.release()
    if writer:
        writer.release()
    
    print(f"\n✅ Processing complete!")
    print(f"   Total frames: {frame_idx}")
    print(f"   Objects detected: {detected_count}")
    if output_path:
        print(f"   Output saved: {output_path}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GSE Detection v11 - Quick Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_demo.py --image path/to/image.jpg
  python quick_demo.py --video path/to/video.mp4
  python quick_demo.py --video path/to/video.mp4 --output result.mp4 --skip 2
        """
    )
    
    parser.add_argument('--image', type=str, help='Path to input image')
    parser.add_argument('--video', type=str, help='Path to input video')
    parser.add_argument('--output', type=str, default=None, help='Output video path')
    parser.add_argument('--skip', type=int, default=1, help='Skip N frames for speed')
    
    args = parser.parse_args()
    
    if args.image:
        detect_image(args.image)
    elif args.video:
        detect_video(args.video, args.output, args.skip)
    else:
        parser.print_help()
        print("\n❌ Please provide either --image or --video argument")


if __name__ == '__main__':
    main()
