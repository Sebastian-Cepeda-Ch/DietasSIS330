from fastapi import FastAPI
from pydantic import BaseModel
# Importa TODAS las funciones de tu lógica
from logic import (
    calculate_bmr, 
    calcular_somatotipo_simplificado, 
    determinar_somatotipo_dominante
)
from gemini_client import get_diet_plan 
import json

app = FastAPI()

# Modelo de ENTRADA: Pedimos los CM manualmente
class UserInput(BaseModel):
    age: int
    gender: str # 'male' or 'female'
    current_weight_kg: float
    height_cm: float
    activity_level: str # 'sedentary', 'light', 'moderate', 'active'
    goal: str # 'lose weight', 'maintain', 'gain muscle'
    
    # --- SIMULACIÓN DE MEDIAPIPE ---
    # Pedimos los datos en CM manualmente
    shoulder_width_cm: float 
    hip_width_cm: float
    shoulder_hip_dist_cm: float # Simplificado a una sola medida promedio
    
    
@app.get("/")
def read_root():
    return {"Status": "Diet App API running"}


# ... (definición de app y UserInput) ...
    
    # ... (app, UserInput)
@app.post("/generate-prototype-diet")
def generate_diet(user_data: UserInput):
    
    # 1. Calcular BMR
    bmr = calculate_bmr(
        user_data.gender, 
        user_data.current_weight_kg, 
        user_data.height_cm, 
        user_data.age
    )
    
    # 2. Calcular Somatotipo (con tu función)
    endo, meso, ecto = calcular_somatotipo_simplificado(
        user_data.current_weight_kg,
        user_data.height_cm,
        user_data.shoulder_width_cm,
        user_data.hip_width_cm,
        user_data.shoulder_hip_dist_cm
    )
    
    # 3. Determinar dominante (para Gemini)
    somatotipo_dominante = determinar_somatotipo_dominante(endo, meso, ecto)
    
    # 4. Llamar a GEMINI (ahora con el somatotipo)
    diet_json = get_diet_plan(
        user_data.age,
        user_data.gender,
        user_data.current_weight_kg,
        user_data.height_cm,
        somatotipo_dominante, # ¡Mucho mejor para el prompt!
        user_data.goal,
        user_data.activity_level,
        bmr
    )
    
    # 5. SIMULAR PREDICCIÓN (Igual que antes)
    target_calories = diet_json.get("resumen_dieta", {}).get("calorias_objetivo_diarias", 2000)
    activity_multiplier = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
    calories_out = bmr * activity_multiplier.get(user_data.activity_level, 1.2)
    daily_deficit = calories_out - target_calories
    predicted_change_kg_4_weeks = (daily_deficit * 28) / 7700

    # 6. Devolver TODO
    return {
        "user_info": user_data,
        "somatotype_analysis": {
            "components": f"Endo: {endo}, Meso: {meso}, Ecto: {ecto}",
            "dominant_profile": somatotipo_dominante
        },
        "diet_plan_from_gemini": diet_json,
        "simple_prediction": {
            "predicted_weight_change_in_4_weeks_kg": round(predicted_change_kg_4_weeks, 2),
            "disclaimer": "Predicción simple basada en fórmula, no en modelo ML."
        }
    }