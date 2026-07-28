"""
Módulo de Validación Estadística para Distribuciones de Probabilidad.
Implementa Pruebas de Medias, Varianza, Chi-Cuadrada de Bondad de Ajuste y Kolmogorov-Smirnov.
"""

import math
import numpy as np
import scipy.stats as stats
from typing import List, Dict, Any

def get_distribution_stats(dist_type: str, params: dict) -> tuple[float, float, str]:
    """
    Retorna (media_teorica, varianza_teorica, nombre_formateado) para la distribución.
    """
    if dist_type == "uniform_continuous":
        a, b = float(params.get("a", 0)), float(params.get("b", 1))
        mu = (a + b) / 2.0
        var = ((b - a) ** 2) / 12.0
        name = f"Uniforme Continua U({a}, {b})"
    elif dist_type == "exponential":
        lambd = float(params.get("lambd", 1.0))
        mu = 1.0 / lambd
        var = 1.0 / (lambd ** 2)
        name = f"Exponencial Exp(λ={lambd})"
    elif dist_type == "normal":
        mu = float(params.get("mu", 0.0))
        sigma = float(params.get("sigma", 1.0))
        var = sigma ** 2
        name = f"Normal N(μ={mu}, σ²={var:.2f})"
    elif dist_type == "erlang":
        k = int(params.get("k", 2))
        lambd = float(params.get("lambd", 1.0))
        mu = k / lambd
        var = k / (lambd ** 2)
        name = f"Erlang E_{k}(λ={lambd})"
    elif dist_type == "triangular":
        a, b, c = float(params.get("a", 0)), float(params.get("b", 1)), float(params.get("c", 0.5))
        mu = (a + b + c) / 3.0
        var = (a**2 + b**2 + c**2 - a*b - a*c - b*c) / 18.0
        name = f"Triangular T({a}, {b}, {c})"
    elif dist_type == "uniform_discrete":
        a, b = int(params.get("a", 1)), int(params.get("b", 6))
        n_elem = b - a + 1
        mu = (a + b) / 2.0
        var = ((n_elem ** 2) - 1) / 12.0
        name = f"Uniforme Discreta U({a}, {b})"
    elif dist_type == "bernoulli":
        p = float(params.get("p", 0.5))
        mu = p
        var = p * (1.0 - p)
        name = f"Bernoulli P(p={p})"
    elif dist_type == "binomial":
        n_trials = int(params.get("n_trials", 10))
        p = float(params.get("p", 0.5))
        mu = n_trials * p
        var = n_trials * p * (1.0 - p)
        name = f"Binomial Bin({n_trials}, {p})"
    elif dist_type == "poisson":
        lambd = float(params.get("lambd", 4.0))
        mu = lambd
        var = lambd
        name = f"Poisson Poi(λ={lambd})"
    elif dist_type == "geometric":
        p = float(params.get("p", 0.5))
        mu = 1.0 / p
        var = (1.0 - p) / (p ** 2)
        name = f"Geométrica G(p={p})"
    else:
        raise ValueError(f"Distribución '{dist_type}' no reconocida")

    return mu, var, name

def get_cdf_function(dist_type: str, params: dict):
    """
    Retorna una función F(x) = P(X <= x) para la distribución continua dada.
    """
    if dist_type == "uniform_continuous":
        a, b = float(params.get("a", 0)), float(params.get("b", 1))
        return lambda x: stats.uniform.cdf(x, loc=a, scale=b - a)
    elif dist_type == "exponential":
        lambd = float(params.get("lambd", 1.0))
        return lambda x: stats.expon.cdf(x, scale=1.0 / lambd)
    elif dist_type == "normal":
        mu, sigma = float(params.get("mu", 0.0)), float(params.get("sigma", 1.0))
        return lambda x: stats.norm.cdf(x, loc=mu, scale=sigma)
    elif dist_type == "erlang":
        k, lambd = int(params.get("k", 2)), float(params.get("lambd", 1.0))
        return lambda x: stats.erlang.cdf(x, a=k, scale=1.0 / lambd)
    elif dist_type == "triangular":
        a, b, c = float(params.get("a", 0)), float(params.get("b", 1)), float(params.get("c", 0.5))
        c_scale = (c - a) / (b - a) if b > a else 0.5
        return lambda x: stats.triang.cdf(x, c=c_scale, loc=a, scale=b - a)
    else:
        return None

# ==============================================================================
# PRUEBAS ESTADÍSTICAS
# ==============================================================================

