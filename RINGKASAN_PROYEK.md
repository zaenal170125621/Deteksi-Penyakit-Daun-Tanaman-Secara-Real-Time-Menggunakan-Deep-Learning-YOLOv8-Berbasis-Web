# Ringkasan Proyek - Deteksi Penyakit Daun Tanaman

## 🌿 Tentang Proyek

**Leaf Disease Detector** adalah aplikasi web berbasis AI untuk mendeteksi penyakit pada daun tanaman secara real-time menggunakan kamera. Sistem ini menggunakan model deep learning YOLOv8 yang telah dilatih pada dataset PlantDoc untuk mengidentifikasi 38+ jenis penyakit daun pada berbagai tanaman.

---

## 🎯 Tujuan Proyek

1. **Deteksi Cepat**: Memberikan deteksi penyakit tanaman secara real-time melalui webcam
2. **Umpan Balik Cerdas**: Menghasilkan saran dan kritik berbasis AI untuk meningkatkan kualitas diagnosis
3. **Aksesibilitas**: Menyediakan tools diagnosis yang mudah diakses untuk petani dan peneliti
4. **Dokumentasi**: Menyimpan history deteksi dengan metadata lengkap untuk analisis lebih lanjut

---

## ✨ Fitur Utama

### 1. **Deteksi Real-Time**
- Stream video langsung dari webcam
- Deteksi penyakit secara kontinu (looping)
- Visualisasi bounding box dan label pada video
- Skor kepercayaan untuk setiap deteksi

### 2. **AI Feedback System**
- Evaluasi kualitas gambar (pencahayaan, ketajaman, resolusi)
- Saran spesifik untuk setiap penyakit terdeteksi
- Kritik konstruktif untuk meningkatkan kualitas capture
- Disclaimer profesional untuk konsultasi ahli

### 3. **Quality Metrics**
- **Brightness (Kecerahan)**: Analisis tingkat pencahayaan
- **Blur Detection (Ketajaman)**: Deteksi gambar blur menggunakan Laplacian variance
- **Contrast (Kontras)**: Evaluasi rentang nilai pixel
- **Resolution (Resolusi)**: Informasi dimensi gambar

### 4. **Image Capture & Gallery**
- Capture snapshot dengan satu klik
- Simpan gambar original dan annotated
- Export metadata dalam format JSON
- Gallery view untuk melihat semua tangkapan
- Download individual captures (image + data)

### 5. **Green Filtering** (Optional)
- Pre-processing untuk fokus pada area vegetasi
- Mengurangi false positives dari background
- Meningkatkan akurasi deteksi pada daun

---

## 🔬 Teknologi yang Digunakan

### **Backend:**
- **FastAPI**: Modern web framework untuk Python
- **YOLOv8**: State-of-the-art object detection model
- **OpenCV**: Computer vision library untuk image processing
- **Pillow**: Python Imaging Library
- **NumPy**: Numerical computing
- **Uvicorn**: ASGI server

### **Frontend:**
- **HTML5**: Struktur halaman
- **CSS3**: Styling dengan dark mode theme
- **JavaScript (Vanilla)**: Client-side logic tanpa framework
- **WebRTC API**: Akses webcam
- **Canvas API**: Drawing bounding boxes

### **Machine Learning:**
- **PyTorch**: Deep learning framework (via Ultralytics)
- **Ultralytics YOLOv8**: Pre-trained model yang di-fine-tune
- **Roboflow**: Dataset augmentation dan preprocessing

---

## 📊 Dataset & Model

### **Dataset: PlantDoc v1**
- **Sumber**: Roboflow Universe
- **Format**: YOLOv8 format
- **Ukuran**: 416x416 pixels (resized)
- **Split**: 
  - Training set
  - Test set
- **Total Classes**: 38+ penyakit daun

### **Model: YOLOv8n (Nano)**
- **Architecture**: YOLOv8 Nano (lightweight)
- **Training**: 100 epochs pada PlantDoc dataset
- **Confidence Threshold**: 0.35
- **IoU Threshold**: 0.5
- **Input Size**: 416x416
- **Model File**: `models/best.pt` (~6MB)

### **Contoh Kelas Penyakit:**
```
✓ Apple Scab
✓ Tomato Early Blight
✓ Tomato Late Blight
✓ Corn Gray Leaf Spot
✓ Grape Black Rot
✓ Potato Early Blight
✓ Bell Pepper Bacterial Spot
✓ Blueberry Leaf
✓ Cherry Leaf
✓ ...dan 29 kelas lainnya
```

