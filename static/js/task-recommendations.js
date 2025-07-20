// Task Recommendations Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Show loading animation
    const loadingContainer = document.querySelector('.loading-container');
    
    // Hide loading animation after 1.5 seconds
    setTimeout(() => {
        if (loadingContainer) {
            loadingContainer.classList.add('hidden');
            setTimeout(() => {
                loadingContainer.style.display = 'none';
            }, 500);
        }
    }, 1500);
    
    // Initialize project selector
    const projectBtns = document.querySelectorAll('.project-btn');
    projectBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project');
            
            // Update active button
            projectBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Update project data
            updateProjectData(projectId);
        });
    });
    
    // Initialize charts
    initCharts();
    
    // Initialize Gantt chart
    initGanttChart();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize animations
    initAnimations();
});

function updateProjectData(projectId) {
    // Simulate loading data
    const loadingContainer = document.querySelector('.loading-container');
    if (loadingContainer) {
        loadingContainer.style.display = 'flex';
        loadingContainer.classList.remove('hidden');
    }
    
    // Fetch and update data based on project ID
    setTimeout(() => {
        // Update team performance chart
        updateTeamPerformanceChart(projectId);
        
        // Update task assignments
        updateTaskAssignments(projectId);
        
        // Update schedule optimization
        updateScheduleOptimization(projectId);
        
        // Update resource allocation
        updateResourceAllocation(projectId);
        
        // Update AI recommendations
        updateAIRecommendations(projectId);
        
        // Hide loading animation
        if (loadingContainer) {
            loadingContainer.classList.add('hidden');
            setTimeout(() => {
                loadingContainer.style.display = 'none';
            }, 500);
        }
    }, 800);
}

