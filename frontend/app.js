// Estado global de la aplicación
let generatedNumbers = [];
let currentChart = null;

// Referencias del DOM (Generador)
const formGenerator = document.getElementById('generator-form');
const methodSelect = document.getElementById('method-select');
const congruentialParams = document.getElementById('congruential-params');
const btnGenerate = document.getElementById('btn-generate');
const btnReset = document.getElementById('btn-reset');
const generationResults = document.getElementById('generation-results');
const numbersTbody = document.getElementById('numbers-tbody');

// Lógica de reseteo del generador
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

// Referencias del DOM (Validador)
const validationSection = document.getElementById('validation-section');
const formValidation = document.getElementById('validation-form');
const btnTest = document.getElementById('btn-test');
const testResults = document.getElementById('test-results');
const testStatusBanner = document.getElementById('test-status-banner');
const testTitle = document.getElementById('test-title');
const testVerdict = document.getElementById('test-verdict');
const latexContainer = document.getElementById('latex-container');

// Mostrar/Ocultar parámetros congruenciales
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

// Manejador del Generador
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
        
        if (!response.ok) {
            throw new Error(resData.detail || 'Error al generar números');
        }
        
        // Extraer los números r_i generados
        generatedNumbers = resData.data.map(item => item.r_i || item.ri); // Soportar diferentes formatos de key
        
        // Renderizar tabla
        renderNumbersTable(resData.data);
        
        // Mostrar sección de validación
        generationResults.classList.remove('hidden');
        validationSection.classList.remove('hidden');
        
        // Limpiar resultados anteriores de tests si los hubiese
        testResults.classList.add('hidden');
        
    } catch (error) {
        alert(error.message);
    } finally {
        setLoading(btnGenerate, false);
    }
});