---

## 🏗️ Arsitektur Sistem

```
┌─────────────┐
│   Browser   │  ← User Interface (HTML/CSS/JS)
└──────┬──────┘
       │ HTTP POST /detect
       ▼
┌─────────────┐
│  FastAPI    │  ← REST API Server
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  YOLOv8     │  ← Detection Engine
│  Inference  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Feedback   │  ← AI Feedback Generator
│  Generator  │
└─────────────┘
```

**Workflow:**
1. Client captures frame dari webcam
2. Frame dikirim ke `/detect` endpoint
3. Server melakukan pre-processing (optional green filter)
4. YOLOv8 inference untuk deteksi
5. Compute quality metrics
6. Generate AI feedback
7. Hasil dikembalikan sebagai JSON
8. Client render bounding boxes dan display hasil

---

## 📁 Struktur Proyek

```
leaf-detector/
│
├── app/                          # Aplikasi utama
│   ├── __init__.py
│   ├── main.py                   # FastAPI endpoints
│   ├── yolo_infer.py             # YOLOv8 detection logic
│   ├── feedback.py               # AI feedback generator
│   ├── utils.py                  # Helper functions
│   │
│   ├── static/                   # Frontend assets
│   │   ├── app.js                # Client-side JavaScript
│   │   └── styles.css            # CSS styling
│   │
│   └── templates/                # HTML templates
│       ├── index.html            # Main camera page
│       └── gallery.html          # Gallery page
│
├── models/                       # Model weights
│   ├── best.pt                   # Trained YOLOv8 model
│   └── README.md                 # Model documentation
│
├── captures/                     # Saved captures
│   ├── *.jpg                     # Image files
│   └── *.json                    # Metadata files
│
├── runs/                         # Training outputs
│   └── detect/
│       └── train/
│           ├── weights/          # Model checkpoints
│           ├── results.csv       # Training metrics
│           └── args.yaml         # Training config
│
├── PlantDoc.v1-resize-416x416.yolov8/  # Dataset
│   ├── train/
│   ├── test/
│   └── data.yaml
│
├── requirements.txt              # Python dependencies
├── train.py                      # Training script
├── setup.ps1                     # Windows setup script
│
├── README.md                     # Project overview
├── ARSITEKTUR.md                 # Architecture documentation
├── PANDUAN_SINGKAT.md            # Quick start guide
├── PERINTAH.md                   # Command reference
└── RINGKASAN_PROYEK.md           # This file (project summary)
```

---

## 🎨 Antarmuka Pengguna

### **Halaman Kamera (index.html)**
- Header dengan judul dan subtitle
- Tabs navigasi (Kamera / Galeri)
- Video feed dari webcam
- Canvas overlay untuk bounding boxes
- Control buttons:
  - 🔄 Ganti Kamera (jika multiple cameras)
  - ▶️ Mulai Deteksi
  - ⏸️ Berhenti
  - 📸 Tangkap
- Panels:
  - Hasil Deteksi (detected diseases)
  - Umpan Balik AI (critique & suggestions)
  - Penilaian Kualitas (quality assessment)
  - Saran (recommendations)
  - Penafian (disclaimer)
  - Metrik Gambar (image metrics)

### **Halaman Galeri (gallery.html)**
- Grid layout untuk thumbnails
- Setiap card menampilkan:
  - Annotated image
  - Jumlah deteksi
  - Timestamp
  - Quality score
  - Daftar penyakit
  - Download buttons (Original, Detected, JSON)
- Modal untuk detail view
- Filter dan search (future feature)

---

## 🚀 Cara Menggunakan

### **Setup Cepat:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan server
python -m uvicorn app.main:app --reload