function initCharts() {
    // Team Performance Chart
    const teamCtx = document.getElementById('teamPerformanceChart');
    if (teamCtx) {
        teamCtx.chart = new Chart(teamCtx, {
            type: 'bar',
            data: {
                labels: ['Бригада 1', 'Бригада 2', 'Бригада 3', 'Бригада 4', 'Бригада 5'],
                datasets: [{
                    label: 'Эффективность',
                    data: [85, 72, 90, 65, 78],
                    backgroundColor: 'rgba(74, 108, 247, 0.7)',
                    borderColor: 'rgba(74, 108, 247, 1)',
                    borderWidth: 1,
                    borderRadius: 5,
                    barThickness: 20,
                }, {
                    label: 'Загруженность',
                    data: [70, 85, 65, 90, 75],
                    backgroundColor: 'rgba(108, 71, 255, 0.7)',
                    borderColor: 'rgba(108, 71, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 5,
                    barThickness: 20,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#94a3b8',
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Resource Allocation Chart
    const resourceCtx = document.getElementById('resourceAllocationChart');
    if (resourceCtx) {
        resourceCtx.chart = new Chart(resourceCtx, {
            type: 'doughnut',
            data: {
                labels: ['Бригада 1', 'Бригада 2', 'Бригада 3', 'Бригада 4', 'Бригада 5'],
                datasets: [{
                    data: [25, 20, 15, 25, 15],
                    backgroundColor: [
                        'rgba(74, 108, 247, 0.8)',
                        'rgba(108, 71, 255, 0.8)',
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderColor: [
                        'rgba(74, 108, 247, 1)',
                        'rgba(108, 71, 255, 1)',
                        'rgba(255, 107, 107, 1)',
                        'rgba(16, 185, 129, 1)',
                        'rgba(245, 158, 11, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#94a3b8',
                            font: {
                                size: 12
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#94a3b8',
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Schedule Optimization Chart
    const scheduleCtx = document.getElementById('scheduleOptimizationChart');
    if (scheduleCtx) {
        scheduleCtx.chart = new Chart(scheduleCtx, {
            type: 'line',
            data: {
                labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                datasets: [{
                    label: 'Текущий график',
                    data: [30, 45, 60, 70, 65, 50, 40],
                    borderColor: 'rgba(255, 107, 107, 1)',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Оптимизированный график',
                    data: [35, 50, 65, 75, 70, 60, 45],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#94a3b8',
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
}

function initGanttChart(projectId = 'project1') {
    const ganttContainer = document.querySelector('.gantt-container');
    if (!ganttContainer) return;
    
    // Get today's date
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    
    // Generate dates for the next 14 days
    const dates = [];
    for (let i = 0; i < 14; i++) {
        const date = new Date();
        date.setDate(today.getDate() + i);
        dates.push({
            date: date.toISOString().split('T')[0],
            day: date.getDate(),
            isToday: i === 0
        });
    }
    
    // Sample tasks data based on project
    let tasks;
    
    if (projectId === 'project2') {
        tasks = [
            {
                name: 'Демонтаж кровли',
                start: 0,
                duration: 3,
                completion: 70
            },
            {
                name: 'Демонтаж стен',
                start: 2,
                duration: 5,
                completion: 40
            },
            {
                name: 'Вывоз мусора',
                start: 4,
                duration: 6,
                completion: 20
            },
            {
                name: 'Планировка участка',
                start: 8,
                duration: 4,
                completion: 0
            }
        ];
    } else {
        tasks = [
            {
                name: 'Земляные работы',
                start: 0,
                duration: 5,
                completion: 60
            },
            {
                name: 'Фундаментные работы',
                start: 3,
                duration: 4,
                completion: 30
            },
            {
                name: 'Монтаж конструкций',
                start: 6,
                duration: 7,
                completion: 0
            },
            {
                name: 'Отделочные работы',
                start: 10,
                duration: 4,
                completion: 0
            }
        ];
    }
    
    // Create Gantt chart HTML
    let ganttHTML = `
        <table class="gantt-chart">
            <thead class="gantt-header">
                <tr>
                    <th>Задача</th>
    `;
    
    // Add date headers
    dates.forEach(date => {
        ganttHTML += `<th class="${date.isToday ? 'gantt-today' : ''}">${date.day}</th>`;
    });
    
    ganttHTML += `
                </tr>
            </thead>
            <tbody>
    `;
    
    // Add task rows
    tasks.forEach(task => {
        ganttHTML += `
            <tr class="gantt-row">
                <td class="gantt-task-name">${task.name}</td>
        `;
        
        // Add task cells
        for (let i = 0; i < dates.length; i++) {
            const isInRange = i >= task.start && i < task.start + task.duration;
            ganttHTML += `
                <td class="gantt-cell ${dates[i].isToday ? 'gantt-today' : ''}">
                    ${isInRange ? `
                        <div class="gantt-bar" style="width: 100%; background: linear-gradient(90deg, rgba(74, 108, 247, 0.8) ${task.completion}%, rgba(74, 108, 247, 0.4) ${task.completion}%)">
                            <div class="gantt-bar-label">${task.completion}%</div>
                        </div>
                    ` : ''}
                </td>
            `;
        }
        
        ganttHTML += `</tr>`;
    });
    
    ganttHTML += `
            </tbody>
        </table>
    `;
    
    ganttContainer.innerHTML = ganttHTML;
}

function initTooltips() {
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    document.body.appendChild(tooltip);
    
    // Add tooltip functionality to team cards
    const teamCards = document.querySelectorAll('.team-card');
    teamCards.forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            const teamName = this.querySelector('.team-name').textContent;
            const teamRole = this.querySelector('.team-role').textContent;
            
            tooltip.innerHTML = `
                <div class="tooltip-title">${teamName}</div>
                <div class="tooltip-content">
                    <p>${teamRole}</p>
                    <p>Эффективность: 85%</p>
                    <p>Загруженность: 70%</p>
                    <p>Завершенных задач: 12</p>
                </div>
            `;
            
            positionTooltip(e, tooltip);
            tooltip.classList.add('visible');
        });
        
        card.addEventListener('mousemove', function(e) {
            positionTooltip(e, tooltip);
        });
        
        card.addEventListener('mouseleave', function() {
            tooltip.classList.remove('visible');
        });
    });
    
    // Add tooltip functionality to task items
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach(item => {
        item.addEventListener('mouseenter', function(e) {
            const taskTitle = this.querySelector('.task-title').textContent;
            const taskDesc = this.querySelector('.task-desc').textContent;
            
            tooltip.innerHTML = `
                <div class="tooltip-title">${taskTitle}</div>
                <div class="tooltip-content">
                    <p>${taskDesc}</p>
                    <p>Срок: 3 дня</p>
                    <p>Требуемые ресурсы: 4 человека</p>
                    <p>Зависимости: Земляные работы</p>
                </div>
            `;
            
            positionTooltip(e, tooltip);
            tooltip.classList.add('visible');
        });
        
        item.addEventListener('mousemove', function(e) {
            positionTooltip(e, tooltip);
        });
        
        item.addEventListener('mouseleave', function() {
            tooltip.classList.remove('visible');
        });
    });
}

function positionTooltip(e, tooltip) {
    const x = e.clientX + 10;
    const y = e.clientY + 10;
    
    // Check if tooltip would go off screen
    const tooltipRect = tooltip.getBoundingClientRect();
    const rightEdge = x + tooltipRect.width;
    const bottomEdge = y + tooltipRect.height;
    
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Adjust position if needed
    const adjustedX = rightEdge > viewportWidth ? viewportWidth - tooltipRect.width - 10 : x;
    const adjustedY = bottomEdge > viewportHeight ? viewportHeight - tooltipRect.height - 10 : y;
    
    tooltip.style.left = `${adjustedX}px`;
    tooltip.style.top = `${adjustedY}px`;
}

function initAnimations() {
    // Animate progress bars
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach(fill => {
        const width = fill.getAttribute('data-width') + '%';
        setTimeout(() => {
            fill.style.width = width;
        }, 300);
    });
    
    // Animate resource bars
    const resourceBars = document.querySelectorAll('.resource-bar');
    resourceBars.forEach(bar => {
        const width = bar.getAttribute('data-width') + '%';
        setTimeout(() => {
            bar.style.width = width;
        }, 300);
    });
    
    // Animate efficiency fill
    const efficiencyFills = document.querySelectorAll('.efficiency-fill');
    efficiencyFills.forEach(fill => {
        const width = fill.getAttribute('data-width') + '%';
        setTimeout(() => {
            fill.style.width = width;
        }, 300);
    });
}

// Placeholder functions for project data updates
function updateTeamPerformanceChart(projectId) {
    console.log('Updating team performance for project:', projectId);
    
    // Fetch team data from the server
    fetch(`/analytics/api/teams/?project=${projectId}`)
        .then(response => response.json())
        .then(data => {
            // In a real application, this would update the chart with new data
            // For now, we'll just update the team list with hardcoded data
            updateTeamList(projectId);
        })
        .catch(error => console.error('Error fetching team data:', error));
}

function updateTeamList(projectId) {
    const teamListContainer = document.getElementById('team-list-container');
    if (!teamListContainer) return;
    
    // Sample team data for project2 (in a real app, this would come from the server)
    if (projectId === 'project2') {
        teamListContainer.innerHTML = `
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #1</div>
                    <div class="team-role">Демонтажные работы</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">78%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">85%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #2</div>
                    <div class="team-role">Вывоз мусора</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">82%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">75%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #3</div>
                    <div class="team-role">Земляные работы</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">75%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">80%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #4</div>
                    <div class="team-role">Планировка участка</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">70%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">65%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Reset to project1 data
        teamListContainer.innerHTML = `
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #1</div>
                    <div class="team-role">Земляные работы</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">85%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">70%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #2</div>
                    <div class="team-role">Фундаментные работы</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">72%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">85%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #3</div>
                    <div class="team-role">Монтажные работы</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">90%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">65%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="team-card">
                <div class="team-avatar">👷</div>
                <div class="team-info">
                    <div class="team-name">Бригада #4</div>
                    <div class="team-role">Отделочные работы</div>
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-value">65%</div>
                            <div class="team-stat-label">Эфф.</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-value">90%</div>
                            <div class="team-stat-label">Загр.</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Reinitialize tooltips for the new team cards
    initTooltips();
}

function updateTaskAssignments(projectId) {
    console.log('Updating task assignments for project:', projectId);
    
    const taskListContainer = document.getElementById('task-list-container');
    if (!taskListContainer) return;
    
    // Sample task data for project2 (in a real app, this would come from the server)
    if (projectId === 'project2') {
        taskListContainer.innerHTML = `
            <div class="task-item">
                <div class="task-icon">🏗️</div>
                <div class="task-content">
                    <div class="task-title">Демонтаж кровли</div>
                    <div class="task-desc">Разбор и вывоз кровельных материалов</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #1</div>
                        <div class="task-priority priority-high">Высокий приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
            
            <div class="task-item">
                <div class="task-icon">🧱</div>
                <div class="task-content">
                    <div class="task-title">Демонтаж стен и перекрытий</div>
                    <div class="task-desc">Разбор несущих и ненесущих конструкций</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #1</div>
                        <div class="task-priority priority-high">Высокий приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
            
            <div class="task-item">
                <div class="task-icon">⚙️</div>
                <div class="task-content">
                    <div class="task-title">Вывоз строительного мусора</div>
                    <div class="task-desc">Погрузка и транспортировка мусора на полигон</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #2</div>
                        <div class="task-priority priority-medium">Средний приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
            
            <div class="task-item">
                <div class="task-icon">🔧</div>
                <div class="task-content">
                    <div class="task-title">Планировка территории</div>
                    <div class="task-desc">Выравнивание участка после сноса</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #4</div>
                        <div class="task-priority priority-low">Низкий приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
        `;
    } else {
        // Reset to project1 data
        taskListContainer.innerHTML = `
            <div class="task-item">
                <div class="task-icon">🏗️</div>
                <div class="task-content">
                    <div class="task-title">Земляные работы на участке B</div>
                    <div class="task-desc">Выемка грунта и подготовка котлована под фундамент</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #1</div>
                        <div class="task-priority priority-high">Высокий приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
            
            <div class="task-item">
                <div class="task-icon">🧱</div>
                <div class="task-content">
                    <div class="task-title">Заливка фундамента секции C</div>
                    <div class="task-desc">Подготовка опалубки и заливка бетона</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #2</div>
                        <div class="task-priority priority-medium">Средний приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
            
            <div class="task-item">
                <div class="task-icon">⚙️</div>
                <div class="task-content">
                    <div class="task-title">Монтаж металлоконструкций</div>
                    <div class="task-desc">Сборка и установка металлического каркаса</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #3</div>
                        <div class="task-priority priority-medium">Средний приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
            
            <div class="task-item">
                <div class="task-icon">🔧</div>
                <div class="task-content">
                    <div class="task-title">Прокладка инженерных коммуникаций</div>
                    <div class="task-desc">Монтаж электропроводки и водопровода</div>
                    <div class="task-meta">
                        <div class="task-tag">Бригада #4</div>
                        <div class="task-priority priority-low">Низкий приоритет</div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn">✓</button>
                </div>
            </div>
        `;
    }
    
    // Reinitialize tooltips for the new task items
    initTooltips();
}

function updateScheduleOptimization(projectId) {
    console.log('Updating schedule optimization for project:', projectId);
    // In a real application, this would fetch data from the server
    // and update the schedule chart with new data
    
    // For now, we'll just update the chart with some random data
    const scheduleCtx = document.getElementById('scheduleOptimizationChart');
    if (scheduleCtx && scheduleCtx.chart) {
        if (projectId === 'project2') {
            scheduleCtx.chart.data.datasets[0].data = [25, 40, 55, 65, 60, 45, 35];
            scheduleCtx.chart.data.datasets[1].data = [30, 45, 60, 70, 65, 55, 40];
        } else {
            scheduleCtx.chart.data.datasets[0].data = [30, 45, 60, 70, 65, 50, 40];
            scheduleCtx.chart.data.datasets[1].data = [35, 50, 65, 75, 70, 60, 45];
        }
        scheduleCtx.chart.update();
    }
    
    // Update Gantt chart
    initGanttChart(projectId);
}

function updateResourceAllocation(projectId) {
    console.log('Updating resource allocation for project:', projectId);
    // In a real application, this would fetch data from the server
    // and update the resource allocation chart with new data
    
    // For now, we'll just update the chart with some random data
    const resourceCtx = document.getElementById('resourceAllocationChart');
    if (resourceCtx && resourceCtx.chart) {
        if (projectId === 'project2') {
            resourceCtx.chart.data.datasets[0].data = [30, 25, 20, 15, 10];
        } else {
            resourceCtx.chart.data.datasets[0].data = [25, 20, 15, 25, 15];
        }
        resourceCtx.chart.update();
    }
}

function updateAIRecommendations(projectId) {
    console.log('Updating AI recommendations for project:', projectId);
    
    const recommendationContainer = document.getElementById('recommendation-list-container');
    if (!recommendationContainer) return;
    
    // Sample recommendation data for project2 (in a real app, this would come from the server)
    if (projectId === 'project2') {
        recommendationContainer.innerHTML = `
            <div class="recommendation-item">
                <div class="recommendation-icon">⚡</div>
                <div class="recommendation-text">
                    <strong>Оптимизация графика демонтажа</strong>
                    Разделите бригаду #1 на две подгруппы для параллельного демонтажа кровли и стен, что сократит общее время работ на 30%.
                </div>
            </div>
            
            <div class="recommendation-item">
                <div class="recommendation-icon">🔄</div>
                <div class="recommendation-text">
                    <strong>Перераспределение ресурсов</strong>
                    Временно привлеките дополнительную технику для ускорения вывоза строительного мусора и сокращения затрат на аренду контейнеров.
                </div>
            </div>
            
            <div class="recommendation-item">
                <div class="recommendation-icon">📈</div>
                <div class="recommendation-text">
                    <strong>Оптимизация логистики</strong>
                    Организуйте непрерывный цикл вывоза мусора с использованием 3 самосвалов вместо 2 для сокращения простоев бригады #2.
                </div>
            </div>
            
            <div class="recommendation-item">
                <div class="recommendation-icon">⚠️</div>
                <div class="recommendation-text">
                    <strong>Предупреждение о безопасности</strong>
                    Усильте меры безопасности при демонтаже несущих конструкций из-за высокого риска обрушения соседних элементов.
                </div>
            </div>
        `;
    } else {
        // Reset to project1 data
        recommendationContainer.innerHTML = `
            <div class="recommendation-item">
                <div class="recommendation-icon">⚡</div>
                <div class="recommendation-text">
                    <strong>Оптимизация бригады #1</strong>
                    Перераспределите 2 рабочих из бригады #1 в бригаду #4 для ускорения отделочных работ и повышения общей эффективности на 15%.
                </div>
            </div>
            
            <div class="recommendation-item">
                <div class="recommendation-icon">🔄</div>
                <div class="recommendation-text">
                    <strong>Изменение последовательности задач</strong>
                    Начните монтаж инженерных коммуникаций параллельно с заливкой фундамента секции C для сокращения общего срока работ на 3 дня.
                </div>
            </div>
            
            <div class="recommendation-item">
                <div class="recommendation-icon">📈</div>
                <div class="recommendation-text">
                    <strong>Повышение эффективности бригады #4</strong>
                    Проведите дополнительный инструктаж по новым технологиям отделки для повышения производительности бригады на 20%.
                </div>
            </div>
            
            <div class="recommendation-item">
                <div class="recommendation-icon">⚠️</div>
                <div class="recommendation-text">
                    <strong>Предупреждение о риске</strong>
                    Высокая вероятность задержки поставки строительных материалов. Рекомендуется заранее согласовать альтернативных поставщиков.
                </div>
            </div>
        `;
    }
}