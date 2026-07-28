"""
Módulo de Generación de Variables Aleatorias (Distribuciones Continuas y Discretas).
Soporta Transformada Inversa, Box-Muller, Método de Sumación y Multiplicación.
"""

import math
import random
from typing import List, Dict, Any

# Helper: clamping para evitar log(0) o divisiones por cero
def _safe_r(r: float) -> float:
    return max(1e-9, min(1 - 1e-9, r))

# ==============================================================================
# DISTRIBUCIONES CONTINUAS
# ==============================================================================

def generate_uniform_continuous(a: float, b: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Uniforme Continua U(a, b).
    Fórmula: X_i = a + (b - a) * r_i
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= n
    
    for i in range(1, n + 1):
        r_i = base_u[i - 1] if use_custom_u else random.random()
        x_i = a + (b - a) * r_i
        
        results.append({
            "i": i,
            "ri": round(r_i, 5),
            "Xi": round(x_i, 5),
            "formula": f"{a:.2f} + ({b:.2f} - {a:.2f}) * {r_i:.5f}"
        })
    return results

def generate_exponential(lambd: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Exponencial Exp(lambda).
    Fórmula: X_i = - (1 / lambda) * ln(1 - r_i)
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= n
    
    for i in range(1, n + 1):
        r_i = base_u[i - 1] if use_custom_u else random.random()
        safe_r = _safe_r(r_i)
        x_i = - (1.0 / lambd) * math.log(1.0 - safe_r)
        
        results.append({
            "i": i,
            "ri": round(r_i, 5),
            "Xi": round(x_i, 5),
            "formula": f"-(1 / {lambd:.4f}) * ln(1 - {r_i:.5f})"
        })
    return results

def generate_normal(mu: float, sigma: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Normal N(mu, sigma^2) mediante Transformada Box-Muller.
    Z1 = sqrt(-2 ln r1) * cos(2 pi r2)
    Z2 = sqrt(-2 ln r1) * sin(2 pi r2)
    X = mu + sigma * Z
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= 2 * n
    
    u_idx = 0
    generated_count = 0
    
    while generated_count < n:
        if use_custom_u:
            r1 = _safe_r(base_u[u_idx])
            r2 = _safe_r(base_u[u_idx + 1])
            u_idx += 2
        else:
            r1 = _safe_r(random.random())
            r2 = _safe_r(random.random())
            
        z1 = math.sqrt(-2.0 * math.log(r1)) * math.cos(2.0 * math.pi * r2)
        z2 = math.sqrt(-2.0 * math.log(r1)) * math.sin(2.0 * math.pi * r2)
        
        x1 = mu + sigma * z1
        generated_count += 1
        results.append({
            "i": generated_count,
            "ri": f"({r1:.4f}, {r2:.4f})",
            "Xi": round(x1, 5),
            "formula": f"{mu:.2f} + {sigma:.2f} * Z1"
        })
        
        if generated_count < n:
            x2 = mu + sigma * z2
            generated_count += 1
            results.append({
                "i": generated_count,
                "ri": f"({r1:.4f}, {r2:.4f})",
                "Xi": round(x2, 5),
                "formula": f"{mu:.2f} + {sigma:.2f} * Z2"
            })
            
    return results

def generate_erlang(k: int, lambd: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Erlang E_k(lambda).
    Fórmula: X_i = - (1 / lambda) * ln( prod_{j=1}^k r_{j} )
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= k * n
    u_idx = 0
    
    for i in range(1, n + 1):
        r_list = []
        prod_r = 1.0
        for _ in range(k):
            r_j = base_u[u_idx] if use_custom_u else random.random()
            u_idx += 1
            r_j_safe = _safe_r(r_j)
            r_list.append(r_j_safe)
            prod_r *= r_j_safe
            
        x_i = - (1.0 / lambd) * math.log(prod_r)
        ri_str = ", ".join([f"{r:.4f}" for r in r_list[:3]]) + ("..." if k > 3 else "")
        
        results.append({
            "i": i,
            "ri": f"[{ri_str}]",
            "Xi": round(x_i, 5),
            "formula": f"-(1 / {lambd:.4f}) * ln(∏ r_j)"
        })
    return results

def generate_triangular(a: float, b: float, c: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Triangular T(a, b, c).
    F_c = (c - a) / (b - a)
    Si r_i < F_c: X_i = a + sqrt(r_i * (b - a) * (c - a))
    Sino: X_i = b - sqrt((1 - r_i) * (b - a) * (b - c))
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= n
    fc = (c - a) / (b - a) if b > a else 0.5
    
    for i in range(1, n + 1):
        r_i = base_u[i - 1] if use_custom_u else random.random()
        
        if r_i < fc:
            x_i = a + math.sqrt(r_i * (b - a) * (c - a))
        else:
            x_i = b - math.sqrt((1.0 - r_i) * (b - a) * (b - c))
            
        results.append({
            "i": i,
            "ri": round(r_i, 5),
            "Xi": round(x_i, 5),
            "formula": f"Triangular (r_i {'<' if r_i < fc else '≥'} {fc:.3f})"
        })
    return results

# ==============================================================================
# DISTRIBUCIONES DISCRETAS
# ==============================================================================

def generate_uniform_discrete(a: int, b: int, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Uniforme Discreta U(a, b).
    Fórmula: X_i = a + floor((b - a + 1) * r_i)
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= n
    
    range_size = b - a + 1
    for i in range(1, n + 1):
        r_i = base_u[i - 1] if use_custom_u else random.random()
        r_safe = min(r_i, 0.999999)
        x_i = a + math.floor(range_size * r_safe)
        
        results.append({
            "i": i,
            "ri": round(r_i, 5),
            "Xi": int(x_i),
            "formula": f"{a} + floor({range_size} * {r_i:.5f})"
        })
    return results

def generate_bernoulli(p: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Bernoulli P(p).
    Fórmula: X_i = 1 si r_i < p else 0
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= n
    
    for i in range(1, n + 1):
        r_i = base_u[i - 1] if use_custom_u else random.random()
        x_i = 1 if r_i < p else 0
        
        results.append({
            "i": i,
            "ri": round(r_i, 5),
            "Xi": int(x_i),
            "formula": f"1 si {r_i:.5f} < {p:.3f} sino 0"
        })
    return results

def generate_binomial(n_trials: int, p: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Binomial(n_trials, p).
    Suma de n_trials ensayos Bernoulli independientes.
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= n_trials * n
    u_idx = 0
    
    for i in range(1, n + 1):
        successes = 0
        r_list = []
        for _ in range(n_trials):
            r_j = base_u[u_idx] if use_custom_u else random.random()
            u_idx += 1
            r_list.append(r_j)
            if r_j < p:
                successes += 1
                
        ri_str = ", ".join([f"{r:.3f}" for r in r_list[:3]]) + ("..." if n_trials > 3 else "")
        results.append({
            "i": i,
            "ri": f"[{ri_str}]",
            "Xi": int(successes),
            "formula": f"Suma de {n_trials} ensayos (p={p:.2f})"
        })
    return results

def generate_poisson(lambd: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Poisson(lambda) por Algoritmo de Multiplicación (Knuth).
    L = exp(-lambda), p = 1, k = 0
    mientras p > L: k += 1, p *= r_j
    X_i = k - 1
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= 20 * n
    u_idx = 0
    
    limit = math.exp(-lambd)
    
    for i in range(1, n + 1):
        k = 0
        prod_p = 1.0
        r_list = []
        
        while True:
            k += 1
            r_j = base_u[u_idx] if use_custom_u else random.random()
            u_idx += 1
            r_safe = _safe_r(r_j)
            r_list.append(r_safe)
            prod_p *= r_safe
            if prod_p <= limit:
                break
                
        x_i = k - 1
        ri_str = ", ".join([f"{r:.3f}" for r in r_list[:3]]) + ("..." if len(r_list) > 3 else "")
        
        results.append({
            "i": i,
            "ri": f"[{ri_str}]",
            "Xi": int(x_i),
            "formula": f"Multiplicación ∏ r_j (≤ e^{-lambd:.2f})"
        })
    return results

def generate_geometric(p: float, n: int, base_u: List[float] = None) -> List[Dict[str, Any]]:
    """
    Distribución Geométrica G(p).
    Fórmula: X_i = floor(ln(1 - r_i) / ln(1 - p)) + 1
    (Número de ensayos requeridos hasta el primer éxito)
    """
    results = []
    use_custom_u = base_u is not None and len(base_u) >= n
    
    log_q = math.log(1.0 - p)
    
    for i in range(1, n + 1):
        r_i = base_u[i - 1] if use_custom_u else random.random()
        safe_r = _safe_r(r_i)
        x_i = math.floor(math.log(1.0 - safe_r) / log_q) + 1
        
        results.append({
            "i": i,
            "ri": round(r_i, 5),
            "Xi": int(x_i),
            "formula": f"floor(ln(1 - {r_i:.4f}) / ln(1 - {p:.2f})) + 1"
        })
    return results
