# Referensi Command - Deteksi Penyakit Daun Tanaman

## 📋 Daftar Isi

1. [Setup & Installation](#setup--installation)
2. [Running Server](#running-server)
3. [Training Model](#training-model)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Utilities](#utilities)

---

## Setup & Installation

### Install Dependencies

```bash
# Install semua dependencies dari requirements.txt
pip install -r requirements.txt

# Install dengan virtual environment (disarankan)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Install Individual Package

```bash
# FastAPI dan Uvicorn
pip install fastapi uvicorn[standard]

# YOLOv8
pip install ultralytics

# OpenCV
pip install opencv-python

# Image processing
pip install pillow numpy

# Templates
pip install jinja2 python-multipart
```

### Setup Script (Windows)

```powershell
# Jalankan setup otomatis
.\setup.ps1

# Setup dengan parameter
.\setup.ps1 -SkipVenv  # Skip virtual environment creation
```

---

## Running Server

### Development Mode

```bash
# Standard development server dengan auto-reload
python -m uvicorn app.main:app --reload

# Dengan host dan port spesifik
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Dengan logging level
python -m uvicorn app.main:app --reload --log-level debug

# Dengan workers (tidak disarankan untuk development)
python -m uvicorn app.main:app --workers 4
```

### Production Mode

```bash
# Menggunakan Gunicorn (Linux/Mac)
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120

# Dengan access log
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile access.log \
  --error-logfile error.log
```

### Quick Start

```bash
# Cara tercepat untuk memulai
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Akses di browser: **http://localhost:8000**

---

## Training Model

### Basic Training

```bash
# Train dengan default settings (100 epochs, batch 16)
python train.py

# Training akan membuat folder:
# runs/detect/train/
```

### Advanced Training

```python
# Edit train.py untuk custom parameters
model.train(
    data='PlantDoc.v1-resize-416x416.yolov8/data.yaml',
    epochs=150,           # Ubah jumlah epoch
    imgsz=640,            # Ubah ukuran gambar
    batch=32,             # Ubah batch size
    patience=20,          # Early stopping patience
    device=0              # 0 untuk GPU, 'cpu' untuk CPU
)
```

### Resume Training

```python
# Resume dari checkpoint terakhir
model = YOLO('runs/detect/train/weights/last.pt')
model.train(resume=True)
```

### Validation

```bash
# Validate model
yolo val model=models/best.pt data=PlantDoc.v1-resize-416x416.yolov8/data.yaml

# Validate dengan custom confidence
yolo val model=models/best.pt data=PlantDoc.v1-resize-416x416.yolov8/data.yaml conf=0.25
```

### Export Model

```bash
# Export ke ONNX
yolo export model=models/best.pt format=onnx

# Export ke TensorFlow
yolo export model=models/best.pt format=tflite

# Export ke CoreML (Mac)
yolo export model=models/best.pt format=coreml
```

---

## Testing

### Test API Endpoint dengan cURL

```bash
# Test /detect endpoint
curl -X POST "http://localhost:8000/detect" \
  -F "file=@test_image.jpg"

# Test dengan verbose output
curl -v -X POST "http://localhost:8000/detect" \
  -F "file=@test_image.jpg"
```

### Test API dengan Python

```python
import requests

# Test detect endpoint
url = "http://localhost:8000/detect"
files = {"file": open("test_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())

# Test capture endpoint
url = "http://localhost:8000/capture"
data = {
    "capture_id": "test_capture",
    "timestamp": "2024-12-29T12:00:00",
    "original_image": "base64_encoded_image",
    "annotated_image": "base64_encoded_annotated",
    "detections": [],
    "quality_metrics": {},
    "feedback": {}
}
response = requests.post(url, json=data)
print(response.status_code)
```

### Unit Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_feedback.py
```

---

## Deployment

### Docker

```bash
# Build Docker image
docker build -t leaf-detector .

# Run container
docker run -d -p 8000:8000 --name leaf-detector-app leaf-detector

# View logs
docker logs -f leaf-detector-app

# Stop container
docker stop leaf-detector-app

# Remove container
docker rm leaf-detector-app
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./captures:/app/captures
      - ./models:/app/models
    environment:
      - MODEL_PATH=models/best.pt
```

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Systemd Service (Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/leaf-detector.service
```

```ini
[Unit]
Description=Leaf Disease Detector
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/leaf-detector
ExecStart=/opt/leaf-detector/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable leaf-detector
sudo systemctl start leaf-detector
sudo systemctl status leaf-detector
```

---

## Utilities

### Check Python Version

```bash
python --version
# Output: Python 3.10.x atau lebih tinggi
```

### List Installed Packages

```bash
# List semua packages
pip list

# List dengan format freeze
pip freeze

# Save to requirements
pip freeze > requirements.txt
```

### Clean Cache

```bash
# Clean Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clean pip cache
pip cache purge
```

### Check Model Info

```python
from ultralytics import YOLO

# Load model
model = YOLO('models/best.pt')

# Print model info
print(model.info())

# Get class names
print(model.names)
```

### Monitor Server Resources

```bash
# Monitor CPU dan Memory (Linux)
top
htop

# Monitor GPU (NVIDIA)
nvidia-smi
watch -n 1 nvidia-smi

# Monitor network
netstat -tuln | grep 8000
```

### View Logs

```bash
# Server logs (jika di-redirect)
tail -f logs/server.log

# Follow logs real-time
tail -f access.log
tail -f error.log

# Search logs
grep "ERROR" logs/server.log
```

### Database Operations (jika menggunakan DB)

```bash
# Backup captures folder
tar -czvf captures_backup_$(date +%Y%m%d).tar.gz captures/

# Restore backup
tar -xzvf captures_backup_20241229.tar.gz
```

### Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils  # Linux
brew install ab  # Mac

# Test endpoint performance
ab -n 1000 -c 10 http://localhost:8000/

# Load test detect endpoint (dengan file)
# Gunakan tools seperti Locust atau k6
```

---

## Environment Variables

### Set Environment Variables

```bash
# Linux/Mac
export MODEL_PATH=models/best.pt
export CONFIDENCE_THRESHOLD=0.35
export IOU_THRESHOLD=0.5
export CAPTURE_DIR=captures

# Windows (PowerShell)
$env:MODEL_PATH="models/best.pt"
$env:CONFIDENCE_THRESHOLD="0.35"
$env:IOU_THRESHOLD="0.5"
$env:CAPTURE_DIR="captures"

# Windows (CMD)
set MODEL_PATH=models/best.pt
set CONFIDENCE_THRESHOLD=0.35
```

### Using .env File

```bash
# Create .env file
cat > .env << EOF
MODEL_PATH=models/best.pt
CONFIDENCE_THRESHOLD=0.35
IOU_THRESHOLD=0.5
CAPTURE_DIR=captures
HOST=0.0.0.0
PORT=8000
EOF

# Install python-dotenv
pip install python-dotenv

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

---

## Git Operations

### Initialize Repository

```bash
# Initialize git
git init

# Add .gitignore
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
venv/
.env
captures/
runs/
*.pt
!models/best.pt
EOF

# First commit
git add .
git commit -m "Initial commit"
```

### Common Git Commands

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Update detection feedback to Indonesian"

# Push to remote
git push origin main

# Pull latest
git pull origin main
```

---

## Quick Reference

### One-Liner Commands

```bash
# Install dan run dalam satu command
pip install -r requirements.txt && python -m uvicorn app.main:app --reload

# Backup captures dan clean cache
tar -czvf backup.tar.gz captures/ && find . -type d -name "__pycache__" -exec rm -r {} +

# Check server health
curl http://localhost:8000/ && echo "Server OK" || echo "Server Down"

# Quick model validation
yolo val model=models/best.pt data=PlantDoc.v1-resize-416x416.yolov8/data.yaml --verbose
```

---

## Troubleshooting Commands

### Port Already in Use

```bash
# Find process using port 8000 (Linux/Mac)
lsof -i :8000
kill -9 <PID>

# Windows (PowerShell)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Permission Errors

```bash
# Fix file permissions (Linux)
chmod -R 755 .
chmod -R 644 captures/

# Run with sudo (tidak disarankan)
sudo python -m uvicorn app.main:app --host 0.0.0.0 --port 80
```

### Module Not Found

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

---

## Keyboard Shortcuts

### Uvicorn Server
- `Ctrl + C`: Stop server
- `Ctrl + Z`: Suspend (background)
- `fg`: Resume suspended process

### Browser
- `F5`: Refresh page
- `Ctrl + Shift + R`: Hard refresh (clear cache)
- `F12`: Open developer tools
- `Ctrl + Shift + I`: Inspect element

---

**Referensi Lengkap Command untuk Leaf Disease Detector**

**Terakhir diperbarui**: 29 Desember 2024
