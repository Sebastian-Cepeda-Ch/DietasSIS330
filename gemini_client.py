import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv() 

# Usamos Flash porque es rápido y eficiente para JSON
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro') 

def get_diet_plan(form_data, somato_scores, bmr):
    
    # Construir strings de contexto
    location_str = f"{form_data.city}, {form_data.country}" if form_data.city else form_data.country
    
    medical_str = "Ninguna reportada."
    if form_data.medical_conditions:
        medical_str = form_data.medical_conditions

    prompt = f"""
    [ROL]
    Eres un nutricionista experto clínico y deportivo.
    
    [PERFIL DEL USUARIO]
    - Ubicación: {location_str} (Prioridad: Alimentos locales y económicos).
    - Biometría: {form_data.gender}, {form_data.age} años, {form_data.current_weight_kg}kg, {form_data.height_cm}cm.
    - BMR: {bmr} kcal.
    - Objetivo: {form_data.goal}.
    - Somatotipo: Endo {somato_scores['endo']} / Meso {somato_scores['meso']} / Ecto {somato_scores['ecto']}.
    - Condiciones Médicas: "{medical_str}" (RESPETAR ESTRICTAMENTE).

    [DIRECTRICES DE GENERACIÓN - CRÍTICO]
    
    1. ECONOMÍA Y SUPLEMENTACIÓN:
       - PROHIBIDO RECETAR SUPLEMENTOS (Whey, Creatina, etc.) a menos que sea médicamente inevitable.
       - Prioriza FUENTES NATURALES: Huevos, pollo, carne, legumbres, lácteos.
       - La dieta debe ser ECONÓMICA y accesible en {form_data.country}.

    2. PRECISIÓN ABSOLUTA DE MEDIDAS:
       - NUNCA uses términos vagos como "un poco", "una porción", "a gusto".
       - SIEMPRE especifica la cantidad VISUAL y MÉTRICA.
       - MALO: "Arroz con pollo" o "1/2 taza de avena".
       - BUENO: "150g de Pechuga de Pollo (tamaño de una mano abierta)" o "40g de Avena (4 cucharadas soperas)".
       - Para unidades (frutas, huevos): Especifica tamaño (ej. "1 unidad MEDIANA").

    3. ESTRATEGIA SEMANAL 5+2 (FLEXIBILIDAD):
       - Días 1 a 5 (Lunes-Viernes): Dieta ESTRICTA y detallada para cumplir el objetivo.
       - Días 6 y 7 (Fines de Semana): DÍAS DE CONTROL FLEXIBLE (NO dieta estricta).
       - Para los días 6 y 7, en lugar de recetas específicas, da PAUTAS GENERALES de comportamiento (ej. "Comida libre alta en proteína, moderar alcohol, evitar frituras profundas").

    [TAREA]
    Genera el plan semanal JSON siguiendo la estructura exacta abajo.

    [FORMATO JSON REQUERIDO]
    Responde SOLO con un JSON válido:
    {{
      "analisis_inicial": {{
        "interpretacion_somatotipo": "...",
        "estrategia_economica": "Breve nota sobre cómo esta dieta cuida el bolsillo y evita suplementos."
      }},
      "resumen_nutricional": {{
        "calorias_diarias_objetivo": <int>,
        "macros": {{ "proteina_g": <int>, "carbos_g": <int>, "grasa_g": <int> }}
      }},
      "plan_semanal_rotativo": {{
        "dia_1": {{ "desayuno": "...", "almuerzo": "...", "cena": "...", "snack": "..." }},
        "dia_2": {{ "desayuno": "...", "almuerzo": "...", "cena": "...", "snack": "..." }},
        "dia_3": {{ "desayuno": "...", "almuerzo": "...", "cena": "...", "snack": "..." }},
        "dia_4": {{ "desayuno": "...", "almuerzo": "...", "cena": "...", "snack": "..." }},
        "dia_5": {{ "desayuno": "...", "almuerzo": "...", "cena": "...", "snack": "..." }},
        "dia_6_flexible": {{ 
             "desayuno": "LIBRE: Recomendación (ej. Huevos revueltos con lo que gustes, evita pan dulce)", 
             "almuerzo": "LIBRE: Recomendación (ej. Disfruta una comida social, prioriza la carne)", 
             "cena": "LIGERA: Recomendación (ej. Algo suave para compensar el día)", 
             "snack": "Opcional" 
        }},
        "dia_7_flexible": {{ 
             "desayuno": "LIBRE: Recomendación...", 
             "almuerzo": "LIBRE: Recomendación...", 
             "cena": "LIGERA: Recomendación...", 
             "snack": "Opcional" 
        }}
      }},
      "lista_compras_semanal": ["item1", "item2"]
    }}
    """

    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"Error Gemini: {e}")
        return {"error": "Fallo al generar dieta", "details": str(e)}