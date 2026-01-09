# GSE Detection v11 - Minimal Project

**核心模型**: `gse_detection_v11.pt` (YOLOv11)

这是一个最小化的、生产就绪的 GSE（地面服务设备）检测项目，基于 YOLOv11 模型。

## 📂 项目结构

```
GSE_Detection_v11_Minimal/
├── config.py                  # 配置文件（模型参数、类别定义等）
├── requirements.txt           # 依赖列表
├── quick_demo.py             # 快速推理演示脚本
├── test_model.py             # 模型自测脚本
├── README.md                 # 本文件
├── weights/
│   └── gse_detection_v11.pt  # 核心YOLOv11模型（需手动复制）
├── utils/
│   ├── __init__.py
│   └── detection.py          # 检测工具类
└── examples/
    └── (用于存放示例数据)
```

## 🚀 快速开始

### 1. 环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# (可选) GPU加速 CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# (可选) GPU加速 CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 2. 准备模型

**重要**: 需要从原项目复制模型文件到 `weights/` 目录：

```bash
# 从 GSE_Detection_Portable 复制模型
copy "D:\Allen\SoftWare\VS Code\Code\Python\GSE_Detection_Portable\weights\gse_detection_v11.pt" ".\weights\"
```

或使用PowerShell:
```powershell
Copy-Item -Path "D:\Allen\SoftWare\VS Code\Code\Python\GSE_Detection_Portable\weights\gse_detection_v11.pt" -Destination ".\weights\"
```

### 3. 测试模型

```bash
# 运行自测脚本（验证环境和模型）
python test_model.py
```

输出示例:
```
╔════════════════════════════════════════════════════════════════╗
║           GSE Detection v11 - Self Test                        ║
╚════════════════════════════════════════════════════════════════╝

🧪 Testing Configuration...
✅ Configuration loaded: ...

✅ All tests passed!
```

### 4. 运行推理

#### 单张图像检测
```bash
python quick_demo.py --image path/to/image.jpg
```

#### 视频检测
```bash
# 处理所有帧
python quick_demo.py --video path/to/video.mp4

# 跳过帧加速处理（每5帧处理1帧）
python quick_demo.py --video path/to/video.mp4 --skip 5

# 保存结果视频
python quick_demo.py --video path/to/video.mp4 --output result.mp4
```

## 📋 模型参数

编辑 `config.py` 调整参数：

```python
# 检测参数
CONFIDENCE_THRESHOLD = 0.25      # 置信度阈值
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

## 🔧 核心API

### GSEDetector 类

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

## 📊 支持的类别

| ID | 类别 | 中文 | 颜色 |
|----|----|------|------|
| 0 | Galley_Truck | 餐车 | 红色 |
| 1 | GSE | 无人地面设备 | 红色 |
| 2 | Ground_Crew | 地勤人员 | 蓝色 |
| 3 | airplane | 飞机 | 绿色 |

## 🎯 特点

✅ **最小化依赖** - 仅需 torch, ultralytics, opencv-python, numpy  
✅ **简洁API** - 易于集成到其他项目  
✅ **CPU/GPU 自动检测** - 自动选择最优设备  
✅ **多格式支持** - 图像、视频推理  
✅ **完整示例** - 包含快速演示和自测脚本  

## 📌 主要文件说明

| 文件 | 说明 |
|------|------|
| `config.py` | 模型配置、类别定义、参数设置 |
| `utils/detection.py` | GSEDetector 检测器类 |
| `quick_demo.py` | 图像/视频推理演示 |
| `test_model.py` | 环境和模型自测 |
| `requirements.txt` | Python依赖列表 |

## ⚙️ 高级配置

### GPU加速

```python
from utils.detection import GSEDetector

# 强制使用CUDA
detector = GSEDetector(device='cuda')

# 强制使用CPU
detector = GSEDetector(device='cpu')

# 自动检测（推荐）
detector = GSEDetector(device=None)
```

### 自定义阈值

```python
from utils.detection import GSEDetector
import config

# 修改全局阈值
config.CONFIDENCE_THRESHOLD = 0.5
config.IOU_THRESHOLD = 0.5

# 单次检测时覆盖
detector = GSEDetector()
results = detector.detect(image, conf_threshold=0.6, iou_threshold=0.6)
```

## 📦 扩展指南

### 添加追踪功能

```python
from utils.detection import GSEDetector

detector = GSEDetector()

# 在循环中使用
for frame in video_frames:
    results = detector.detect(frame)
    detections = detector.get_detections_info(results)
    # 自行实现追踪逻辑
```

### 添加标定功能

参考 `config.py` 中的 `CALIBRATION_POINTS` 和 `PERSPECTIVE_MATRIX` 字段，可以实现透视标定。

## ❓ 常见问题

**Q: 模型文件不存在怎么办？**  
A: 需要从原项目手动复制 `gse_detection_v11.pt` 到 `weights/` 目录。

**Q: 如何提升推理速度？**  
A: 
- 使用 GPU (CUDA)
- 降低输入分辨率 (修改 INPUT_SIZE)
- 跳帧处理 (使用 --skip 参数)
- 使用更小的模型版本

**Q: 如何修改检测阈值？**  
A: 编辑 `config.py` 或在推理时传入参数。

**Q: 支持哪些视频格式？**  
A: OpenCV支持的所有格式 (mp4, avi, mov, mkv等)

## 📞 联系与支持

基于原始项目: `d:\Allen\SoftWare\VS Code\Code\Python\GSE_Detection_Portable`

---

**最后更新**: 2026年1月9日  
**主模型**: gse_detection_v11.pt (YOLOv11)
