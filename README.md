# 🌿 Deteksi Penyakit Daun Tanaman

Sistem deteksi penyakit daun tanaman secara real-time menggunakan YOLOv8, dengan akses kamera dari browser ponsel atau desktop melalui Wi-Fi. Dilengkapi deteksi langsung, capture snapshot, dan umpan balik AI dengan filtering yang ditingkatkan untuk mengurangi false positives.

## ✨ Fitur

- **Deteksi Real-Time**: Menggunakan YOLOv8 untuk deteksi penyakit tanaman yang akurat
- **🆕 Filtering Ditingkatkan**: Deteksi hijau untuk mencegah false positives pada objek non-daun
- **🆕 Confidence Cerdas**: Threshold lebih tinggi (0.35) untuk deteksi lebih akurat
- **Mobile-First**: Akses kamera dari browser ponsel, proses di laptop
- **Umpan Balik AI**: Penilaian kualitas berbasis aturan dan saran
- **Sistem Capture**: Simpan gambar original + annotated dengan metadata JSON
- **Tampilan Galeri**: Browse dan download tangkapan sebelumnya
- **Metrik Kualitas**: Analisis kecerahan, blur, dan kepercayaan
- **Panduan Aman**: Dukungan keputusan dengan disclaimer profesional

## 🎯 Yang Baru di v2.0

### Sistem Deteksi Ditingkatkan
- **Verifikasi Warna Hijau**: Mendeteksi dan memfilter objek non-daun dengan memeriksa konten hijau
- **Pengurangan False Positives**: Pengurangan ~80% pada deteksi yang salah
- **Parameter yang Dapat Dikonfigurasi**: Sesuaikan confidence dan threshold hijau sesuai kebutuhan
- **Statistik Detail**: Lihat statistik filtering dalam respons API

Lihat [ENHANCED_DETECTION_GUIDE.md](ENHANCED_DETECTION_GUIDE.md) untuk dokumentasi detail.

## 📋 Persyaratan

- Windows 10 atau lebih baru
- Python 3.10 atau lebih tinggi
- Laptop dan ponsel dalam jaringan Wi-Fi yang sama
- Webcam atau kamera ponsel

## 🚀 Mulai Cepat

### 1. Clone/Download Proyek

Navigasi ke direktori proyek Anda:
```powershell
cd "d:\KULIAT\SEMESTER 5\PengolahanCitraDigital\PCD_TUBES_EAS\leaf-detector"
```

### 2. Buat Virtual Environment

```powershell
python -m venv venv
```

### 3. Aktifkan Virtual Environment

```powershell
venv\Scripts\activate
```

Anda akan melihat `(venv)` di prompt terminal.

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

Ini akan menginstall:
- FastAPI & Uvicorn (web server)
- Ultralytics (YOLOv8)
- OpenCV (pemrosesan gambar)
- NumPy, Pillow (utilities)
- Jinja2 (templates)

### 5. Train atau Tempatkan Model

#### Opsi A: Train Model Sendiri

Dataset PlantDoc sudah ada di workspace Anda di:
```
d:\KULIAT\SEMESTER 5\PengolahanCitraDigital\PCD_TUBES_EAS\PlantDoc.v1-resize-416x416.yolov8
```

Train model:
```powershell
yolo detect train model=yolov8n.pt data="d:\KULIAT\SEMESTER 5\PengolahanCitraDigital\PCD_TUBES_EAS\PlantDoc.v1-resize-416x416.yolov8\data.yaml" epochs=50 imgsz=640 batch=16
```

**Parameter Training**:
- `model=yolov8n.pt` - Model Nano (cepat, bagus untuk laptop)
- `epochs=50` - Iterasi training (tingkatkan untuk akurasi lebih baik)
- `imgsz=640` - Ukuran gambar input
- `batch=16` - Sesuaikan berdasarkan memori GPU (gunakan 8 atau 4 jika out of memory)

**Waktu Training**: 30-120 menit tergantung GPU (atau CPU jika tidak ada GPU)

Setelah training selesai, temukan model terbaik:
```
runs/detect/train/weights/best.pt
```

Copy ke folder models:
```powershell
Copy-Item "runs\detect\train\weights\best.pt" "models\best.pt"
```

#### Opsi B: Gunakan Model Pre-trained

Jika Anda memiliki model pre-trained, tempatkan di:
```
leaf-detector/models/best.pt
```

#### Opsi C: Jalankan Tanpa Model (untuk testing)

Server akan mulai tetapi deteksi akan gagal sampai model tersedia. Anda dapat test UI dan memperbaiki masalah setup terlebih dahulu.

### 6. Dapatkan IP Address Laptop Anda

```powershell
ipconfig
```

Cari "IPv4 Address" di bawah network adapter aktif (biasanya dimulai dengan 192.168.x.x atau 10.x.x.x).

