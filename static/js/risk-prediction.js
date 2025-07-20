/**
 * Risk Prediction Analytics Dashboard JavaScript
 * 
 * This script handles the interactive elements of the risk prediction dashboard,
 * including charts, animations, and data updates.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Hide loader after page loads
    setTimeout(() => {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }
    }, 1500);
    
    // Initialize animations
    initAnimations();
    
    // Initialize charts
    initCharts();
    
    // Project selection
    document.querySelectorAll('.project-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.project-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update charts for the selected project
            updateCharts(this.getAttribute('data-project'));
        });
    });
    
    // Card hover effects
    document.querySelectorAll('.dashboard-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const glow = this.querySelector('.card-glow');
            if (glow) {
                glow.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(0, 212, 255, 0.2), transparent 70%)`;
            }
        });
    });
});

function initAnimations() {
    // Animate header elements
    gsap.from(".dashboard-title", {duration: 1, y: -50, opacity: 0, ease: "power3.out"});
    gsap.from(".dashboard-subtitle", {duration: 1, y: -30, opacity: 0, ease: "power3.out", delay: 0.3});
    gsap.from(".project-btn", {duration: 0.5, y: -20, opacity: 0, stagger: 0.1, ease: "power3.out", delay: 0.5});
    
    // Animate dashboard cards
    gsap.utils.toArray('.dashboard-card').forEach((card, i) => {
        gsap.from(card, {
            duration: 0.8,
            y: 50,
            opacity: 0,
            delay: 0.8 + (i * 0.1),
            ease: "power3.out"
        });
    });
    
    // Initialize progress bars with animation
    setTimeout(() => {
        document.querySelectorAll('.progress-fill').forEach(bar => {
            const width = bar.getAttribute('data-width');
            bar.style.width = width + '%';
        });
        
        document.querySelectorAll('.resource-bar').forEach(bar => {
            const width = bar.getAttribute('data-width');
            bar.style.width = width + '%';
        });
    }, 1000);
}

function initCharts() {
    // Main risk prediction chart
    const riskCtx = document.getElementById('riskChart');
    if (riskCtx) {
        const riskChart = new Chart(riskCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен'],
                datasets: [
                    {
                        label: 'Бюджет',
                        data: [500000, 520000, 540000, 580000, 600000, 620000, 650000, 680000, 700000],
                        borderColor: '#56ab2f',
                        backgroundColor: 'rgba(86, 171, 47, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Фактические расходы',
                        data: [500000, 530000, 570000, 620000, 650000, 690000, 740000, 800000, 850000],
                        borderColor: '#ff5e62',
                        backgroundColor: 'rgba(255, 94, 98, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Прогноз расходов',
                        data: [null, null, null, null, null, null, 740000, 820000, 900000],
                        borderColor: '#ffb347',
                        backgroundColor: 'rgba(255, 179, 71, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: 'white',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#00d4ff',
                        bodyColor: 'white',
                        borderColor: 'rgba(0, 212, 255, 0.3)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            callback: function(value) {
                                return value.toLocaleString() + ' ₽';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }
    
    // Resource distribution chart
    const resourceCtx = document.getElementById('resourceChart');
    if (resourceCtx) {
        const resourceChart = new Chart(resourceCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Материалы', 'Оборудование', 'Рабочая сила', 'Транспорт', 'Прочее'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        '#00d4ff',
                        '#ff00aa',
                        '#ffcc00',
                        '#00cc88',
                        '#aa88ff'
                    ],
                    borderColor: 'rgba(18, 18, 18, 0.8)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'white',
                            font: {
                                size: 12
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#00d4ff',
                        bodyColor: 'white',
                        borderColor: 'rgba(0, 212, 255, 0.3)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.raw + '%';
                            }
                        }
                    }
                },
                cutout: '60%',
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }
    
    // Risk factors radar chart
    const radarCtx = document.getElementById('radarChart');
    if (radarCtx) {
        const radarChart = new Chart(radarCtx.getContext('2d'), {
            type: 'radar',
            data: {
                labels: [
                    'Перерасход бюджета',
                    'Задержки поставок',
                    'Нехватка персонала',
                    'Качество материалов',
                    'Погодные условия',
                    'Изменения в проекте'
                ],
                datasets: [{
                    label: 'Текущие риски',
                    data: [80, 60, 45, 30, 70, 55],
                    backgroundColor: 'rgba(255, 0, 170, 0.2)',
                    borderColor: 'rgba(255, 0, 170, 0.8)',
                    borderWidth: 2,
                    pointBackgroundColor: '#ff00aa',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#ff00aa'
                }, {
                    label: 'Средние по отрасли',
                    data: [50, 50, 50, 50, 50, 50],
                    backgroundColor: 'rgba(0, 212, 255, 0.2)',
                    borderColor: 'rgba(0, 212, 255, 0.8)',
                    borderWidth: 2,
                    pointBackgroundColor: '#00d4ff',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#00d4ff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: {
                                size: 10
                            }
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            backdropColor: 'transparent',
                            font: {
                                size: 8
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'white',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#00d4ff',
                        bodyColor: 'white',
                        borderColor: 'rgba(0, 212, 255, 0.3)',
                        borderWidth: 1
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }
}

function updateCharts(projectId) {
    // This function would typically fetch new data from the server
    // For demo purposes, we'll just animate the existing charts
    
    // Define different datasets for each project
    const projectData = {
        'project1': {
            budget: [500000, 520000, 540000, 580000, 600000, 620000, 650000, 680000, 700000],
            actual: [500000, 530000, 570000, 620000, 650000, 690000, 740000, 800000, 850000],
            forecast: [null, null, null, null, null, null, 740000, 820000, 900000],
            resources: [35, 25, 20, 15, 5],
            risks: [80, 60, 45, 30, 70, 55]
        },
        'project2': {
            budget: [800000, 820000, 840000, 860000, 880000, 900000, 920000, 940000, 960000],
            actual: [800000, 830000, 870000, 900000, 950000, 1000000, 1050000, 1100000, 1150000],
            forecast: [null, null, null, null, null, null, 1050000, 1120000, 1200000],
            resources: [40, 20, 25, 10, 5],
            risks: [90, 50, 60, 40, 80, 70]
        }
    };
    
    // Get the selected project data
    const data = projectData[projectId] || projectData.project1;
    
    // Update the main risk chart
    const riskChart = Chart.getChart('riskChart');
    if (riskChart) {
        riskChart.data.datasets[0].data = data.budget;
        riskChart.data.datasets[1].data = data.actual;
        riskChart.data.datasets[2].data = data.forecast;
        riskChart.update();
    }
    
    // Update the resource chart
    const resourceChart = Chart.getChart('resourceChart');
    if (resourceChart) {
        resourceChart.data.datasets[0].data = data.resources;
        resourceChart.update();
    }
    
    // Update the radar chart
    const radarChart = Chart.getChart('radarChart');
    if (radarChart) {
        radarChart.data.datasets[0].data = data.risks;
        radarChart.update();
    }
    
    // Update metrics with animation
    document.querySelectorAll('.metric-value').forEach(metric => {
        const newValue = Math.floor(Math.random() * 30) + 70;
        gsap.to(metric, {
            innerHTML: newValue + '%',
            duration: 1,
            snap: { innerHTML: 1 }
        });
    });
    
    // Update progress bars
    document.querySelectorAll('.progress-fill').forEach(bar => {
        const newWidth = Math.floor(Math.random() * 50) + 50;
        bar.setAttribute('data-width', newWidth);
        bar.style.width = newWidth + '%';
    });
    
    // Update resource bars
    document.querySelectorAll('.resource-bar').forEach(bar => {
        const newWidth = Math.floor(Math.random() * 40) + 60;
        bar.setAttribute('data-width', newWidth);
        bar.style.width = newWidth + '%';
    });
}