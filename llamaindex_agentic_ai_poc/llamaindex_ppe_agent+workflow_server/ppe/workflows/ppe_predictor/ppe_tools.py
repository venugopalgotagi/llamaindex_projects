from typing import List

import ultralytics.engine.results
from ultralytics import YOLO

yolo_model :YOLO = YOLO('ppe/workflows/ppe_predictor/model/best.pt')


async def ppe_risk_analyser(user_id:str,site_id:str,image:str) ->bool | None:
    """
    Analyse image for ppe violations
    :param user_id:
    :param site_id:
    :param image:
    :return:
    """
    print('ppe_risk_analyser working')
    global yolo_response
    try:
        detected_objects = await predict_model(image)
        if detected_objects and len(detected_objects) > 0:
            from collections import Counter
            classes_counts = set(Counter(detected_objects[0]))
            if 'Person' in classes_counts:
                return  ('helmet' not in classes_counts or 'gloves' not in classes_counts or 'vest' not in classes_counts or 'boots' not in classes_counts)
            else:
                return None
        return None



    except Exception as ex:
        import traceback ,logging
        logging.error(ex)
        traceback.print_exc()
        raise RuntimeError(f'Unable to analyse image from site {site_id} for  PPE compliance')


async def predict_model(image: str) -> list[str]:
    global yolo_response
    import base64
    from io import BytesIO
    from PIL import Image
    img_bytes = base64.b64decode(image)
    import numpy as np
    img_np = np.frombuffer(img_bytes, np.uint8)
    import cv2
    img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    yolo_responses: List[ultralytics.engine.results.Results] = yolo_model.predict(img_cv2)
    if yolo_responses and len(yolo_responses) > 0:
        yolo_response = yolo_responses[0]
    detected_objects = []
    if yolo_response.boxes is not None:
        detected_objects.append([yolo_model.names[int(c)] for c in yolo_response.boxes.cls])
    return detected_objects