import numpy as np
import scipy.stats as stats
import math
from collections import Counter

def test_medias(numbers: list[float], alpha: float = 0.05) -> dict:
    """
    Prueba de Medias:
    Verifica que el valor esperado de los números sea 0.5 (uniformidad).
    """
    n = len(numbers)
    if n == 0:
        return {"error": "No hay números para analizar"}
    
    # 1. Calculamos la media de la muestra
    media = sum(numbers) / n
    
    # 2. Calculamos el estadístico Z_0
    # La desviación estándar teórica de U(0,1) es 1/sqrt(12)
    # z0 = (media - 0.5) * sqrt(12 * n)
    z0 = (media - 0.5) * math.sqrt(12 * n)
    
    # 3. Buscamos el valor Z de la distribución normal (a dos colas)
    z_alpha_2 = stats.norm.ppf(1 - alpha / 2)
    
    # 4. Determinamos los límites de aceptación para la media
    limite_inferior = 0.5 - z_alpha_2 * (1 / math.sqrt(12 * n))
    limite_superior = 0.5 + z_alpha_2 * (1 / math.sqrt(12 * n))
    
    # 5. La prueba pasa si |Z0| < Z_alpha/2 (equivalente a que la media esté en los límites)
    passed = bool(abs(z0) < z_alpha_2)
    
    return {
        "test": "Prueba de Medias",
        "passed": passed,
        "details": {
            "n": n,
            "media": media,
            "z0": z0,
            "z_alpha_2": z_alpha_2,
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
            "alpha": alpha
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \mu = 0.5 \\
        \bar{x} &= \frac{1}{n}\sum x_i = """ + f"{media:.4f}" + r""" \\
        Z_0 &= (\bar{x} - 0.5)\sqrt{12n} = """ + f"{z0:.4f}" + r""" \\
        Z_{\alpha/2} &= """ + f"{z_alpha_2:.4f}" + r""" \\
        \end{align*}
        """
    }

def test_variancia(numbers: list[float], alpha: float = 0.05) -> dict:
    """
    Prueba de Varianza:
    Verifica que la varianza de los números sea 1/12 (uniformidad).
    """
    n = len(numbers)
    if n <= 1:
         return {"error": "Se requieren al menos 2 números para la varianza"}
    
    media = sum(numbers) / n
    
    # 1. Calculamos la varianza muestral
    varianza = sum((x - media)**2 for x in numbers) / (n - 1)
    
    # 2. Calculamos los valores críticos de Chi-cuadrado
    # Para la prueba de 2 colas, se usa alpha/2 y 1-alpha/2 con n-1 grados de libertad
    chi2_inf = stats.chi2.ppf(alpha / 2, n - 1)
    chi2_sup = stats.chi2.ppf(1 - alpha / 2, n - 1)
    
    # 3. Calculamos los límites de aceptación para la varianza
    limite_inferior = chi2_inf / (12 * (n - 1))
    limite_superior = chi2_sup / (12 * (n - 1))
    
    # 4. La prueba pasa si la varianza está dentro de los límites
    passed = bool(limite_inferior <= varianza <= limite_superior)
    
    return {
        "test": "Prueba de Varianza",
        "passed": passed,
        "details": {
            "n": n,
            "varianza": varianza,
            "chi2_inf": chi2_inf,
            "chi2_sup": chi2_sup,
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
            "alpha": alpha
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \sigma^2 = \frac{1}{12} \\
        V(x) &= \frac{\sum (x_i - \bar{x})^2}{n-1} = """ + f"{varianza:.4f}" + r""" \\
        L_I &= \frac{\chi^2_{\alpha/2, n-1}}{12(n-1)} = """ + f"{limite_inferior:.4f}" + r""" \\
        L_S &= \frac{\chi^2_{1-\alpha/2, n-1}}{12(n-1)} = """ + f"{limite_superior:.4f}" + r"""
        \end{align*}
        """
    }

def test_chi_cuadrada(numbers: list[float], alpha: float = 0.05, num_intervals: int = 0) -> dict:
    """
    Prueba Chi-Cuadrada (Bondad de Ajuste):
    Divide el rango [0,1) en intervalos y cuenta la frecuencia observada,
    comparando con la frecuencia esperada (n/m).
    """
    n = len(numbers)
    # 1. Determinar número de intervalos sugeridos si no se especifica
    if num_intervals <= 0:
        num_intervals = int(math.sqrt(n))
        if num_intervals < 5: num_intervals = 5  # Por regla de Freedman / regla general
        
    m = num_intervals
    frecuencia_esperada = n / m
    
    # 2. Contar frecuencias observadas
    frecuencias_observadas = [0] * m
    for x in numbers:
        # Encontrar el índice del intervalo para x
        idx = int(x * m)
        if idx == m: idx = m - 1 # Por si x es exactamente 1.0
        frecuencias_observadas[idx] += 1
        
    # 3. Calcular estadístico C (Chi-cuadrado observado)
    chi2_obs = sum(((fo - frecuencia_esperada)**2) / frecuencia_esperada for fo in frecuencias_observadas)
    
    # 4. Calcular el valor crítico de Chi-cuadrado con m-1 grados de libertad
    grados_libertad = m - 1
    chi2_critico = stats.chi2.ppf(1 - alpha, grados_libertad)
    
    # 5. Si chi2_obs es menor al critico, aceptamos uniformidad
    passed = bool(chi2_obs < chi2_critico)
    
    return {
        "test": "Prueba Chi-Cuadrada",
        "passed": passed,
        "details": {
            "n": n,
            "m": m,
            "frecuencia_esperada": frecuencia_esperada,
            "frecuencias_observadas": frecuencias_observadas,
            "chi2_obs": chi2_obs,
            "chi2_critico": chi2_critico,
            "grados_libertad": grados_libertad,
            "alpha": alpha
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \text{Los números se distribuyen uniformemente} \\
        FE_i &= \frac{n}{m} = """ + f"{frecuencia_esperada:.2f}" + r""" \\
        C &= \sum_{i=1}^m \frac{(FO_i - FE_i)^2}{FE_i} = """ + f"{chi2_obs:.4f}" + r""" \\
        \chi^2_{1-\alpha, m-1} &= """ + f"{chi2_critico:.4f}" + r"""
        \end{align*}
        """
    }

def test_poker(numbers: list[float], alpha: float = 0.05) -> dict:
    """
    Prueba de Poker (Independencia):
    Evalúa la secuencia de decimales (normalmente 5) para clasificar
    en categorías similares al juego de Poker.
    """
    n = len(numbers)
    # Probabilidades teóricas para 5 decimales
    # TD: Todos diferentes, 1P: Un par, 2P: Dos pares, T: Tercia, FH: Full House, P: Poker, Q: Quintilla
    probs = {
        "TD": 0.3024,
        "1P": 0.5040,
        "2P": 0.1080,
        "T":  0.0720,
        "FH": 0.0090,
        "P":  0.0045,
        "Q":  0.0001
    }
    
    fo = {k: 0 for k in probs.keys()}
    
    # 1. Clasificamos cada número en una categoría
    for num in numbers:
        # Tomar los primeros 5 decimales como string
        s = f"{num:.5f}".split(".")[1]
        if len(s) < 5:
            s = s.ljust(5, '0')
            
        counts = list(Counter(s).values())
        counts.sort(reverse=True) # [5] (Quintilla), [4,1] (Poker), etc.
        
        if counts == [5]: fo["Q"] += 1
        elif counts == [4, 1]: fo["P"] += 1
        elif counts == [3, 2]: fo["FH"] += 1
        elif counts == [3, 1, 1]: fo["T"] += 1
        elif counts == [2, 2, 1]: fo["2P"] += 1
        elif counts == [2, 1, 1, 1]: fo["1P"] += 1
        else: fo["TD"] += 1
            
    # 2. Calcular Frecuencias Esperadas y Agrupar
    # Para Chi-cuadrado, se aconseja que FE >= 5. Así que agrupamos las de menor probabilidad
    fe_raw = {k: v * n for k, v in probs.items()}
    
    # Agruparemos Q, P, FH y tal vez T, dependiendo de n, pero por simplicidad
    # y para evitar fallas con n pequeña, agrupamos las últimas clases en una sola "Otras" (O)
    
    clases_agrupadas = {}
    fe_agrupado = {}
    fo_agrupado = {}
    
    acc_fe = 0
    acc_fo = 0
    clases_actuales = []
    
    # Recorremos desde los más probables hasta los menos probables
    orden = ["TD", "1P", "2P", "T", "FH", "P", "Q"]
    for k in orden:
        acc_fe += fe_raw[k]
        acc_fo += fo[k]
        clases_actuales.append(k)
        
        if acc_fe >= 5 or k == "Q": 
            # Si acumulamos más de 5, o estamos en el último
            nombre_grupo = "+".join(clases_actuales)
            fe_agrupado[nombre_grupo] = acc_fe
            fo_agrupado[nombre_grupo] = acc_fo
            acc_fe = 0
            acc_fo = 0
            clases_actuales = []
            
    # Si el último grupo quedó con FE < 5, lo sumamos al penúltimo (si existe)
    keys = list(fe_agrupado.keys())
    if len(keys) > 1 and fe_agrupado[keys[-1]] < 5:
        last_key = keys[-1]
        prev_key = keys[-2]
        
        new_key = prev_key + "+" + last_key
        fe_agrupado[new_key] = fe_agrupado[prev_key] + fe_agrupado[last_key]
        fo_agrupado[new_key] = fo_agrupado[prev_key] + fo_agrupado[last_key]
        
        del fe_agrupado[last_key]
        del fe_agrupado[prev_key]
        
    # 3. Calculamos Estadístico C
    chi2_obs = 0
    for k in fe_agrupado.keys():
        chi2_obs += ((fo_agrupado[k] - fe_agrupado[k])**2) / fe_agrupado[k]
        
    grados_libertad = len(fe_agrupado) - 1
    # Si grados_libertad es 0, no podemos calcular chi cuadrado de manera significativa
    if grados_libertad <= 0:
        return {
            "test": "Prueba de Poker",
            "passed": False,
            "error": "El tamaño de la muestra es muy pequeño para realizar la prueba de Poker"
        }
    
    chi2_critico = stats.chi2.ppf(1 - alpha, grados_libertad)
    passed = bool(chi2_obs < chi2_critico)
    
    return {
        "test": "Prueba de Poker",
        "passed": passed,
        "details": {
            "fo_raw": fo,
            "fe_raw": fe_raw,
            "fo_agrupado": fo_agrupado,
            "fe_agrupado": fe_agrupado,
            "chi2_obs": chi2_obs,
            "chi2_critico": chi2_critico,
            "grados_libertad": grados_libertad
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \text{Los números son independientes (Prueba de Poker)} \\
        C &= \sum \frac{(FO_i - FE_i)^2}{FE_i} = """ + f"{chi2_obs:.4f}" + r""" \\
        \chi^2_{1-\alpha, k-1} &= """ + f"{chi2_critico:.4f}" + r"""
        \end{align*}
        """
    }

def test_corridas(numbers: list[float], alpha: float = 0.05) -> dict:
    """
    Prueba de Corridas Arriba/Abajo (Independencia):
    Evalúa la alternancia entre incrementos y decrementos.
    """
    n = len(numbers)
    if n < 2:
        return {"error": "Se requieren al menos 2 números"}
        
    # 1. Generar la secuencia S (1 si sube, 0 si baja)
    S = []
    for i in range(1, n):
        if numbers[i] >= numbers[i-1]:
            S.append(1)
        else:
            S.append(0)
            
    # 2. Contar número de corridas (a)
    a = 1 # Empezamos con una corrida
    for i in range(1, len(S)):
        if S[i] != S[i-1]:
            a += 1
            
    # 3. Media y Varianza teórica de corridas
    mu_a = (2 * n - 1) / 3
    var_a = (16 * n - 29) / 90
    sigma_a = math.sqrt(var_a)
    
    # 4. Estadístico Z
    z0 = (a - mu_a) / sigma_a
    z_alpha_2 = stats.norm.ppf(1 - alpha / 2)
    
    passed = bool(abs(z0) < z_alpha_2)
    
    return {
        "test": "Prueba de Corridas (Arriba/Abajo)",
        "passed": passed,
        "details": {
            "n": n,
            "corridas": a,
            "mu_a": mu_a,
            "var_a": var_a,
            "z0": z0,
            "z_alpha_2": z_alpha_2,
            "secuencia_S": S[:20] # Enviamos solo los primeros 20 para no saturar
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \text{Los números son independientes (Corridas)} \\
        \mu_a &= \frac{2n - 1}{3} = """ + f"{mu_a:.4f}" + r""" \\
        \sigma_a &= \sqrt{\frac{16n - 29}{90}} = """ + f"{sigma_a:.4f}" + r""" \\
        Z_0 &= \frac{a - \mu_a}{\sigma_a} = """ + f"{z0:.4f}" + r""" \\
        Z_{\alpha/2} &= """ + f"{z_alpha_2:.4f}" + r"""
        \end{align*}
        """
    }

def test_series(numbers: list[float], alpha: float = 0.05, m: int = 5) -> dict:
    """
    Prueba de Series (Independencia):
    Evalúa la distribución de pares consecutivos en un grid 2D de mxm.
    """
    n = len(numbers)
    if n < 2:
        return {"error": "Se requieren al menos 2 números"}
        
    pares = n - 1
    
    # 1. Crear matriz m x m observada (iniciada en 0)
    fo = np.zeros((m, m))
    
    # 2. Frecuencia Esperada
    fe = pares / (m * m)
    
    # 3. Clasificar cada par (x_i, x_{i+1})
    for i in range(pares):
        x1 = numbers[i]
        x2 = numbers[i+1]
        
        # Encontrar el índice (fila, columna)
        fila = int(x1 * m)
        columna = int(x2 * m)
        
        # Limitar al borde superior (si hay valores de 1.0)
        if fila == m: fila = m - 1
        if columna == m: columna = m - 1
            
        fo[fila][columna] += 1
        
    # 4. Calcular Estadístico C
    chi2_obs = np.sum(((fo - fe) ** 2) / fe)
    
    grados_libertad = m * m - 1
    chi2_critico = stats.chi2.ppf(1 - alpha, grados_libertad)
    
    passed = bool(chi2_obs < chi2_critico)
    
    return {
        "test": "Prueba de Series (2D)",
        "passed": passed,
        "details": {
            "n": n,
            "pares_totales": pares,
            "m": m,
            "fe": fe,
            "fo_matrix": fo.tolist(),
            "chi2_obs": float(chi2_obs),
            "chi2_critico": chi2_critico,
            "grados_libertad": grados_libertad
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \text{Los números son independientes (Pares 2D uniformes)} \\
        FE &= \frac{n-1}{m^2} = """ + f"{fe:.4f}" + r""" \\
        C &= \sum \frac{(FO_{ij} - FE)^2}{FE} = """ + f"{chi2_obs:.4f}" + r""" \\
        \chi^2_{1-\alpha, m^2-1} &= """ + f"{chi2_critico:.4f}" + r"""
        \end{align*}
        """
    }

def test_kolmogorov_smirnov(numbers: list[float], alpha: float = 0.05) -> dict:
    """
    Prueba de Kolmogorov-Smirnov (Uniformidad Continua):
    Compara la función de distribución acumulada empírica con la teórica U(0,1).
    """
    n = len(numbers)
    if n == 0:
        return {"error": "Se requieren datos"}
        
    # 1. Ordenamos los números
    ordenados = sorted(numbers)
    
    # 2. Calculamos D+ y D- para cada punto
    # D+ = max(i/n - x_i)
    # D- = max(x_i - (i-1)/n)
    
    d_mas_max = 0
    d_menos_max = 0
    
    for i, x in enumerate(ordenados, start=1):
        d_mas = (i / n) - x
        d_menos = x - ((i - 1) / n)
        
        if d_mas > d_mas_max: d_mas_max = d_mas
        if d_menos > d_menos_max: d_menos_max = d_menos
            
    # 3. El estadístico de prueba es D = max(D+, D-)
    d_max = max(d_mas_max, d_menos_max)
    
    # 4. Cálculo de D_alpha crítico 
    # Para alfa=0.05 y n > 35, D_crit = 1.36 / sqrt(n)
    # Usaremos scipy (Kolmogorov-Smirnov one-sample test) para exactitud
    # ks_stat, p_value = stats.ks_1samp(numbers, stats.uniform.cdf)
    # Sin embargo, la fórmula clásica aproxima para reportar el valor crítico de tabla:
    
    if alpha == 0.05:
        if n > 35:
            d_critico = 1.36 / math.sqrt(n)
        else:
            # Aproximación para n pequeño (stats.ksone.ppf en scipy)
            d_critico = stats.ksone.ppf(1 - alpha, n)
    elif alpha == 0.01:
         if n > 35: d_critico = 1.63 / math.sqrt(n)
         else: d_critico = stats.ksone.ppf(1 - alpha, n)
    else:
         d_critico = stats.ksone.ppf(1 - alpha, n)
         
    passed = bool(d_max < d_critico)
    
    return {
        "test": "Prueba Kolmogorov-Smirnov",
        "passed": passed,
        "details": {
            "n": n,
            "d_mas": d_mas_max,
            "d_menos": d_menos_max,
            "d_max": d_max,
            "d_critico": d_critico,
            "alpha": alpha
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \text{Los números se ajustan a la distribución } U(0,1) \\
        D^+ &= \max \left(\frac{i}{n} - x_{(i)}\right) = """ + f"{d_mas_max:.4f}" + r""" \\
        D^- &= \max \left(x_{(i)} - \frac{i-1}{n}\right) = """ + f"{d_menos_max:.4f}" + r""" \\
        D &= \max(D^+, D^-) = """ + f"{d_max:.4f}" + r""" \\
        D_{\alpha, n} &= """ + f"{d_critico:.4f}" + r"""
        \end{align*}
        """
    }
