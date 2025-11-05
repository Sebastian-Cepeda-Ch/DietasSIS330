import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv() # Carga el archivo .env

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro')

def get_diet_plan(age, gender, weight, height, somatotype, goal, activity_level, bmr):

    # Este es el prompt "maestro". Es la clave.
    prompt = f"""
    Eres un nutricionista experto de IA. Tu tarea es generar un plan de dieta.
    El usuario es un: {gender} de {age} años.
    Pesa: {weight} kg y mide: {height} cm.
    Su somatotipo es: {somatotype}.
    Su nivel de actividad es: {activity_level}.
    Su objetivo es: {goal}.
    Su Tasa Metabólica Basal (BMR) calculada es: {bmr} calorías.

    Basado en TODOS estos datos, genera un plan de comidas simple para UN (1) día.
    El plan debe ser balanceado y alineado con su somatotipo y objetivo.

    Devuelve tu respuesta ESTRICTAMENTE en formato JSON, usando esta estructura exacta:
    {{
      "resumen_dieta": {{
        "calorias_objetivo_diarias": <int>,
        "proteinas_gramos": <int>,
        "carbohidratos_gramos": <int>,
        "grasas_gramos": <int>
      }},
      "plan_dia_1": {{
        "desayuno": "<descripcion detallada>",
        "almuerzo": "<descripcion detallada>",
        "cena": "<descripcion detallada>",
        "snack": "<descripcion detallada>"
      }},
      "disclaimer": "Este es un plan generado por IA. Consulta a un profesional."
    }}
    """

    try:
        response = model.generate_content(prompt)
        # Extraemos el texto, que debería ser un string JSON
        json_text = response.text.strip().replace("```json", "").replace("```", "")

        # Convertimos el string a un diccionario de Python
        diet_plan = json.loads(json_text)
        return diet_plan

    except Exception as e:
        print(f"Error al llamar a Gemini o parsear JSON: {e}")
        return {"error": "No se pudo generar la dieta. Intenta de nuevo."}