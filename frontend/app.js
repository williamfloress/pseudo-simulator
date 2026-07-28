// ==============================================================================
// Estado Global de la Aplicación
// ==============================================================================
let generatedNumbers = [];        // Muestra de números U(0,1) del Tab 1
let currentChart = null;          // Instancia de Chart.js del Tab 1

let distGeneratedNumbers = [];    // Muestra de variables aleatorias X_i del Tab 2
let currentDistType = "";         // Tipo de distribución activa
let currentDistParams = {};       // Parámetros activos de la distribución
let currentDistChart = null;      // Instancia de Chart.js del Tab 2

// ==============================================================================
// NAVEGACIÓN POR PESTAÑAS (TABS)
// ==============================================================================
const tabBtnPseudo = document.getElementById('tab-btn-pseudo');
const tabBtnDistrib = document.getElementById('tab-btn-distrib');
const tabPseudo = document.getElementById('tab-pseudo');
const tabDistrib = document.getElementById('tab-distrib');

tabBtnPseudo.addEventListener('click', () => {
    tabBtnPseudo.classList.add('active');
    tabBtnDistrib.classList.remove('active');
    tabPseudo.classList.remove('hidden');
    tabDistrib.classList.add('hidden');
});

tabBtnDistrib.addEventListener('click', () => {
    tabBtnDistrib.classList.add('active');
    tabBtnPseudo.classList.remove('active');
    tabDistrib.classList.remove('hidden');
    tabPseudo.classList.add('hidden');
});

// ==============================================================================
// LOGICA PESTAÑA 1: PSEUDOALEATORIOS U(0,1)
// ==============================================================================
const formGenerator = document.getElementById('generator-form');
const methodSelect = document.getElementById('method-select');
const congruentialParams = document.getElementById('congruential-params');
const btnGenerate = document.getElementById('btn-generate');
const btnReset = document.getElementById('btn-reset');
const generationResults = document.getElementById('generation-results');
const numbersTbody = document.getElementById('numbers-tbody');

const validationSection = document.getElementById('validation-section');
const formValidation = document.getElementById('validation-form');
const btnTest = document.getElementById('btn-test');
const testResults = document.getElementById('test-results');
const testStatusBanner = document.getElementById('test-status-banner');
const testTitle = document.getElementById('test-title');
const testVerdict = document.getElementById('test-verdict');
const latexContainer = document.getElementById('latex-container');

btnReset.addEventListener('click', () => {
    generatedNumbers = [];
    formGenerator.reset();
    methodSelect.dispatchEvent(new Event('change'));
    
    generationResults.classList.add('hidden');
    validationSection.classList.add('hidden');
    testResults.classList.add('hidden');
    
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
});

methodSelect.addEventListener('change', (e) => {
    if (e.target.value === 'congruential') {
        congruentialParams.classList.remove('hidden');
        document.getElementById('input-a').required = true;
        document.getElementById('input-c').required = true;
        document.getElementById('input-m').required = true;
    } else {
        congruentialParams.classList.add('hidden');
        document.getElementById('input-a').required = false;
        document.getElementById('input-c').required = false;
        document.getElementById('input-m').required = false;
    }
});

formGenerator.addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading(btnGenerate, true);
    
    try {
        const method = methodSelect.value;
        const n = parseInt(document.getElementById('input-n').value);
        const seed = parseInt(document.getElementById('input-seed').value);
        
        const payload = { method, n, seed };
        
        if (method === 'congruential') {
            payload.a = parseInt(document.getElementById('input-a').value);
            payload.c = parseInt(document.getElementById('input-c').value);
            payload.m = parseInt(document.getElementById('input-m').value);
        }
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const resData = await response.json();
        if (!response.ok) throw new Error(resData.detail || 'Error al generar números');
        
        generatedNumbers = resData.data.map(item => item.r_i || item.ri);
        renderNumbersTable(resData.data);
        
        generationResults.classList.remove('hidden');
        validationSection.classList.remove('hidden');
        testResults.classList.add('hidden');
        
    } catch (error) {
        alert(error.message);
    } finally {
        setLoading(btnGenerate, false);
    }
});