def test_medias_distribucion(numbers: List[float], dist_type: str, params: dict, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Prueba de Medias para una distribución continua o discreta general:
    H0: E(X) = mu_teorica
    """
    n = len(numbers)
    if n == 0:
        return {"error": "No hay números para analizar"}
        
    mu_0, var_0, dist_name = get_distribution_stats(dist_type, params)
    sigma_0 = math.sqrt(var_0)
    
    media_muestral = float(np.mean(numbers))
    
    # Estadístico Z0 = (X_bar - mu_0) / (sigma_0 / sqrt(n))
    if sigma_0 == 0:
        z0 = 0.0
    else:
        z0 = (media_muestral - mu_0) / (sigma_0 / math.sqrt(n))
        
    z_alpha_2 = stats.norm.ppf(1 - alpha / 2.0)
    
    limite_inferior = mu_0 - z_alpha_2 * (sigma_0 / math.sqrt(n))
    limite_superior = mu_0 + z_alpha_2 * (sigma_0 / math.sqrt(n))
    
    passed = bool(abs(z0) < z_alpha_2)
    
    return {
        "test": f"Prueba de Medias ({dist_name})",
        "passed": passed,
        "details": {
            "n": n,
            "media_muestral": media_muestral,
            "mu_teorica": mu_0,
            "var_teorica": var_0,
            "z0": z0,
            "z_alpha_2": z_alpha_2,
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
            "alpha": alpha,
            "dist_name": dist_name
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \mu = """ + f"{mu_0:.4f}" + r""" \\
        \bar{x} &= \frac{1}{n}\sum x_i = """ + f"{media_muestral:.4f}" + r""" \\
        Z_0 &= \frac{\bar{x} - \mu_0}{\sigma_0 / \sqrt{n}} = """ + f"{z0:.4f}" + r""" \\
        Z_{\alpha/2} &= """ + f"{z_alpha_2:.4f}" + r"""
        \end{align*}
        """
    }

def test_variancia_distribucion(numbers: List[float], dist_type: str, params: dict, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Prueba de Varianza para una distribución general:
    H0: Var(X) = var_teorica
    """
    n = len(numbers)
    if n <= 1:
        return {"error": "Se requieren al menos 2 números para la prueba de varianza"}
        
    mu_0, var_0, dist_name = get_distribution_stats(dist_type, params)
    
    if var_0 <= 0:
        return {"error": "La varianza teórica debe ser mayor a 0"}
        
    var_muestral = float(np.var(numbers, ddof=1))
    
    # Estadístico Chi-cuadrado = (n - 1) * S^2 / sigma_0^2
    chi2_obs = (n - 1) * var_muestral / var_0
    
    chi2_inf = stats.chi2.ppf(alpha / 2.0, n - 1)
    chi2_sup = stats.chi2.ppf(1 - alpha / 2.0, n - 1)
    
    limite_inferior = chi2_inf * var_0 / (n - 1)
    limite_superior = chi2_sup * var_0 / (n - 1)
    
    passed = bool(limite_inferior <= var_muestral <= limite_superior)
    
    return {
        "test": f"Prueba de Varianza ({dist_name})",
        "passed": passed,
        "details": {
            "n": n,
            "varianza_muestral": var_muestral,
            "var_teorica": var_0,
            "chi2_obs": chi2_obs,
            "chi2_inf": chi2_inf,
            "chi2_sup": chi2_sup,
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
            "alpha": alpha,
            "dist_name": dist_name
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \sigma^2 = """ + f"{var_0:.4f}" + r""" \\
        S^2 &= \frac{\sum (x_i - \bar{x})^2}{n-1} = """ + f"{var_muestral:.4f}" + r""" \\
        \chi^2_0 &= \frac{(n-1)S^2}{\sigma_0^2} = """ + f"{chi2_obs:.4f}" + r""" \\
        L_I &= """ + f"{limite_inferior:.4f}" + r""", \quad L_S = """ + f"{limite_superior:.4f}" + r"""
        \end{align*}
        """
    }

