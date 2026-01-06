"""
YOLOv8 inference module for plant leaf disease detection.
Enhanced with green detection and confidence filtering to reduce false positives.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ultralytics import YOLO


class YOLODetector:
    """Singleton YOLOv8 detector for plant leaf diseases with enhanced filtering."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(YOLODetector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize detector (lazy loading)."""
        pass

    def load_model(self, model_path: str, conf_threshold: float = 0.35):
        """
        Load YOLO model.

        Args:
            model_path: Path to model weights (.pt file)
            conf_threshold: Confidence threshold for detections (default: 0.35)
        """
        if self._model is None:
            model_file = Path(model_path)
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")

            print(f"Loading YOLO model from {model_path}...")
            self._model = YOLO(model_path)
            self.conf_threshold = conf_threshold
            print(f"Model loaded successfully. Classes: {self._model.names}")
            print(f"Confidence threshold: {conf_threshold}")

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None

    def get_class_names(self) -> dict:
        """Get class names dictionary."""
        if self._model is None:
            return {}
        return self._model.names

    @staticmethod
    def calculate_green_ratio(image_bgr: np.ndarray, bbox_xyxy: List[float]) -> float:
        """
        Calculate the ratio of green pixels in the bounding box.
        This helps verify if the detected region contains leaf-like colors.

        Args:
            image_bgr: Full image in BGR format
            bbox_xyxy: Bounding box coordinates [x1, y1, x2, y2]

        Returns:
            Green ratio (0-1) where higher values indicate more green content
        """
        x1, y1, x2, y2 = map(int, bbox_xyxy)

        # Ensure valid crop region
        h, w = image_bgr.shape[:2]
        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(x1 + 1, min(x2, w))
        y2 = max(y1 + 1, min(y2, h))

        # Crop the detection region
        roi = image_bgr[y1:y2, x1:x2]

        if roi.size == 0:
            return 0.0

        # Convert to HSV for better green detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Define green color range in HSV
        # Green hue is typically 35-85 in OpenCV HSV (0-180 scale)
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([90, 255, 255])

        # Create mask for green pixels
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # Calculate ratio of green pixels
        green_pixels = np.sum(green_mask > 0)
        total_pixels = green_mask.size

        return green_pixels / total_pixels if total_pixels > 0 else 0.0

    @staticmethod
    def calculate_box_area_ratio(bbox_xyxy: List[float], image_shape: Tuple[int, int]) -> float:
        """
        Calculate the ratio of bounding box area to image area.
        Helps filter out unreasonably large or small detections.

        Args:
            bbox_xyxy: Bounding box coordinates [x1, y1, x2, y2]
            image_shape: Image shape (height, width)

        Returns:
            Area ratio (0-1)
        """
        x1, y1, x2, y2 = bbox_xyxy
        box_area = (x2 - x1) * (y2 - y1)
        image_area = image_shape[0] * image_shape[1]
        return box_area / image_area if image_area > 0 else 0.0

    def filter_detections(
        self,
        detections: List[Dict],
        image_bgr: np.ndarray,
        min_green_ratio: float = 0.15,
        min_area_ratio: float = 0.001,
        max_area_ratio: float = 0.95
    ) -> List[Dict]:
        """
        Filter detections based on green content and size constraints.
        This helps reduce false positives on non-leaf objects.

        Args:
            detections: List of raw detection dictionaries
            image_bgr: Original image in BGR format
            min_green_ratio: Minimum green pixel ratio (0-1)
            min_area_ratio: Minimum box area ratio relative to image
            max_area_ratio: Maximum box area ratio relative to image

        Returns:
            Filtered list of detections
        """
        if not detections:
            return []

        filtered = []
        image_shape = image_bgr.shape[:2]

        for det in detections:
            bbox = det['bbox_xyxy']

            # Check green content
            green_ratio = self.calculate_green_ratio(image_bgr, bbox)

            # Check box size
            area_ratio = self.calculate_box_area_ratio(bbox, image_shape)

            # Apply filters
            if (green_ratio >= min_green_ratio and
                    min_area_ratio <= area_ratio <= max_area_ratio):
                det['green_ratio'] = green_ratio
                det['area_ratio'] = area_ratio
                filtered.append(det)

        return filtered

    def run_inference(
        self,
        image_bgr: np.ndarray,
        conf_threshold: Optional[float] = None,
        imgsz: int = 640,
        enable_filtering: bool = True,
        min_green_ratio: float = 0.15,
        min_area_ratio: float = 0.001,
        max_area_ratio: float = 0.95
    ) -> Dict:
        """
        Run inference on image with enhanced filtering.

        Args:
            image_bgr: Input image in BGR format
            conf_threshold: Override confidence threshold
            imgsz: Input image size for model
            enable_filtering: Enable green detection filtering
            min_green_ratio: Minimum green content (0-1)
            min_area_ratio: Minimum box area ratio
            max_area_ratio: Maximum box area ratio

        Returns:
            Dictionary containing:
                - detections: List of detection dictionaries
                - raw_detections: Unfiltered detections
                - annotated_image_bgr: Annotated image
                - inference_time_ms: Inference time in milliseconds
                - filtering_stats: Statistics about filtering
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        conf = conf_threshold if conf_threshold is not None else self.conf_threshold

        # Run inference with higher IOU threshold to reduce overlapping boxes
        results = self._model.predict(
            image_bgr,
            conf=conf,
            iou=0.5,  # Higher IOU threshold for better NMS
            imgsz=imgsz,
            verbose=False,
            max_det=100  # Limit maximum detections
        )

        # Parse results
        raw_detections = []
        result = results[0]  # Single image

        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes[i]

                # Extract box data
                xyxy = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]
                conf_val = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self._model.names[cls_id]

                detection = {
                    'class_id': cls_id,
                    'class_name': cls_name,
                    'confidence': conf_val,
                    'bbox_xyxy': xyxy
                }
                raw_detections.append(detection)

        # Apply filtering if enabled
        if enable_filtering:
            filtered_detections = self.filter_detections(
                raw_detections,
                image_bgr,
                min_green_ratio=min_green_ratio,
                min_area_ratio=min_area_ratio,
                max_area_ratio=max_area_ratio
            )
            detections = filtered_detections

            filtering_stats = {
                'raw_count': len(raw_detections),
                'filtered_count': len(filtered_detections),
                'removed_count': len(raw_detections) - len(filtered_detections)
            }
        else:
            detections = raw_detections
            filtering_stats = {
                'raw_count': len(raw_detections),
                'filtered_count': len(raw_detections),
                'removed_count': 0
            }

        # Create annotated image with only filtered detections
        annotated_image_bgr = image_bgr.copy()

        if detections:
            for det in detections:
                x1, y1, x2, y2 = map(int, det['bbox_xyxy'])
                conf = det['confidence']
                cls_name = det['class_name']

                # Draw bounding box
                color = (0, 255, 0)  # Green
                cv2.rectangle(annotated_image_bgr,
                              (x1, y1), (x2, y2), color, 2)

                # Prepare label with confidence and green ratio if available
                label = f"{cls_name} {conf:.2f}"
                if 'green_ratio' in det:
                    label += f" (G:{det['green_ratio']:.2f})"

                # Draw label background
                (label_w, label_h), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                cv2.rectangle(
                    annotated_image_bgr,
                    (x1, y1 - label_h - 10),
                    (x1 + label_w + 10, y1),
                    color,
                    -1
                )

                # Draw label text
                cv2.putText(
                    annotated_image_bgr,
                    label,
                    (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                    cv2.LINE_AA
                )

        # Get inference time
        inference_time_ms = result.speed['inference'] if hasattr(
            result, 'speed') else 0

        return {
            'detections': detections,
            'raw_detections': raw_detections,
            'annotated_image_bgr': annotated_image_bgr,
            'inference_time_ms': inference_time_ms,
            'filtering_stats': filtering_stats
        }


# Global detector instance
detector = YOLODetector()


def initialize_detector(model_path: str = "models/best.pt", conf_threshold: float = 0.35):
    """
    Initialize the global detector instance.

    Args:
        model_path: Path to model weights
        conf_threshold: Confidence threshold (default: 0.35 for reduced false positives)
    """
    detector.load_model(model_path, conf_threshold)


def run_inference(image_bgr: np.ndarray, **kwargs) -> Dict:
    """
    Convenience function to run inference on global detector.

    Args:
        image_bgr: Input image in BGR format
        **kwargs: Additional arguments for detector.run_inference()
            - conf_threshold: Override confidence threshold
            - enable_filtering: Enable green detection filtering (default: True)
            - min_green_ratio: Minimum green content ratio (default: 0.15)
            - min_area_ratio: Minimum box area ratio (default: 0.001)
            - max_area_ratio: Maximum box area ratio (default: 0.95)

    Returns:
        Inference results dictionary with:
            - detections: Filtered detections
            - raw_detections: All detections before filtering
            - annotated_image_bgr: Annotated image
            - inference_time_ms: Inference time
            - filtering_stats: Statistics about filtering process
    """
    return detector.run_inference(image_bgr, **kwargs)


def get_detector() -> YOLODetector:
    """
    Get the global detector instance.

    Returns:
        YOLODetector instance
    """
    return detector