function renderNumbersTable(data) {
    numbersTbody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        const i = row.i;
        const x_i = row.Xi !== undefined ? row.Xi : (row.x_i !== undefined ? row.x_i : row.xi);
        const r_i = row.ri !== undefined ? row.ri : row.r_i;
        
        tr.innerHTML = `
            <td>${i}</td>
            <td>${x_i}</td>
            <td><strong>${r_i.toFixed(5)}</strong></td>
        `;
        numbersTbody.appendChild(tr);
    });
}

formValidation.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (generatedNumbers.length === 0) {
        alert("Primero debe generar números U(0,1)");
        return;
    }
    
    setLoading(btnTest, true);
    
    try {
        const testName = document.getElementById('test-select').value;
        const alpha = parseFloat(document.getElementById('input-alpha').value);
        
        const payload = { numbers: generatedNumbers, alpha: alpha };
        
        const response = await fetch(`/api/test/${testName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const resData = await response.json();
        if (!response.ok) throw new Error(resData.detail || 'Error al ejecutar prueba');
        
        renderTestResults(resData.result, testName);
        
    } catch (error) {
        alert(error.message);
    } finally {
        setLoading(btnTest, false);
    }
});

function renderTestResults(result, testName) {
    testResults.classList.remove('hidden');
    testTitle.textContent = result.test;
    testStatusBanner.className = 'status-banner ' + (result.passed ? 'success' : 'fail');
    testVerdict.textContent = result.passed ? 'Aceptado' : 'Rechazado';
    
    const reasoningText = document.getElementById('reasoning-text');
    let msg = "";
    if (result.test === "Prueba de Medias") {
        msg = `La prueba evalúa si el promedio de los números generados (${result.details.media.toFixed(4)}) se aproxima a la media teórica de 0.5. Como el estadístico Z_0 (${result.details.z0.toFixed(4)}) ${result.passed ? 'cae dentro' : 'cae fuera'} del rango permitido [-${result.details.z_alpha_2.toFixed(4)}, ${result.details.z_alpha_2.toFixed(4)}], la hipótesis de uniformidad se ${result.passed ? 'acepta' : 'rechaza'}.`;
    } else if (result.test === "Prueba de Varianza") {
        msg = `La prueba verifica si la dispersión (varianza) de la muestra (${result.details.varianza.toFixed(4)}) es consistente con 1/12 ≈ 0.0833. Al estar ${result.passed ? 'dentro' : 'fuera'} de los límites [${result.details.limite_inferior.toFixed(4)}, ${result.details.limite_superior.toFixed(4)}], la prueba es ${result.passed ? 'aprobada' : 'rechazada'}.`;
    } else if (result.test === "Prueba Chi-Cuadrada") {
        msg = `La prueba clasifica los números en ${result.details.m} intervalos. El estadístico C fue ${result.details.chi2_obs.toFixed(4)}, que es ${result.passed ? 'menor' : 'mayor'} que el límite crítico ${result.details.chi2_critico.toFixed(4)}, por tanto ${result.passed ? 'pasa' : 'no pasa'} la validación.`;
    } else if (result.test === "Prueba de Poker") {
        msg = `Se analizó cada número como una mano de poker. El valor Chi-cuadrado fue ${result.details.chi2_obs.toFixed(4)} (${result.passed ? 'inferior' : 'superior'} al límite crítico ${result.details.chi2_critico.toFixed(4)}), por lo que los números ${result.passed ? 'son independientes' : 'tienen patrones'}.`;
    } else if (result.test === "Prueba de Corridas (Arriba/Abajo)") {
        msg = `Se contó un total de ${result.details.corridas} corridas. El estadístico Z0 (${result.details.z0.toFixed(4)}) está ${result.passed ? 'dentro' : 'fuera'} del margen ±${result.details.z_alpha_2.toFixed(4)}.`;
    } else if (result.test === "Prueba de Series (2D)") {
        msg = `Se distribuyeron pares en cuadrícula ${result.details.m}x${result.details.m}. Variación Chi-cuadrado C = ${result.details.chi2_obs.toFixed(4)} vs límite ${result.details.chi2_critico.toFixed(4)}.`;
    } else if (result.test === "Prueba Kolmogorov-Smirnov") {
        msg = `Desviación máxima D = ${result.details.d_max.toFixed(4)} vs límite D_critico = ${result.details.d_critico.toFixed(4)}. La muestra ${result.passed ? 'cumple' : 'no cumple'} uniformidad.`;
    }
    reasoningText.innerHTML = `<strong>Conclusión Analítica:</strong> ${msg}`;
    
    latexContainer.innerHTML = result.latex;
    if (window.renderMathInElement) {
        renderMathInElement(latexContainer, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true},
                {left: '\\begin{align*}', right: '\\end{align*}', display: true}
            ],
            throwOnError: false
        });
    }
    
    renderChart(testName, result.details);
    renderExtraDetails(testName, result.details);
}

function renderChart(testName, details) {
    const ctx = document.getElementById('test-chart').getContext('2d');
    if (currentChart) currentChart.destroy();
    
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    let config = {};
    
    if (testName === 'medias') {
        const za2 = details.z_alpha_2;
        const z0 = details.z0;
        const zMax = Math.max(Math.abs(z0) * 1.3, za2 * 1.6, 3.5);
        const steps = 100;
        const curvaTotal = [], zonaAceptacion = [];
        
        for (let i = 0; i <= steps; i++) {
            const z = -zMax + (2 * zMax * i / steps);
            const y = Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI);
            curvaTotal.push({ x: parseFloat(z.toFixed(4)), y: parseFloat(y.toFixed(5)) });
            zonaAceptacion.push({ x: parseFloat(z.toFixed(4)), y: (z >= -za2 && z <= za2) ? parseFloat(y.toFixed(5)) : null });
        }
        
        config = {
            type: 'scatter',
            data: {
                datasets: [
                    { label: 'N(0,1)', data: curvaTotal, borderColor: '#94a3b8', showLine: true, pointRadius: 0 },
                    { label: 'Zona Aceptación', data: zonaAceptacion, backgroundColor: 'rgba(16, 185, 129, 0.2)', showLine: true, fill: true, pointRadius: 0 },
                    { label: `Z₀ = ${z0.toFixed(4)}`, data: [{x: z0, y: 0}, {x: z0, y: 0.3}], borderColor: '#f59e0b', showLine: true, borderWidth: 3 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    } else if (testName === 'varianza') {
        config = {
            type: 'bar',
            data: {
                labels: ['S² Muestral', 'σ² Teórica'],
                datasets: [{
                    label: 'Varianza',
                    data: [details.varianza, 1/12],
                    backgroundColor: [details.passed ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)', 'rgba(148, 163, 184, 0.5)']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    } else if (testName === 'chi_cuadrada' || testName === 'poker') {
        const labels = testName === 'chi_cuadrada' ? details.frecuencias_observadas.map((_, i) => `Int ${i+1}`) : Object.keys(details.fo_agrupado);
        const fo = testName === 'chi_cuadrada' ? details.frecuencias_observadas : Object.values(details.fo_agrupado);
        const fe = testName === 'chi_cuadrada' ? Array(details.m).fill(details.frecuencia_esperada) : Object.values(details.fe_agrupado);
        
        config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Observado (FO)', data: fo, backgroundColor: 'rgba(59, 130, 246, 0.6)' },
                    { label: 'Esperado (FE)', data: fe, type: 'line', borderColor: '#10b981', borderWidth: 2 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    } else {
        const sorted = [...generatedNumbers].sort((a, b) => a - b);
        const n = sorted.length;
        const empData = [{ x: 0, y: 0 }];
        sorted.forEach((val, i) => {
            empData.push({ x: val, y: i / n });
            empData.push({ x: val, y: (i + 1) / n });
        });
        empData.push({ x: 1, y: 1 });
        
        config = {
            type: 'scatter',
            data: {
                datasets: [
                    { label: 'FDA Empírica Sₙ(x)', data: empData, borderColor: '#3b82f6', showLine: true, pointRadius: 0 },
                    { label: 'FDA Teórica F(x)=x', data: [{x:0, y:0}, {x:1, y:1}], borderColor: '#10b981', showLine: true, borderDash: [5,5], pointRadius: 0 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    }
    
    currentChart = new Chart(ctx, config);
}

function renderExtraDetails(testName, details) {
    const container = document.getElementById('extra-details-container');
    const thead = document.querySelector('#extra-table thead');
    const tbody = document.getElementById('extra-tbody');
    
    thead.innerHTML = '';
    tbody.innerHTML = '';
    container.classList.add('hidden');
    
    if (testName === 'chi_cuadrada') {
        container.classList.remove('hidden');
        thead.innerHTML = '<tr><th>Intervalo</th><th>FO</th><th>FE</th><th>(FO-FE)²/FE</th></tr>';
        details.frecuencias_observadas.forEach((fo, i) => {
            const fe = details.frecuencia_esperada;
            const contrib = ((fo - fe) ** 2) / fe;
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>Int ${i+1}</td><td>${fo}</td><td>${fe.toFixed(2)}</td><td>${contrib.toFixed(4)}</td>`;
            tbody.appendChild(tr);
        });
    }
}

