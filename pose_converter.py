import cv2
import mediapipe as mp
import numpy as np
import math

# Inicializar MediaPipe una sola vez para no recargar el modelo en cada petición
mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

def _get_distance(p1, p2):
    """Calcula distancia Euclidiana entre tuplas (x, y)"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def process_image_for_measurements(image_bytes: bytes, estatura_real_cm: float) -> dict:
    """
    Recibe la imagen en bytes (desde FastAPI), corre MediaPipe,
    y calcula las medidas en CM usando la estatura para calibrar.
    """
    
    # 1. Convertir bytes a imagen OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        return {"error": "No se pudo decodificar la imagen."}

    # 2. Convertir a RGB (MediaPipe lo requiere)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 3. Procesar con MediaPipe
    results = pose_model.process(image_rgb)
    
    if not results.pose_landmarks:
        return {"error": "No se detectó ninguna persona en la imagen. Intenta con una foto más clara."}

    landmarks = results.pose_landmarks.landmark
    h, w, _ = image.shape

    # 4. Extraer Puntos Clave (Convertimos de normalizado a Píxeles aquí mismo)
    # Indices: 11=HombroIzq, 12=HombroDer, 23=CaderaIzq, 24=CaderaDer, 29=TalonIzq, 30=TalonDer, 0=Nariz
    
    def to_px(lm):
        return (lm.x * w, lm.y * h)

    nose = to_px(landmarks[0])
    l_shoulder = to_px(landmarks[11])
    r_shoulder = to_px(landmarks[12])
    l_hip = to_px(landmarks[23])
    r_hip = to_px(landmarks[24])
    l_heel = to_px(landmarks[29])
    r_heel = to_px(landmarks[30])

    # 5. Calcular Estatura en Píxeles (Calibración)
    # Usamos la Y de la nariz hasta el promedio de Y de los talones
    top_y = nose[1]
    bottom_y = (l_heel[1] + r_heel[1]) / 2.0
    estatura_px = abs(bottom_y - top_y)

    if estatura_px == 0:
        return {"error": "Error de calibración: Altura en píxeles irreconocible."}

    # FACTOR DE CONVERSIÓN
    cm_per_pixel = estatura_real_cm / estatura_px

    # 6. Calcular distancias en Píxeles
    ancho_hombros_px = _get_distance(l_shoulder, r_shoulder)
    ancho_caderas_px = _get_distance(l_hip, r_hip)
    
    # Distancia torso (promedio de los dos lados)
    torso_left_px = _get_distance(l_shoulder, l_hip)
    torso_right_px = _get_distance(r_shoulder, r_hip)
    torso_avg_px = (torso_left_px + torso_right_px) / 2.0

    # 7. Convertir a CM y retornar
    return {
        "ancho_hombros_cm": round(ancho_hombros_px * cm_per_pixel, 2),
        "ancho_caderas_cm": round(ancho_caderas_px * cm_per_pixel, 2),
        "dist_hombro_cadera_cm": round(torso_avg_px * cm_per_pixel, 2)
    }