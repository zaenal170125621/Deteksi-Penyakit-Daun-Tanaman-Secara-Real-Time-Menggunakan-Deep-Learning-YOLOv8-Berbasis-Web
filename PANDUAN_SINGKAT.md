# Panduan Singkat - Deteksi Penyakit Daun Tanaman

## 🚀 Mulai Cepat

### Prasyarat
- Python 3.8 atau lebih tinggi
- Webcam atau kamera (untuk deteksi real-time)
- Browser modern (Chrome, Firefox, Safari, Edge)

---

## 📦 Instalasi

### 1. Clone atau Download Repository
```bash
cd leaf-detector
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies utama:**
- FastAPI
- Ultralytics (YOLOv8)
- OpenCV
- Pillow
- NumPy

### 3. Verifikasi Model
Pastikan file model ada:
```
models/best.pt
```

Jika belum ada, Anda perlu melatih model terlebih dahulu (lihat bagian Training).

---

## ▶️ Menjalankan Aplikasi

### Menggunakan PowerShell Script (Windows - Rekomendasi)
```powershell
.\setup.ps1
```

Script ini akan:
- Memeriksa instalasi Python
- Membuat virtual environment
- Install dependencies
- Menjalankan server

### Manual
```bash
# Aktifkan virtual environment (opsional tapi disarankan)
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Jalankan server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌐 Mengakses Aplikasi

1. Buka browser Anda
2. Navigasi ke: **http://localhost:8000**
3. Izinkan akses kamera saat diminta
4. Mulai deteksi!

---

## 📱 Cara Menggunakan

### 1. **Halaman Kamera (Home)**

#### Langkah-langkah:
1. **Klik "Mulai Deteksi"**
   - Kamera akan aktif
   - Deteksi real-time dimulai

2. **Posisikan Daun**
   - Tahan daun di depan kamera
   - Pastikan pencahayaan cukup
   - Fokus pada area yang terinfeksi

3. **Lihat Hasil Real-Time**
   - Bounding box muncul pada penyakit
   - Skor kepercayaan ditampilkan
   - Umpan balik AI muncul di panel kanan

4. **Tangkap Gambar** (opsional)
   - Klik tombol "Tangkap"
   - Gambar disimpan dengan metadata
   - Dapat diakses di halaman Galeri

5. **Berhenti Deteksi**
   - Klik "Berhenti" untuk menghentikan

---

### 2. **Halaman Galeri**

#### Melihat Tangkapan Tersimpan:
- Klik tab **"Galeri"** di navigasi
- Lihat semua deteksi yang telah ditangkap
- Setiap tangkapan menampilkan:
  - Gambar beranotasi
  - Jumlah deteksi
  - Timestamp
  - Skor kualitas
  - Daftar penyakit terdeteksi

#### Download Data:
- **📥 Asli**: Download gambar original
- **📥 Terdeteksi**: Download gambar dengan bounding box
- **📄 JSON**: Download metadata lengkap

---

## 🎯 Tips Penggunaan

### Untuk Hasil Terbaik:

#### 1. **Pencahayaan**
- ✅ Gunakan cahaya natural atau lampu putih terang
- ❌ Hindari backlight atau cahaya terlalu terang
- ⚠️ Jangan terlalu gelap (brightness < 80)

#### 2. **Fokus**
- ✅ Tahan kamera steady
- ✅ Fokuskan pada daun
- ❌ Hindari gerakan blur

#### 3. **Jarak**
- ✅ 15-30 cm dari kamera (ideal)
- ❌ Terlalu jauh: deteksi kecil dan kurang akurat
- ❌ Terlalu dekat: memotong bagian penting

#### 4. **Framing**
- ✅ Daun mengisi 50-70% frame
- ✅ Fokus pada area yang terinfeksi
- ❌ Hindari background yang ramai

#### 5. **Kualitas Gambar**
- ✅ Gunakan resolusi tinggi jika tersedia
- ✅ Pastikan daun terlihat jelas
- ❌ Hindari overexposure

---

