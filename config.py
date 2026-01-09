"""
GSE Detection v11 Model Configuration
机场GSE检测模型 v11 配置文件
"""

# ============================================================================
# Model Configuration
# ============================================================================

# Model path
MODEL_PATH = "weights/gse_detection_v11.pt"

# Input size for inference
INPUT_SIZE = 1280

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.25

# IoU threshold for NMS
IOU_THRESHOLD = 0.45

# ============================================================================
# Class Configuration
# ============================================================================

# Class names mapping
CLASS_NAMES = {
    0: "Galley_Truck",      # 餐车
    1: "GSE",               # 地面服务设备 (无人)
    2: "Ground_Crew",       # 地勤人员
    3: "airplane"           # 飞机
}

# Class names in Chinese
CLASS_NAMES_CN = {
    0: "餐车",
    1: "无人地面设备(GSE)",
    2: "地勤人员",
    3: "飞机"
}

# Class colors (BGR format for OpenCV)
CLASS_COLORS = {
    0: (0, 0, 255),      # 餐车 - Red
    1: (0, 0, 255),      # GSE - Red
    2: (255, 0, 0),      # Ground Crew - Blue
    3: (0, 255, 0)       # Airplane - Green
}

# Primary GSE class ID
GSE_CLASS_ID = 1

# ============================================================================
# Device Configuration
# ============================================================================

# Device selection: "cuda", "mps", "cpu", or None for auto-detection
DEVICE = None  # Auto-detect optimal device

# ============================================================================
# Tracking Configuration (Optional)
# ============================================================================

# ByteTrack parameters
TRACK_THRESH = 0.45
TRACK_BUFFER = 30
MATCH_THRESH = 0.8
FRAME_RATE = 30

# ============================================================================
# Calibration Configuration (Optional)
# ============================================================================

# For perspective calibration if needed
CALIBRATION_POINTS = None
PERSPECTIVE_MATRIX = None

# Physical region size (example: 50m x 20m)
PHYSICAL_SIZE = {
    "length": 50.0,  # meters
    "width": 20.0    # meters
}
