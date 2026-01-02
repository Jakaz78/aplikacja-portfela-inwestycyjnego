

(function () {
    // --- Helper Config ---
    const formatterPLN = (v) => new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(v);
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        animation: { duration: 400, easing: 'easeOutQuart' },
        elements: { line: { borderWidth: 2 }, point: { hitRadius: 12 } },
        plugins: { legend: { display: false } }
    };

    // --- 1. Value Chart (Main) ---
    const tsEl = document.getElementById('ts-data');
    const tsCanvas = document.getElementById('valueChart');
    let chartInstance = null;

    if (tsEl && tsCanvas) {
        let initialData = { labels: [], values: [] };
        try { initialData = JSON.parse(tsEl.textContent); } catch (e) { }

        const ctx = tsCanvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, tsCanvas.height);
        gradient.addColorStop(0, 'rgba(13, 110, 253, 0.25)');
        gradient.addColorStop(1, 'rgba(13, 110, 253, 0.00)');

        function renderValueChart(data) {
            if (chartInstance) {
                chartInstance.data.labels = data.labels;
                chartInstance.data.datasets[0].data = data.values;
                chartInstance.update();
                return;
            }

            chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Wartość (PLN)',
                        data: data.values,
                        borderColor: '#0d6efd',
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 2,
                        pointHoverRadius: 6,
                    }]
                },
                options: {
                    ...commonOptions,
                    layout: { padding: { left: 8, right: 16, top: 8, bottom: 8 } },
                    scales: {
                        x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
                        y: { beginAtZero: false, grid: { color: 'rgba(0,0,0,0.06)' }, ticks: { callback: formatterPLN } }
                    },
                    plugins: {
                        ...commonOptions.plugins,
                        tooltip: { enabled: true, intersect: false, mode: 'index', callbacks: { label: (c) => ` ${formatterPLN(c.parsed.y)}` } }
                    }
                }
            });
        }

        if (initialData.labels && initialData.labels.length) {
            renderValueChart(initialData);
        }

        // Logic handled via API fetch
        const periodSelect = document.getElementById('period');
        if (periodSelect) {
            periodSelect.addEventListener('change', (e) => {
                const map = { 'day': 'D', 'week': 'W', 'month': 'M', 'quarter': 'Q' };
                const apiFreq = map[e.target.value] || 'D';
                fetch(`/portfolio/chart-data?freq=${apiFreq}`)
                    .then(r => r.json())
                    .then(d => renderValueChart(d))
                    .catch(e => console.error('Chart fetch error:', e));
            });
        }
    }

    // --- 2. Inflation Comparison Chart ---
    const infEl = document.getElementById('inflation-data');
    const infCanvas = document.getElementById('inflationCompare');

    if (infEl && infCanvas) {
        let cmp = {};
        try { cmp = JSON.parse(infEl.textContent); } catch (e) { }

        if (cmp.labels && cmp.labels.length) {
            const icCtx = infCanvas.getContext('2d');
            const labels = cmp.labels.map(d => new Date(d).toISOString().slice(0, 7)); // YYYY-MM

            new Chart(icCtx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Portfel r/r (%)',
                            data: cmp.portfolio_yoy,
                            borderColor: '#0d6efd',
                            backgroundColor: 'rgba(13,110,253,0.12)',
                            tension: 0.25,
                            pointRadius: 0,
                            yAxisID: 'y',
                        },
                        {
                            label: 'Inflacja CPI r/r (%)',
                            data: cmp.cpi_yoy,
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220,53,69,0.10)',
                            tension: 0.25,
                            pointRadius: 0,
                            yAxisID: 'y',
                        }
                    ]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        x: { grid: { display: false } },
                        y: {
                            grid: { color: 'rgba(0,0,0,0.06)' },
                            ticks: { callback: (v) => `${v}%` }
                        }
                    },
                    plugins: {
                        legend: { position: 'bottom', display: true },
                        tooltip: {
                            callbacks: {
                                label: (c) => ` ${c.dataset.label}: ${c.parsed.y?.toFixed(2)}%`
                            }
                        }
                    }
                }
            });
        }
    }
})();
