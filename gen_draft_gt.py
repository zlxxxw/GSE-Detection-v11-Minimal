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
        
        # [新增] 自动生成 seqinfo.ini (TrackEval 评测工具需要)
        self._write_seqinfo(video_path, output_dir, width, height, fps, total_frames)
        
        # 完成提示
        print(f"\n✅ 预标注完成！")
        print(f"📊 统计信息:")
        print(f"   - 处理帧数: {frame_count}")
        print(f"   - 检测目标数: {tracked_count}")
        print(f"   - 输出文件: {output_path}")
        print(f"\n💡 提示: 请使用标注工具 (如 DarkLabel) 打开此文件进行人工修正")
        
        return output_path
    
    def _write_seqinfo(self, video_path, output_dir, width, height, fps, total_frames):
        """
        生成 TrackEval 所需的 seqinfo.ini 文件
        
        MOT Challenge 评测工具需要此文件来获取视频的元信息：
        - 视频名称
        - 帧率
        - 总帧数
        - 分辨率 (宽 x 高)
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            width: 视频宽度 (像素)
            height: 视频高度 (像素)
            fps: 帧率 (frames per second)
            total_frames: 总帧数
        """
        video_name = Path(video_path).stem
        seqinfo_path = Path(output_dir) / "seqinfo.ini"
        
        # MOT Challenge 标准的 seqinfo.ini 格式
        content = f"""[Sequence]
name={video_name}
imDir=img1
frameRate={fps}
seqLength={total_frames}
imWidth={width}
imHeight={height}
imExt=.jpg
"""
        
        with open(seqinfo_path, 'w') as f:
            f.write(content)
        
        print(f"   📝 已生成配置文件: {seqinfo_path.name}")


def main():
    """
    主函数 - 命令行入口
    支持单个文件和文件夹批量处理
    """
    parser = argparse.ArgumentParser(
        description="生成草稿标注文件 (Generate Draft Ground Truth)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个视频文件
  python gen_draft_gt.py --video video.webm
  
  # 处理视频目录 (推荐)
  python gen_draft_gt.py --video H:/GSE论文资料/实验/video_data
  
  # 完整路径
  python gen_draft_gt.py --video H:\\GSE论文资料\\实验\\video_data\\video.webm
  
  # 调整置信度阈值
  python gen_draft_gt.py --video video_dir --conf 0.2
  
  # 跳过已存在的标注
  python gen_draft_gt.py --video video_dir
  
  # 强制覆盖已存在的标注
  python gen_draft_gt.py --video video_dir --force
        """
    )
    
    parser.add_argument('--video', '-v', type=str, required=True,
                        help='输入视频路径 (文件或目录)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出标注文件路径 (单文件模式时使用，默认使用视频同名)')
    parser.add_argument('--conf', type=float, default=0.1,
                        help='置信度阈值 (默认 0.1，范围 0.0-1.0)')
    parser.add_argument('--model', '-m', type=str, default=None,
                        help='模型路径 (可选，默认使用 config.MODEL_PATH)')
    parser.add_argument('--force', '-f', action='store_true',
                        help='强制覆盖已存在的标注文件')
    
    args = parser.parse_args()
    
    # 验证置信度阈值
    if not 0.0 <= args.conf <= 1.0:
        print(f"❌ 错误: 置信度阈值必须在 0.0-1.0 之间，得到: {args.conf}")
        return 1
    
    # 创建生成器
    generator = DraftGTGenerator(model_path=args.model)
    
    # 判断输入是文件还是目录
    input_path = Path(args.video)
    
    if not input_path.exists():
        print(f"❌ 错误: 路径不存在: {args.video}")
        return 1
    
    # 文件模式：处理单个视频
    if input_path.is_file():
        output_file = generator.process_video(
            video_path=str(input_path),
            output_path=args.output,
            conf_threshold=args.conf
        )
        
        if output_file is None:
            return 1
        
        print(f"\n🎉 任务完成！")
        print(f"📁 输出文件已保存: {Path(output_file).absolute()}")
        return 0
    
    # 目录模式：批量处理所有视频
    if input_path.is_dir():
        return _process_video_directory(
            generator=generator,
            video_dir=input_path,
            conf_threshold=args.conf,
            force_overwrite=args.force
        )
    
    return 1


def _process_video_directory(generator, video_dir, conf_threshold=0.1, force_overwrite=False):
    """
    批量处理视频目录
    
    Args:
        generator: DraftGTGenerator 实例
        video_dir: 视频目录路径
        conf_threshold: 置信度阈值
        force_overwrite: 是否强制覆盖已存在的文件
    
    Returns:
        返回码 (0: 成功, 1: 失败)
    """
    video_dir = Path(video_dir)
    
    # 查找所有视频文件
    video_files = []
    for ext in ['*.webm', '*.mp4', '*.avi', '*.mov']:
        video_files.extend(video_dir.glob(f"**/{ext}"))
        video_files.extend(video_dir.glob(f"**/{ext.upper()}"))
    
    video_files = sorted(list(set(video_files)))  # 去重并排序
    
    if not video_files:
        print(f"❌ 错误: 未找到视频文件 ({video_dir})")
        return 1
    
    print(f"🎬 找到 {len(video_files)} 个视频文件\n")
    
    # 统计信息
    success_count = 0
    skip_count = 0
    fail_count = 0
    output_files = []
    
    # 批量处理
    for idx, video_file in enumerate(video_files, 1):
        # 输出标注文件路径 (与视频同目录)
        output_path = video_file.parent / f"{video_file.stem}_gt.txt"
        
        print(f"[{idx}/{len(video_files)}] 📹 {video_file.name}")
        
        # 检查文件是否已存在
        if output_path.exists() and not force_overwrite:
            print(f"           ⏭️  跳过 (文件已存在，使用 --force 强制覆盖)")
            skip_count += 1
            print()
            continue
        
        # 处理视频
        output_file = generator.process_video(
            video_path=str(video_file),
            output_path=str(output_path),
            conf_threshold=conf_threshold
        )
        
        if output_file is None:
            fail_count += 1
        else:
            success_count += 1
            output_files.append(output_file)
        
        print()
    
    # 最终统计
    print(f"{'='*70}")
    print(f"📊 批量处理完成！")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ⏭️  跳过: {skip_count} 个")
    print(f"   ❌ 失败: {fail_count} 个")
    print(f"   📁 视频目录: {video_dir.absolute()}")
    
    if output_files:
        print(f"\n📄 生成的文件:")
        for output_file in output_files:
            print(f"   ✓ {Path(output_file).name}")
    
    print(f"{'='*70}\n")
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())