# 3. Buka browser
# http://localhost:8000
```

### **Workflow Deteksi:**
1. Akses aplikasi di browser
2. Izinkan akses kamera
3. Klik "Mulai Deteksi"
4. Posisikan daun di depan kamera
5. Lihat hasil real-time
6. Klik "Tangkap" untuk menyimpan (optional)
7. Klik "Berhenti" untuk mengakhiri

---

## 📈 Metrik & Performa

### **Model Performance:**
- **Inference Time**: ~50-100ms per frame (CPU)
- **Inference Time**: ~10-30ms per frame (GPU)
- **Confidence Threshold**: 0.35 (adjustable)
- **IoU Threshold**: 0.5
- **Image Size**: 416x416

### **Quality Thresholds:**
- **Brightness Low**: < 80
- **Brightness High**: > 180
- **Blur Threshold**: < 100 (Laplacian variance)
- **Confidence Low**: < 0.5
- **BBox Area Min**: < 0.05 (5% of frame)
- **BBox Area Max**: > 0.8 (80% of frame)

---

## 🔒 Keamanan & Privacy

### **Implementasi Saat Ini:**
- File upload size limit (default 10MB)
- Image format validation
- Path sanitization untuk file access
- CORS configuration

### **Rekomendasi Production:**
- HTTPS/SSL encryption
- Rate limiting untuk API
- User authentication (OAuth2/JWT)
- Input validation lebih ketat
- Secure headers (HSTS, CSP, etc.)
- Logging dan monitoring
- Regular security audits

---

## 🧪 Testing & Quality Assurance

### **Testing Strategy:**
1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test API endpoints
3. **Model Testing**: Validation set accuracy
4. **Browser Testing**: Cross-browser compatibility
5. **Performance Testing**: Load testing with Apache Bench

### **Quality Metrics:**
- Code coverage: Target 80%+
- API response time: < 200ms (excluding inference)
- Model accuracy: Depends on validation set
- Browser compatibility: Chrome, Firefox, Safari, Edge

---

## 🌐 Deployment Options

### **Local Development:**
```bash
uvicorn app.main:app --reload
```

### **Production (Gunicorn):**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Docker:**
```bash
docker build -t leaf-detector .
docker run -p 8000:8000 leaf-detector
```

### **Cloud Platforms:**
- **Heroku**: `Procfile` + `requirements.txt`
- **AWS EC2**: Deploy dengan systemd service
- **Google Cloud Run**: Containerized deployment
- **Azure App Service**: Python web app

---

## 🔮 Fitur Masa Depan

### **Planned Features:**
1. **Multi-language Support**: English, Indonesian, Spanish, etc.
2. **User Accounts**: Login, saved history, preferences
3. **Database Integration**: PostgreSQL/MongoDB untuk metadata
4. **Advanced Analytics**: Charts, trends, statistics
5. **Mobile App**: React Native atau Flutter
6. **Batch Processing**: Upload multiple images
7. **API Documentation**: Swagger/OpenAPI
8. **Model Versioning**: A/B testing untuk models
9. **Notification System**: Email/SMS alerts
10. **Export Reports**: PDF generation untuk diagnoses

### **Potential Improvements:**
- Improve model accuracy dengan more training data
- Add temporal tracking (track disease progression)
- Integrate dengan weather data untuk predictions
- Support untuk leaf counting
- Multi-disease detection pada single leaf
- Severity level classification (mild, moderate, severe)

---

## 🤝 Kontribusi

### **Cara Berkontribusi:**
1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### **Contribution Guidelines:**
- Follow PEP 8 style guide untuk Python
- Write meaningful commit messages
- Add unit tests untuk new features
- Update documentation
- Ensure all tests pass

---

## 📝 Lisensi

Proyek ini untuk keperluan edukasi. Silakan gunakan dan modifikasi sesuai kebutuhan dengan memberikan credit yang sesuai.

---

## 📞 Kontak & Support

- **Issues**: Gunakan GitHub Issues untuk bug reports
- **Discussions**: GitHub Discussions untuk feature requests
- **Email**: [your-email@example.com]
- **Documentation**: Lihat file ARSITEKTUR.md, PANDUAN_SINGKAT.md, PERINTAH.md

---

## 🙏 Acknowledgments

- **Ultralytics**: Untuk YOLOv8 framework
- **Roboflow**: Untuk PlantDoc dataset
- **FastAPI**: Untuk modern web framework
- **OpenCV**: Untuk computer vision tools
- **Community**: Untuk inspirasi dan feedback

---

## 📚 Referensi

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PlantDoc Dataset](https://github.com/pratikkayal/PlantDoc-Dataset)
- [OpenCV Documentation](https://docs.opencv.org/)
- [WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)

---

**Leaf Disease Detector** - Deteksi Penyakit Daun Tanaman dengan AI

**Version**: 1.0.0  
**Last Updated**: 29 Desember 2024  
**Status**: Active Development
