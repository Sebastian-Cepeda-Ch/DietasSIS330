from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORTANTE
from pydantic import BaseModel
from typing import List, Dict, Optional
import json

# Tus imports de lógica
from logic import calculate_bmr, calcular_somatotipo_scores
from gemini_client import get_diet_plan
from pose_converter import process_image_for_measurements

app = FastAPI()

# --- 1. CONFIGURACIÓN DE PERMISOS (CORS) ---
# Este bloque debe estar JUSTO AQUÍ, antes de los endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # "*" permite conectarse desde cualquier origen (localhost:5500, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# --- 2. MODELOS DE DATOS ---
class UserFormData(BaseModel):
    age: int
    gender: str 
    current_weight_kg: float
    height_cm: float
    activity_level: str 
    goal: str 
    country: str
    city: Optional[str] = None
    medical_conditions: Optional[str] = "Ninguna"

# --- 3. ENDPOINTS ---

@app.get("/")
def read_root():
    return {"Status": "API de Dietas Inteligente - ACTIVA"}

@app.post("/generate-diet-with-image")
async def generate_diet_with_image(
    # Recibimos datos como Form fields
    age: int = Form(...),
    gender: str = Form(...),
    current_weight_kg: float = Form(...),
    height_cm: float = Form(...),
    activity_level: str = Form(...),
    goal: str = Form(...),
    country: str = Form(...),
    city: str = Form(None),
    medical_conditions: str = Form("Ninguna"),
    # Recibimos la imagen
    file: UploadFile = File(...) 
):
    
    # A. LEER LA IMAGEN
    image_bytes = await file.read()
    
    # B. PROCESAR MEDIAPIPE EN EL BACKEND
    medidas_cm = process_image_for_measurements(image_bytes, height_cm)
    
    if "error" in medidas_cm:
        # Si no detecta persona, lanzamos error 400
        raise HTTPException(status_code=400, detail=medidas_cm["error"])

    # C. PREPARAR DATOS PARA GEMINI
    # Reconstruimos el objeto form_data manual para pasarlo a las funciones
    class FormDataObj:
        def __init__(self):
            self.age = age
            self.gender = gender
            self.current_weight_kg = current_weight_kg
            self.height_cm = height_cm
            self.activity_level = activity_level
            self.goal = goal
            self.country = country
            self.city = city
            self.medical_conditions = medical_conditions
    
    form_data_obj = FormDataObj()

    # Calcular Somatotipo
    somato_scores = calcular_somatotipo_scores(
        peso_kg=current_weight_kg,
        estatura_cm=height_cm,
        ancho_hombros_cm=medidas_cm["ancho_hombros_cm"],
        ancho_caderas_cm=medidas_cm["ancho_caderas_cm"],
        dist_hombro_cadera_cm=medidas_cm["dist_hombro_cadera_cm"]
    )

    # Calcular BMR
    bmr = calculate_bmr(gender, current_weight_kg, height_cm, age)

    # D. LLAMAR A GEMINI (Tu Prompt corregido ya está en gemini_client.py)
    diet_response = get_diet_plan(
        form_data=form_data_obj,
        somato_scores=somato_scores,
        bmr=bmr
    )

    # E. PREDICCIÓN DE PESO (Cálculo simple)
    # Intentamos leer las calorias objetivo, si falla usamos 2000 por defecto
    try:
        target_cal = diet_response.get("resumen_nutricional", {}).get("calorias_diarias_objetivo", 2000)
    except:
        target_cal = 2000
        
    # Factores de actividad
    act_factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
    factor = act_factors.get(activity_level, 1.2)
    
    daily_burn = bmr * factor
    daily_deficit = daily_burn - target_cal
    
    # 7700 kcal = 1kg grasa aprox. Predicción a 28 días.
    weight_loss_kg = (daily_deficit * 28) / 7700
    final_weight_pred = current_weight_kg - weight_loss_kg

    # F. RESPUESTA FINAL JSON
    return {
        "status": "success",
        "user_profile": {
            "biometrics": medidas_cm,
            "somatotype_scores": somato_scores
        },
        "diet_plan": diet_response,
        "prediction_4_weeks": {
            "estimated_final_weight_kg": round(final_weight_pred, 2),
            "estimated_loss_kg": round(weight_loss_kg, 2)
        }
    }