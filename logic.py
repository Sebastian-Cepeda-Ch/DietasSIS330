import math

def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    """Mifflin-St Jeor Formula"""
    if gender.lower() == 'male':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    return int(bmr)

def calcular_somatotipo_scores(
    peso_kg: float, 
    estatura_cm: float, 
    ancho_hombros_cm: float, 
    ancho_caderas_cm: float, 
    dist_hombro_cadera_cm: float, 
    factor_escala_meso: float = 10.0
) -> dict:
    """
    Retorna un diccionario con los scores individuales.
    """
    
    # 1. ECTOMORFIA (Indice Ponderal)
    ip = estatura_cm / math.pow(peso_kg, 1/3)
    if ip >= 40.75:
        ecto = (0.732 * ip) - 28.58
    elif ip > 38.25:
        ecto = (0.463 * ip) - 17.63
    else:
        ecto = 0.1
    ecto = max(0.1, ecto)

    # 2. ENDOMORFIA (Proxy IMC)
    estatura_m = estatura_cm / 100.0
    if estatura_m > 0:
        imc = peso_kg / (estatura_m ** 2)
        endo = (imc * 0.7) - 7.0
        endo = max(0.5, endo)
    else:
        endo = 5.0 # Fallback

    # 3. MESOMORFIA (Robustez)
    robustez = ancho_hombros_cm + ancho_caderas_cm + dist_hombro_cadera_cm
    if estatura_cm > 0:
        meso = (robustez / estatura_cm) * factor_escala_meso
    else:
        meso = 0.5
    meso = max(0.5, meso)

    return {
        "endo": round(endo, 1),
        "meso": round(meso, 1),
        "ecto": round(ecto, 1)
    }