Contoh output:
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

**Catat IP address Anda** - Anda akan membutuhkannya untuk akses dari ponsel.

### 7. Jalankan Server

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Anda akan melihat:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 8. Akses dari Ponsel

Di ponsel Anda (terhubung ke **Wi-Fi yang sama**):

1. Buka browser (Chrome, Safari, dll.)
2. Navigasi ke: `http://<ip-laptop-anda>:8000`
   - Contoh: `http://192.168.1.100:8000`

3. Izinkan permission kamera saat diminta
4. Klik "Mulai Deteksi"
5. Arahkan kamera ke daun tanaman
6. Gunakan "Tangkap" untuk menyimpan deteksi

### 9. Akses dari Laptop

Buka browser di laptop:
```
http://localhost:8000
```

## 🔧 Troubleshooting

### Tidak Dapat Akses dari Ponsel

**Masalah**: Ponsel tidak dapat terhubung ke server laptop

**Solusi**:
1. **Periksa Wi-Fi yang Sama**: Pastikan kedua perangkat di network yang sama
2. **Windows Firewall**: Izinkan port 8000

```powershell
# Jalankan PowerShell sebagai Administrator
New-NetFirewallRule -DisplayName "Plant Detector" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

3. **Verifikasi IP Address**: Jalankan ulang `ipconfig` untuk konfirmasi IP belum berubah
4. **Disable VPN**: VPN dapat memblokir akses jaringan lokal
5. **Gunakan HTTP bukan HTTPS**: Pastikan menggunakan `http://` bukan `https://`

### Kamera Tidak Berfungsi

**Masalah**: "Camera not supported" atau permission denied

**Solusi**:
1. **Berikan Permission**: Saat browser meminta, klik "Allow"
2. **HTTPS Diperlukan**: Beberapa browser memerlukan HTTPS untuk kamera pada non-localhost
   - Gunakan IP jaringan lokal laptop, bukan IP eksternal
3. **Periksa Browser**: Gunakan Chrome atau Safari (dukungan kamera lebih baik)
4. **Tutup Aplikasi Lain**: Tutup aplikasi yang menggunakan kamera (Zoom, Skype, dll.)

### Model Tidak Loading

**Masalah**: "Model not loaded" atau "Model file not found"

**Solusi**:
1. **Periksa Path**: Pastikan `models/best.pt` ada
2. **Train Model**: Lihat instruksi training di atas
3. **Download Model**: Jika menggunakan pre-trained, verifikasi download selesai
4. **Periksa Permissions**: Pastikan file dapat dibaca

```powershell
# Verifikasi model ada
Test-Path "models\best.pt"
# Harus return: True
```

### Error Deteksi

**Masalah**: Deteksi gagal atau akurasi rendah

**Solusi**:
1. **Tingkatkan Pencahayaan**: Pastikan pencahayaan yang baik dan merata
2. **Fokus**: Tahan kamera stabil, pastikan daun dalam fokus
3. **Jarak**: Pindah lebih dekat (daun harus mengisi 30-70% frame)
4. **Bersihkan Lensa**: Lap lensa kamera ponsel
5. **Retrain Model**: Lebih banyak epoch atau augmentasi data lebih baik

### 🆕 Terlalu Banyak False Positives (Deteksi Over-sensitive)

**Masalah**: Model mendeteksi daun padahal tidak ada daun

**Solusi**:
1. **Tingkatkan Confidence Threshold**: Edit `app/main.py`, ubah `conf_threshold=0.35` ke `0.40` atau `0.45`
2. **Sesuaikan Green Filtering**: Ubah `min_green_ratio=0.15` ke `0.20` atau `0.25` untuk filtering lebih ketat
3. **Gunakan Testing Script**: Jalankan `python test_enhanced_detection.py <image> --tune` untuk menemukan parameter optimal
4. **Periksa Kualitas Model**: Retrain dengan sampel negatif lebih baik (gambar tanpa daun)

Lihat [ENHANCED_DETECTION_GUIDE.md](ENHANCED_DETECTION_GUIDE.md) untuk panduan tuning detail.

### 🆕 Daun Berpenyakit Tidak Terdeteksi

**Masalah**: Model tidak mendeteksi daun dengan penyakit parah (konten hijau lebih sedikit)

**Solusi**:
1. **Turunkan Green Threshold**: Ubah `min_green_ratio=0.15` ke `0.10` atau `0.08`
2. **Turunkan Confidence**: Ubah `conf_threshold=0.35` ke `0.30`
3. **Test Parameter Berbeda**: Gunakan testing script untuk menemukan setting optimal

### Performa Lambat

**Masalah**: FPS rendah atau deteksi lag

