"""
Script de pruebas unitarias y de integración para distribuciones continuas y discretas.
"""

import sys
import os

# Forzar codificación UTF-8 para stdout en Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from distribution_generators import (
    generate_uniform_continuous, generate_exponential, generate_normal,
    generate_erlang, generate_triangular, generate_uniform_discrete,
    generate_bernoulli, generate_binomial, generate_poisson, generate_geometric
)
from distribution_validators import (
    test_medias_distribucion, test_variancia_distribucion,
    test_chi_cuadrada_distribucion, test_ks_distribucion
)

def test_all_distributions():
    print("--- INICIANDO PRUEBAS DE GENERACION Y VALIDACION ---")
    n = 200
    
    # 1. Exponencial
    print("1. Probando Exponencial Exp(lambda=0.5)...")
    data_exp = generate_exponential(0.5, n)
    nums_exp = [x["Xi"] for x in data_exp]
    assert len(nums_exp) == n
    
    res_medias = test_medias_distribucion(nums_exp, "exponential", {"lambd": 0.5})
    assert "error" not in res_medias
    print(f"  -> Medias: {res_medias['test']} PASSED: {res_medias['passed']}")
    
    res_chi2 = test_chi_cuadrada_distribucion(nums_exp, "exponential", {"lambd": 0.5})
    assert "error" not in res_chi2
    print(f"  -> Chi2: {res_chi2['test']} PASSED: {res_chi2['passed']}")
    
    res_ks = test_ks_distribucion(nums_exp, "exponential", {"lambd": 0.5})
    assert "error" not in res_ks
    print(f"  -> KS: {res_ks['test']} PASSED: {res_ks['passed']}")

    # 2. Normal
    print("\n2. Probando Normal N(mu=10, sigma=2)...")
    data_norm = generate_normal(10, 2, n)
    nums_norm = [x["Xi"] for x in data_norm]
    assert len(nums_norm) == n
    res_norm_m = test_medias_distribucion(nums_norm, "normal", {"mu": 10, "sigma": 2})
    print(f"  -> Medias Normal: {res_norm_m['test']} PASSED: {res_norm_m['passed']}")

    # 3. Poisson
    print("\n3. Probando Poisson Poi(lambda=4)...")
    data_poi = generate_poisson(4, n)
    nums_poi = [x["Xi"] for x in data_poi]
    assert len(nums_poi) == n
    res_poi_chi2 = test_chi_cuadrada_distribucion(nums_poi, "poisson", {"lambd": 4})
    print(f"  -> Chi2 Poisson: {res_poi_chi2['test']} PASSED: {res_poi_chi2['passed']}")

    # 4. Binomial
    print("\n4. Probando Binomial Bin(n_trials=10, p=0.4)...")
    data_bin = generate_binomial(10, 0.4, n)
    nums_bin = [x["Xi"] for x in data_bin]
    assert len(nums_bin) == n
    res_bin_var = test_variancia_distribucion(nums_bin, "binomial", {"n_trials": 10, "p": 0.4})
    print(f"  -> Varianza Binomial: {res_bin_var['test']} PASSED: {res_bin_var['passed']}")

    # 5. Triangular
    print("\n5. Probando Triangular T(a=0, b=10, c=3)...")
    data_tri = generate_triangular(0, 10, 3, n)
    nums_tri = [x["Xi"] for x in data_tri]
    assert len(nums_tri) == n
    res_tri_ks = test_ks_distribucion(nums_tri, "triangular", {"a": 0, "b": 10, "c": 3})
    print(f"  -> KS Triangular: {res_tri_ks['test']} PASSED: {res_tri_ks['passed']}")

    print("\n--- ¡TODAS LAS PRUEBAS COMPLETADAS CON EXITO! ---")

if __name__ == "__main__":
    test_all_distributions()
