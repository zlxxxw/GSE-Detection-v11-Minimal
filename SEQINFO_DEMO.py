#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示 seqinfo.ini 自动生成功能

这个脚本展示了如何使用更新后的 gen_draft_gt.py 生成 MOT Challenge 格式的标注
以及 TrackEval 所需的 seqinfo.ini 文件。

用法:
    python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"

生成的文件结构:
    H:\GSE论文资料\实验\video_data\
    ├── video_01.webm
    ├── video_01_gt.txt          ← MOT Challenge 格式的标注文件
    ├── seqinfo.ini              ← TrackEval 需要的配置文件 (自动生成)
    ├── video_02.webm
    ├── video_02_gt.txt
    ├── seqinfo.ini
    └── ...
"""

import os
from pathlib import Path

# ============================================================================
# 演示 1: 查看生成的 seqinfo.ini 内容
# ============================================================================

seqinfo_example = """
[Sequence]
name=video_01              # 视频文件名 (无扩展名)
imDir=img1                 # 图片目录 (MOT Challenge 标准)
frameRate=30               # 帧率 (自动从视频提取)
seqLength=1500             # 总帧数 (自动从视频提取)
imWidth=1920               # 视频宽度 (自动从视频提取)
imHeight=1080              # 视频高度 (自动从视频提取)
imExt=.jpg                 # 图片扩展名 (MOT 标准)
"""

print("=" * 70)
print("seqinfo.ini 自动生成演示")
print("=" * 70)
print("\n📄 生成的 seqinfo.ini 文件内容示例：")
print(seqinfo_example)

# ============================================================================
# 演示 2: gen_draft_gt.py 的工作流程
# ============================================================================

print("\n" + "=" * 70)
print("gen_draft_gt.py 的工作流程 (v1.2+)")
print("=" * 70)

workflow = """
步骤 1: 加载模型
  📦 加载 weights/gse_detection_v11.pt
  ✅ 模型加载成功
  📊 检测类别: ['Galley_Truck', 'GSE', 'Ground_Crew', 'airplane']

步骤 2: 处理视频
  🎬 处理视频: video_01.webm
  📍 输入路径: H:\GSE论文资料\实验\video_data\video_01.webm
  📍 输出路径: H:\GSE论文资料\实验\video_data\video_01_gt.txt
  📊 视频信息: 1920x1080, 30.0fps, 1500 帧

步骤 3: 运行推理和追踪
  🔍 开始推理和追踪 (conf=0.1)...
  处理帧: 100%|████████████████████████| 1500/1500 [05:23<00:00, 4.64it/s]

步骤 4: 生成输出文件
  ✅ 预标注完成！
  📊 统计信息:
     - 处理帧数: 1500
     - 检测目标数: 3245
     - 输出文件: H:\...\video_01_gt.txt
     📝 已生成配置文件: seqinfo.ini    ← 新增！

步骤 5: 准备 TrackEval 评测
  💡 现在您可以使用 TrackEval 来评测标注质量
     - seqinfo.ini: TrackEval 已自动识别
     - video_01_gt.txt: 标注文件
     → TrackEval 会自动读取 seqinfo.ini 获取视频元信息
"""

print(workflow)

# ============================================================================
# 演示 3: MOT Challenge 格式详解
# ============================================================================

print("\n" + "=" * 70)
print("生成的 MOT Challenge 格式详解")
print("=" * 70)

mot_example = """
文件: video_01_gt.txt

内容示例:
1,1,100.50,200.50,50.00,80.00,0.85,0,-1,-1
1,2,300.00,250.50,60.00,90.00,0.92,1,-1,-1
2,1,105.50,205.00,50.50,80.20,0.86,0,-1,-1
2,2,305.00,255.00,59.50,89.50,0.91,1,-1,-1
3,1,110.50,210.00,50.80,80.50,0.84,0,-1,-1

列说明:
  frame_idx  (第1列): 帧号 (从1开始)
  track_id   (第2列): 追踪ID (同一物体在不同帧中的ID相同)
  x1         (第3列): 左上角 x 坐标
  y1         (第4列): 左上角 y 坐标
  w          (第5列): 宽度
  h          (第6列): 高度
  conf       (第7列): 置信度 [0, 1]
  class_id   (第8列): 物体类别ID (0=Galley_Truck, 1=GSE, 2=Ground_Crew, 3=airplane)
  -1         (第9列): MOT 标准占位符
  -1         (第10列): MOT 标准占位符
"""

print(mot_example)

# ============================================================================
# 演示 4: TrackEval 集成
# ============================================================================

print("\n" + "=" * 70)
print("TrackEval 集成流程")
print("=" * 70)

trackeval_flow = """
第 1 步: 运行 gen_draft_gt.py 生成标注
  $ python gen_draft_gt.py --video "H:\video_data"
  ✅ 生成 video_01_gt.txt 和 seqinfo.ini
  ✅ 生成 video_02_gt.txt 和 seqinfo.ini
  ✅ ...