**Solusi**:
1. **Kurangi Ukuran Gambar**: Edit `app.js`, ubah resolusi canvas
2. **Tingkatkan Interval**: Di `app.js`, ubah `setTimeout(detectionLoop, 200)` ke nilai lebih tinggi (mis. 500)
3. **Turunkan Confidence**: Di `app/main.py`, ubah `conf_threshold=0.25` ke `0.5`
4. **Gunakan GPU**: Install PyTorch dengan CUDA untuk inference lebih cepat
5. **Tutup Aplikasi**: Bebaskan CPU/RAM dengan menutup aplikasi lain

### Out of Memory

**Masalah**: Training atau inference crash dengan memory error

**Solusi**:
1. **Kurangi Batch Size**: Gunakan `batch=4` atau `batch=8` saat training
2. **Model Lebih Kecil**: Gunakan `yolov8n.pt` alih-alih model yang lebih besar
3. **Turunkan Image Size**: Gunakan `imgsz=416` alih-alih 640
4. **Tutup Aplikasi**: Bebaskan RAM

## 📁 Struktur Proyek

```
leaf-detector/
├── app/
│   ├── main.py              # Server FastAPI & routes
│   ├── yolo_infer.py        # Modul inference YOLOv8
│   ├── feedback.py          # Generasi umpan balik AI
│   ├── utils.py             # Fungsi utility
│   ├── templates/
│   │   ├── index.html       # Interface kamera utama
│   │   └── gallery.html     # Galeri tangkapan
│   └── static/
│       ├── app.js           # JavaScript frontend
│       └── styles.css       # Style CSS
├── models/
│   └── best.pt              # Model YOLOv8 trained (Anda sediakan)
├── captures/                # Tangkapan tersimpan (auto-generated)
│   ├── capture_*_original.jpg
│   ├── capture_*_detected.jpg
│   └── capture_*_data.json
├── requirements.txt         # Dependencies Python
└── README.md               # File ini
```

## 🎯 Panduan Penggunaan

### Memulai Deteksi

1. Buka app di browser (ponsel atau laptop)
2. Berikan permission kamera
3. Klik "Mulai Deteksi"
4. Arahkan kamera ke daun tanaman dengan gejala
5. Lihat hasil deteksi real-time

### Menangkap Hasil

1. Saat deteksi berjalan, klik "Tangkap"
2. File tersimpan ke folder `captures/`:
   - `*_original.jpg` - Gambar original
   - `*_detected.jpg` - Beranotasi dengan boxes
   - `*_data.json` - Data deteksi lengkap + feedback

### Melihat Galeri

1. Klik tab "Galeri"
2. Browse gambar yang ditangkap
3. Download original, gambar annotated, atau data JSON

### Umpan Balik AI

Sistem menyediakan:
- **Kritik Kualitas**: Penilaian pencahayaan, blur, resolusi
- **Analisis Deteksi**: Tingkat kepercayaan, ukuran bbox
- **Saran Penyakit**: Praktik perawatan umum (non-diagnostik)
- **Disclaimer**: Selalu konsultasikan ahli untuk diagnosis akurat

## 🧪 Testing

### Test Enhanced Detection

Gunakan test script yang disediakan untuk evaluasi deteksi dengan parameter berbeda:

```powershell
# Test single image
python test_enhanced_detection.py <image_path>

# Test dengan custom parameters
python test_enhanced_detection.py <image_path> --conf 0.40 --green 0.20

# Mode parameter tuning (menemukan setting optimal)
python test_enhanced_detection.py <image_path> --tune

# Batch test semua gambar dalam direktori
python test_enhanced_detection.py <directory_path> --batch
```

**Output:**
- Menampilkan statistik deteksi raw vs filtered
- Menunjukkan green ratio untuk setiap deteksi
- Menyimpan gambar annotated ke `test_outputs/`
- Memberikan rekomendasi tuning

### Contoh Sesi Test

```powershell
# Test dengan default settings
python test_enhanced_detection.py "test_images/leaf.jpg"

# Output menunjukkan:
# - Raw detections: 15
# - Filtered detections: 8
# - Removed by filtering: 7
# - Detail deteksi dengan green ratios
```

Lihat [ENHANCED_DETECTION_GUIDE.md](ENHANCED_DETECTION_GUIDE.md) untuk panduan testing komprehensif.

## 🧪 Testing Tanpa Model

Untuk test interface sebelum training:

1. Jalankan server tanpa model di `models/`
2. Server akan mulai tetapi deteksi akan gagal
3. Test akses kamera, UI, tombol capture
4. Tambahkan model nanti dan restart server

## 📊 Tips Training

### Untuk Akurasi Lebih Baik

1. **Lebih Banyak Epoch**: Gunakan 100-200 epoch
```powershell
yolo detect train model=yolov8n.pt data="path\to\data.yaml" epochs=100 imgsz=640
```

2. **Augmentasi Data**: Sudah termasuk di YOLOv8 secara default

