# GSE Detection v11 - Minimal Project

**核心模型**: `gse_detection_v11.pt` (YOLOv11)

这是一个最小化的、生产就绪的 GSE（地面服务设备）检测项目，基于 YOLOv11 模型。本文档整合了所有使用说明、最佳实践和故障排除指南。

⚡ **一句话快速开始**：`python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"`

## 📂 项目结构

```
GSE_Detection_v11_Minimal/
├── config.py                  # 配置文件（模型参数、类别定义等）
├── requirements.txt           # 依赖列表
├── quick_demo.py             # 快速推理演示脚本
├── test_model.py             # 模型自测脚本
├── gen_draft_gt.py           # 批量生成MOT标注和seqinfo.ini
├── save_tracks.py            # 批量提取追踪信息
├── README.md                 # 本文档 (综合说明)
├── weights/
│   └── gse_detection_v11.pt  # 核心YOLOv11模型（需手动复制）
├── utils/
│   ├── __init__.py
│   └── detection.py          # 检测工具类
├── data/
│   └── result/               # 输出目录
└── examples/
    └── (用于存放示例数据)
```

---

## 🚀 快速开始 (3 步)

### 1️⃣ 环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# (可选) GPU加速 CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 2️⃣ 准备模型

从 GSE_Detection_Portable 复制模型到 `weights/` 目录：

```bash
# Windows CMD
copy "D:\Allen\...\GSE_Detection_Portable\weights\gse_detection_v11.pt" ".\weights\"

# PowerShell
Copy-Item -Path "D:\Allen\...\GSE_Detection_Portable\weights\gse_detection_v11.pt" -Destination ".\weights\"
```

### 3️⃣ 验证并运行

```bash
# 验证环境
python test_model.py

# 一键处理整个视频目录！
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"
```

✅ **完成！** 生成的文件：
- `video_01_gt.txt` (MOT Challenge 标注)
- `seqinfo.ini` (TrackEval 评测配置)

---

## 📚 完整功能说明

### 📖 目录

