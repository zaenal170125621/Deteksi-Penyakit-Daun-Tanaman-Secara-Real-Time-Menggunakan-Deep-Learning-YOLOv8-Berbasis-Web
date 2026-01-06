/**
 * Deteksi Penyakit Daun Tanaman - JavaScript Client
 */

// Status global
let videoStream = null;
let isDetecting = false;
let detectionInterval = null;
let lastFrameBlob = null;
let frameCount = 0;
let fpsStartTime = Date.now();
let currentFacingMode = "environment"; // Mulai dengan kamera belakang

// Elemen DOM
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const captureBtn = document.getElementById("captureBtn");
const switchCameraBtn = document.getElementById("switchCameraBtn");
const statusText = document.getElementById("statusText");
const fpsCounter = document.getElementById("fpsCounter");
const resultContainer = document.getElementById("resultContainer");
const noResultsMessage = document.getElementById("noResultsMessage");
const annotatedImage = document.getElementById("annotatedImage");
const detectionsList = document.getElementById("detectionsList");
const critiqueList = document.getElementById("critiqueList");
const suggestionsList = document.getElementById("suggestionsList");
const disclaimerText = document.getElementById("disclaimerText");
const metricsDisplay = document.getElementById("metricsDisplay");
const captureToast = document.getElementById("captureToast");
const loadingOverlay = document.getElementById("loadingOverlay");

// Video preview state
let videoPreviewInterval = null;

/**
 * Gambar video ke canvas secara kontinyu
 */
function drawVideoToCanvas() {
  if (video.videoWidth && video.videoHeight) {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  }
}

/**
 * Mulai preview video di canvas
 */
function startVideoPreview() {
  if (videoPreviewInterval) return;
  videoPreviewInterval = setInterval(drawVideoToCanvas, 33); // ~30 FPS
}

/**
 * Hentikan preview video di canvas
 */
function stopVideoPreview() {
  if (videoPreviewInterval) {
    clearInterval(videoPreviewInterval);
    videoPreviewInterval = null;
  }
}

/**
 * Inisialisasi kamera
 */
async function initCamera() {
  try {
    // Hentikan stream yang ada
    if (videoStream) {
      videoStream.getTracks().forEach((track) => track.stop());
    }

    const constraints = {
      video: {
        facingMode: currentFacingMode,
        width: { ideal: 720 },
        height: { ideal: 1280 },
      },
      audio: false,
    };

    videoStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = videoStream;

    await video.play();

    // Setel ukuran canvas sesuai video
    video.addEventListener("loadedmetadata", () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    });

    statusText.textContent = "Kamera siap";
    startBtn.disabled = false;

    return true;
  } catch (error) {
    console.error("Error mengakses kamera:", error);
    statusText.textContent = `Error kamera: ${error.message}`;
    alert(
      `Gagal mengakses kamera: ${error.message}\n\nPastikan:\n1. Izin kamera telah diberikan\n2. Perangkat memiliki kamera\n3. Tidak ada aplikasi lain yang menggunakan kamera`
    );
    return false;
  }
}

/**
 * Ganti antara kamera depan dan belakang
 */
async function switchCamera() {
  currentFacingMode =
    currentFacingMode === "environment" ? "user" : "environment";
  await initCamera();
}

/**
 * Tangkap frame dari video dan konversi ke JPEG blob
 */
function captureFrame() {
  if (!video.videoWidth || !video.videoHeight) {
    return null;
  }

  // Gambar frame video saat ini ke canvas
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Konversi ke blob
  return new Promise((resolve) => {
    canvas.toBlob(
      (blob) => {
        resolve(blob);
      },
      "image/jpeg",
      0.7
    );
  });
}

/**
 * Kirim frame ke server untuk deteksi
 */
