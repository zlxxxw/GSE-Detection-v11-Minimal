import cv2
from ultralytics import YOLO
import os

# 1. 设置
video_path = "data/video_data/*.webm"    # 视频数据路径 (支持通配符)
output_txt = "data/result/my_video.txt" # 结果保存路径
os.makedirs("data/result", exist_ok=True)

# 2. 加载您的训练模型
model = YOLO("weights/best.pt")

# 3. 运行并写入文件
with open(output_txt, 'w') as f:
    # 这里的 tracker 可以是 bytetrack.yaml 或者您自定义的配置文件
    results = model.track(source=video_path, tracker="bytetrack.yaml", persist=True, stream=True)
    
    for frame_idx, r in enumerate(results):
        if r.boxes.id is not None:
            # 提取数据
            boxes = r.boxes.xywh.cpu().numpy()  # 中心点x,y,宽,高 (注意：MOT格式通常需要 左上角x,y)
            track_ids = r.boxes.id.int().cpu().tolist()
            confs = r.boxes.conf.cpu().tolist()

            for box, track_id, conf in zip(boxes, track_ids, confs):
                x_c, y_c, w, h = box
                
                # 转换坐标: xywh (中心) -> xywh (左上角)
                x1 = x_c - w / 2
                y1 = y_c - h / 2
                
                # 写入格式: frame, id, x1, y1, w, h, conf, -1, -1, -1
                # 注意：MOT格式帧数从1开始
                line = f"{frame_idx + 1},{track_id},{x1:.2f},{y1:.2f},{w:.2f},{h:.2f},{conf:.2f},-1,-1,-1\n"
                f.write(line)

print(f"预测结果已保存至 {output_txt}")