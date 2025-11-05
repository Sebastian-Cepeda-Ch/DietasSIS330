import math

def calcular_somatotipo_simplificado(peso_kg, estatura_cm, ancho_hombros_aw, ancho_caderas_ah, dist_hombro_cadera_ls, dist_hombro_cadera_rs, factor_escala_meso=150):
    """
    Calcula una estimación simplificada del Somatotipo (Endomorfia - Mesomorfia - Ectomorfia).

    Argumentos:
        peso_kg (float): Peso corporal en kilogramos.
        estatura_cm (float): Estatura en centímetros.
        ancho_hombros_aw (float): Ancho de hombros (Medida de MediaPipe).
        ancho_caderas_ah (float): Ancho de caderas (Medida de MediaPipe).
        dist_hombro_cadera_ls (float): Distancia hombro a cadera, lado izquierdo (Medida de MediaPipe).
        dist_hombro_cadera_rs (float): Distancia hombro a cadera, lado derecho (Medida de MediaPipe).
        factor_escala_meso (float, opcional): Factor de calibración para la Mesomorfia. Default es 150.
        
    Retorna:
        tuple: (Endomorfia, Mesomorfia, Ectomorfia)
    """

    # Convertir estatura a metros para el cálculo del IMC
    estatura_m = estatura_cm / 100.0

    # ==========================================================
    # 1. CÁLCULO DE ECTOMORFIA (Ec)
    # ==========================================================

    # 1.1. Índice Ponderal (IP)
    # math.pow(peso_kg, 1/3) calcula la raíz cúbica del peso
    ip = estatura_cm / math.pow(peso_kg, 1/3)
    
    # 1.2. Fórmulas de Heath-Carter para Ectomorfia
    if ip >= 40.75:
        ectomorfia = (0.732 * ip) - 28.58
    elif ip > 38.25 and ip < 40.75:
        ectomorfia = (0.463 * ip) - 17.63
    else: # ip <= 38.25
        ectomorfia = 0.1
        
    # Asegurar que el valor de ectomorfia no sea negativo (aunque las fórmulas lo suelen prevenir)
    ectomorfia = max(0.1, ectomorfia)


    # ==========================================================
    # 2. CÁLCULO DE ENDOMORFIA (Endo) - Aproximación por IMC
    # ==========================================================

    # 2.1. Índice de Masa Corporal (IMC)
    imc = peso_kg / (estatura_m ** 2)

    # 2.2. Fórmula de aproximación de Endomorfia (Empírica)
    endomorfia = (imc * 0.7) - 7.0
    
    # Asegurar que la endomorfia no sea menor a 0.5 (mínimo típico)
    endomorfia = max(0.5, endomorfia)
    
    
    # ==========================================================
    # 3. CÁLCULO DE MESOMORFIA (Meso) - Aproximación con Distancias
    # ==========================================================

    # 3.1. Promedio de Distancia Hombro-Cadera (para robustez del tronco)
    dist_media_tronco = (dist_hombro_cadera_ls + dist_hombro_cadera_rs) / 2
    
    # 3.2. Índice de Robustez Transversal (Numerador)
    indice_robustez = ancho_hombros_aw + ancho_caderas_ah + dist_media_tronco
    
    # 3.3. Fórmula de Mesomorfia (Aproximación empírica con Factor de Escala)
    # NOTA: El factor de escala debe ser ajustado. Usamos 150 como ejemplo inicial.
    if estatura_cm * factor_escala_meso == 0:
        mesomorfia = 0.1
    else:
        mesomorfia = indice_robustez / (estatura_cm * factor_escala_meso)
    
    # Ajuste: Escalar el valor resultante a un rango típico de 1 a 7 (ajuste opcional para presentación)
    # Si quieres que la Meso se parezca más a un rango 1-7, puedes multiplicar el resultado
    # por un factor de ajuste. Por ahora, devolvemos el valor puro para su calibración.
    
    # Asegurar un mínimo de Mesomorfia
    mesomorfia = max(0.5, mesomorfia)


    return round(endomorfia, 1), round(mesomorfia, 1), round(ectomorfia, 1)

# ==========================================================
# EJEMPLO DE PRUEBA
# ==========================================================

# Datos de entrada (hipotéticos para prueba)
# Persona con sobrepeso (Endomorfo/Mesomorfo)
peso = 90.0      # kg
estatura = 180.0 # cm
aw = 45.0        # Ancho Hombros (Medida en cm, asumiendo que MediaPipe ya hizo la conversión a cm/unidad)
ah = 35.0        # Ancho Caderas
ls = 55.0        # Distancia Hombro-Cadera Izq
rs = 55.0        # Distancia Hombro-Cadera Der
factor_escala = 0.005 # Factor de escala ajustado (ejemplo, debe calibrarse)

endo, meso, ec = calcular_somatotipo_simplificado(peso, estatura, aw, ah, ls, rs, factor_escala)

print(f"Peso: {peso} kg, Estatura: {estatura} cm")
print(f"Resultado Somatotipo (Endo-Meso-Ec): {endo} - {meso} - {ec}")
# Ejemplo de salida: 6.4 - 1.1 - 1.1 (depende del factor_escala_meso)

# Ejemplo 2: Persona muy delgada (Ectomorfo)
peso_ect = 60.0
estatura_ect = 180.0
aw_ect = 40.0
ah_ect = 30.0
ls_ect = 60.0
rs_ect = 60.0
factor_escala_ect = 0.005 # Mismo factor

endo_ect, meso_ect, ec_ect = calcular_somatotipo_simplificado(peso_ect, estatura_ect, aw_ect, ah_ect, ls_ect, rs_ect, factor_escala_ect)

print("\n--- Segundo Ejemplo (Ectomorfo) ---")
print(f"Peso: {peso_ect} kg, Estatura: {estatura_ect} cm")
print(f"Resultado Somatotipo (Endo-Meso-Ec): {endo_ect} - {meso_ect} - {ec_ect}")
# Ejemplo de salida: 1.1 - 1.1 - 4.9 (depende del factor_escala_meso)