// ==============================================================================
// LOGICA PESTAÑA 2: VARIABLES ALEATORIAS Y DISTRIBUCIONES DE PROBABILIDAD
// ==============================================================================
const distTypeSelect = document.getElementById('dist-type-select');
const distParamsContainer = document.getElementById('dist-params-container');
const distFormGenerator = document.getElementById('dist-generator-form');
const btnDistGenerate = document.getElementById('btn-dist-generate');
const btnDistReset = document.getElementById('btn-dist-reset');

const distGenerationResults = document.getElementById('dist-generation-results');
const distNumbersTbody = document.getElementById('dist-numbers-tbody');

const distValidationSection = document.getElementById('dist-validation-section');
const distFormValidation = document.getElementById('dist-validation-form');
const btnDistTest = document.getElementById('btn-dist-test');
const distTestResults = document.getElementById('dist-test-results');

const distTestStatusBanner = document.getElementById('dist-test-status-banner');
const distTestTitle = document.getElementById('dist-test-title');
const distTestVerdict = document.getElementById('dist-test-verdict');
const distLatexContainer = document.getElementById('dist-latex-container');

// Renderizado dinámico de campos de parámetros según distribución
function updateDistParamFields() {
    const dist = distTypeSelect.value;
    distParamsContainer.innerHTML = '';
    
    let fields = [];
    if (dist === 'uniform_continuous') {
        fields = [
            { id: 'dist-param-a', label: 'Límite Inferior (a)', type: 'number', val: 0, step: 'any' },
            { id: 'dist-param-b', label: 'Límite Superior (b)', type: 'number', val: 10, step: 'any' }
        ];
    } else if (dist === 'exponential') {
        fields = [
            { id: 'dist-param-lambd', label: 'Tasa (λ > 0)', type: 'number', val: 0.5, step: 'any' }
        ];
    } else if (dist === 'normal') {
        fields = [
            { id: 'dist-param-mu', label: 'Media (μ)', type: 'number', val: 0, step: 'any' },
            { id: 'dist-param-sigma', label: 'Desviación Estándar (σ > 0)', type: 'number', val: 1, step: 'any' }
        ];
    } else if (dist === 'erlang') {
        fields = [
            { id: 'dist-param-k', label: 'Etapas (k ∈ ℤ⁺)', type: 'number', val: 3, step: 1 },
            { id: 'dist-param-lambd', label: 'Tasa por etapa (λ)', type: 'number', val: 0.5, step: 'any' }
        ];
    } else if (dist === 'triangular') {
        fields = [
            { id: 'dist-param-a', label: 'Mínimo (a)', type: 'number', val: 0, step: 'any' },
            { id: 'dist-param-b', label: 'Máximo (b)', type: 'number', val: 10, step: 'any' },
            { id: 'dist-param-c', label: 'Moda (c: a ≤ c ≤ b)', type: 'number', val: 4, step: 'any' }
        ];
    } else if (dist === 'uniform_discrete') {
        fields = [
            { id: 'dist-param-a', label: 'Mínimo entero (a)', type: 'number', val: 1, step: 1 },
            { id: 'dist-param-b', label: 'Máximo entero (b)', type: 'number', val: 6, step: 1 }
        ];
    } else if (dist === 'bernoulli') {
        fields = [
            { id: 'dist-param-p', label: 'Probabilidad de éxito (p)', type: 'number', val: 0.5, step: '0.01' }
        ];
    } else if (dist === 'binomial') {
        fields = [
            { id: 'dist-param-n_trials', label: 'Número de ensayos (n)', type: 'number', val: 10, step: 1 },
            { id: 'dist-param-p', label: 'Probabilidad de éxito (p)', type: 'number', val: 0.5, step: '0.01' }
        ];
    } else if (dist === 'poisson') {
        fields = [
            { id: 'dist-param-lambd', label: 'Tasa promedio (λ)', type: 'number', val: 4, step: 'any' }
        ];
    } else if (dist === 'geometric') {
        fields = [
            { id: 'dist-param-p', label: 'Probabilidad de éxito (p)', type: 'number', val: 0.3, step: '0.01' }
        ];
    }
    
    fields.forEach(f => {
        const div = document.createElement('div');
        div.className = 'input-group';
        div.innerHTML = `
            <label for="${f.id}">${f.label}</label>
            <input type="${f.type}" id="${f.id}" value="${f.val}" step="${f.step || 'any'}" required>
        `;
        distParamsContainer.appendChild(div);
    });
}