第 2 步: TrackEval 自动识别
  - TrackEval 读取 seqinfo.ini
  - 自动获取视频信息:
    * name: video_01
    * frameRate: 30
    * seqLength: 1500
    * imWidth: 1920
    * imHeight: 1080

第 3 步: 执行评测
  $ python -m pycocotools.coco evaluate --gt_file video_01_gt.txt
  (具体命令取决于您使用的评测工具)

第 4 步: 获取评测结果
  - MOTA (Multi-Object Tracking Accuracy)
  - IDF1 (ID F1 Score)
  - 其他指标...
"""

print(trackeval_flow)

# ============================================================================
# 演示 5: 快速开始
# ============================================================================

print("\n" + "=" * 70)
print("快速开始 (一句命令搞定)")
print("=" * 70)

quick_start = """
# 进入项目目录
$ cd d:\Allen\SoftWare\VS Code\Code\Python\GSE_Detection_v11_Minimal

# 一键处理所有视频 (自动生成 gt.txt 和 seqinfo.ini)
$ python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"

# ✅ 完成！所有输出文件已生成，准备就绪进行 TrackEval 评测！

# 输出文件位置:
H:\GSE论文资料\实验\video_data\
├── video_01_gt.txt
├── seqinfo.ini          ← TrackEval 需要
├── video_02_gt.txt
├── seqinfo.ini
└── ...
"""

print(quick_start)

# ============================================================================
# 演示 6: 代码级别的 seqinfo.ini 生成
# ============================================================================

print("\n" + "=" * 70)
print("代码级别 - seqinfo.ini 自动生成逻辑")
print("=" * 70)

code_example = """
# 在 gen_draft_gt.py 的 DraftGTGenerator 类中

def _write_seqinfo(self, video_path, output_dir, width, height, fps, total_frames):
    '''
    自动生成 TrackEval 所需的 seqinfo.ini 文件
    '''
    video_name = Path(video_path).stem
    seqinfo_path = Path(output_dir) / "seqinfo.ini"
    
    # 标准 MOT Challenge 格式
    content = f'''[Sequence]
name={video_name}              # 自动从视频文件名提取
imDir=img1                     # MOT 标准目录
frameRate={fps}                # 自动从视频元数据提取
seqLength={total_frames}       # 自动从视频元数据提取
imWidth={width}                # 自动从视频元数据提取
imHeight={height}              # 自动从视频元数据提取
imExt=.jpg                     # MOT 标准扩展名
'''
    
    with open(seqinfo_path, 'w') as f:
        f.write(content)
    
    print(f"   📝 已生成配置文件: {seqinfo_path.name}")

# 在 process_video 方法中的调用:
def process_video(self, video_path, output_path=None, conf_threshold=0.1):
    # ... (处理视频逻辑)
    
    # 提取视频属性
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    # ... (推理和追踪逻辑)
    
    # [新增] 在返回结果前生成 seqinfo.ini
    self._write_seqinfo(video_path, output_dir, width, height, fps, total_frames)
    
    return output_path
"""

print(code_example)

# ============================================================================
# 演示 7: 常见问题
# ============================================================================

print("\n" + "=" * 70)
print("常见问题 (FAQ)")
print("=" * 70)

faq = """
Q: seqinfo.ini 为什么这么重要？
A: MOT Challenge 评测工具 (如 TrackEval) 需要通过 seqinfo.ini 来获取视频的
   基本信息，比如帧率、分辨率、总帧数等。没有它，评测工具会报错。
   现在 gen_draft_gt.py 会自动生成它，无需手动编辑。

Q: seqinfo.ini 会被 TrackEval 覆盖吗？
A: 不会。seqinfo.ini 只是配置文件，TrackEval 只会读取它，不会修改。

Q: 如果视频信息不对怎么办？
A: seqinfo.ini 是从视频文件的元数据自动提取的。如果信息有误，可能表示：
   1. 视频文件本身的元数据有问题
   2. OpenCV 无法正确读取该视频格式
   建议使用 ffprobe 或 MediaInfo 检查视频的实际参数。

Q: 我可以手动编辑 seqinfo.ini 吗？
A: 可以，但不建议。最好的做法是确保输入视频的元数据正确。
   如果必须修改，注意格式必须严格遵循 MOT Challenge 标准。

Q: 不同视频可以共用一个 seqinfo.ini 吗？
A: 不行。每个视频都有不同的 fps、分辨率等参数，需要独立的 seqinfo.ini。
   gen_draft_gt.py 会为每个视频自动生成一个。

Q: seqinfo.ini 中的 imExt=.jpg 是什么意思？
A: 这是 MOT Challenge 的标准约定，表示提取的图片格式（如果提取的话）。
   它不影响当前的 txt 标注文件的生成和评测。
"""

print(faq)

print("\n" + "=" * 70)
print("更多信息请参考 README.md 或 BATCH_PROCESSING_GUIDE.md")
print("=" * 70)
