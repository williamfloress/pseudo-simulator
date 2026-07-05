"""
Módulo de Generadores de Números Pseudoaleatorios.
Implementa el Método Congruencial (Mixto/Multiplicativo) y el Método del Cuadrado Medio.
"""

def congruential_generator(seed: int, a: int, c: int, m: int, n: int) -> list:
    """
    Genera n números pseudoaleatorios usando el método congruencial.
    Fórmula: X_{i+1} = (a * X_i + c) mod m
    r_i = X_{i+1} / (m - 1)
    
    Args:
        seed (int): Semilla inicial (X_0).
        a (int): Multiplicador.
        c (int): Constante aditiva (0 para congruencial multiplicativo).
        m (int): Módulo.
        n (int): Cantidad de números a generar.
        
    Returns:
        list: Lista de diccionarios con el paso a paso y los números generados r_i.
    """
    results = []
    x_i = seed
    
    for i in range(1, n + 1):
        x_next = (a * x_i + c) % m
        # Se divide entre m - 1 como se indica en la documentación académica
        # Para evitar división por cero, aseguramos m > 1 en la validación externa.
        r_i = x_next / (m - 1) if m > 1 else 0
        
        results.append({
            "i": i,
            "Xi": x_i,
            "X_next": x_next,
            "ri": round(r_i, 5) # Redondeamos a 5 decimales para las pruebas y presentación
        })
        
        x_i = x_next
        
    return results

def mid_square_generator(seed: int, n: int) -> list:
    """
    Genera n números pseudoaleatorios usando el método del cuadrado medio.
    
    Args:
        seed (int): Semilla inicial (X_0). Debe tener d dígitos (ej. 4 dígitos).
        n (int): Cantidad de números a generar.
        
    Returns:
        list: Lista de diccionarios con los pasos intermedios y el número generado r_i.
    """
    results = []
    x_i = seed
    d = len(str(abs(seed))) # Cantidad de dígitos de la semilla inicial
    
    for i in range(1, n + 1):
        x_squared = x_i ** 2
        str_squared = str(x_squared)
        
        # Rellenar con ceros a la izquierda si el cuadrado no tiene 2d dígitos
        str_squared = str_squared.zfill(2 * d)
        
        # Extraer los d dígitos centrales
        start_idx = (len(str_squared) - d) // 2
        mid_str = str_squared[start_idx : start_idx + d]
        
        x_next = int(mid_str)
        r_i = x_next / (10 ** d)
        
        results.append({
            "i": i,
            "Xi": x_i,
            "Xi_squared": x_squared,
            "extracted": mid_str,
            "X_next": x_next,
            "ri": round(r_i, 5)
        })
        
        x_i = x_next
        
        # Si la semilla llega a 0, el ciclo degenera. Se sigue generando pero serán ceros.
            
    return results
