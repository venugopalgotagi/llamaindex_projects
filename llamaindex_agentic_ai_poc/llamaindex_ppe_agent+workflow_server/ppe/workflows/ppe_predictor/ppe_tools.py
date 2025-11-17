"""PPE prediction tools using YOLO model.

This module provides tools for analyzing images to detect PPE violations
using a YOLO (You Only Look Once) object detection model.
"""

import base64
import logging
import traceback
from collections import Counter
from io import BytesIO
from typing import List

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import ultralytics.engine.results

yolo_model: YOLO = YOLO('ppe/workflows/ppe_predictor/model/best.pt')


async def ppe_risk_analyser(
    user_id: str,
    site_id: str,
    image: str
) -> bool | None:
    """Analyze an image for PPE violations.

    Processes a base64-encoded image to detect PPE violations using YOLO.
    Checks if persons are detected and whether they are wearing required
    PPE items (helmet, gloves, vest, boots).

    Args:
        user_id: Identifier for the user associated with the image.
        site_id: Identifier for the site where the image was captured.
        image: Base64-encoded image data.

    Returns:
        True if violations are detected (person found without required PPE),
        None if no person is detected or if an error occurs.

    Raises:
        RuntimeError: If image analysis fails for any reason.
    """
    print('ppe_risk_analyser working')
    try:
        detected_objects = await predict_model(image)
        if detected_objects and len(detected_objects) > 0:
            classes_counts = set(Counter(detected_objects[0]))
            if 'Person' in classes_counts:
                return (
                    'helmet' not in classes_counts or
                    'gloves' not in classes_counts or
                    'vest' not in classes_counts or
                    'boots' not in classes_counts
                )
            else:
                return None
        return None

    except Exception as ex:
        logging.error(ex)
        traceback.print_exc()
        raise RuntimeError(
            f'Unable to analyse image from site {site_id} for PPE compliance'
        )


async def predict_model(image: str) -> List[List[str]]:
    """Predict objects in an image using YOLO model.

    Decodes a base64-encoded image and runs YOLO object detection to
    identify objects present in the image.

    Args:
        image: Base64-encoded image data.

    Returns:
        List of lists containing detected object class names. Each inner
        list represents detections from one image (currently single image).
    """
    img_bytes = base64.b64decode(image)
    img_np = np.frombuffer(img_bytes, np.uint8)
    img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    yolo_responses: List[ultralytics.engine.results.Results] = (
        yolo_model.predict(img_cv2)
    )

    detected_objects = []
    if yolo_responses and len(yolo_responses) > 0:
        yolo_response = yolo_responses[0]
        if yolo_response.boxes is not None:
            detected_objects.append([
                yolo_model.names[int(c)]
                for c in yolo_response.boxes.cls
            ])
    return detected_objects
