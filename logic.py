# En logic.py
import math

def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    """
    Calcula la Tasa Metabólica Basal (BMR) usando la fórmula de Mifflin-St Jeor.
    """
    if gender == 'male':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    return bmr

def calcular_somatotipo_simplificado(
    peso_kg: float, 
    estatura_cm: float, 
    ancho_hombros_cm: float, 
    ancho_caderas_cm: float, 
    dist_hombro_cadera_cm: float, 
    factor_escala_meso: float = 10.0  # Factor de escala ajustado
) -> tuple:
    """
    Calcula una estimación simplificada del Somatotipo (Endo - Meso - Ec).
    Usa fórmulas estándar para Endo (IMC) y Ecto (Ponderal), y una
    aproximación escalada para Meso.
    """
    
    # --- 1. ECTOMORFIA (Índice Ponderal) ---
    ip = estatura_cm / math.pow(peso_kg, 1/3)
    if ip >= 40.75:
        ectomorfia = (0.732 * ip) - 28.58
    elif ip > 38.25 and ip < 40.75:
        ectomorfia = (0.463 * ip) - 17.63
    else: # ip <= 38.25
        ectomorfia = 0.1
    ectomorfia = max(0.1, ectomorfia)

    # --- 2. ENDOMORFIA (Proxy de IMC) ---
    estatura_m = estatura_cm / 100.0
    if estatura_m == 0: # Evitar división por cero
        return (0.5, 0.5, 0.1) 
        
    imc = peso_kg / (estatura_m ** 2)
    endomorfia = (imc * 0.7) - 7.0
    endomorfia = max(0.5, endomorfia)
    
    # --- 3. MESOMORFIA (Aproximación por Robustez) ---
    # (Usamos una sola medida de dist_hombro_cadera para simplificar la entrada)
    indice_robustez = ancho_hombros_cm + ancho_caderas_cm + dist_hombro_cadera_cm
    
    # Fórmula Corregida: (Robustez / Estatura) * FactorEscala
    if estatura_cm == 0:
        mesomorfia = 0.5
    else:
        mesomorfia = (indice_robustez / estatura_cm) * factor_escala_meso
        
    mesomorfia = max(0.5, mesomorfia)

    return round(endomorfia, 1), round(mesomorfia, 1), round(ectomorfia, 1)


def determinar_somatotipo_dominante(endo: float, meso: float, ecto: float) -> str:
    """
    Determina la categoría dominante para enviar a Gemini.
    """
    if endo > meso and endo > ecto:
        return "Endomorfo"
    elif meso > endo and meso > ecto:
        return "Mesomorfo"
    elif ecto > endo and ecto > meso:
        return "Ectomorfo"
    elif endo + meso > ecto:
        return "Endo-Mesomorfo"
    elif ecto + meso > endo:
        return "Ecto-Mesomorfo"
    else:
        return "Balanceado"