distTypeSelect.addEventListener('change', updateDistParamFields);
updateDistParamFields(); // Inicializar

btnDistReset.addEventListener('click', () => {
    distGeneratedNumbers = [];
    distFormGenerator.reset();
    updateDistParamFields();
    
    distGenerationResults.classList.add('hidden');
    distValidationSection.classList.add('hidden');
    distTestResults.classList.add('hidden');
    
    if (currentDistChart) {
        currentDistChart.destroy();
        currentDistChart = null;
    }
});

// Función para extraer objeto de parámetros
function getDistParamsFromUI() {
    const dist = distTypeSelect.value;
    const params = {};
    
    if (dist === 'uniform_continuous' || dist === 'uniform_discrete') {
        params.a = parseFloat(document.getElementById('dist-param-a').value);
        params.b = parseFloat(document.getElementById('dist-param-b').value);
    } else if (dist === 'exponential' || dist === 'poisson') {
        params.lambd = parseFloat(document.getElementById('dist-param-lambd').value);
    } else if (dist === 'normal') {
        params.mu = parseFloat(document.getElementById('dist-param-mu').value);
        params.sigma = parseFloat(document.getElementById('dist-param-sigma').value);
    } else if (dist === 'erlang') {
        params.k = parseInt(document.getElementById('dist-param-k').value);
        params.lambd = parseFloat(document.getElementById('dist-param-lambd').value);
    } else if (dist === 'triangular') {
        params.a = parseFloat(document.getElementById('dist-param-a').value);
        params.b = parseFloat(document.getElementById('dist-param-b').value);
        params.c = parseFloat(document.getElementById('dist-param-c').value);
    } else if (dist === 'bernoulli' || dist === 'geometric') {
        params.p = parseFloat(document.getElementById('dist-param-p').value);
    } else if (dist === 'binomial') {
        params.n_trials = parseInt(document.getElementById('dist-param-n_trials').value);
        params.p = parseFloat(document.getElementById('dist-param-p').value);
    }
    
    return params;
}

