"""
Servidor FastAPI principal.
Expone los endpoints para generar números y realizar pruebas estadísticas, 
y sirve los archivos estáticos del frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from fastapi.staticfiles import StaticFiles

# Importar los generadores y validadores
from generators import congruential_generator, mid_square_generator
from validators import (
    test_medias, test_variancia, test_chi_cuadrada, 
    test_poker, test_corridas, test_series, test_kolmogorov_smirnov
)

app = FastAPI(
    title="Simulación y Modelos - MVP",
    description="API para generación y validación de números pseudoaleatorios.",
    version="1.0.0"
)

# Permitir CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para la validación de requests
class GenerateRequest(BaseModel):
    method: str  # 'congruential' o 'mid_square'
    seed: int
    a: Optional[int] = None
    c: Optional[int] = None
    m: Optional[int] = None
    n: int

class TestRequest(BaseModel):
    numbers: list[float]
    alpha: float = 0.05
    intervals: Optional[int] = 0  # Para la prueba Chi-cuadrada
    matrix_size: Optional[int] = 5 # Para la prueba de Series

@app.post("/api/generate", summary="Genera números pseudoaleatorios")
async def generate_numbers(req: GenerateRequest):
    """
    Genera `n` números pseudoaleatorios usando el método especificado.
    Retorna el paso a paso matemático y los resultados finales.
    """
    if req.n <= 0:
        raise HTTPException(status_code=400, detail="La cantidad (n) debe ser mayor a 0.")
        
    if req.method == "congruential":
        if req.a is None or req.c is None or req.m is None:
            raise HTTPException(status_code=400, detail="Faltan parámetros (a, c, m) para el método congruencial.")
        if req.m <= 1:
            raise HTTPException(status_code=400, detail="El módulo (m) debe ser mayor a 1.")
            
        data = congruential_generator(req.seed, req.a, req.c, req.m, req.n)
        return {"status": "success", "data": data}
        
    elif req.method == "mid_square":
        # Se requiere al menos una semilla válida
        if req.seed <= 0:
             raise HTTPException(status_code=400, detail="La semilla debe ser mayor a 0.")
        data = mid_square_generator(req.seed, req.n)
        return {"status": "success", "data": data}
        
    else:
        raise HTTPException(status_code=400, detail="Método desconocido. Use 'congruential' o 'mid_square'.")

@app.post("/api/test/{test_name}", summary="Ejecuta una prueba estadística de validación")
async def run_statistical_test(test_name: str, req: TestRequest):
    """
    Ejecuta la prueba estadística indicada (test_name) sobre la lista de números.
    Retorna el resultado de la prueba, los cálculos intermedios y las fórmulas LaTeX.
    """
    if not req.numbers:
        raise HTTPException(status_code=400, detail="La lista de números no puede estar vacía.")
        
    if test_name == "medias":
        result = test_medias(req.numbers, req.alpha)
    elif test_name == "varianza":
        result = test_variancia(req.numbers, req.alpha)
    elif test_name == "chi_cuadrada":
        result = test_chi_cuadrada(req.numbers, req.alpha, req.intervals)
    elif test_name == "poker":
        result = test_poker(req.numbers, req.alpha)
    elif test_name == "corridas":
        result = test_corridas(req.numbers, req.alpha)
    elif test_name == "series":
        result = test_series(req.numbers, req.alpha, req.matrix_size)
    elif test_name == "kolmogorov_smirnov":
        result = test_kolmogorov_smirnov(req.numbers, req.alpha)
    else:
        raise HTTPException(status_code=400, detail=f"Prueba '{test_name}' desconocida.")
        
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return {"status": "success", "result": result}

# Servir archivos estáticos si la carpeta frontend existe (Render Ready)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
