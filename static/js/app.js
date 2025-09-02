// static/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    // Basic form validation (optional)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add any custom validation if needed
        });
    });

    // Render chart if on match_results page
    const chartCanvas = document.getElementById('tutorChart');
    if (chartCanvas && typeof tutorsData !== 'undefined') {
        const labels = tutorsData.map(t => t.name);
        const currentLoads = tutorsData.map(t => t.current_load);
        const availabilities = tutorsData.map(t => t.availability);

        new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Current Load',
                        data: currentLoads,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Availability',
                        data: availabilities,
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});


    



       
    