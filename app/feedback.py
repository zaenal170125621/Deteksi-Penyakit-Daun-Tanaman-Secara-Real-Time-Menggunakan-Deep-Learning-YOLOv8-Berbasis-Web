"""
Modul Umpan Balik AI untuk deteksi penyakit daun tanaman.
Menyediakan dukungan keputusan yang aman berbasis aturan dengan kritik kualitas dan saran.
"""
from typing import Dict, List
from app.utils import compute_bbox_area_ratio


# Ambang batas untuk penilaian kualitas
BRIGHTNESS_LOW_THRESHOLD = 60
BRIGHTNESS_HIGH_THRESHOLD = 200
BLUR_THRESHOLD = 100  # Ambang varians Laplacian
CONFIDENCE_LOW_THRESHOLD = 0.5
BBOX_AREA_MIN_THRESHOLD = 0.05  # 5% dari gambar
BBOX_AREA_MAX_THRESHOLD = 0.95  # 95% dari gambar


# Saran umum spesifik penyakit (aman, non-diagnostik)
DISEASE_SUGGESTIONS = {
    'apple_scab_leaf': [
        "Pertimbangkan untuk membuang daun yang sangat terinfeksi untuk mengurangi penyebaran spora",
        "Tingkatkan sirkulasi udara di sekitar tanaman",
        "Hindari penyiraman dari atas; siram di permukaan tanah",
        "Pantau secara teratur untuk deteksi dini penyebaran"
    ],
    'apple_rust_leaf': [
        "Hapus pohon cedar terdekat jika memungkinkan (inang alternatif)",
        "Aplikasikan fungisida selama cuaca basah di musim semi",
        "Pilih varietas tahan untuk penanaman masa depan",
        "Tingkatkan drainase dan sirkulasi udara"
    ],
    'apple_leaf': [
        "Daun tampak sehat - lanjutkan praktik perawatan saat ini",
        "Pertahankan pemantauan rutin untuk deteksi masalah dini",
        "Pastikan nutrisi dan manajemen air yang memadai"
    ],
    'bell_pepper_leaf_spot': [
        "Gunakan benih dan transplantasi bebas patogen",
        "Hindari bekerja dengan tanaman saat basah",
        "Aplikasikan produk berbasis tembaga secara preventif",
        "Praktikkan rotasi tanaman dengan tanaman non-inang"
    ],
    'bell_pepper_leaf': [
        "Tanaman paprika tampak sehat",
        "Lanjutkan praktik pertumbuhan saat ini"
    ],
    'blueberry_leaf': [
        "Daun blueberry tampak sehat",
        "Pertahankan pH tanah (4.5-5.5) dan kelembaban yang memadai"
    ],
    'cherry_leaf': [
        "Daun ceri tampak sehat",
        "Lanjutkan pemantauan rutin dan praktik budidaya yang baik"
    ],
    'corn_gray_leaf_spot': [
        "Praktikkan rotasi tanaman dengan tanaman non-inang",
        "Buang sisa tanaman setelah panen",
        "Pertimbangkan hibrida tahan untuk musim berikutnya",
        "Pantau kondisi cuaca yang mendukung penyebaran penyakit"
    ],
    'corn_leaf_blight': [
        "Praktikkan rotasi tanaman (minimal 2-3 tahun)",
        "Kubur sisa tanaman melalui pengolahan tanah dalam",
        "Gunakan hibrida tahan",
        "Aplikasikan fungisida pada tahap awal penyakit jika diperlukan"
    ],
    'corn_rust_leaf': [
        "Tanam hibrida tahan jika tersedia",
        "Pantau perkembangan penyakit secara teratur",
        "Aplikasikan fungisida jika ambang ekonomi tercapai",
        "Pastikan nutrisi seimbang, terutama nitrogen"
    ],
    'peach_leaf': [
        "Daun persik tampak sehat",
        "Pertahankan pemantauan dan perawatan kebun secara teratur"
    ],
    'potato_leaf_early_blight': [
        "Buang daun bawah yang terinfeksi",
        "Aplikasikan fungisida yang sesuai secara preventif",
        "Pertahankan jarak tanam yang memadai untuk sirkulasi udara",
        "Praktikkan rotasi tanaman"
    ],
    'potato_leaf_late_blight': [
        "Ini adalah penyakit serius - bertindak cepat",
        "Buang dan hancurkan tanaman yang terinfeksi segera",
        "Aplikasikan fungisida protektif pada tanaman sehat",
        "Pantau kondisi cuaca (cuaca dingin dan basah mendukung penyakit)"
    ],
    'potato_leaf': [
        "Dedaunan kentang tampak sehat",
        "Lanjutkan pemantauan dan praktik saat ini"
    ],
    'raspberry_leaf': [
        "Daun raspberry tampak sehat",
        "Pertahankan rejimen perawatan saat ini"
    ],
    'soyabean_leaf': [
        "Daun kedelai tampak sehat",
        "Lanjutkan pemantauan sepanjang musim tanam"
    ],
    'soybean_leaf': [
        "Daun kedelai tampak sehat",
        "Lanjutkan pemantauan sepanjang musim tanam"
    ],
    'squash_powdery_mildew_leaf': [
        "Tingkatkan sirkulasi udara di sekitar tanaman",
        "Siram di permukaan tanah, hindari membasahi dedaunan",
        "Aplikasikan perawatan sulfur atau kalium bikarbonat",
        "Buang daun yang sangat terinfeksi"
    ],
    'strawberry_leaf': [
        "Daun stroberi tampak sehat",
        "Pertahankan praktik budidaya yang baik"
    ],
    'tomato_early_blight_leaf': [
        "Buang daun bawah yang terinfeksi",
        "Mulsa untuk mencegah percikan tanah",
        "Aplikasikan fungisida secara preventif",
        "Pastikan jarak tanam yang memadai"
    ],
    'tomato_septoria_leaf_spot': [
        "Buang daun bawah yang terinfeksi",
        "Hindari penyiraman dari atas",
        "Aplikasikan fungisida yang sesuai",
        "Praktikkan rotasi tanaman"
    ],
    'tomato_leaf_bacterial_spot': [
        "Gunakan benih dan transplantasi bebas penyakit",
        "Hindari irigasi dari atas",
        "Aplikasikan produk berbasis tembaga secara preventif",
        "Buang tanaman yang sangat terinfeksi"
    ],
    'tomato_leaf_late_blight': [
        "Ini adalah penyakit serius yang memerlukan tindakan segera",
        "Buang dan hancurkan tanaman yang terinfeksi",
        "Aplikasikan fungisida protektif pada tanaman yang tidak terinfeksi",
        "Pantau cuaca (kondisi dingin dan basah mendukung penyakit)"
    ],
    'tomato_leaf_mosaic_virus': [
        "Buang dan hancurkan tanaman yang terinfeksi segera",
        "Kendalikan vektor kutu daun",
        "Gunakan varietas tahan virus",
        "Praktikkan sanitasi yang baik (cuci tangan, desinfeksi alat)"
    ],
    'tomato_leaf_yellow_virus': [
        "Kendalikan vektor kutu putih (metode transmisi utama)",
        "Buang tanaman yang terinfeksi untuk mencegah penyebaran",
        "Gunakan mulsa reflektif untuk menghalau kutu putih",
        "Tanam varietas tahan jika tersedia"
    ],
    'tomato_leaf': [
        "Daun tomat tampak sehat",
        "Lanjutkan praktik pertumbuhan dan pemantauan saat ini"
    ],
    'tomato_mold_leaf': [
        "Tingkatkan ventilasi rumah kaca jika tumbuh di dalam ruangan",
        "Kurangi tingkat kelembaban",
        "Buang daun yang terinfeksi",
        "Beri jarak tanaman yang memadai untuk sirkulasi udara"
    ],
    'tomato_two_spotted_spider_mites_leaf': [
        "Tingkatkan kelembaban di sekitar tanaman (tungau lebih suka kondisi kering)",
        "Semprot tanaman dengan air untuk mengusir tungau",
        "Gunakan sabun insektisida atau minyak neem",
        "Dorong serangga predator yang bermanfaat"
    ],
    'grape_leaf_black_rot': [
        "Buang buah anggur yang mummi dan daun yang terinfeksi",
        "Pangkas untuk meningkatkan sirkulasi udara dan penetrasi cahaya",
        "Aplikasikan fungisida preventif selama periode rentan",
        "Pertahankan sanitasi kebun anggur"
    ],
    'grape_leaf': [
        "Daun anggur tampak sehat",
        "Lanjutkan praktik manajemen kebun anggur saat ini"
    ],
}