async function detectFrame(frameBlob) {
  const formData = new FormData();
  formData.append("file", frameBlob, "frame.jpg");

  try {
    const response = await fetch("/detect", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Deteksi gagal");
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Error deteksi:", error);
    throw error;
  }
}

/**
 * Update UI dengan hasil deteksi
 */
function updateResults(result) {
  // Tampilkan container hasil
  resultContainer.classList.remove("hidden");
  noResultsMessage.classList.add("hidden");

  // Update gambar hasil deteksi
  annotatedImage.src = `data:image/jpeg;base64,${result.annotated_jpeg_base64}`;

  // Update daftar deteksi
  detectionsList.innerHTML = "";
  if (result.detections && result.detections.length > 0) {
    result.detections.forEach((det) => {
      const detDiv = document.createElement("div");
      detDiv.className = "detection-item";

      const confidence = (det.confidence * 100).toFixed(1);
      const confidenceClass =
        det.confidence >= 0.7
          ? "high"
          : det.confidence >= 0.5
          ? "medium"
          : "low";

      detDiv.innerHTML = `
                <div class="detection-name">${det.class_name}</div>
                <div class="detection-confidence confidence-${confidenceClass}">
                    ${confidence}%
                </div>
            `;
      detectionsList.appendChild(detDiv);
    });
  } else {
    detectionsList.innerHTML =
      '<div class="no-detection">Tidak ada penyakit terdeteksi</div>';
  }

  // Update feedback - kritik
  critiqueList.innerHTML = "";
  if (result.feedback && result.feedback.critique) {
    result.feedback.critique.forEach((critique) => {
      const item = document.createElement("div");
      item.className = "feedback-item";

      // Style berdasarkan prefix
      if (critique.startsWith("⚠️")) {
        item.classList.add("warning");
      } else if (critique.startsWith("✓")) {
        item.classList.add("success");
      } else if (critique.startsWith("ℹ️")) {
        item.classList.add("info");
      }

      item.textContent = critique;
      critiqueList.appendChild(item);
    });
  }

  // Update feedback - saran
  suggestionsList.innerHTML = "";
  if (result.feedback && result.feedback.suggestions) {
    result.feedback.suggestions.forEach((suggestion) => {
      const item = document.createElement("div");
      item.className = "feedback-item";
      item.textContent = suggestion;
      suggestionsList.appendChild(item);
    });
  }

  // Update disclaimer
  if (result.feedback && result.feedback.disclaimer) {
    disclaimerText.textContent = result.feedback.disclaimer;
  }

  // Update metrik
  metricsDisplay.innerHTML = "";
  if (result.quality_metrics) {
    const metrics = [
      {
        label: "Kecerahan",
        value: result.quality_metrics.brightness.toFixed(0) + "/255",
      },
      {
        label: "Ketajaman",
        value: result.quality_metrics.blur_metric.toFixed(1),
      },
      {
        label: "Resolusi",
        value: `${result.quality_metrics.width}x${result.quality_metrics.height}`,
      },
      {
        label: "Waktu Inferensi",
        value: result.inference_time_ms.toFixed(1) + "ms",
      },
    ];

    if (result.feedback && result.feedback.summary) {
      metrics.push({
        label: "Skor Kualitas",
        value: result.feedback.summary.quality_score,
      });
    }

    metrics.forEach((metric) => {
      const metricDiv = document.createElement("div");
      metricDiv.className = "metric-item";
      metricDiv.innerHTML = `
                <div class="metric-label">${metric.label}</div>
                <div class="metric-value">${metric.value}</div>
            `;
      metricsDisplay.appendChild(metricDiv);
    });
  }
}
async function detectionLoop() {
  if (!isDetecting) return;

  try {
    // Tangkap frame
    const frameBlob = await captureFrame();
    if (!frameBlob) {
      setTimeout(detectionLoop, 200);
      return;
    }

    lastFrameBlob = frameBlob;

    // Kirim ke server
    const result = await detectFrame(frameBlob);

    // Update UI
    updateResults(result);

    // Update FPS
    frameCount++;
    const now = Date.now();
    const elapsed = (now - fpsStartTime) / 1000;
    if (elapsed >= 1) {
      const fps = (frameCount / elapsed).toFixed(1);
      fpsCounter.textContent = `${fps} FPS`;
      frameCount = 0;
      fpsStartTime = now;
    }

    // Aktifkan tombol tangkap setelah deteksi pertama berhasil
    captureBtn.disabled = false;
  } catch (error) {
    console.error("Error loop deteksi:", error);
    statusText.textContent = `Error: ${error.message}`;
  }

  // Lanjutkan loop dengan delay (lebih lambat untuk ngrok)
  setTimeout(detectionLoop, 500); // ~2 FPS untuk koneksi lambat
}

/**
 * Mulai deteksi
 */
async function startDetection() {
  if (isDetecting) return;

  // Cek apakah kamera siap
  if (!videoStream) {
    const success = await initCamera();
    if (!success) return;
  }

  isDetecting = true;
  startBtn.disabled = true;
  stopBtn.disabled = false;
  statusText.textContent = "Mendeteksi...";

  frameCount = 0;
  fpsStartTime = Date.now();

  // Mulai loop deteksi
  detectionLoop();
}

/**
 * Hentikan deteksi
 */
function stopDetection() {
  isDetecting = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  captureBtn.disabled = true;
  statusText.textContent = "Deteksi dihentikan";
  fpsCounter.textContent = "0 FPS";
}

/**
 * Tangkap frame dan hasil saat ini
 */
async function captureImage() {
  if (!lastFrameBlob) {
    alert("Tidak ada frame yang tersedia untuk ditangkap");
    return;
  }

  try {
    loadingOverlay.classList.remove("hidden");

    const formData = new FormData();
    formData.append("file", lastFrameBlob, "capture.jpg");

    const response = await fetch("/capture", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Tangkapan gagal");
    }

    const result = await response.json();

    loadingOverlay.classList.add("hidden");

    // Tampilkan toast sukses
    showToast(`Tangkapan tersimpan! (${result.capture_id})`);
  } catch (error) {
    loadingOverlay.classList.add("hidden");
    console.error("Error tangkap:", error);
    alert(`Gagal menyimpan tangkapan: ${error.message}`);
  }
}

/**
 * Tampilkan notifikasi toast
}

/**
 * Show toast notification
 */
function showToast(message) {
  const toast = captureToast;
  const messageEl = toast.querySelector(".toast-message");
  messageEl.textContent = message;

  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3000);
}
startBtn.addEventListener("click", startDetection);
stopBtn.addEventListener("click", stopDetection);
captureBtn.addEventListener("click", captureImage);
switchCameraBtn.addEventListener("click", switchCamera);

/**
 * Inisialisasi saat halaman dimuat
 */
window.addEventListener("load", async () => {
  console.log("Menginisialisasi Deteksi Penyakit Daun Tanaman...");

  // Cek dukungan kamera
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Browser Anda tidak mendukung akses kamera. Gunakan browser modern.");
    statusText.textContent = "Kamera tidak didukung";
    return;
  }

  // Inisialisasi kamera
  await initCamera();
});

/**
 * Bersihkan saat halaman dibongkar
});

/**
 * Cleanup on page unload
 */
window.addEventListener("beforeunload", () => {
  if (videoStream) {
    videoStream.getTracks().forEach((track) => track.stop());
  }
});
