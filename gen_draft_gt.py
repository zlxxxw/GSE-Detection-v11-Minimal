import cv2
from ultralytics import YOLO
import os

# --- 配置区域 ---
video_path = r"H:\GSE论文资料\实验\video_data\*.webm"   # 视频数据路径 (支持通配符)
output_gt  = "data/result/draft_gt.txt" # 输出的草稿文件
model_path = "weights/gse_detection_v11.pt"       # 你的模型
# ----------------

model = YOLO(model_path)

# 打开文件准备写入 (DarkLabel 识别格式: frame_id, target_id, x, y, w, h)
# 注意：DarkLabel 的帧号通常从 0 开始，但 MOT 评测标准从 1 开始。
# 这里我们先按 MOT 标准生成，导入 DarkLabel 时它会自动处理。
with open(output_gt, 'w') as f:
    # 启用 ByteTrack，调低阈值以防漏检 (conf=0.1)
    results = model.track(source=video_path, tracker="bytetrack.yaml", 
                          persist=True, conf=0.1, stream=True)
    
    for frame_idx, r in enumerate(results):
        if r.boxes.id is not None:
            boxes = r.boxes.xywh.cpu().numpy()
            track_ids = r.boxes.id.int().cpu().tolist()
            
            for box, track_id in zip(boxes, track_ids):
                x_c, y_c, w, h = box
                # 转为左上角坐标
                x1 = int(x_c - w / 2)
                y1 = int(y_c - h / 2)
                w = int(w)
                h = int(h)
                
                # 写入格式: frame_id, track_id, x, y, w, h
                # 这里的 track_id 是模型预测的，可能不准，后续人工修
                line = f"{frame_idx},{track_id},{x1},{y1},{w},{h}\n"
                f.write(line)

print(f"预标注完成！文件已保存至: {output_gt}")