def test_chi_cuadrada_distribucion(numbers: List[float], dist_type: str, params: dict, alpha: float = 0.05, num_intervals: int = 0) -> Dict[str, Any]:
    """
    Prueba Chi-Cuadrada de Bondad de Ajuste para Distribuciones Continuas y Discretas.
    """
    n = len(numbers)
    if n == 0:
        return {"error": "Lista vacía"}
        
    mu_0, var_0, dist_name = get_distribution_stats(dist_type, params)
    
    is_discrete = dist_type in ["uniform_discrete", "bernoulli", "binomial", "poisson", "geometric"]
    
    if is_discrete:
        # Frecuencias por valor entero
        int_numbers = [int(round(x)) for x in numbers]
        val_counts = {}
        for val in int_numbers:
            val_counts[val] = val_counts.get(val, 0) + 1
            
        min_v = min(val_counts.keys())
        max_v = max(val_counts.keys())
        
        categories = list(range(min_v, max_v + 1))
        fo = [val_counts.get(k, 0) for k in categories]
        
        # Calcular Probabilidad Teórica PMF
        fe = []
        for k in categories:
            if dist_type == "uniform_discrete":
                a, b = int(params.get("a", 1)), int(params.get("b", 6))
                pk = 1.0 / (b - a + 1) if a <= k <= b else 0.0
            elif dist_type == "bernoulli":
                p = float(params.get("p", 0.5))
                pk = p if k == 1 else (1.0 - p if k == 0 else 0.0)
            elif dist_type == "binomial":
                n_trials, p = int(params.get("n_trials", 10)), float(params.get("p", 0.5))
                pk = stats.binom.pmf(k, n_trials, p)
            elif dist_type == "poisson":
                lambd = float(params.get("lambd", 4.0))
                pk = stats.poisson.pmf(k, lambd)
            elif dist_type == "geometric":
                p = float(params.get("p", 0.5))
                pk = stats.geom.pmf(k, p)
            else:
                pk = 1.0 / len(categories)
            fe.append(pk * n)
            
        # Agrupar categorías con FE < 5
        fo_agrup = []
        fe_agrup = []
        labels_agrup = []
        
        acc_fo = 0
        acc_fe = 0.0
        acc_labels = []
        
        for idx in range(len(categories)):
            acc_fo += fo[idx]
            acc_fe += fe[idx]
            acc_labels.append(str(categories[idx]))
            
            if acc_fe >= 5.0 or idx == len(categories) - 1:
                fo_agrup.append(acc_fo)
                fe_agrup.append(acc_fe)
                labels_agrup.append("-".join(acc_labels) if len(acc_labels) > 1 else acc_labels[0])
                acc_fo = 0
                acc_fe = 0.0
                acc_labels = []
                
        # Si el último grupo quedó con FE < 5 y hay más de 1 grupo, fusionar con el anterior
        if len(fe_agrup) > 1 and fe_agrup[-1] < 5.0:
            last_fo = fo_agrup.pop()
            last_fe = fe_agrup.pop()
            last_lbl = labels_agrup.pop()
            
            fo_agrup[-1] += last_fo
            fe_agrup[-1] += last_fe
            labels_agrup[-1] += f" / {last_lbl}"
            
        m = len(fe_agrup)
        if m <= 1:
            return {"error": "No hay suficientes categorías con frecuencias esperadas adecuadas para la prueba Chi-cuadrada"}
            
        chi2_obs = sum(((fo_agrup[j] - fe_agrup[j]) ** 2) / fe_agrup[j] for j in range(m))
        grados_libertad = max(1, m - 1)
        chi2_critico = stats.chi2.ppf(1 - alpha, grados_libertad)
        passed = bool(chi2_obs < chi2_critico)
        
        return {
            "test": f"Prueba Chi-Cuadrada ({dist_name})",
            "passed": passed,
            "details": {
                "n": n,
                "m": m,
                "frecuencias_observadas": fo_agrup,
                "frecuencias_esperadas": [round(f, 4) for f in fe_agrup],
                "labels": labels_agrup,
                "chi2_obs": chi2_obs,
                "chi2_critico": chi2_critico,
                "grados_libertad": grados_libertad,
                "alpha": alpha,
                "dist_name": dist_name
            },
            "latex": r"""
            \begin{align*}
            H_0 &: \text{Los datos siguen la distribución } """ + dist_name + r""" \\
            C &= \sum_{i=1}^m \frac{(FO_i - FE_i)^2}{FE_i} = """ + f"{chi2_obs:.4f}" + r""" \\
            \chi^2_{1-\alpha, gl} &= """ + f"{chi2_critico:.4f}" + r"""
            \end{align*}
            """
        }
        
    else:
        # Distribución Continua: división por intervalos en [min(X), max(X)]
        cdf_func = get_cdf_function(dist_type, params)
        if cdf_func is None:
            return {"error": "Función CDF no definida"}
            
        if num_intervals <= 0:
            num_intervals = int(math.sqrt(n))
            if num_intervals < 5: num_intervals = 5
            
        m = num_intervals
        x_min, x_max = float(min(numbers)), float(max(numbers))
        
        # Extender un poco los bordes para inclusión
        step = (x_max - x_min) / m if x_max > x_min else 1.0
        bins = [x_min + i * step for i in range(m + 1)]
        
        fo = [0] * m
        for x in numbers:
            idx = int((x - x_min) / step) if step > 0 else 0
            if idx >= m: idx = m - 1
            fo[idx] += 1
            
        fe = []
        for i in range(m):
            b_inf, b_sup = bins[i], bins[i + 1]
            p_interval = cdf_func(b_sup) - cdf_func(b_inf)
            fe.append(p_interval * n)
            
        # Agrupar si FE < 5
        fo_agrup, fe_agrup, labels_agrup = [], [], []
        acc_fo, acc_fe = 0, 0.0
        b_start = bins[0]
        
        for i in range(m):
            acc_fo += fo[i]
            acc_fe += fe[i]
            if acc_fe >= 5.0 or i == m - 1:
                fo_agrup.append(acc_fo)
                fe_agrup.append(acc_fe)
                labels_agrup.append(f"[{b_start:.2f}, {bins[i+1]:.2f})")
                acc_fo = 0
                acc_fe = 0.0
                if i < m - 1: b_start = bins[i+1]
                
        if len(fe_agrup) > 1 and fe_agrup[-1] < 5.0:
            l_fo, l_fe = fo_agrup.pop(), fe_agrup.pop()
            fo_agrup[-1] += l_fo
            fe_agrup[-1] += l_fe
            labels_agrup[-1] = f"{labels_agrup[-1].split(',')[0]}, {bins[-1]:.2f})"
            
        num_cat = len(fe_agrup)
        if num_cat <= 1:
            return {"error": "Muestra insuficiente para intervalos Chi-cuadrada"}
            
        chi2_obs = sum(((fo_agrup[j] - fe_agrup[j]) ** 2) / (fe_agrup[j] if fe_agrup[j] > 0 else 1.0) for j in range(num_cat))
        grados_libertad = max(1, num_cat - 1)
        chi2_critico = stats.chi2.ppf(1 - alpha, grados_libertad)
        passed = bool(chi2_obs < chi2_critico)
        
        return {
            "test": f"Prueba Chi-Cuadrada ({dist_name})",
            "passed": passed,
            "details": {
                "n": n,
                "m": num_cat,
                "frecuencias_observadas": fo_agrup,
                "frecuencias_esperadas": [round(f, 4) for f in fe_agrup],
                "labels": labels_agrup,
                "chi2_obs": chi2_obs,
                "chi2_critico": chi2_critico,
                "grados_libertad": grados_libertad,
                "alpha": alpha,
                "dist_name": dist_name
            },
            "latex": r"""
            \begin{align*}
            H_0 &: \text{Los datos se ajustan a } """ + dist_name + r""" \\
            C &= \sum_{i=1}^m \frac{(FO_i - FE_i)^2}{FE_i} = """ + f"{chi2_obs:.4f}" + r""" \\
            \chi^2_{1-\alpha, gl} &= """ + f"{chi2_critico:.4f}" + r"""
            \end{align*}
            """
        }

