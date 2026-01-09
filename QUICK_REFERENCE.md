# 快速参考卡片

## 🚀 一句话启动

```bash
# 一键处理所有视频！
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"
```

---

## 📋 两个脚本对比

### save_tracks.py - 仅提取追踪信息
```bash
python save_tracks.py --video "H:\video_data"
# 输出: data/result/video_01.txt, video_02.txt, ...
```

**特点：**
- ✅ 批量处理多个视频
- ✅ 帧号自动重置 (每个视频从 1 开始)
- ✅ 文件名与视频同名
- ✅ 保存到统一目录 `data/result/`

---

### gen_draft_gt.py - 生成草稿标注 (推荐)
```bash
# 单个文件
python gen_draft_gt.py --video "video.webm"

# 整个目录 (推荐)
python gen_draft_gt.py --video "H:\video_data"

# 强制覆盖已存在文件
python gen_draft_gt.py --video "H:\video_data" --force
```

**特点：**
- ✅ 支持文件和目录两种模式
- ✅ 自动跳过已存在的 `_gt.txt` 文件
- ✅ 输出文件保存在视频同一目录
- ✅ 帧号从 1 开始

---

## 🔑 关键参数

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| `--video` | - | - | 输入视频路径或目录 (必需) |
| `--conf` | 0.1 | 0.0-1.0 | 置信度阈值 (越低越敏感) |
| `--force` | False | - | gen_draft_gt: 强制覆盖 |
| `--output` | 同名 | - | gen_draft_gt: 自定义输出路径 (单文件模式) |
| `--model` | config.MODEL_PATH | - | 自定义模型路径 |

---

## ⚠️ 常见错误修正

```python
# ❌ 错误: Windows 路径没有转义
"H:\GSE论文资料\实验\video_data"  # \t 会被解析为 Tab!

# ✅ 正确: 使用原始字符串
r"H:\GSE论文资料\实验\video_data"

# ✅ 正确: 或使用正斜杠
"H:/GSE论文资料/实验/video_data"
```

---

## 📊 输出文件示例

```txt
1,1,100.50,200.50,50.00,80.00,0.85,0,-1,-1
1,2,300.00,250.50,60.00,90.00,0.92,1,-1,-1
2,1,105.50,205.00,50.50,80.20,0.86,0,-1,-1
2,2,305.00,255.00,59.50,89.50,0.91,1,-1,-1
3,1,110.50,210.00,50.80,80.50,0.84,0,-1,-1
```

**字段解释：**
```
frame_idx, track_id, x1, y1, w, h, conf, class_id, -1, -1
  帧号      追踪ID   左x  左y  宽  高   置信度   类别    占位符  占位符
```

---

## 🎯 工作流示例

### 场景 1: 批量生成初版标注

```bash
cd d:\Allen\SoftWare\VS Code\Code\Python\GSE_Detection_v11_Minimal

# 一键处理视频目录
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"

# ✅ 所有 _gt.txt 文件已生成，保存在各视频所在目录

# 在标注工具 (DarkLabel) 中打开 .txt 文件进行人工修正
```

### 场景 2: 重新处理部分视频

```bash
# 对失败的视频重新处理 (跳过已成功的)
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data"

# ✅ 自动跳过已存在的 _gt.txt 文件
```

### 场景 3: 覆盖之前的标注

```bash
# 重新生成所有 _gt.txt (覆盖之前版本)
python gen_draft_gt.py --video "H:\GSE论文资料\实验\video_data" --force

# ⚠️ 注意：这会覆盖之前的文件！
```

### 场景 4: 调整置信度重新标注

```bash
# 增加置信度 (减少误检，可能增加漏检)
python gen_draft_gt.py --video "H:\video_data" --conf 0.2 --force

# 降低置信度 (减少漏检，可能增加误检)
python gen_draft_gt.py --video "H:\video_data" --conf 0.05 --force
```

---

## 🔧 环境检查

```bash
# 检查 Python 版本
python --version
# 应该是 3.11 或更高

# 检查 CUDA (可选，用于 GPU 加速)
python -c "import torch; print(torch.cuda.is_available())"

# 检查模型文件
dir weights\gse_detection_v11.pt

# 检查视频目录
dir "H:\GSE论文资料\实验\video_data"
```

---

## 📞 故障排除

### 问题: 找不到视频文件
```bash
# 检查路径是否正确
python -c "from pathlib import Path; print(Path(r'H:\GSE论文资料\实验\video_data').exists())"
# 应该返回 True

# 列出目录下的文件
dir "H:\GSE论文资料\实验\video_data"
```

### 问题: 模型加载失败
```bash
# 检查模型文件
ls -la weights/gse_detection_v11.pt

# 确保文件大小合理 (通常 > 100MB)
# 如果不存在，从其他项目复制
```

### 问题: MOT 格式错误
```bash
# 打开输出的 .txt 文件检查
# 应该有 10 列，逗号分隔，浮点数 2 位小数
# 第 1 列应该是 1, 2, 3, ... (从 1 开始)
```

---

## 💡 提示

- **置信度 0.1** 是标注任务的推荐值 (减少漏检)
- **使用 --force 前备份** 重要的人工修正
- **分次处理** 避免一次处理过多文件导致内存溢出
- **定期提交** git 以便恢复误操作

---

**最后更新：2026-01-09**
