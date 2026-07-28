"""
Servidor FastAPI principal.
Expone los endpoints para generar números pseudoaleatorios, variables aleatorias
con distribuciones de probabilidad continuas y discretas, y realizar pruebas estadísticas.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from fastapi.staticfiles import StaticFiles

# Importar los generadores y validadores de números U(0,1)
from generators import congruential_generator, mid_square_generator
from validators import (
    test_medias, test_variancia, test_chi_cuadrada, 
    test_poker, test_corridas, test_series, test_kolmogorov_smirnov
)

# Importar los generadores y validadores de Distribuciones de Probabilidad
from distribution_generators import (
    generate_uniform_continuous, generate_exponential, generate_normal,
    generate_erlang, generate_triangular, generate_uniform_discrete,
    generate_bernoulli, generate_binomial, generate_poisson, generate_geometric
)
from distribution_validators import (
    test_medias_distribucion, test_variancia_distribucion,
    test_chi_cuadrada_distribucion, test_ks_distribucion
)

app = FastAPI(
    title="Simulación y Modelos - Plataforma de Simulación",
    description="API para generación y validación de números pseudoaleatorios y distribuciones de probabilidad.",
    version="2.0.0"
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

class DistributionGenerateRequest(BaseModel):
    dist_type: str
    n: int
    params: Dict[str, Any] = {}
    base_generator: Optional[str] = "random"  # 'random', 'congruential', 'mid_square'
    seed: Optional[int] = 3708
    a: Optional[int] = 17
    c: Optional[int] = 43
    m: Optional[int] = 1000

class DistributionTestRequest(BaseModel):
    numbers: List[float]
    dist_type: str
    params: Dict[str, Any] = {}
    alpha: float = 0.05
    intervals: Optional[int] = 0

# ==============================================================================
# ENDPOINTS PROYECTO 1: PSEUDOALEATORIOS U(0,1)
# ==============================================================================

@app.post("/api/generate", summary="Genera números pseudoaleatorios U(0,1)")
async def generate_numbers(req: GenerateRequest):
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
        if req.seed <= 0:
             raise HTTPException(status_code=400, detail="La semilla debe ser mayor a 0.")
        data = mid_square_generator(req.seed, req.n)
        return {"status": "success", "data": data}
        
    else:
        raise HTTPException(status_code=400, detail="Método desconocido. Use 'congruential' o 'mid_square'.")

@app.post("/api/test/{test_name}", summary="Ejecuta una prueba estadística sobre U(0,1)")
async def run_statistical_test(test_name: str, req: TestRequest):
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

# ==============================================================================
# ENDPOINTS PROYECTO 2: DISTRIBUCIONES DE PROBABILIDAD (CONTINUAS Y DISCRETAS)
# ==============================================================================

@app.post("/api/distributions/generate", summary="Genera variables aleatorias con distribuciones continuas o discretas")
async def generate_distribution_variates(req: DistributionGenerateRequest):
    if req.n <= 0:
        raise HTTPException(status_code=400, detail="La cantidad (n) debe ser mayor a 0.")

    # Generar secuencia base U(0,1) si se solicita un generador específico
    base_u = None
    if req.base_generator == "congruential":
        n_base = req.n * 20  # Asegurar suficientes números para métodos multinúmero (Erlang, Normal, etc.)
        raw_congruential = congruential_generator(req.seed or 3708, req.a or 17, req.c or 43, req.m or 1000, n_base)
        base_u = [item["ri"] for item in raw_congruential]
    elif req.base_generator == "mid_square":
        n_base = req.n * 20
        raw_mid = mid_square_generator(req.seed or 3708, n_base)
        base_u = [item["ri"] for item in raw_mid]

    dist = req.dist_type
    p = req.params

    try:
        if dist == "uniform_continuous":
            data = generate_uniform_continuous(float(p.get("a", 0)), float(p.get("b", 1)), req.n, base_u)
        elif dist == "exponential":
            data = generate_exponential(float(p.get("lambd", 1.0)), req.n, base_u)
        elif dist == "normal":
            data = generate_normal(float(p.get("mu", 0)), float(p.get("sigma", 1)), req.n, base_u)
        elif dist == "erlang":
            data = generate_erlang(int(p.get("k", 2)), float(p.get("lambd", 1.0)), req.n, base_u)
        elif dist == "triangular":
            data = generate_triangular(float(p.get("a", 0)), float(p.get("b", 1)), float(p.get("c", 0.5)), req.n, base_u)
        elif dist == "uniform_discrete":
            data = generate_uniform_discrete(int(p.get("a", 1)), int(p.get("b", 6)), req.n, base_u)
        elif dist == "bernoulli":
            data = generate_bernoulli(float(p.get("p", 0.5)), req.n, base_u)
        elif dist == "binomial":
            data = generate_binomial(int(p.get("n_trials", 10)), float(p.get("p", 0.5)), req.n, base_u)
        elif dist == "poisson":
            data = generate_poisson(float(p.get("lambd", 4.0)), req.n, base_u)
        elif dist == "geometric":
            data = generate_geometric(float(p.get("p", 0.5)), req.n, base_u)
        else:
            raise HTTPException(status_code=400, detail=f"Distribución '{dist}' desconocida.")

        return {"status": "success", "data": data, "dist_type": dist}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/distributions/test/{test_name}", summary="Ejecuta una prueba estadística sobre una distribución")
async def run_distribution_test(test_name: str, req: DistributionTestRequest):
    if not req.numbers:
        raise HTTPException(status_code=400, detail="La lista de números no puede estar vacía.")

    if test_name == "medias":
        result = test_medias_distribucion(req.numbers, req.dist_type, req.params, req.alpha)
    elif test_name == "varianza":
        result = test_variancia_distribucion(req.numbers, req.dist_type, req.params, req.alpha)
    elif test_name == "chi_cuadrada":
        result = test_chi_cuadrada_distribucion(req.numbers, req.dist_type, req.params, req.alpha, req.intervals)
    elif test_name == "kolmogorov_smirnov":
        result = test_ks_distribucion(req.numbers, req.dist_type, req.params, req.alpha)
    else:
        raise HTTPException(status_code=400, detail=f"Prueba de distribución '{test_name}' desconocida.")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {"status": "success", "result": result}

# Servir archivos estáticos si la carpeta frontend existe (Render Ready)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