1. [基础推理 (quick_demo.py)](#基础推理)
2. [批量标注生成 (gen_draft_gt.py)](#批量标注生成) ⭐ 推荐
3. [批量追踪提取 (save_tracks.py)](#批量追踪提取)
4. [MOT Challenge 格式](#mot-challenge-格式)
5. [TrackEval 评测集成](#trackeval-评测集成)
6. [模型参数配置](#模型参数配置)
7. [核心 API](#核心-api)
8. [命令速查](#命令速查)
9. [常见问题](#常见问题)
10. [工作流示例](#工作流示例)

---

### 基础推理

#### 单张图像检测
```bash
python quick_demo.py --image path/to/image.jpg
```

#### 视频检测
```bash
# 基础处理
python quick_demo.py --video path/to/video.mp4

# 跳帧加速 (每5帧处理1帧)
python quick_demo.py --video path/to/video.mp4 --skip 5

# 保存结果视频
python quick_demo.py --video path/to/video.mp4 --output result.mp4
```

---

### 批量标注生成

**gen_draft_gt.py** - 生成 MOT Challenge 格式标注和 seqinfo.ini ⭐

#### 工作流程：
1. 输入视频目录或单个文件
2. 自动递归搜索所有 `.webm` 和 `.mp4` 文件
3. 使用 YOLOv11 + ByteTrack 推理追踪
4. 输出 MOT Challenge 格式的 `_gt.txt` 文件
5. **自动生成** `seqinfo.ini` (TrackEval 评测工具需要)

#### 使用方法：
```bash
# 处理单个视频
python gen_draft_gt.py --video "video.webm"

# 处理整个目录 (推荐)
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"

# 强制覆盖已存在的文件
python gen_draft_gt.py --video "path" --force

# 调整置信度阈值 (0.1推荐用于标注，减少漏检)
python gen_draft_qt.py --video "path" --conf 0.15
```

#### 输出示例：
```
🎬 找到 5 个视频文件

[1/5] 📹 video_01.webm
      🔍 开始推理和追踪 (conf=0.1)...
      ✅ 预标注完成！
      📊 统计信息:
         - 处理帧数: 1500
         - 检测目标数: 3245
         - 输出文件: H:\...\video_01_gt.txt
         📝 已生成配置文件: seqinfo.ini

======================================================================
📊 批量处理完成！
   ✅ 成功: 4 个
   ⏭️  跳过: 1 个  (已存在，使用--force覆盖)
   ❌ 失败: 0 个
   📁 视频目录: H:\GSE论文资料\实验\video_data
======================================================================
```

#### 生成的文件示例：
```
H:\GSE论文资料\实验\video_data\
├── video_01.webm
├── video_01_gt.txt          ← MOT Challenge 标注
├── seqinfo.ini              ← TrackEval 配置 (自动生成)
├── video_02.webm
├── video_02_gt.txt
├── seqinfo.ini
└── ...
```

---

### 批量追踪提取

**save_tracks.py** - 批量提取追踪信息

#### 使用方法：
```bash
# 使用默认目录
python save_tracks.py

# 指定自定义视频目录
python save_tracks.py --video "H:\video_data"

# 调整置信度阈值
python save_tracks.py --video "path" --conf 0.15
```

#### 特点：
- 自动查找所有 `.webm` 和 `.mp4` 文件
- 逐个处理，帧号自动重置
- 输出文件保存在 `data/result/` 目录
- 文件名与视频同名

---

## 📊 MOT Challenge 格式

### 标注文件格式示例

**文件**: `video_01_gt.txt`

```
1,1,100.50,200.50,50.00,80.00,0.85,0,-1,-1
1,2,300.00,250.50,60.00,90.00,0.92,1,-1,-1
2,1,105.50,205.00,50.50,80.20,0.86,0,-1,-1
2,2,305.00,255.00,59.50,89.50,0.91,1,-1,-1
3,1,110.50,210.00,50.80,80.50,0.84,0,-1,-1
```

| 列号 | 字段 | 说明 | 示例值 |
|-----|------|------|--------|
| 1 | frame_idx | 帧号 (从1开始) | 1, 2, 3... |
| 2 | track_id | 追踪ID (同一物体在不同帧的ID相同) | 1, 2, 3... |
| 3 | x1 | 左上角 x 坐标 | 100.50 |
| 4 | y1 | 左上角 y 坐标 | 200.50 |
| 5 | w | 宽度 (像素) | 50.00 |
| 6 | h | 高度 (像素) | 80.00 |
| 7 | conf | 置信度 [0-1] | 0.85 |
| 8 | class_id | 物体类别 (0=Galley_Truck, 1=GSE, 2=Ground_Crew, 3=airplane) | 0, 1, 2, 3 |
| 9 | - | MOT标准占位符 | -1 |
| 10 | - | MOT标准占位符 | -1 |

### 坐标转换说明

YOLO 输出为**中心坐标系**，自动转换为**左上角坐标系** (MOT 标准)：

```python
# 转换公式
x_center = 125.5, y_center = 240.5, w = 50.0, h = 80.0
x1 = x_center - w / 2  →  125.5 - 25.0 = 100.5
y1 = y_center - h / 2  →  240.5 - 40.0 = 200.5
```

---

## 🔬 TrackEval 评测工具集成

### seqinfo.ini 文件说明

`gen_draft_gt.py` **自动生成** `seqinfo.ini` 文件，这是 MOT Challenge 评测工具的必需配置。

#### 自动生成的内容示例：

```ini
[Sequence]
name=video_01              # 视频文件名 (无扩展名)
imDir=img1                 # 图片目录 (MOT Challenge 标准)
frameRate=30               # 帧率 (自动从视频提取)
seqLength=1500             # 总帧数 (自动从视频提取)
imWidth=1920               # 视频宽度 (自动从视频提取)
imHeight=1080              # 视频高度 (自动从视频提取)
imExt=.jpg                 # 图片扩展名 (MOT 标准)
```

#### 工作流程：

```
步骤 1: 运行生成脚本
  $ python gen_draft_gt.py --video "H:\video_data"
  ✅ 生成: video_01_gt.txt + seqinfo.ini
  
步骤 2: TrackEval 自动识别
  - 读取 seqinfo.ini
  - 获取视频元信息 (fps, 分辨率, 总帧数等)
  
步骤 3: 执行评测
  $ python trackeval_script.py --gt_file video_01_gt.txt
  (具体命令取决于您使用的评测工具)
  
步骤 4: 获取评测结果
  - MOTA (Multi-Object Tracking Accuracy)
  - IDF1 (ID F1 Score)
  - 其他指标...
```

#### seqinfo.ini FAQ：

**Q: 为什么需要 seqinfo.ini？**  
A: MOT Challenge 评测工具需要通过此文件获取视频的基本信息。

**Q: seqinfo.ini 会被覆盖吗？**  
A: 不会。TrackEval 只读取，不修改。

**Q: 可以手动编辑 seqinfo.ini 吗？**  
A: 可以，但不建议。最好确保输入视频的元数据正确。如果必须修改，要严格遵循 MOT Challenge 标准格式。

**Q: 不同视频可以共用一个 seqinfo.ini 吗？**  
A: 不行。每个视频的参数不同，需要独立的 seqinfo.ini。脚本自动为每个视频生成。

---

## 📋 模型参数配置

编辑 `config.py` 调整参数：

```python
# 检测参数
CONFIDENCE_THRESHOLD = 0.25      # 置信度阈值 (推荐: 0.1 用于标注)
IOU_THRESHOLD = 0.45             # NMS IoU阈值
INPUT_SIZE = 1280                # 输入尺寸

# 类别定义
CLASS_NAMES = {
    0: "Galley_Truck",      # 餐车
    1: "GSE",               # 无人地面设备
    2: "Ground_Crew",       # 地勤人员
    3: "airplane"           # 飞机
}

# 设备选择
DEVICE = None  # None=自动检测，"cuda"/"cpu"/"mps"
```

### GPU 加速配置

```python
from utils.detection import GSEDetector

# 强制使用 CUDA
detector = GSEDetector(device='cuda')

# 强制使用 CPU
detector = GSEDetector(device='cpu')

# 自动检测 (推荐)
detector = GSEDetector(device=None)
```

---

## 🔧 核心 API

### GSEDetector 类 (utils/detection.py)

```python
from utils.detection import GSEDetector

# 初始化检测器
detector = GSEDetector()

# 检测所有对象
results = detector.detect(image)

# 仅检测GSE
results = detector.detect_gse_only(image)

# 获取检测信息
detections = detector.get_detections_info(results)
# 返回: [{'class_id': 1, 'class_name': 'GSE', 'confidence': 0.95, 'bbox': [x1, y1, x2, y2]}, ...]

# 在图像上绘制检测框
annotated = detector.draw_detections(image, results)
```

### 完整示例

```python
import cv2
from utils.detection import GSEDetector

# 初始化
detector = GSEDetector()

# 加载图像
image = cv2.imread('image.jpg')

# 检测
results = detector.detect(image)
detections = detector.get_detections_info(results)

# 输出结果
for det in detections:
    print(f"{det['class_name']}: {det['confidence']:.3f}")
    print(f"  Box: {det['bbox']}")

# 可视化
annotated = detector.draw_detections(image, results)
cv2.imwrite('result.jpg', annotated)
```
annotated = detector.draw_detections(image, results)
```

### 完整示例

```python
import cv2
from utils.detection import GSEDetector

# 初始化
detector = GSEDetector()

# 加载图像
image = cv2.imread('image.jpg')

# 检测
results = detector.detect(image)
detections = detector.get_detections_info(results)

# 输出结果
for det in detections:
    print(f"{det['class_name']}: {det['confidence']:.3f}")
    print(f"  Box: {det['bbox']}")

# 可视化
annotated = detector.draw_detections(image, results)
cv2.imwrite('result.jpg', annotated)
```

---

## 📊 支持的类别

| ID | 类别 | 中文 |
|----|------|------|
| 0 | Galley_Truck | 餐车 |
| 1 | GSE | 无人地面设备 |
| 2 | Ground_Crew | 地勤人员 |
| 3 | airplane | 飞机 |

---

## 🎯 项目特点

✅ **最小化依赖** - 仅需 torch, ultralytics, opencv-python, numpy  
✅ **简洁API** - 易于集成到其他项目  
✅ **CPU/GPU 自动检测** - 自动选择最优设备  
✅ **多格式支持** - 图像、视频推理  
✅ **批量处理** - 一个命令处理整个目录  
✅ **TrackEval 集成** - 自动生成评测所需配置  
✅ **智能文件管理** - 跳过已处理文件，支持强制覆盖  

---

## 📌 命令速查表

### 基础推理
```bash
python quick_demo.py --image file.jpg              # 单张图像
python quick_demo.py --video file.mp4              # 视频处理
python quick_demo.py --video file.mp4 --skip 5     # 跳帧加速
```

### 批量标注生成 (推荐)
```bash
python gen_draft_gt.py --video "path"              # 处理目录
python gen_draft_gt.py --video "path" --force      # 强制覆盖
python gen_draft_gt.py --video "path" --conf 0.2   # 调整置信度
```

### 批量追踪提取
```bash
python save_tracks.py                              # 默认目录
python save_tracks.py --video "path"               # 自定义目录
python save_tracks.py --video "path" --conf 0.15   # 调整置信度
```

### 模型自测
```bash
python test_model.py                               # 验证环境和模型
```

---

## ⚠️ 关键检查清单

### Windows 路径处理
```python
# ✅ 正确 (使用原始字符串)
r"H:\GSE论文资料\实验\video_data"

# ❌ 错误 (\t 会被转义为 Tab)
"H:\GSE论文资料\实验\video_data"
```

### 模型文件验证
```bash
# 检查模型文件是否存在
dir weights\gse_detection_v11.pt

# 文件大小应该 > 100MB
```

### MOT 格式验证
打开生成的 `.txt` 文件，确保格式如下：
```
1,1,100.50,200.50,50.00,80.00,0.85,0,-1,-1
```
- 第1列应从1开始 (不是0)
- 10列逗号分隔
- 浮点数2位小数

---

## ❓ 常见问题

**Q: 模型文件不存在怎么办？**  
A: 需要从 GSE_Detection_Portable 手动复制 `gse_detection_v11.pt` 到 `weights/` 目录。

**Q: 如何使用 TrackEval 评测标注效果？**  
A: 1. 运行 `gen_draft_gt.py` 生成 `_gt.txt` 和 `seqinfo.ini`
   2. TrackEval 会自动读取 seqinfo.ini 获取视频元信息
   3. 查看评测结果

**Q: seqinfo.ini 文件有什么作用？**  
A: MOT Challenge 评测工具需要通过此文件获取视频的帧率、分辨率、总帧数等信息。现已自动生成，无需手动编辑。

**Q: 输出文件的 class_id 列是什么？**  
A: MOT 格式的第8列。这里用 class_id 填充，便于区分物体类型 (0=Galley_Truck, 1=GSE, 2=Ground_Crew, 3=airplane)。

**Q: 不同视频可以共用一个 seqinfo.ini 吗？**  
A: 不行。每个视频的参数不同 (fps、分辨率等)，需要独立的 seqinfo.ini。脚本自动为每个视频生成。

**Q: 已处理的文件会被覆盖吗？**  
A: 默认不会。脚本智能跳过已存在的 `_gt.txt` 文件。使用 `--force` 参数强制覆盖。

**Q: 如何处理多个视频目录？**  
A: 对每个目录分别运行脚本。输出文件自动保存在各自目录。

**Q: 如何提升推理速度？**  
A: 1. 使用 GPU (CUDA)
   2. 降低输入分辨率 (修改 config.py)
   3. 跳帧处理 (使用 --skip 参数)
   4. 使用更小的模型版本

**Q: 如何修改检测阈值？**  
A: 编辑 `config.py` 或在命令行传入 `--conf` 参数。

**Q: 支持哪些视频格式？**  
A: OpenCV 支持的所有格式 (mp4, avi, mov, mkv, webm等)。

**Q: 为什么找不到视频文件？**  
A: 检查路径是否正确，使用 `r"..."` 原始字符串避免转义问题。

**Q: 如果视频信息不对怎么办？**  
A: seqinfo.ini 从视频元数据自动提取。如果不对，可能是视频文件的元数据问题。使用 ffprobe 或 MediaInfo 检查实际参数。

**Q: 可以手动编辑 seqinfo.ini 吗？**  
A: 可以，但不建议。最好确保输入视频的元数据正确。如果必须修改，要严格遵循 MOT Challenge 标准格式。

**Q: 处理大量视频时如何避免内存不足？**  
A: 分批处理。每次处理一个目录或子目录。脚本会逐个处理，不会一次性加载所有视频。

---

## 🔄 工作流示例

### 场景 1: 初次生成标注

```bash
# 处理整个视频目录
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"

# ✅ 生成所有视频的 _gt.txt 和 seqinfo.ini
# → 用标注工具 (DarkLabel) 打开 .txt 进行人工修正
```

### 场景 2: 重新处理新增视频

```bash
# 只处理新增的视频 (自动跳过已存在的)
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"

# ✅ 新视频生成标注，已处理的文件保留
```

### 场景 3: 调整参数重新标注

```bash
# 增加置信度阈值 (减少误检)
python gen_draft_qt.py --video "path" --conf 0.2 --force

# 或降低置信度阈值 (减少漏检)
python gen_draft_gt.py --video "path" --conf 0.05 --force
```

### 场景 4: 进行 TrackEval 评测

```bash
# 步骤1: 生成标注和配置
python gen_draft_gt.py --video "H:\video_data"

# 步骤2: 使用 TrackEval 评测 (具体命令见 TrackEval 文档)
# TrackEval 自动读取 seqinfo.ini 获取视频信息

# 步骤3: 查看评测结果 (MOTA, IDF1 等指标)
```

---

## 📝 更新日志

### v1.2 - TrackEval 评测支持 (2026-01-10)
- ✅ 自动生成 seqinfo.ini 文件
- ✅ TrackEval 评测工具完整集成
- ✅ MOT Challenge 格式详细说明
- ✅ **完整文档整合** (单一 README.md)
- ✅ 删除所有多余说明文件

### v1.1 - 批量处理能力 (2026-01-09)
- ✅ `gen_draft_gt.py` - 支持目录批处理
- ✅ `save_tracks.py` - 批量提取追踪信息
- ✅ 智能文件跳过和强制覆盖

### v1.0 - 初始发布 (2026-01-09)
- ✅ 核心检测模型
- ✅ 快速演示脚本
- ✅ 模型自测工具

---

## 📞 联系与支持

**原始项目**: GSE_Detection_Portable  
**项目位置**: `d:\Allen\SoftWare\VS Code\Code\Python\GSE_Detection_v11_Minimal`  
**GitHub**: https://github.com/zlxxxw/GSE-Detection-v11-Minimal.git

---

**最后更新**: 2026年1月10日  
**当前版本**: v1.2  
**核心模型**: gse_detection_v11.pt (YOLOv11)  
**文档**: 单一整合文档 (README.md)