// Generador de Variables Aleatorias
distFormGenerator.addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading(btnDistGenerate, true);
    
    try {
        const distType = distTypeSelect.value;
        const n = parseInt(document.getElementById('dist-input-n').value);
        const baseGenerator = document.getElementById('dist-base-gen').value;
        const params = getDistParamsFromUI();
        
        currentDistType = distType;
        currentDistParams = params;
        
        const payload = {
            dist_type: distType,
            n: n,
            params: params,
            base_generator: baseGenerator
        };
        
        const response = await fetch('/api/distributions/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const resData = await response.json();
        if (!response.ok) throw new Error(resData.detail || 'Error al generar variables aleatorias');
        
        distGeneratedNumbers = resData.data.map(item => item.Xi);
        renderDistNumbersTable(resData.data);
        
        distGenerationResults.classList.remove('hidden');
        distValidationSection.classList.remove('hidden');
        distTestResults.classList.add('hidden');
        
    } catch (error) {
        alert(error.message);
    } finally {
        setLoading(btnDistGenerate, false);
    }
});

function renderDistNumbersTable(data) {
    distNumbersTbody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.i}</td>
            <td>${row.ri}</td>
            <td><strong>${row.Xi}</strong></td>
            <td><code>${row.formula}</code></td>
        `;
        distNumbersTbody.appendChild(tr);
    });
}

// Validador de Distribuciones
distFormValidation.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (distGeneratedNumbers.length === 0) {
        alert("Primero debe generar variables aleatorias");
        return;
    }
    
    setLoading(btnDistTest, true);
    
    try {
        const testName = document.getElementById('dist-test-select').value;
        const alpha = parseFloat(document.getElementById('dist-input-alpha').value);
        
        const payload = {
            numbers: distGeneratedNumbers,
            dist_type: currentDistType,
            params: currentDistParams,
            alpha: alpha
        };
        
        const response = await fetch(`/api/distributions/test/${testName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const resData = await response.json();
        if (!response.ok) throw new Error(resData.detail || 'Error al ejecutar prueba de distribución');
        
        renderDistTestResults(resData.result, testName);
        
    } catch (error) {
        alert(error.message);
    } finally {
        setLoading(btnDistTest, false);
    }
});