def get_disease_suggestions(class_name: str) -> List[str]:
    """
    Dapatkan saran umum untuk kelas penyakit.
    Kembali ke saran generik jika kelas tidak ditemukan.

    Args:
        class_name: Nama kelas penyakit

    Returns:
        Daftar string saran
    """
    # Normalisasi nama kelas (huruf kecil, ganti spasi/garis bawah)
    normalized = class_name.lower().replace(' ', '_').replace('-', '_')

    # Coba kecocokan tepat terlebih dahulu
    if normalized in DISEASE_SUGGESTIONS:
        return DISEASE_SUGGESTIONS[normalized]

    # Coba kecocokan parsial
    for key in DISEASE_SUGGESTIONS:
        if key in normalized or normalized in key:
            return DISEASE_SUGGESTIONS[key]

    # Fallback generik
    if 'healthy' in normalized:
        return ["Daun tampak sehat", "Lanjutkan praktik perawatan saat ini"]
    else:
        return [
            "Konsultasikan dengan layanan penyuluhan pertanian atau patolog tanaman",
            "Dokumentasikan gejala dengan foto yang jelas",
            "Pantau perkembangan penyakit",
            "Pertimbangkan pengujian laboratorium untuk diagnosis akurat"
        ]


def generate_feedback(
    detections: List[Dict],
    quality_metrics: Dict,
    image_width: int,
    image_height: int
) -> Dict:
    """
    Hasilkan umpan balik AI berdasarkan deteksi dan kualitas gambar.

    Args:
        detections: Daftar kamus deteksi
        quality_metrics: Kamus dengan kecerahan, blur_metric, dll.
        image_width: Lebar gambar dalam piksel
        image_height: Tinggi gambar dalam piksel

    Returns:
        Kamus dengan kritik, saran, dan penafian
    """
    critique = []
    suggestions = []

    brightness = quality_metrics.get('brightness', 128)
    blur_metric = quality_metrics.get('blur_metric', 100)

    # 1) Nilai pencahayaan
    if brightness < BRIGHTNESS_LOW_THRESHOLD:
        critique.append(
            f"⚠️ Pencahayaan rendah terdeteksi (kecerahan: {brightness:.0f}/255). Gambar mungkin terlalu gelap.")
        suggestions.append(
            "Tingkatkan pencahayaan atau pindah ke area yang lebih terang")
    elif brightness > BRIGHTNESS_HIGH_THRESHOLD:
        critique.append(
            f"⚠️ Pencahayaan sangat terang (kecerahan: {brightness:.0f}/255). Dapat menyebabkan overexposure.")
        suggestions.append(
            "Kurangi cahaya langsung atau sesuaikan eksposur kamera")
    else:
        critique.append(
            f"✓ Pencahayaan memadai (kecerahan: {brightness:.0f}/255)")

    # 2) Nilai blur
    if blur_metric < BLUR_THRESHOLD:
        critique.append(
            f"⚠️ Gambar tampak blur (skor ketajaman: {blur_metric:.1f})")
        suggestions.append(
            "Tahan kamera dengan stabil atau gunakan kecepatan rana lebih cepat")
        suggestions.append("Pastikan fokus yang tepat pada daun")
    else:
        critique.append(
            f"✓ Ketajaman gambar dapat diterima (skor: {blur_metric:.1f})")

    # 3) Nilai deteksi
    if not detections:
        critique.append(
            "⚠️ Tidak ada penyakit tanaman terdeteksi dalam gambar ini")
        suggestions.append(
            "Pastikan daun terlihat jelas dan dibingkai dengan baik")
        suggestions.append("Coba sudut atau jarak yang berbeda")
        suggestions.append(
            "Verifikasi bahwa daun menunjukkan gejala yang terlihat")
    else:
        # Periksa tingkat kepercayaan
        max_conf = max(d['confidence'] for d in detections)
        min_conf = min(d['confidence'] for d in detections)
        avg_conf = sum(d['confidence'] for d in detections) / len(detections)

        if max_conf < CONFIDENCE_LOW_THRESHOLD:
            critique.append(
                f"⚠️ Deteksi dengan kepercayaan rendah (tertinggi: {max_conf:.2%})")
            suggestions.append("Coba tangkap dari jarak lebih dekat")
            suggestions.append("Pastikan pencahayaan dan fokus lebih baik")
            suggestions.append("Tangkap ulang jika gejala tidak jelas")
        else:
            critique.append(
                f"✓ Deteksi ditemukan dengan kepercayaan hingga {max_conf:.2%}")

        # Periksa ukuran kotak pembatas
        small_boxes = []
        large_boxes = []

        for det in detections:
            bbox_ratio = compute_bbox_area_ratio(
                det['bbox_xyxy'],
                image_width,
                image_height
            )

            if bbox_ratio < BBOX_AREA_MIN_THRESHOLD:
                small_boxes.append((det['class_name'], bbox_ratio))
            elif bbox_ratio > BBOX_AREA_MAX_THRESHOLD:
                large_boxes.append((det['class_name'], bbox_ratio))

        if small_boxes:
            critique.append(
                f"⚠️ Wilayah terdeteksi kecil ({small_boxes[0][1]:.1%} dari bingkai)")
            suggestions.append("Pindahkan kamera lebih dekat ke daun")
            suggestions.append("Zoom pada area yang terkena")

        if large_boxes:
            critique.append(
                f"ℹ️ Deteksi mengisi sebagian besar bingkai ({large_boxes[0][1]:.1%})")
            suggestions.append(
                "Pertimbangkan menangkap dari jarak sedikit lebih jauh untuk konteks")

        # Periksa beberapa kelas yang berbeda
        unique_classes = set(d['class_name'] for d in detections)
        if len(unique_classes) > 1:
            critique.append(
                f"ℹ️ Beberapa jenis penyakit terdeteksi: {', '.join(unique_classes)}")
            suggestions.append(
                "Pertimbangkan menangkap daun individual secara terpisah untuk diagnosis yang lebih jelas")
            suggestions.append(
                "Beberapa gejala dapat menunjukkan infeksi kompleks")

        # Tambahkan saran khusus penyakit
        for class_name in unique_classes:
            disease_suggestions = get_disease_suggestions(class_name)
            suggestions.append(f"\n📋 Untuk {class_name}:")
            suggestions.extend([f"  • {s}" for s in disease_suggestions])

    # 4) Pemeriksaan resolusi gambar
    if image_width < 400 or image_height < 400:
        critique.append(f"⚠️ Resolusi rendah ({image_width}x{image_height})")
        suggestions.append(
            "Gunakan resolusi kamera lebih tinggi jika tersedia")

    # Hasilkan penafian
    disclaimer = (
        "⚠️ PENAFIAN PENTING: Sistem ini hanya menyediakan dukungan keputusan dan BUKAN "
        "pengganti diagnosis profesional. Untuk identifikasi penyakit yang akurat dan "
        "rekomendasi perawatan, silakan berkonsultasi dengan:\n"
        "  • Layanan penyuluhan pertanian\n"
        "  • Patolog tanaman bersertifikat\n"
        "  • Agronom profesional\n\n"
        "Selalu konfirmasi penyakit yang dicurigai melalui pengujian laboratorium bila memungkinkan. "
        "Saran yang diberikan adalah praktik budidaya umum dan harus disesuaikan "
        "dengan kondisi pertumbuhan spesifik Anda, peraturan lokal, dan panduan ahli."
    )

    return {
        'critique': critique,
        'suggestions': suggestions,
        'disclaimer': disclaimer,
        'summary': {
            'detections_count': len(detections),
            'unique_diseases': len(set(d['class_name'] for d in detections)) if detections else 0,
            'max_confidence': max((d['confidence'] for d in detections), default=0.0),
            'quality_score': _compute_quality_score(brightness, blur_metric, detections)
        }
    }