## 📊 Memahami Hasil

### **Panel Deteksi**
```
Penyakit Terdeteksi:
┌────────────────────────────────────┐
│ tomato_early_blight_leaf           │
│ Kepercayaan: 87.3%                 │
└────────────────────────────────────┘
```

### **Umpan Balik AI**
```
Penilaian Kualitas:
✓ Pencahayaan memadai (kecerahan: 132/255)
✓ Ketajaman gambar dapat diterima (skor: 87.3)
✓ Deteksi ditemukan dengan kepercayaan hingga 87%
```

### **Saran**
```
📋 Untuk tomato_early_blight_leaf:
  • Buang daun bawah yang terinfeksi
  • Mulsa untuk mencegah percikan tanah
  • Aplikasikan fungisida secara preventif
  • Pastikan jarak tanam yang memadai
```

### **Penafian**
⚠️ **PENTING**: Sistem ini hanya dukungan keputusan, BUKAN pengganti diagnosis profesional. Selalu konsultasikan dengan:
- Layanan penyuluhan pertanian
- Patolog tanaman bersertifikat
- Agronom profesional

---

## 🛠️ Training Model (Opsional)

Jika Anda ingin melatih model dengan dataset sendiri:

### 1. **Siapkan Dataset**
```
PlantDoc.v1-resize-416x416.yolov8/
├── train/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```

### 2. **Jalankan Training**
```bash
python train.py
```

Training akan:
- Memuat dataset PlantDoc
- Melatih YOLOv8n untuk 100 epochs
- Menyimpan model terbaik ke `runs/detect/train/weights/best.pt`
- Generate metrics dan visualizations

### 3. **Gunakan Model Baru**
```bash
# Copy model ke folder models
copy runs\detect\train\weights\best.pt models\best.pt
```

---

## 🔧 Troubleshooting

### **Masalah: Kamera tidak muncul**
- Periksa izin browser untuk akses kamera
- Tutup aplikasi lain yang menggunakan kamera
- Coba refresh halaman (F5)
- Gunakan HTTPS jika di production

### **Masalah: "Camera not ready"**
- Tunggu beberapa detik untuk inisialisasi
- Periksa koneksi webcam
- Restart browser

### **Masalah: Deteksi tidak muncul**
- Pastikan ada daun dalam frame
- Periksa pencahayaan
- Pastikan daun menunjukkan gejala penyakit
- Confidence threshold: 0.35 (bisa disesuaikan)

### **Masalah: Server error**
- Periksa log di terminal
- Pastikan semua dependencies terinstall
- Verifikasi model file ada (`models/best.pt`)
- Restart server

### **Masalah: Performa lambat**
- Kurangi resolusi kamera
- Tutup aplikasi lain yang berat
- Gunakan GPU jika tersedia (CUDA)

---

## 📁 Struktur File Penting

```
leaf-detector/
├── app/
│   ├── main.py              # FastAPI server
│   ├── yolo_infer.py        # Deteksi YOLOv8
│   ├── feedback.py          # AI feedback generator
│   ├── static/
│   │   ├── app.js           # Client logic
│   │   └── styles.css       # Styling
│   └── templates/
│       ├── index.html       # Halaman kamera
│       └── gallery.html     # Halaman galeri
├── models/
│   └── best.pt              # Model YOLOv8 trained
├── captures/                # Folder untuk tangkapan
├── requirements.txt         # Python dependencies
├── train.py                 # Script training
└── setup.ps1                # Setup script Windows
```

---

## 🎓 Pelajari Lebih Lanjut

- **ARSITEKTUR.md**: Penjelasan detail arsitektur sistem
- **README.md**: Informasi umum proyek
- **COMMANDS.md**: Referensi command lengkap

---

## 📞 Bantuan & Support

Jika mengalami masalah:
1. Baca section Troubleshooting di atas
2. Periksa log error di terminal
3. Periksa console browser (F12)
4. Hubungi maintainer proyek

---

**Selamat menggunakan! 🌿**

**Terakhir diperbarui**: 29 Desember 2024
