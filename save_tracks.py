#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存追踪信息 (Save Tracks)
批量处理视频，提取追踪信息并保存为 MOT Challenge 格式

使用方法:
    python save_tracks.py
    python save_tracks.py --video H:/GSE论文资料/实验/video_data
"""

import cv2
import sys
import argparse
import glob
from pathlib import Path
from tqdm import tqdm

from ultralytics import YOLO
import config


class TrackingSaver:
    """
    追踪信息保存器
    基于 YOLOv11 + ByteTrack 提取追踪信息并保存为 MOT 格式
    """
    
    # MOT Challenge 标注格式
    MOT_FORMAT = "{frame_idx},{track_id},{x1:.2f},{y1:.2f},{w:.2f},{h:.2f},{conf:.2f},{class_id},-1,-1\n"
    
    def __init__(self, model_path=None, output_dir="data/result"):
        """
        初始化保存器
        
        Args:
            model_path: 模型路径，默认使用 config.MODEL_PATH
            output_dir: 输出目录
        """
        self.model_path = model_path or config.MODEL_PATH
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 加载模型: {self.model_path}")
        self.model = YOLO(self.model_path)
        print(f"✅ 模型加载成功")
        
        # 类别映射
        self.class_names = self.model.names
        print(f"📊 检测类别: {list(self.class_names.values())}")
        print(f"📁 输出目录: {self.output_dir.absolute()}\n")
    
    def process_video(self, video_path, conf_threshold=0.1):
        """
        处理单个视频并保存追踪信息
        
        Args:
            video_path: 输入视频路径
            conf_threshold: 置信度阈值
        
        Returns:
            (是否成功, 输出文件路径)
        """
        # 验证视频文件
        video_file = Path(video_path)
        if not video_file.exists():
            print(f"  ❌ 错误: 视频文件不存在: {video_path}")
            return False, None
        
        # 确定输出路径（视频同名，保存在 output_dir 下）
        output_path = self.output_dir / f"{video_file.stem}.txt"
        
        print(f"  📹 处理视频: {video_file.name}")
        print(f"     → 输出: {output_path.name}")
        
        # 打开视频获取属性
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"  ❌ 错误: 无法打开视频")
            return False, None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        print(f"     视频: {width}x{height}, {fps:.1f}fps, {total_frames} 帧")
        
        # 运行推理和追踪
        tracked_count = 0
        frame_count = 0
        
        with open(output_path, 'w') as f:
            # 使用 model.track() 进行推理和追踪
            # 注意：对于每个新视频，都会重新初始化追踪，帧号自动从 0 开始
            results = self.model.track(
                source=str(video_path),
                tracker="bytetrack.yaml",
                persist=True,
                conf=conf_threshold,
                stream=True,
                verbose=False
            )
            
            # 使用进度条处理每一帧
            pbar = tqdm(results, total=total_frames, desc="     处理帧", 
                       leave=False, ncols=80)
            for frame_idx, r in enumerate(pbar):
                frame_count += 1
                
                # 检查是否有检测结果和追踪 ID
                if r.boxes is not None and r.boxes.id is not None:
                    # 提取检测信息
                    boxes = r.boxes.xywh.cpu().numpy()  # 中心坐标 (xc, yc, w, h)
                    track_ids = r.boxes.id.int().cpu().numpy()
                    confidences = r.boxes.conf.cpu().numpy()
                    class_ids = r.boxes.cls.int().cpu().numpy()
                    
                    # 逐个目标写入标注
                    for box, track_id, conf, class_id in zip(boxes, track_ids, confidences, class_ids):
                        # 提取坐标和尺寸
                        x_center, y_center, w, h = box
                        
                        # 转换为左上角坐标 (MOT 标准)
                        x1 = x_center - w / 2
                        y1 = y_center - h / 2
                        
                        # 写入 MOT Challenge 格式
                        # frame_idx 从 1 开始计数 (MOT 标准)
                        line = self.MOT_FORMAT.format(
                            frame_idx=frame_idx + 1,      # 帧号 (从 1 开始)
                            track_id=int(track_id),        # 追踪 ID
                            x1=x1,                         # 左上角 x
                            y1=y1,                         # 左上角 y
                            w=w,                           # 宽度
                            h=h,                           # 高度
                            conf=conf,                     # 置信度
                            class_id=int(class_id)         # 类别 ID
                        )
                        f.write(line)
                        tracked_count += 1
        
        print(f"     ✅ 完成: {tracked_count} 个检测 | {frame_count} 帧")
        return True, str(output_path)
    
    def process_videos_batch(self, video_dir, conf_threshold=0.1):
        """
        批量处理视频目录
        
        Args:
            video_dir: 视频目录路径
            conf_threshold: 置信度阈值
        
        Returns:
            (成功数, 失败数, 输出文件列表)
        """
        video_dir = Path(video_dir)
        if not video_dir.exists():
            print(f"❌ 错误: 目录不存在: {video_dir}")
            return 0, 0, []
        
        # 查找所有视频文件
        video_files = []
        for ext in ['*.webm', '*.mp4', '*.avi', '*.mov']:
            video_files.extend(video_dir.glob(f"**/{ext}"))
            video_files.extend(video_dir.glob(f"**/{ext.upper()}"))
        
        video_files = sorted(list(set(video_files)))  # 去重并排序
        
        if not video_files:
            print(f"❌ 错误: 未找到视频文件 ({video_dir})")
            return 0, 0, []
        
        print(f"🎬 找到 {len(video_files)} 个视频文件\n")
        
        # 批量处理
        success_count = 0
        fail_count = 0
        output_files = []
        
        for idx, video_file in enumerate(video_files, 1):
            print(f"[{idx}/{len(video_files)}]")
            success, output_path = self.process_video(video_file, conf_threshold)
            
            if success:
                success_count += 1
                output_files.append(output_path)
            else:
                fail_count += 1
            print()
        
        return success_count, fail_count, output_files


def main():
    """
    主函数 - 命令行入口
    """
    parser = argparse.ArgumentParser(
        description="批量保存追踪信息 (Batch Save Tracks)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理默认目录
  python save_tracks.py
  
  # 指定视频目录
  python save_tracks.py --video H:/GSE论文资料/实验/video_data
  
  # 调整置信度阈值
  python save_tracks.py --video video_dir --conf 0.2
  
  # 使用自定义模型
  python save_tracks.py --video video_dir --model weights/custom_model.pt
        """
    )
    
    parser.add_argument('--video', '-v', type=str, 
                        default=r"H:\GSE论文资料\实验\video_data",
                        help='输入视频目录或文件路径 (默认: H:\\GSE论文资料\\实验\\video_data)')
    parser.add_argument('--output', '-o', type=str, default="data/result",
                        help='输出结果目录 (默认: data/result)')
    parser.add_argument('--conf', type=float, default=0.1,
                        help='置信度阈值 (默认 0.1，范围 0.0-1.0)')
    parser.add_argument('--model', '-m', type=str, default=None,
                        help='模型路径 (可选，默认使用 config.MODEL_PATH)')
    
    args = parser.parse_args()
    
    # 验证置信度阈值
    if not 0.0 <= args.conf <= 1.0:
        print(f"❌ 错误: 置信度阈值必须在 0.0-1.0 之间，得到: {args.conf}")
        return 1
    
    # 创建保存器
    saver = TrackingSaver(model_path=args.model, output_dir=args.output)
    
    # 判断是文件还是目录
    video_path = Path(args.video)
    
    if not video_path.exists():
        print(f"❌ 错误: 路径不存在: {args.video}")
        return 1
    
    # 批量处理
    success, fail, output_files = saver.process_videos_batch(
        video_dir=args.video,
        conf_threshold=args.conf
    )
    
    # 统计输出
    print(f"\n{'='*70}")
    print(f"📊 处理完成!")
    print(f"   ✅ 成功: {success} 个")
    print(f"   ❌ 失败: {fail} 个")
    print(f"   📁 输出目录: {saver.output_dir.absolute()}")
    
    if output_files:
        print(f"\n📄 生成的文件:")
        for output_file in output_files:
            print(f"   ✓ {Path(output_file).name}")
    
    print(f"{'='*70}\n")
    
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())