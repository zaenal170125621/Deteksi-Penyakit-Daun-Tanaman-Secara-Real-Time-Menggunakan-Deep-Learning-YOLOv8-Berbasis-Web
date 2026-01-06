# Models Directory

Place your trained YOLOv8 model here as `best.pt`.

## Training the Model

Navigate to the leaf-detector directory and run:

```powershell
yolo detect train model=yolov8n.pt data="d:\KULIAT\SEMESTER 5\PengolahanCitraDigital\PCD_TUBES_EAS\PlantDoc.v1-resize-416x416.yolov8\data.yaml" epochs=50 imgsz=640 batch=16
```

After training completes, copy the best model:

```powershell
Copy-Item "runs\detect\train\weights\best.pt" "models\best.pt"
```

## Model File

Expected file: `best.pt` (YOLO format, .pt extension)

The server will check for this file on startup. If not found, detection will fail but the UI will still be accessible for testing.

## Alternative Models

You can use different YOLOv8 variants:
- `yolov8n.pt` - Nano (fastest, least accurate)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (slower, more accurate)
- `yolov8l.pt` - Large (slowest, most accurate)
- `yolov8x.pt` - Extra Large (requires powerful GPU)

For laptop use, `yolov8n` or `yolov8s` recommended.
