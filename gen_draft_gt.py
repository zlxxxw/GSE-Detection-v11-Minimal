#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成草稿标注文件 (Generate Draft Ground Truth)
利用训练好的 YOLOv11 模型对视频进行推理和追踪，输出 MOT Challenge 格式的标注文件

使用方法:
    python gen_draft_gt.py --video path/to/video.webm
    python gen_draft_gt.py --video H:/GSE论文资料/实验/video_data/video.webm
"""

import cv2
import sys
import argparse
import os
from pathlib import Path
from tqdm import tqdm

from ultralytics import YOLO
import config


class DraftGTGenerator:
    """
    草稿标注生成器
    基于 YOLOv11 + ByteTrack 生成 MOT Challenge 格式的标注文件
    """
    
    # MOT Challenge 标注格式
    MOT_FORMAT = "{frame_idx},{track_id},{x1:.2f},{y1:.2f},{w:.2f},{h:.2f},{conf:.2f},{class_id},{dummy1},{dummy2}\n"
    
    def __init__(self, model_path=None):
        """
        初始化生成器
        
        Args:
            model_path: 模型路径，默认使用 config.MODEL_PATH
        """
        self.model_path = model_path or config.MODEL_PATH
        print(f"📦 加载模型: {self.model_path}")
        self.model = YOLO(self.model_path)
        print(f"✅ 模型加载成功")
        
        # 类别映射
        self.class_names = self.model.names
        print(f"📊 检测类别: {list(self.class_names.values())}")
    
    def process_video(self, video_path, output_path=None, conf_threshold=0.1):
        """
        处理视频并生成标注文件
        
        Args:
            video_path: 输入视频路径
            output_path: 输出标注文件路径 (默认使用视频同名的 _gt.txt)
            conf_threshold: 置信度阈值 (默认 0.1 以减少漏检)
        
        Returns:
            输出文件路径
        """
        # 验证视频文件
        video_file = Path(video_path)
        if not video_file.exists():
            print(f"❌ 错误: 视频文件不存在: {video_path}")
            return None
        
        # 确定输出路径
        if output_path is None:
            output_path = str(video_file.parent / f"{video_file.stem}_gt.txt")
        
        # 创建输出目录
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🎬 处理视频: {video_file.name}")
        print(f"📍 输入路径: {video_path}")
        print(f"📍 输出路径: {output_path}")
        
        # 打开视频获取帧数和视频属性
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"❌ 错误: 无法打开视频: {video_path}")
            return None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        print(f"📊 视频信息: {width}x{height}, {fps:.1f}fps, {total_frames} 帧")
        
        # 运行推理和追踪
        print(f"\n🔍 开始推理和追踪 (conf={conf_threshold})...")
        
        tracked_count = 0
        frame_count = 0
        
        with open(output_path, 'w') as f:
            # 使用 model.track() 进行推理和追踪
            # persist=True: 保持追踪 ID
            # tracker="bytetrack.yaml": 使用 ByteTrack
            # conf: 置信度阈值 (降低以减少漏检)
            results = self.model.track(
                source=str(video_path),
                tracker="bytetrack.yaml",
                persist=True,
                conf=conf_threshold,
                stream=True,
                verbose=False
            )
            
            # 使用进度条处理每一帧
            for frame_idx, r in enumerate(tqdm(results, total=total_frames, desc="处理帧")):
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
                            class_id=int(class_id),        # 类别 ID
                            dummy1=-1,                     # MOT 标准占位符
                            dummy2=-1                      # MOT 标准占位符
                        )
                        f.write(line)
                        tracked_count += 1
        
        # 完成提示
        print(f"\n✅ 预标注完成！")
        print(f"📊 统计信息:")
        print(f"   - 处理帧数: {frame_count}")
        print(f"   - 检测目标数: {tracked_count}")
        print(f"   - 输出文件: {output_path}")
        print(f"\n💡 提示: 请使用标注工具 (如 DarkLabel) 打开此文件进行人工修正")
        
        return output_path


def main():
    """
    主函数 - 命令行入口
    """
    parser = argparse.ArgumentParser(
        description="生成草稿标注文件 (Generate Draft Ground Truth)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 指定视频文件
  python gen_draft_gt.py --video video.webm
  
  # 完整路径
  python gen_draft_gt.py --video H:/GSE论文资料/实验/video_data/video.webm
  
  # 自定义输出路径
  python gen_draft_gt.py --video video.webm --output custom_gt.txt
  
  # 调整置信度阈值
  python gen_draft_gt.py --video video.webm --conf 0.2
        """
    )
    
    parser.add_argument('--video', '-v', type=str, required=True,
                        help='输入视频路径 (必需)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出标注文件路径 (可选，默认使用视频同名)')
    parser.add_argument('--conf', type=float, default=0.1,
                        help='置信度阈值 (默认 0.1，范围 0.0-1.0)')
    parser.add_argument('--model', '-m', type=str, default=None,
                        help='模型路径 (可选，默认使用 config.MODEL_PATH)')
    
    args = parser.parse_args()
    
    # 验证置信度阈值
    if not 0.0 <= args.conf <= 1.0:
        print(f"❌ 错误: 置信度阈值必须在 0.0-1.0 之间，得到: {args.conf}")
        return 1
    
    # 创建生成器
    generator = DraftGTGenerator(model_path=args.model)
    
    # 处理视频
    output_file = generator.process_video(
        video_path=args.video,
        output_path=args.output,
        conf_threshold=args.conf
    )
    
    if output_file is None:
        return 1
    
    print(f"\n🎉 任务完成！")
    print(f"📁 输出文件已保存: {Path(output_file).absolute()}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())