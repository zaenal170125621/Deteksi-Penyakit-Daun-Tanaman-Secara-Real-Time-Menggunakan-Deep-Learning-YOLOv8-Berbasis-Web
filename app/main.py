"""
FastAPI server for plant leaf disease detection.
"""
import json
import io
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app import yolo_infer, feedback, utils


# Initialize FastAPI app
app = FastAPI(
    title="Plant Leaf Disease Detector",
    description="Real-time plant leaf disease detection using YOLOv8",
    version="1.0.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local network access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup paths
BASE_DIR = Path(__file__).parent.parent
CAPTURES_DIR = BASE_DIR / "captures"
MODELS_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

# Ensure directories exist
utils.ensure_dir(CAPTURES_DIR)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Store last inference result for capture functionality
last_inference_result = {
    'detections': [],
    'annotated_image_bgr': None,
    'original_image_bgr': None,
    'quality_metrics': {},
    'timestamp': None
}


@app.on_event("startup")
async def startup_event():
    """Initialize YOLO model on startup."""
    model_path = MODELS_DIR / "best.pt"

    if not model_path.exists():
        print(f"WARNING: Model file not found at {model_path}")
        print("Please train a model or place best.pt in the models/ directory")
        print("The server will start but detection will fail until model is available")
    else:
        try:
            # Initialize with conf_threshold=0.35 for reduced false positives
            yolo_infer.initialize_detector(
                str(model_path), conf_threshold=0.35)
            print("YOLO model loaded successfully")
            print(
                f"Available classes: {yolo_infer.detector.get_class_names()}")
            print("Green detection filtering enabled by default")
        except Exception as e:
            print(f"ERROR loading model: {e}")
            print("Server will start but detection will fail")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request):
    """Render gallery page."""
    # Get all captures
    captures = []
    for json_file in sorted(CAPTURES_DIR.glob("capture_*_data.json"), reverse=True):
        try:
            with open(json_file, 'r') as f:
                capture_data = json.load(f)
                captures.append(capture_data)
        except Exception as e:
            print(f"Error reading {json_file}: {e}")

    return templates.TemplateResponse(
        "gallery.html",
        {"request": request, "captures": captures}
    )


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    """
    Detect plant diseases in uploaded image.

    Args:
        file: Uploaded image file

    Returns:
        JSON with detections, feedback, and annotated image
    """
    try:
        # Check if model is loaded
        if not yolo_infer.detector.is_loaded():
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Please ensure best.pt is in models/ directory and restart server."
            )

        # Read and decode image
        image_bytes = await file.read()
        image_bgr = utils.decode_image_bytes(image_bytes)

        # Run inference with green detection filtering enabled
        inference_result = yolo_infer.run_inference(
            image_bgr,
            imgsz=640,
            enable_filtering=True,
            min_green_ratio=0.15
        )

        # Compute quality metrics
        quality_metrics = utils.compute_image_quality_metrics(image_bgr)

        # Generate feedback
        feedback_result = feedback.generate_feedback(
            detections=inference_result['detections'],
            quality_metrics=quality_metrics,
            image_width=image_bgr.shape[1],
            image_height=image_bgr.shape[0]
        )

        # Convert annotated image to base64 JPEG
        annotated_base64 = utils.image_to_base64_jpeg(
            inference_result['annotated_image_bgr'],
            quality=85
        )

        # Store for potential capture
        global last_inference_result
        last_inference_result = {
            'detections': inference_result['detections'],
            'annotated_image_bgr': inference_result['annotated_image_bgr'],
            'original_image_bgr': image_bgr,
            'quality_metrics': quality_metrics,
            'feedback': feedback_result,
            'timestamp': datetime.now().isoformat()
        }

        # Build response with filtering statistics
        response = {
            'success': True,
            'detections': inference_result['detections'],
            'feedback': feedback_result,
            'annotated_jpeg_base64': annotated_base64,
            'inference_time_ms': inference_result['inference_time_ms'],
            'quality_metrics': quality_metrics,
            'filtering_stats': inference_result.get('filtering_stats', {}),
            'timestamp': datetime.now().isoformat()
        }

        return JSONResponse(content=response)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    except Exception as e:
        print(f"Error in /detect: {e}")
        raise HTTPException(
            status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/capture")
async def capture(file: UploadFile = File(...)):
    """
    Capture and save current detection results.

    Args:
        file: Original image file

    Returns:
        JSON with saved file paths and capture ID
    """
    try:
        # Read original image
        image_bytes = await file.read()
        original_image_bgr = utils.decode_image_bytes(image_bytes)

        # Run inference on this image with filtering enabled
        inference_result = yolo_infer.run_inference(
            original_image_bgr,
            imgsz=640,
            enable_filtering=True,
            min_green_ratio=0.15
        )
        quality_metrics = utils.compute_image_quality_metrics(
            original_image_bgr)

        feedback_result = feedback.generate_feedback(
            detections=inference_result['detections'],
            quality_metrics=quality_metrics,
            image_width=original_image_bgr.shape[1],
            image_height=original_image_bgr.shape[0]
        )

        # Generate timestamp-based filenames
        capture_id = utils.generate_timestamp_filename("capture", "")

        original_filename = f"{capture_id}_original.jpg"
        annotated_filename = f"{capture_id}_detected.jpg"
        data_filename = f"{capture_id}_data.json"

        original_path = CAPTURES_DIR / original_filename
        annotated_path = CAPTURES_DIR / annotated_filename
        data_path = CAPTURES_DIR / data_filename

        # Save original image
        original_jpeg = utils.encode_image_to_jpeg(
            original_image_bgr, quality=95)
        with open(original_path, 'wb') as f:
            f.write(original_jpeg)

        # Save annotated image
        annotated_jpeg = utils.encode_image_to_jpeg(
            inference_result['annotated_image_bgr'],
            quality=95
        )
        with open(annotated_path, 'wb') as f:
            f.write(annotated_jpeg)

        # Save JSON data
        capture_data = {
            'capture_id': capture_id,
            'timestamp': datetime.now().isoformat(),
            'original_image': original_filename,
            'annotated_image': annotated_filename,
            'detections': inference_result['detections'],
            'quality_metrics': quality_metrics,
            'feedback': feedback_result,
            'inference_time_ms': inference_result['inference_time_ms']
        }

        with open(data_path, 'w') as f:
            json.dump(capture_data, f, indent=2)

        return JSONResponse(content={
            'success': True,
            'capture_id': capture_id,
            'files': {
                'original': str(original_filename),
                'annotated': str(annotated_filename),
                'data': str(data_filename)
            },
            'message': f'Capture saved successfully with {len(inference_result["detections"])} detection(s)'
        })

    except Exception as e:
        print(f"Error in /capture: {e}")
        raise HTTPException(
            status_code=500, detail=f"Capture failed: {str(e)}")


@app.get("/captures/{filename}")
async def get_capture_file(filename: str):
    """Serve capture files."""
    file_path = CAPTURES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    from fastapi.responses import FileResponse
    return FileResponse(file_path)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_loaded = yolo_infer.detector.is_loaded()
    return {
        'status': 'healthy' if model_loaded else 'degraded',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/model-info")
async def model_info():
    """Get information about loaded model."""
    if not yolo_infer.detector.is_loaded():
        return {
            'loaded': False,
            'message': 'Model not loaded'
        }

    return {
        'loaded': True,
        'classes': yolo_infer.detector.get_class_names(),
        'num_classes': len(yolo_infer.detector.get_class_names())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