def _compute_quality_score(brightness: float, blur_metric: float, detections: List[Dict]) -> str:
    """
    Hitung skor kualitas keseluruhan.

    Returns:
        Skor kualitas: "sangat baik", "baik", "cukup", "buruk"
    """
    score = 0

    # Kontribusi kecerahan (0-2 poin)
    if BRIGHTNESS_LOW_THRESHOLD <= brightness <= BRIGHTNESS_HIGH_THRESHOLD:
        score += 2
    elif brightness < BRIGHTNESS_LOW_THRESHOLD - 20 or brightness > BRIGHTNESS_HIGH_THRESHOLD + 20:
        score += 0
    else:
        score += 1

    # Kontribusi blur (0-2 poin)
    if blur_metric >= BLUR_THRESHOLD * 2:
        score += 2
    elif blur_metric >= BLUR_THRESHOLD:
        score += 1
    else:
        score += 0

    # Kontribusi kepercayaan deteksi (0-2 poin)
    if detections:
        max_conf = max(d['confidence'] for d in detections)
        if max_conf >= 0.7:
            score += 2
        elif max_conf >= 0.5:
            score += 1

    # Peta skor ke tingkat kualitas
    if score >= 5:
        return "sangat baik"
    elif score >= 4:
        return "baik"
    elif score >= 2:
        return "cukup"
    else:
        return "buruk"