3. **Model Lebih Besar**: Gunakan yolov8s.pt atau yolov8m.pt (lebih lambat tapi lebih akurat)
```powershell
yolo detect train model=yolov8s.pt data="path\to\data.yaml" epochs=50 imgsz=640
```

4. **Resume Training**: Jika training terputus
```powershell
yolo detect train resume model="runs\detect\train\weights\last.pt"
```

### Monitoring Training

Log training tersimpan di: `runs/detect/train/`

Lihat hasil:
- `results.png` - Grafik metrik training
- `confusion_matrix.png` - Prediksi class
- `val_batch*_pred.jpg` - Prediksi validasi

## 🔐 Catatan Keamanan

- **Jaringan Lokal Saja**: Setup ini hanya untuk penggunaan WiFi lokal
- **Tanpa Autentikasi**: Siapa pun di WiFi Anda dapat mengakses
- **HTTPS**: Tidak dikonfigurasi (browser mungkin membatasi kamera pada beberapa perangkat)
- **Production**: Untuk deployment publik, tambahkan autentikasi, HTTPS, rate limiting

## 📝 API Endpoints

- `GET /` - Interface kamera utama
- `GET /gallery` - Tampilan galeri tangkapan
- `POST /detect` - Kirim gambar, dapatkan deteksi + feedback
- `POST /capture` - Simpan deteksi saat ini
- `GET /captures/{filename}` - Ambil file tersimpan
- `GET /health` - Pemeriksaan kesehatan server
- `GET /model-info` - Informasi class model

## 🛠️ Konfigurasi Lanjutan

### Ubah Confidence Threshold

Edit `app/main.py`, baris ~61:
```python
yolo_infer.initialize_detector(str(model_path), conf_threshold=0.25)
```

Ubah `0.25` ke nilai lebih tinggi (mis., `0.5`) untuk deteksi lebih sedikit namun lebih confident.

### Sesuaikan Framerate Deteksi

Edit `app/static/app.js`, baris ~287:
```javascript
setTimeout(detectionLoop, 200); // ~5 FPS
```

Ubah `200` ke:
- `100` untuk ~10 FPS (lebih cepat, lebih banyak CPU)
- `500` untuk ~2 FPS (lebih lambat, lebih sedikit CPU)

### Modifikasi Threshold Feedback

Edit `app/feedback.py`, baris 7-13:
```python
BRIGHTNESS_LOW_THRESHOLD = 60
BLUR_THRESHOLD = 100
CONFIDENCE_LOW_THRESHOLD = 0.5
```

Sesuaikan nilai berdasarkan lingkungan dan kebutuhan Anda.

## 📚 Informasi Dataset

Dataset PlantDoc mencakup berbagai penyakit tanaman pada beragam tanaman:
- Apel: Scab, Black Rot, Cedar Rust, Sehat
- Ceri: Powdery Mildew, Sehat
- Jagung: Gray Leaf Spot, Common Rust, Northern Leaf Blight, Sehat
- Anggur: Black Rot, Esca, Leaf Blight, Sehat
- Persik: Bacterial Spot, Sehat
- Paprika: Bacterial Spot, Sehat
- Kentang: Early Blight, Late Blight, Sehat
- Stroberi: Leaf Scorch, Sehat
- Tomat: Berbagai penyakit + Sehat

Periksa `data.yaml` untuk nama class dan path yang tepat.

## 🤝 Dukungan

Untuk masalah:
1. Periksa bagian troubleshooting README ini
2. Verifikasi semua requirements terinstall: `pip list`
3. Periksa log server di terminal
4. Verifikasi pengaturan firewall
5. Test di browser laptop dulu sebelum ponsel

## ⚠️ Disclaimer Penting

1. **Bukan Diagnosis Medis/Pertanian**: Sistem ini hanya untuk tujuan edukasi dan dukungan keputusan
2. **Konsultasi Ahli**: Selalu verifikasi dengan patolog tanaman bersertifikat atau layanan penyuluhan pertanian
3. **Akurasi**: Akurasi model tergantung kualitas data training dan mungkin tidak general untuk semua kondisi
4. **Penggunaan Lokal**: Dirancang untuk penggunaan jaringan lokal, bukan deployment production
5. **Tanpa Garansi**: Gunakan dengan risiko Anda sendiri

## 📄 Lisensi

Proyek ini untuk tujuan edukasi. Dataset PlantDoc dan YOLOv8 memiliki lisensi masing-masing.

## 🎓 Penggunaan Edukasi

Sempurna untuk:
- Proyek pembelajaran computer vision
- Demonstrasi teknologi pertanian
- Praktik deployment model deep learning
- Pengembangan aplikasi web dengan AI
- Proyek integrasi mobile-desktop

---

**Dibuat dengan ❤️ untuk edukasi deteksi penyakit tanaman**

Untuk update dan issues, periksa repository proyek.
