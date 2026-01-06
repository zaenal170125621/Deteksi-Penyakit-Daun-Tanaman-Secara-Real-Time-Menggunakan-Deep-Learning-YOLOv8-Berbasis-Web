# Arsitektur Sistem - Deteksi Penyakit Daun Tanaman

## Gambaran Umum

Sistem deteksi penyakit daun tanaman ini dibangun dengan arsitektur modern berbasis web yang menggabungkan:

- **Backend FastAPI**: Server Python ringan untuk menangani deteksi real-time
- **Model YOLOv8**: Model deep learning untuk deteksi penyakit daun
- **Frontend Web**: Antarmuka HTML/CSS/JavaScript untuk akses kamera dan visualisasi
- **Sistem Umpan Balik AI**: Menghasilkan saran dan kritik berbasis kualitas gambar

---

## Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                     BROWSER (CLIENT)                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Camera     │  │  Canvas      │  │   Results    │    │
│  │   Stream     │  │  Detection   │  │   Display    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         app.js (JavaScript Client Logic)             │ │
│  │  - initCamera()                                      │ │
│  │  - detectFrame()                                     │ │
│  │  - captureImage()                                    │ │
│  │  - updateResults()                                   │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST /detect
                            │ (FormData: image blob)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI SERVER (Backend)                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              main.py (Endpoints)                     │ │
│  │  - POST /detect                                      │ │
│  │  - POST /capture                                     │ │
│  │  - GET /gallery                                      │ │
│  │  - GET /captures/{filename}                          │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         yolo_infer.py (Detection Engine)             │ │
│  │  - YOLODetector class                                │ │
│  │  - detect_diseases()                                 │ │
│  │  - green_filter_preprocessing()                      │ │
│  │  - compute_quality_metrics()                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │      feedback.py (AI Feedback Generator)             │ │
│  │  - generate_feedback()                               │ │
│  │  - get_disease_suggestions()                         │ │
│  │  - compute_quality_score()                           │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         YOLOv8 Model (models/best.pt)                │ │
│  │  - Trained on PlantDoc dataset                       │ │
│  │  - 38 disease classes                                │ │
│  │  - Confidence threshold: 0.35                        │ │
│  │  - IoU threshold: 0.5                                │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                             │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │   captures/      │  │    models/       │               │
│  │  - Images        │  │  - best.pt       │               │
│  │  - JSON data     │  │  - yolov8n.pt    │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## Komponen Detail

### 1. **Frontend (Client-Side)**

#### **File: `app/templates/index.html`**
- Menyediakan antarmuka pengguna untuk akses kamera
- Menampilkan hasil deteksi real-time
- Menampilkan umpan balik AI dan metrik kualitas

#### **File: `app/static/app.js`**
- **Fungsi `initCamera()`**: Mengakses webcam pengguna
- **Fungsi `detectFrame()`**: Mengirim frame ke backend untuk deteksi
- **Fungsi `detectionLoop()`**: Loop deteksi kontinu
- **Fungsi `updateResults()`**: Memperbarui UI dengan hasil deteksi
- **Fungsi `captureImage()`**: Menyimpan snapshot dengan deteksi

#### **File: `app/static/styles.css`**
- Responsif untuk desktop dan mobile
- Dark mode dengan aksen hijau
- Animasi untuk transisi yang halus

---

### 2. **Backend (Server-Side)**

#### **File: `app/main.py`**
Endpoint utama:

```python
@app.post("/detect")
async def detect_endpoint(file: UploadFile)
    # Menerima gambar dari client
    # Menjalankan deteksi YOLOv8
    # Menghasilkan umpan balik AI
    # Mengembalikan JSON dengan deteksi dan feedback

@app.post("/capture")
async def capture_endpoint(data: CaptureData)
    # Menyimpan gambar yang ditangkap
    # Menyimpan metadata JSON
    # Mengembalikan konfirmasi

@app.get("/gallery")
async def gallery()
    # Memuat semua tangkapan dari folder
    # Render template gallery.html

@app.get("/captures/{filename}")
async def get_capture(filename: str)
    # Melayani file tangkapan (gambar/JSON)
```

---

#### **File: `app/yolo_infer.py`**
Modul deteksi inti:

```python
class YOLODetector:
    def __init__(self, model_path: str, conf: float, iou: float)
    def detect_diseases(self, image: np.ndarray) -> Dict
```

**Fitur Utama:**
- **Green Filtering**: Pra-pemrosesan untuk fokus pada area vegetasi
  ```python
  def green_filter_preprocessing(image: np.ndarray) -> np.ndarray:
      # Konversi ke HSV
      # Ekstrak saluran hijau
      # Buat mask untuk vegetasi
      # Terapkan mask ke gambar asli
  ```

- **Quality Metrics**: Menghitung metrik kualitas gambar
  ```python
  def compute_quality_metrics(image: np.ndarray) -> Dict:
      # Brightness (kecerahan)
      # Blur detection (deteksi blur)
      # Contrast (kontras)
      # Resolution (resolusi)
  ```

---

#### **File: `app/feedback.py`**
Menghasilkan umpan balik AI cerdas:

```python
def generate_feedback(detections, quality_metrics, width, height) -> Dict:
    # Evaluasi pencahayaan
    # Evaluasi ketajaman
    # Evaluasi tingkat kepercayaan deteksi
    # Evaluasi ukuran bounding box
    # Hasilkan saran spesifik penyakit
```

