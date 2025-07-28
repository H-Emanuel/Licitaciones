// JS para estadísticas de licitaciones
window.addEventListener('DOMContentLoaded', function() {
    var labels = window.estadisticasLabels || [];
    var data = window.estadisticasData || [];
    const ctx = document.getElementById('chartLicitaciones').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Licitaciones por Operador',
                data: data,
                backgroundColor: '#0275d8',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
});