// Renderizar tabla de números generados
function renderNumbersTable(data) {
    numbersTbody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        // Extraemos valores asegurando compatibilidad con los generadores
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

// Manejador del Validador
formValidation.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (generatedNumbers.length === 0) {
        alert("Primero debe generar números");
        return;
    }
    
    setLoading(btnTest, true);
    
    try {
        const testName = document.getElementById('test-select').value;
        const alpha = parseFloat(document.getElementById('input-alpha').value);
        
        const payload = {
            numbers: generatedNumbers,
            alpha: alpha
        };
        
        const response = await fetch(`/api/test/${testName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const resData = await response.json();
        
        if (!response.ok) {
            throw new Error(resData.detail || 'Error al ejecutar prueba');
        }
        
        renderTestResults(resData.result, testName);
        
    } catch (error) {
        alert(error.message);
    } finally {
        setLoading(btnTest, false);
    }
});

function renderTestResults(result, testName) {
    testResults.classList.remove('hidden');
    
    // Actualizar Banner
    testTitle.textContent = result.test;
    testStatusBanner.className = 'status-banner ' + (result.passed ? 'success' : 'fail');
    testVerdict.textContent = result.passed ? 'Aceptado' : 'Rechazado';
    
    // Generar razonamiento
    const reasoningText = document.getElementById('reasoning-text');
    let msg = "";
    if (result.test === "Prueba de Medias") {
        msg = `La prueba evalúa si el promedio de los números generados (${result.details.media.toFixed(4)}) se aproxima a la media teórica de 0.5. Como el estadístico Z_0 (${result.details.z0.toFixed(4)}) ${result.passed ? 'cae dentro' : 'cae fuera'} del rango permitido por el nivel de significancia [-${result.details.z_alpha_2.toFixed(4)}, ${result.details.z_alpha_2.toFixed(4)}], la hipótesis de uniformidad se ${result.passed ? 'acepta' : 'rechaza'}.`;
    } else if (result.test === "Prueba de Varianza") {
        msg = `La prueba verifica si la dispersión (varianza) de la muestra (${result.details.varianza.toFixed(4)}) es consistente con la teórica (1/12 ≈ 0.0833). Al estar ${result.passed ? 'dentro' : 'fuera'} de los límites de aceptación Chi-cuadrado [${result.details.limite_inferior.toFixed(4)}, ${result.details.limite_superior.toFixed(4)}], la prueba es ${result.passed ? 'aprobada' : 'rechazada'}.`;
    } else if (result.test === "Prueba Chi-Cuadrada") {
        msg = `La prueba clasifica los números en ${result.details.m} intervalos buscando que la cantidad en cada intervalo (frecuencia observada) se parezca a la esperada (${result.details.frecuencia_esperada.toFixed(2)}). El estadístico calculado fue ${result.details.chi2_obs.toFixed(4)}, que es ${result.passed ? 'menor' : 'mayor'} que el límite crítico ${result.details.chi2_critico.toFixed(4)}, por tanto ${result.passed ? 'pasa' : 'no pasa'} la validación de uniformidad.`;
    } else if (result.test === "Prueba de Poker") {
        msg = `Se analizó cada número como una mano de poker según sus 5 primeros decimales. El valor Chi-cuadrado calculado agrupando clases fue ${result.details.chi2_obs.toFixed(4)}, que al ser ${result.passed ? 'inferior' : 'superior'} al límite crítico ${result.details.chi2_critico.toFixed(4)}, indica que los números ${result.passed ? 'son independientes' : 'tienen un patrón'}.`;
    } else if (result.test === "Prueba de Corridas (Arriba/Abajo)") {
        msg = `Se contó cuántas secuencias de crecimiento/decrecimiento ocurrieron (${result.details.corridas} corridas). El estadístico Z calculado (${result.details.z0.toFixed(4)}) está ${result.passed ? 'dentro' : 'fuera'} del margen de aceptación ±${result.details.z_alpha_2.toFixed(4)}. Los números ${result.passed ? 'superan' : 'fallan'} la prueba de independencia.`;
    } else if (result.test === "Prueba de Series (2D)") {
        msg = `Se tomaron pares consecutivos y se distribuyeron en una cuadrícula ${result.details.m}x${result.details.m}. El valor de variación espacial Chi-cuadrado fue ${result.details.chi2_obs.toFixed(4)}. Como es ${result.passed ? 'menor' : 'mayor'} al límite tolerado (${result.details.chi2_critico.toFixed(4)}), los pares de datos ${result.passed ? 'no muestran' : 'muestran'} correlación bidimensional.`;
    } else if (result.test === "Prueba Kolmogorov-Smirnov") {
        msg = `Esta prueba mide la mayor diferencia entre la distribución empírica de los datos y una uniforme perfecta. La desviación encontrada fue D = ${result.details.d_max.toFixed(4)}, la cual es ${result.passed ? 'menor' : 'mayor'} que la divergencia máxima permitida (${result.details.d_critico.toFixed(4)}). Por ende, se ${result.passed ? 'acepta' : 'rechaza'} que provienen de una distribución Uniforme.`;
    }
    reasoningText.innerHTML = `<strong>Conclusión Analítica:</strong> ${msg}`;
    
    // Renderizar LaTeX
    latexContainer.innerHTML = result.latex;
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
    
    // Renderizar Gráfico según la prueba
    renderChart(testName, result.details);
    
    // Renderizar tabla de detalles extras (chi_cuadrada y poker)
    renderExtraDetails(testName, result.details);
}

function renderChart(testName, details) {
    const ctx = document.getElementById('test-chart').getContext('2d');
    
    if (currentChart) {
        currentChart.destroy();
    }
    
    // Tema Oscuro para Chart.js
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    
    let config = {};
    
    if (testName === 'medias') {
        // Curva normal N(0,1) con Z0 marcado y región de aceptación sombreada
        const za2 = details.z_alpha_2;
        const z0 = details.z0;
        const zMax = Math.max(Math.abs(z0) * 1.3, za2 * 1.6, 3.5);
        const steps = 120;
        const curvaTotal = [];
        const zonaAceptacion = [];
        
        for (let i = 0; i <= steps; i++) {
            const z = -zMax + (2 * zMax * i / steps);
            const y = Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI);
            curvaTotal.push({ x: parseFloat(z.toFixed(4)), y: parseFloat(y.toFixed(5)) });
            zonaAceptacion.push({ x: parseFloat(z.toFixed(4)), y: (z >= -za2 && z <= za2) ? parseFloat(y.toFixed(5)) : null });
        }
        
        // Línea vertical para Z0
        const yMax = 1 / Math.sqrt(2 * Math.PI);
        const lineaZ0 = [
            { x: parseFloat(z0.toFixed(4)), y: 0 },
            { x: parseFloat(z0.toFixed(4)), y: parseFloat((yMax * 0.85).toFixed(5)) }
        ];
        
        config = {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Distribución N(0,1)',
                        data: curvaTotal,
                        borderColor: 'rgba(148, 163, 184, 0.7)',
                        backgroundColor: 'transparent',
                        showLine: true,
                        pointRadius: 0,
                        borderWidth: 1.5
                    },
                    {
                        label: `Zona de Aceptación (|Z| < ${za2.toFixed(4)})`,
                        data: zonaAceptacion,
                        borderColor: 'rgba(16, 185, 129, 0)',
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        showLine: true,
                        fill: true,
                        pointRadius: 0,
                        borderWidth: 0
                    },
                    {
                        label: `Z₀ = ${z0.toFixed(4)}`,
                        data: lineaZ0,
                        borderColor: '#f59e0b',
                        backgroundColor: '#f59e0b',
                        showLine: true,
                        pointRadius: [5, 0],
                        borderWidth: 2.5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: 'Z (estadístico normalizado)' } },
                    y: { min: 0, title: { display: true, text: 'Densidad f(Z)' } }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Prueba bilateral: se rechaza si |Z₀| ≥ Z_α/2 = ${za2.toFixed(4)}`
                    },
                    legend: { position: 'bottom' }
                }
            }
        };

    } else if (testName === 'varianza') {
        // Bar chart: varianza muestral vs teórica, con líneas de límites LI y LS
        const varianza = details.varianza;
        const li = details.limite_inferior;
        const ls = details.limite_superior;
        const teo = 1 / 12;
        const dentroLimites = varianza >= li && varianza <= ls;
        
        config = {
            type: 'bar',
            data: {
                labels: ['Varianza Muestral', 'Varianza Teórica (1/12)'],
                datasets: [
                    {
                        label: 'Valor de Varianza',
                        data: [varianza, teo],
                        backgroundColor: [
                            dentroLimites ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)',
                            'rgba(148, 163, 184, 0.5)'
                        ],
                        borderColor: [
                            dentroLimites ? '#10b981' : '#ef4444',
                            '#94a3b8'
                        ],
                        borderWidth: 2
                    },
                    {
                        label: `Límite Inferior LI = ${li.toFixed(5)}`,
                        data: [li, li],
                        type: 'line',
                        borderColor: '#f59e0b',
                        borderDash: [6, 4],
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false
                    },
                    {
                        label: `Límite Superior LS = ${ls.toFixed(5)}`,
                        data: [ls, ls],
                        type: 'line',
                        borderColor: '#ef4444',
                        borderDash: [6, 4],
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        title: { display: true, text: 'Varianza' }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Intervalo de aceptación: [${li.toFixed(5)}, ${ls.toFixed(5)}]`
                    },
                    legend: { position: 'bottom' }
                }
            }
        };

    } else if (testName === 'chi_cuadrada' || testName === 'poker') {
        // Gráfico de Barras: Frecuencias Observadas vs Esperadas
        let labels, fo, fe;
        
        if (testName === 'chi_cuadrada') {
            labels = details.frecuencias_observadas.map((_, i) => `Int ${i+1}`);
            fo = details.frecuencias_observadas;
            fe = Array(details.m).fill(details.frecuencia_esperada);
        } else {
            labels = Object.keys(details.fo_agrupado);
            fo = Object.values(details.fo_agrupado);
            fe = Object.values(details.fe_agrupado);
        }
        
        config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Frecuencia Observada (FO)',
                        data: fo,
                        backgroundColor: 'rgba(59, 130, 246, 0.6)',
                        borderColor: '#3b82f6',
                        borderWidth: 1
                    },
                    {
                        label: 'Frecuencia Esperada (FE)',
                        data: fe,
                        type: 'line',
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        borderWidth: 2,
                        pointBackgroundColor: '#10b981'
                    }
                ]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `C = ${details.chi2_obs.toFixed(4)} vs χ²_crítico = ${details.chi2_critico.toFixed(4)} (gl=${details.grados_libertad})`
                    },
                    legend: { position: 'bottom' }
                }
            }
        };

    } else if (testName === 'corridas') {
        // Bar chart de la secuencia S: 1=sube (verde), 0=baja (rojo)
        // Los agrupamientos de barras del mismo color representan las "corridas"
        const S = details.secuencia_S;
        const labelsS = S.map((_, i) => i + 1);
        
        config = {
            type: 'bar',
            data: {
                labels: labelsS,
                datasets: [{
                    label: 'Dirección de la serie (1=Sube, 0=Baja)',
                    data: S,
                    backgroundColor: S.map(v => v === 1 ? 'rgba(16, 185, 129, 0.75)' : 'rgba(239, 68, 68, 0.75)'),
                    borderColor: S.map(v => v === 1 ? '#10b981' : '#ef4444'),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: -0.1,
                        max: 1.3,
                        ticks: {
                            stepSize: 1,
                            callback: val => val === 1 ? 'Sube' : val === 0 ? 'Baja' : ''
                        },
                        title: { display: true, text: 'Dirección' }
                    },
                    x: {
                        title: { display: true, text: 'Posición en secuencia (primeros 20)' }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `${details.corridas} corridas | Esperado: ${details.mu_a.toFixed(2)} | Z₀ = ${details.z0.toFixed(4)}`
                    },
                    legend: { display: false }
                }
            }
        };

    } else if (testName === 'series') {
        // Gráfico de Dispersión 2D de pares consecutivos
        const dataPoints = [];
        for (let i = 0; i < generatedNumbers.length - 1; i++) {
            dataPoints.push({ x: generatedNumbers[i], y: generatedNumbers[i+1] });
        }
        
        config = {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Pares consecutivos (xᵢ, xᵢ₊₁)',
                    data: dataPoints,
                    backgroundColor: 'rgba(139, 92, 246, 0.55)',
                    borderColor: '#8b5cf6',
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { min: 0, max: 1, title: { display: true, text: 'xᵢ' } },
                    y: { min: 0, max: 1, title: { display: true, text: 'xᵢ₊₁' } }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Cuadrícula ${details.m}×${details.m} | C = ${details.chi2_obs.toFixed(4)} vs χ²_crítico = ${details.chi2_critico.toFixed(4)}`
                    }
                }
            }
        };

    } else if (testName === 'kolmogorov_smirnov') {
        // FDA Empírica (función escalón) vs FDA Teórica F(x)=x
        const sorted = [...generatedNumbers].sort((a, b) => a - b);
        const n = sorted.length;
        const dMax = details.d_max;
        const dCrit = details.d_critico;
        
        // Construir la función escalón empírica con saltos explícitos en cada x_i
        const empData = [{ x: 0, y: 0 }];
        for (let i = 0; i < n; i++) {
            // Punto justo antes del salto (valor previo)
            empData.push({ x: sorted[i], y: i / n });
            // Punto del salto (valor nuevo)
            empData.push({ x: sorted[i], y: (i + 1) / n });
        }
        empData.push({ x: 1, y: 1 });
        
        // FDA Teórica: dos puntos bastan (línea recta)
        const teoData = [{ x: 0, y: 0 }, { x: 1, y: 1 }];
        
        config = {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'FDA Empírica Sₙ(x)',
                        data: empData,
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        showLine: true,
                        pointRadius: 0,
                        borderWidth: 2
                    },
                    {
                        label: 'FDA Teórica F(x) = x',
                        data: teoData,
                        borderColor: '#10b981',
                        backgroundColor: 'transparent',
                        showLine: true,
                        pointRadius: 0,
                        borderWidth: 2,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { min: 0, max: 1, title: { display: true, text: 'x' } },
                    y: { min: 0, max: 1, title: { display: true, text: 'F(x)' } }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `D_max = ${dMax.toFixed(4)} vs D_crítico = ${dCrit.toFixed(4)} (la brecha máxima entre curvas)`
                    },
                    legend: { position: 'bottom' }
                }
            }
        };

    } else {
        // Histograma genérico (fallback)
        const bins = 10;
        const counts = Array(bins).fill(0);
        generatedNumbers.forEach(n => {
            let b = Math.floor(n * bins);
            if (b === bins) b = bins - 1;
            counts[b]++;
        });
        
        config = {
            type: 'bar',
            data: {
                labels: Array.from({length: bins}, (_, i) => `[${(i/10).toFixed(1)}, ${((i+1)/10).toFixed(1)})`),
                datasets: [{
                    label: 'Distribución de Frecuencias',
                    data: counts,
                    backgroundColor: 'rgba(59, 130, 246, 0.4)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución General de la Muestra (Histograma)'
                    }
                }
            }
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
        // Tabla: Intervalo | FO | FE | (FO-FE)^2/FE
        container.classList.remove('hidden');
        const fe = details.frecuencia_esperada;
        thead.innerHTML = '<tr><th>Intervalo</th><th>F. Observada (FO)</th><th>F. Esperada (FE)</th><th>(FO - FE)² / FE</th></tr>';
        details.frecuencias_observadas.forEach((fo, i) => {
            const contrib = ((fo - fe) ** 2) / fe;
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>Int. ${i + 1}</td><td>${fo}</td><td>${fe.toFixed(4)}</td><td>${contrib.toFixed(4)}</td>`;
            tbody.appendChild(tr);
        });
        // Fila de total
        const totalTr = document.createElement('tr');
        totalTr.style.fontWeight = 'bold';
        totalTr.innerHTML = `<td><strong>Total</strong></td><td>${details.frecuencias_observadas.reduce((a,b)=>a+b,0)}</td><td>—</td><td><strong>${details.chi2_obs.toFixed(4)}</strong></td>`;
        tbody.appendChild(totalTr);
        
    } else if (testName === 'poker') {
        // Tabla: Categoría | FO | FE | FO_grup | FE_grup
        container.classList.remove('hidden');
        thead.innerHTML = '<tr><th>Categoría</th><th>FO Bruta</th><th>FE Bruta</th></tr>';
        const categorias = ['TD', '1P', '2P', 'T', 'FH', 'P', 'Q'];
        const nombres = {
            TD: 'Todos Diferentes',
            '1P': 'Un Par',
            '2P': 'Dos Pares',
            T: 'Tercia',
            FH: 'Full House',
            P: 'Poker (4 iguales)',
            Q: 'Quintilla'
        };
        categorias.forEach(k => {
            const tr = document.createElement('tr');
            const fo = details.fo_raw[k] !== undefined ? details.fo_raw[k] : 0;
            const fe = details.fe_raw[k] !== undefined ? details.fe_raw[k].toFixed(2) : '0.00';
            tr.innerHTML = `<td>${nombres[k]} (${k})</td><td>${fo}</td><td>${fe}</td>`;
            tbody.appendChild(tr);
        });
    }
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

// Inicialización de la vista
document.getElementById('input-a').required = true;
document.getElementById('input-c').required = true;
document.getElementById('input-m').required = true;