**Sistem Saran Penyakit:**
- Database 38+ penyakit dengan rekomendasi spesifik
- Saran berbasis konteks (pencahayaan, jarak, fokus)
- Disclaimer profesional untuk konsultasi ahli

---

### 3. **Model Machine Learning**

#### **YOLOv8 Custom Model**
- **File**: `models/best.pt`
- **Dataset**: PlantDoc v1 (resize 416x416)
- **Classes**: 38 kelas penyakit daun
- **Training**: Dilatih dengan `train.py`
- **Hyperparameters**:
  - Confidence threshold: 0.35
  - IoU threshold: 0.5
  - Image size: 416x416

**Kelas Penyakit (Contoh):**
```
- apple_scab_leaf
- tomato_early_blight_leaf
- corn_gray_leaf_spot
- grape_leaf_black_rot
- potato_leaf_early_blight
- ...dan 33 lainnya
```

---

### 4. **Storage & Data Flow**

#### **Folder: `captures/`**
Menyimpan hasil tangkapan:
```
captures/
├── capture_20241229_125149_913945_original.jpg   # Gambar asli
├── capture_20241229_125149_913945_annotated.jpg  # Gambar dengan bbox
└── capture_20241229_125149_913945_data.json      # Metadata deteksi
```

**Format JSON:**
```json
{
  "capture_id": "capture_20241229_125149_913945",
  "timestamp": "2024-12-29T12:51:49.913945",
  "detections": [
    {
      "class_name": "tomato_early_blight_leaf",
      "confidence": 0.87,
      "bbox_xyxy": [120, 150, 340, 380]
    }
  ],
  "quality_metrics": {
    "brightness": 132.5,
    "blur_metric": 87.3,
    "resolution": "640x480"
  },
  "feedback": {
    "critique": [...],
    "suggestions": [...],
    "disclaimer": "..."
  }
}
```

---

## Alur Data Deteksi

```
1. USER mengakses kamera
   ↓
2. JavaScript menangkap frame dari video stream
   ↓
3. Frame dikirim ke /detect endpoint (POST)
   ↓
4. Backend memproses:
   a. Green filtering (opsional)
   b. YOLOv8 inference
   c. Compute quality metrics
   d. Generate AI feedback
   ↓
5. Hasil dikembalikan sebagai JSON
   ↓
6. Frontend menampilkan:
   - Bounding boxes pada canvas
   - Daftar penyakit terdeteksi
   - Skor kepercayaan
   - Kritik dan saran AI
   - Metrik kualitas gambar
```

---

## Teknologi & Dependencies

### **Backend:**
- **FastAPI**: Web framework modern untuk API
- **Ultralytics YOLOv8**: Model deteksi objek
- **OpenCV (cv2)**: Pemrosesan gambar
- **Pillow**: Manipulasi gambar
- **NumPy**: Operasi numerik
- **Uvicorn**: ASGI server

### **Frontend:**
- **Vanilla JavaScript**: Tanpa framework tambahan
- **HTML5 Canvas**: Rendering deteksi
- **WebRTC API**: Akses kamera
- **Fetch API**: Komunikasi HTTP

### **Training:**
- **PyTorch**: Deep learning framework (via Ultralytics)
- **Roboflow**: Augmentasi dataset

---

## Konfigurasi & Environment

### **File: `requirements.txt`**
```
fastapi
uvicorn[standard]
python-multipart
pillow
opencv-python
numpy
ultralytics
jinja2
```

### **File: `.env` (opsional)**
```
MODEL_PATH=models/best.pt
CONFIDENCE_THRESHOLD=0.35
IOU_THRESHOLD=0.5
```

---

## Skalabilitas & Performa

### **Optimasi Saat Ini:**
- Green filtering untuk mengurangi noise
- Threshold confidence yang disesuaikan (0.35)
- Caching model di memori (singleton pattern)

### **Pertimbangan Skalabilitas:**
- **Horizontal scaling**: Deploy multiple FastAPI instances
- **Model serving**: Gunakan TorchServe atau TensorFlow Serving
- **Caching**: Redis untuk caching hasil deteksi
- **Load balancing**: Nginx untuk distribusi traffic
- **Database**: PostgreSQL untuk metadata tangkapan (saat ini file-based)

---

## Security & Privacy

### **Implementasi Saat Ini:**
- File upload size limit (10MB default)
- Image validation (format check)
- Path sanitization untuk mencegah directory traversal

### **Rekomendasi untuk Production:**
- HTTPS dengan SSL/TLS
- Rate limiting untuk API endpoints
- User authentication (OAuth2/JWT)
- CORS configuration yang ketat
- Input sanitization lebih ketat
- Logging dan monitoring (Sentry, Prometheus)

---

## Testing & Quality Assurance

### **Testing Strategy:**
- Unit tests untuk `feedback.py` dan `utils.py`
- Integration tests untuk API endpoints
- Model accuracy testing dengan validation set
- Browser compatibility testing (Chrome, Firefox, Safari)

### **Monitoring:**
- Inference time tracking
- API response time
- Error rate monitoring
- Model confidence distribution

---

## Deployment

### **Development:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Production (contoh dengan Gunicorn):**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Docker (contoh):**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Kontak & Kontribusi

Untuk pertanyaan atau kontribusi, silakan hubungi maintainer atau buat issue di repository.

---

**Terakhir diperbarui**: 29 Desember 2024