function renderDistTestResults(result, testName) {
    distTestResults.classList.remove('hidden');
    distTestTitle.textContent = result.test;
    distTestStatusBanner.className = 'status-banner ' + (result.passed ? 'success' : 'fail');
    distTestVerdict.textContent = result.passed ? 'Aceptado' : 'Rechazado';
    
    const reasoningText = document.getElementById('dist-reasoning-text');
    let msg = "";
    if (testName === "medias") {
        msg = `Evaluación de la media muestral (${result.details.media_muestral.toFixed(4)}) frente a la media teórica μ_0 (${result.details.mu_teorica.toFixed(4)}). El estadístico Z_0 (${result.details.z0.toFixed(4)}) ${result.passed ? 'está dentro' : 'está fuera'} del rango de aceptación.`;
    } else if (testName === "varianza") {
        msg = `Evaluación de la varianza muestral (${result.details.varianza_muestral.toFixed(4)}) respecto a la varianza teórica σ_0² (${result.details.var_teorica.toFixed(4)}). Se halla ${result.passed ? 'dentro' : 'fuera'} de los límites Chi-cuadrado.`;
    } else if (testName === "chi_cuadrada") {
        msg = `Prueba de bondad de ajuste en ${result.details.m} categorías/intervalos. Estadístico C = ${result.details.chi2_obs.toFixed(4)} vs límite crítico ${result.details.chi2_critico.toFixed(4)} (${result.passed ? 'cumple' : 'no cumple'}).`;
    } else if (testName === "kolmogorov_smirnov") {
        msg = `Compara la distribución empírica de la muestra con la FDA teórica de la distribución. Desviación D = ${result.details.d_max.toFixed(4)} vs límite D_critico = ${result.details.d_critico.toFixed(4)}.`;
    }
    reasoningText.innerHTML = `<strong>Conclusión Analítica:</strong> ${msg}`;
    
    distLatexContainer.innerHTML = result.latex;
    if (window.renderMathInElement) {
        renderMathInElement(distLatexContainer, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true},
                {left: '\\begin{align*}', right: '\\end{align*}', display: true}
            ],
            throwOnError: false
        });
    }
    
    renderDistChart(testName, result.details);
    renderDistExtraDetails(testName, result.details);
}