def test_ks_distribucion(numbers: List[float], dist_type: str, params: dict, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Prueba Kolmogorov-Smirnov para Distribuciones Continuas.
    Compara la FDA empírica Sn(x) con la FDA teórica F_X(x).
    """
    n = len(numbers)
    if n == 0:
        return {"error": "Lista vacía"}
        
    mu_0, var_0, dist_name = get_distribution_stats(dist_type, params)
    cdf_func = get_cdf_function(dist_type, params)
    
    if cdf_func is None:
        return {"error": f"La prueba Kolmogorov-Smirnov solo es aplicable a distribuciones continuas."}
        
    sorted_x = sorted(numbers)
    d_mas_max = 0.0
    d_menos_max = 0.0
    
    for i, x in enumerate(sorted_x, start=1):
        f_val = cdf_func(x)
        d_mas = (i / n) - f_val
        d_menos = f_val - ((i - 1) / n)
        
        if d_mas > d_mas_max: d_mas_max = d_mas
        if d_menos > d_menos_max: d_menos_max = d_menos
        
    d_max = max(d_mas_max, d_menos_max)
    
    if n > 35:
        if alpha == 0.01: d_critico = 1.63 / math.sqrt(n)
        elif alpha == 0.10: d_critico = 1.22 / math.sqrt(n)
        else: d_critico = 1.36 / math.sqrt(n)
    else:
        d_critico = stats.ksone.ppf(1 - alpha, n)
        
    passed = bool(d_max < d_critico)
    
    return {
        "test": f"Prueba Kolmogorov-Smirnov ({dist_name})",
        "passed": passed,
        "details": {
            "n": n,
            "d_mas": d_mas_max,
            "d_menos": d_menos_max,
            "d_max": d_max,
            "d_critico": d_critico,
            "alpha": alpha,
            "dist_name": dist_name
        },
        "latex": r"""
        \begin{align*}
        H_0 &: \text{Los datos se ajustan a } """ + dist_name + r""" \\
        D^+ &= \max \left(\frac{i}{n} - F(x_{(i)})\right) = """ + f"{d_mas_max:.4f}" + r""" \\
        D^- &= \max \left(F(x_{(i)}) - \frac{i-1}{n}\right) = """ + f"{d_menos_max:.4f}" + r""" \\
        D &= \max(D^+, D^-) = """ + f"{d_max:.4f}" + r""" \\
        D_{\alpha, n} &= """ + f"{d_critico:.4f}" + r"""
        \end{align*}
        """
    }