function renderDistChart(testName, details) {
    const ctx = document.getElementById('dist-test-chart').getContext('2d');
    if (currentDistChart) currentDistChart.destroy();
    
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    let config = {};
    
    if (testName === 'chi_cuadrada') {
        config = {
            type: 'bar',
            data: {
                labels: details.labels,
                datasets: [
                    { label: 'Frecuencia Observada (FO)', data: details.frecuencias_observadas, backgroundColor: 'rgba(0, 229, 255, 0.6)' },
                    { label: 'Frecuencia Esperada (FE)', data: details.frecuencias_esperadas, type: 'line', borderColor: '#ff3d00', borderWidth: 2 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    } else if (testName === 'kolmogorov_smirnov') {
        const sorted = [...distGeneratedNumbers].sort((a, b) => a - b);
        const n = sorted.length;
        const empData = [];
        sorted.forEach((val, i) => {
            empData.push({ x: val, y: (i + 1) / n });
        });
        
        config = {
            type: 'scatter',
            data: {
                datasets: [
                    { label: 'FDA Empírica Sₙ(x)', data: empData, borderColor: '#00e5ff', showLine: true, pointRadius: 2 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    } else if (testName === 'medias') {
        config = {
            type: 'bar',
            data: {
                labels: ['Media Muestral', 'Media Teórica μ₀'],
                datasets: [{
                    label: 'Valores de Media',
                    data: [details.media_muestral, details.mu_teorica],
                    backgroundColor: [details.passed ? 'rgba(0, 255, 102, 0.6)' : 'rgba(255, 0, 60, 0.6)', 'rgba(148, 163, 184, 0.5)']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    } else {
        config = {
            type: 'bar',
            data: {
                labels: ['Varianza Muestral S²', 'Varianza Teórica σ₀²'],
                datasets: [{
                    label: 'Valores de Varianza',
                    data: [details.varianza_muestral, details.var_teorica],
                    backgroundColor: [details.passed ? 'rgba(0, 255, 102, 0.6)' : 'rgba(255, 0, 60, 0.6)', 'rgba(148, 163, 184, 0.5)']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        };
    }
    
    currentDistChart = new Chart(ctx, config);
}

function renderDistExtraDetails(testName, details) {
    const container = document.getElementById('dist-extra-details-container');
    const thead = document.querySelector('#dist-extra-table thead');
    const tbody = document.getElementById('dist-extra-tbody');
    
    thead.innerHTML = '';
    tbody.innerHTML = '';
    container.classList.add('hidden');
    
    if (testName === 'chi_cuadrada') {
        container.classList.remove('hidden');
        thead.innerHTML = '<tr><th>Categoría / Intervalo</th><th>FO</th><th>FE</th><th>(FO-FE)²/FE</th></tr>';
        details.frecuencias_observadas.forEach((fo, i) => {
            const fe = details.frecuencias_esperadas[i];
            const label = details.labels[i];
            const contrib = fe > 0 ? ((fo - fe) ** 2) / fe : 0;
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${label}</td><td>${fo}</td><td>${fe.toFixed(2)}</td><td>${contrib.toFixed(4)}</td>`;
            tbody.appendChild(tr);
        });
    }
}

// Helpers
function setLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}
