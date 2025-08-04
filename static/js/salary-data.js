// Функция для отображения модального окна с данными из таблицы sotrudniki_zarplaty
function showRealEmployeesModal(objectId, position, dateText) {
    // Создаем модальное окно
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.zIndex = '1000';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    
    // Создаем содержимое модального окна
    const content = document.createElement('div');
    content.style.backgroundColor = '#2c3e50';
    content.style.padding = '20px';
    content.style.borderRadius = '5px';
    content.style.width = '800px';
    content.style.maxWidth = '90vw';
    content.style.color = 'white';
    
    // Заголовок
    const header = document.createElement('h3');
    header.textContent = 'Сотрудники: ' + position + ' за ' + dateText + '';
    header.style.marginTop = '0';
    content.appendChild(header);
    
    // Загрузка данных
    const loading = document.createElement('p');
    loading.textContent = 'Загрузка данных...';
    content.appendChild(loading);
    
    // Кнопка закрытия
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✗';
    closeBtn.style.backgroundColor = '#e74c3c';
    closeBtn.style.color = 'white';
    closeBtn.style.border = 'none';
    closeBtn.style.padding = '8px 16px';
    closeBtn.style.borderRadius = '4px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.marginTop = '20px';
    closeBtn.style.float = 'right';
    
    closeBtn.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Кнопка сохранения в табель (будет добавлена после таблицы)
    const saveBtn = document.createElement('button');
    saveBtn.textContent = '✓';
    saveBtn.style.backgroundColor = '#27ae60';
    saveBtn.style.color = 'white';
    saveBtn.style.border = 'none';
    saveBtn.style.padding = '8px 16px';
    saveBtn.style.borderRadius = '4px';
    saveBtn.style.cursor = 'pointer';
    saveBtn.style.marginTop = '20px';
    saveBtn.style.marginRight = '10px';
    saveBtn.style.float = 'right';
    
    saveBtn.addEventListener('click', function() {
        // Получаем данные из контекста функции
        const salaryData = window.currentSalaryData || {};
        saveEmployeeHours(objectId, position, dateText, modal, salaryData.total_hours);
    });
    
    content.appendChild(closeBtn);
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Закрытие по клику вне модального окна
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // Загружаем данные о сотрудниках из таблицы sotrudniki_zarplaty
    console.log(`Запрос данных о зарплате: /objects/${objectId}/get-salary-data/?position=${encodeURIComponent(position)}&date=${encodeURIComponent(dateText)}`)
    
    // Вызываем отладочные эндпоинты для вывода информации в терминал
    // Очищаем символ '−' (минус) из строки position для отладочного эндпоинта
    const cleanPositionForDebug = position.replace(/−/g, '-').trim();
    fetch(`/objects/${objectId}/debug-cell/?position=${encodeURIComponent(cleanPositionForDebug)}&date=${encodeURIComponent(dateText)}`);
    fetch(`/objects/${objectId}/debug-salary/?position=${encodeURIComponent(cleanPositionForDebug)}&date=${encodeURIComponent(dateText)}`)
    
    // Используем относительный URL для избежания проблем с разными доменами
    // Очищаем символ '−' (минус) из строки position, который может вызывать проблемы
    const cleanPosition = position.replace(/−/g, '-').trim();
    console.log(`Очищенная должность: ${cleanPosition}`);
    
    fetch(`/objects/${objectId}/get-salary-data/?position=${encodeURIComponent(cleanPosition)}&date=${encodeURIComponent(dateText)}`)

        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Получены данные о зарплате:', data);
            
            // Сохраняем данные в глобальной переменной
            window.currentSalaryData = data;
            
            // Удаляем сообщение о загрузке
            content.removeChild(loading);
            
            if (data.success && data.employees && data.employees.length > 0) {
                // Создаем таблицу сотрудников
                const table = document.createElement('table');
                table.style.width = '100%';
                table.style.borderCollapse = 'collapse';
                table.style.marginTop = '10px';
                
                // Заголовок таблицы
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                headerRow.style.backgroundColor = '#34495e';
                
                const thName = document.createElement('th');
                thName.textContent = 'ФИО';
                thName.style.padding = '4px';
                thName.style.textAlign = 'left';
                thName.style.border = '1px solid #2c3e50';
                thName.style.width = '30%';
                
                const thOrg = document.createElement('th');
                thOrg.textContent = 'Организация';
                thOrg.style.padding = '4px';
                thOrg.style.textAlign = 'center';
                thOrg.style.border = '1px solid #2c3e50';
                thOrg.style.width = '25%';
                
                const thSpec = document.createElement('th');
                thSpec.textContent = 'Специальность';
                thSpec.style.padding = '4px';
                thSpec.style.textAlign = 'center';
                thSpec.style.border = '1px solid #2c3e50';
                thSpec.style.width = '25%';
                
                const thHours = document.createElement('th');
                thHours.textContent = 'Отработал';
                thHours.style.padding = '4px';
                thHours.style.textAlign = 'center';
                thHours.style.border = '1px solid #2c3e50';
                thHours.style.width = '10%';
                
                const thKPI = document.createElement('th');
                thKPI.textContent = 'KPI';
                thKPI.style.padding = '4px';
                thKPI.style.textAlign = 'center';
                thKPI.style.border = '1px solid #2c3e50';
                thKPI.style.width = '10%';
                
                headerRow.appendChild(thName);
                headerRow.appendChild(thOrg);
                headerRow.appendChild(thSpec);
                headerRow.appendChild(thHours);
                headerRow.appendChild(thKPI);
                thead.appendChild(headerRow);
                table.appendChild(thead);
                
                // Тело таблицы
                const tbody = document.createElement('tbody');
                
                // Используем данные из таблицы sotrudniki_zarplaty
                data.employees.forEach(employee => {
                    const row = document.createElement('tr');
                    row.style.backgroundColor = 'rgba(255,255,255,0.1)';
                    row.dataset.employeeId = employee.id;
                    
                    const tdName = document.createElement('td');
                    tdName.textContent = employee.fio;
                    tdName.style.padding = '4px';
                    tdName.style.border = '1px solid #34495e';
                    
                    const tdOrg = document.createElement('td');
                    tdOrg.textContent = employee.organizaciya || '-';
                    tdOrg.style.padding = '4px';
                    tdOrg.style.border = '1px solid #34495e';
                    tdOrg.style.textAlign = 'center';
                    
                    const tdSpec = document.createElement('td');
                    tdSpec.textContent = employee.specialnost || '-';
                    tdSpec.style.padding = '4px';
                    tdSpec.style.border = '1px solid #34495e';
                    tdSpec.style.textAlign = 'center';
                    
                    const tdHours = document.createElement('td');
                    tdHours.textContent = employee.hours || '8';
                    tdHours.style.padding = '4px';
                    tdHours.style.border = '1px solid #34495e';
                    tdHours.style.textAlign = 'center';
                    tdHours.contentEditable = 'true';
                    tdHours.style.cursor = 'pointer';
                    tdHours.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    
                    const tdKPI = document.createElement('td');
                    tdKPI.textContent = employee.kpi || '1.0';
                    tdKPI.style.padding = '4px';
                    tdKPI.style.border = '1px solid #34495e';
                    tdKPI.style.textAlign = 'center';
                    tdKPI.contentEditable = 'true';
                    tdKPI.style.cursor = 'pointer';
                    tdKPI.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    
                    row.appendChild(tdName);
                    row.appendChild(tdOrg);
                    row.appendChild(tdSpec);
                    row.appendChild(tdHours);
                    row.appendChild(tdKPI);
                    tbody.appendChild(row);
                });
                
                table.appendChild(tbody);
                content.insertBefore(table, closeBtn);
                
                // Добавляем информацию о количестве сотрудников
                const info = document.createElement('p');
                info.textContent = `Всего сотрудников: ${data.employees.length}`;
                info.style.marginTop = '10px';
                info.style.textAlign = 'right';
                info.style.color = '#bdc3c7';
                content.insertBefore(info, closeBtn);
                
                // Добавляем кнопку "Сохранить в табель" после таблицы
                content.insertBefore(saveBtn, closeBtn);
            } else {
                // Если данные не найдены, показываем сообщение
                const noData = document.createElement('p');
                noData.textContent = 'Сотрудники не найдены';
                content.insertBefore(noData, closeBtn);
                
                // Пробуем получить данные через обычный API
                const cleanPosition = position.replace(/−/g, '-').trim();
                console.log(`Получение сотрудников через API: ${cleanPosition}`);
                fetch(`/objects/${objectId}/employees/?position=${encodeURIComponent(cleanPosition)}`)

                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(employeesData => {
                        console.log('Получены данные о сотрудниках:', employeesData);
                        
                        if (employeesData.success && employeesData.employees && employeesData.employees.length > 0) {
                            // Удаляем сообщение "Сотрудники не найдены"
                            content.removeChild(noData);
                            
                            // Создаем таблицу сотрудников
                            const table = document.createElement('table');
                            table.style.width = '100%';
                            table.style.borderCollapse = 'collapse';
                            table.style.marginTop = '10px';
                            
                            // Заголовок таблицы
                            const thead = document.createElement('thead');
                            const headerRow = document.createElement('tr');
                            headerRow.style.backgroundColor = '#34495e';
                            
                            const thName = document.createElement('th');
                            thName.textContent = 'ФИО';
                            thName.style.padding = '4px';
                            thName.style.textAlign = 'left';
                            thName.style.border = '1px solid #2c3e50';
                            thName.style.width = '30%';
                            
                            const thOrg = document.createElement('th');
                            thOrg.textContent = 'Организация';
                            thOrg.style.padding = '4px';
                            thOrg.style.textAlign = 'center';
                            thOrg.style.border = '1px solid #2c3e50';
                            thOrg.style.width = '25%';
                            
                            const thSpec = document.createElement('th');
                            thSpec.textContent = 'Специальность';
                            thSpec.style.padding = '4px';
                            thSpec.style.textAlign = 'center';
                            thSpec.style.border = '1px solid #2c3e50';
                            thSpec.style.width = '25%';
                            
                            const thHours = document.createElement('th');
                            thHours.textContent = 'Отработал';
                            thHours.style.padding = '4px';
                            thHours.style.textAlign = 'center';
                            thHours.style.border = '1px solid #2c3e50';
                            thHours.style.width = '10%';
                            
                            const thKPI = document.createElement('th');
                            thKPI.textContent = 'KPI';
                            thKPI.style.padding = '4px';
                            thKPI.style.textAlign = 'center';
                            thKPI.style.border = '1px solid #2c3e50';
                            thKPI.style.width = '10%';
                            
                            headerRow.appendChild(thName);
                            headerRow.appendChild(thOrg);
                            headerRow.appendChild(thSpec);
                            headerRow.appendChild(thHours);
                            headerRow.appendChild(thKPI);
                            thead.appendChild(headerRow);
                            table.appendChild(thead);
                            
                            // Тело таблицы
                            const tbody = document.createElement('tbody');
                            
                            // Фильтруем сотрудников только по указанной должности
                            const filteredEmployees = employeesData.employees.filter(employee => {
                                // Проверяем, содержит ли специальность сотрудника указанную должность
                                // или должность содержит специальность сотрудника
                                const employeePosition = employee.specialnost || '';
                                return employeePosition.toLowerCase().includes(position.toLowerCase()) || 
                                       position.toLowerCase().includes(employeePosition.toLowerCase());
                            });
                            
                            filteredEmployees.forEach(employee => {
                                const row = document.createElement('tr');
                                row.style.backgroundColor = 'rgba(255,255,255,0.1)';
                                row.dataset.employeeId = employee.id;
                                
                                const tdName = document.createElement('td');
                                tdName.textContent = employee.fio;
                                tdName.style.padding = '4px';
                                tdName.style.border = '1px solid #34495e';
                                
                                const tdOrg = document.createElement('td');
                                tdOrg.textContent = employee.organizaciya || '-';
                                tdOrg.style.padding = '4px';
                                tdOrg.style.border = '1px solid #34495e';
                                tdOrg.style.textAlign = 'center';
                                
                                const tdSpec = document.createElement('td');
                                tdSpec.textContent = employee.specialnost || '-';
                                tdSpec.style.padding = '4px';
                                tdSpec.style.border = '1px solid #34495e';
                                tdSpec.style.textAlign = 'center';
                                
                                const tdHours = document.createElement('td');
                                tdHours.textContent = '8';
                                tdHours.style.padding = '4px';
                                tdHours.style.border = '1px solid #34495e';
                                tdHours.style.textAlign = 'center';
                                tdHours.contentEditable = 'true';
                                tdHours.style.cursor = 'pointer';
                                tdHours.style.backgroundColor = 'rgba(255,255,255,0.05)';
                                
                                const tdKPI = document.createElement('td');
                                tdKPI.textContent = '1.0';
                                tdKPI.style.padding = '4px';
                                tdKPI.style.border = '1px solid #34495e';
                                tdKPI.style.textAlign = 'center';
                                tdKPI.contentEditable = 'true';
                                tdKPI.style.cursor = 'pointer';
                                tdKPI.style.backgroundColor = 'rgba(255,255,255,0.05)';
                                
                                row.appendChild(tdName);
                                row.appendChild(tdOrg);
                                row.appendChild(tdSpec);
                                row.appendChild(tdHours);
                                row.appendChild(tdKPI);
                                tbody.appendChild(row);
                            });
                            
                            table.appendChild(tbody);
                            content.insertBefore(table, closeBtn);
                            
                            // Добавляем информацию о количестве сотрудников
                            const info = document.createElement('p');
                            info.textContent = `Всего сотрудников: ${filteredEmployees.length}`;
                            info.style.marginTop = '10px';
                            info.style.textAlign = 'right';
                            info.style.color = '#bdc3c7';
                            content.insertBefore(info, closeBtn);
                            
                            // Добавляем кнопку "Сохранить в табель" после таблицы
                            content.insertBefore(saveBtn, closeBtn);
                        }
                    })
                    .catch(error => {
                        console.error('Error loading employees:', error);
                        // Показываем фиксированные данные в случае ошибки
                        showFixedEmployeesData(content, closeBtn, position, saveBtn);
                    });
            }
        })
        .catch(error => {
            console.error('Error loading salary data:', error);
            
            // Удаляем сообщение о загрузке
            content.removeChild(loading);
            
            // Пробуем получить данные через обычный API
            const cleanPosition = position.replace(/−/g, '-').trim();
            console.log(`Получение сотрудников через API (после ошибки): ${cleanPosition}`);
            fetch(`/objects/${objectId}/employees/?position=${encodeURIComponent(cleanPosition)}`)

                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Получены данные о сотрудниках:', data);
                    
                    if (data.success && data.employees && data.employees.length > 0) {
                        // Создаем таблицу сотрудников
                        const table = document.createElement('table');
                        table.style.width = '100%';
                        table.style.borderCollapse = 'collapse';
                        table.style.marginTop = '10px';
                        
                        // Заголовок таблицы
                        const thead = document.createElement('thead');
                        const headerRow = document.createElement('tr');
                        headerRow.style.backgroundColor = '#34495e';
                        
                        const thName = document.createElement('th');
                        thName.textContent = 'ФИО';
                        thName.style.padding = '4px';
                        thName.style.textAlign = 'left';
                        thName.style.border = '1px solid #2c3e50';
                        thName.style.width = '30%';
                        
                        const thOrg = document.createElement('th');
                        thOrg.textContent = 'Организация';
                        thOrg.style.padding = '4px';
                        thOrg.style.textAlign = 'center';
                        thOrg.style.border = '1px solid #2c3e50';
                        thOrg.style.width = '25%';
                        
                        const thSpec = document.createElement('th');
                        thSpec.textContent = 'Специальность';
                        thSpec.style.padding = '4px';
                        thSpec.style.textAlign = 'center';
                        thSpec.style.border = '1px solid #2c3e50';
                        thSpec.style.width = '25%';
                        
                        const thHours = document.createElement('th');
                        thHours.textContent = 'Отработал';
                        thHours.style.padding = '4px';
                        thHours.style.textAlign = 'center';
                        thHours.style.border = '1px solid #2c3e50';
                        thHours.style.width = '10%';
                        
                        const thKPI = document.createElement('th');
                        thKPI.textContent = 'KPI';
                        thKPI.style.padding = '4px';
                        thKPI.style.textAlign = 'center';
                        thKPI.style.border = '1px solid #2c3e50';
                        thKPI.style.width = '10%';
                        
                        headerRow.appendChild(thName);
                        headerRow.appendChild(thOrg);
                        headerRow.appendChild(thSpec);
                        headerRow.appendChild(thHours);
                        headerRow.appendChild(thKPI);
                        thead.appendChild(headerRow);
                        table.appendChild(thead);
                        
                        // Тело таблицы
                        const tbody = document.createElement('tbody');
                        
                        // Фильтруем сотрудников только по указанной должности
                        const filteredEmployees = data.employees.filter(employee => {
                            // Проверяем, содержит ли специальность сотрудника указанную должность
                            // или должность содержит специальность сотрудника
                            const employeePosition = employee.specialnost || '';
                            return employeePosition.toLowerCase().includes(position.toLowerCase()) || 
                                   position.toLowerCase().includes(employeePosition.toLowerCase());
                        });
                        
                        filteredEmployees.forEach(employee => {
                            const row = document.createElement('tr');
                            row.style.backgroundColor = 'rgba(255,255,255,0.1)';
                            row.dataset.employeeId = employee.id;
                            
                            const tdName = document.createElement('td');
                            tdName.textContent = employee.fio;
                            tdName.style.padding = '4px';
                            tdName.style.border = '1px solid #34495e';
                            
                            const tdOrg = document.createElement('td');
                            tdOrg.textContent = employee.organizaciya || '-';
                            tdOrg.style.padding = '4px';
                            tdOrg.style.border = '1px solid #34495e';
                            tdOrg.style.textAlign = 'center';
                            
                            const tdSpec = document.createElement('td');
                            tdSpec.textContent = employee.specialnost || '-';
                            tdSpec.style.padding = '4px';
                            tdSpec.style.border = '1px solid #34495e';
                            tdSpec.style.textAlign = 'center';
                            
                            const tdHours = document.createElement('td');
                            tdHours.textContent = '8';
                            tdHours.style.padding = '4px';
                            tdHours.style.border = '1px solid #34495e';
                            tdHours.style.textAlign = 'center';
                            tdHours.contentEditable = 'true';
                            tdHours.style.cursor = 'pointer';
                            tdHours.style.backgroundColor = 'rgba(255,255,255,0.05)';
                            
                            const tdKPI = document.createElement('td');
                            tdKPI.textContent = '1.0';
                            tdKPI.style.padding = '4px';
                            tdKPI.style.border = '1px solid #34495e';
                            tdKPI.style.textAlign = 'center';
                            tdKPI.contentEditable = 'true';
                            tdKPI.style.cursor = 'pointer';
                            tdKPI.style.backgroundColor = 'rgba(255,255,255,0.05)';
                            
                            row.appendChild(tdName);
                            row.appendChild(tdOrg);
                            row.appendChild(tdSpec);
                            row.appendChild(tdHours);
                            row.appendChild(tdKPI);
                            tbody.appendChild(row);
                        });
                        
                        table.appendChild(tbody);
                        content.insertBefore(table, closeBtn);
                        
                        // Добавляем информацию о количестве сотрудников
                        const info = document.createElement('p');
                        info.textContent = `Всего сотрудников: ${filteredEmployees.length}`;
                        info.style.marginTop = '10px';
                        info.style.textAlign = 'right';
                        info.style.color = '#bdc3c7';
                        content.insertBefore(info, closeBtn);
                        
                        // Добавляем кнопку "Сохранить в табель" после таблицы
                        content.insertBefore(saveBtn, closeBtn);
                    } else {
                        // Показываем фиксированные данные в случае ошибки
                        showFixedEmployeesData(content, closeBtn, position, saveBtn);
                    }
                })
                .catch(error => {
                    console.error('Error loading employees:', error);
                    // Показываем фиксированные данные в случае ошибки
                    showFixedEmployeesData(content, closeBtn, position, saveBtn);
                });
        });
}

// Функция для сохранения часов сотрудников в табель
function saveEmployeeHours(objectId, position, dateText, modal, cellTotalHours) {
    // Получаем все строки таблицы сотрудников
    const rows = modal.querySelectorAll('tbody tr');
    if (!rows || rows.length === 0) {
        return;
    }
    
    // Собираем данные о часах сотрудников
    const hoursData = [];
    let totalHours = 0;
    
    rows.forEach(row => {
        const employeeId = row.dataset.employeeId;
        const fio = row.cells[0].textContent;
        const specialnost = row.cells[2].textContent;
        const hours = parseFloat(row.cells[3].textContent) || 0;
        const kpi = parseFloat(row.cells[4].textContent) || 1.0;
        
        if (hours > 0) {
            hoursData.push({
                employee_id: employeeId,
                employee_fio: fio,
                position: specialnost,
                hours: hours,
                kpi: kpi
            });
            
            totalHours += hours;
        }
    });
    
    if (hoursData.length === 0) {
        return;
    }
    
    // Если есть значение общего количества часов в ячейке, используем его
    if (cellTotalHours && cellTotalHours > 0 && Math.abs(totalHours - cellTotalHours) > 0.01) {
        console.log(`Корректируем часы: в ячейке ${cellTotalHours}, в модальном окне ${totalHours}`);
        totalHours = cellTotalHours;
    }
    
    // Преобразуем дату в нужный формат
    let formattedDate = dateText;
    if (dateText.includes('.')) {
        const parts = dateText.split('.');
        if (parts.length === 2) {
            // Формат DD.MM
            const day = parts[0].padStart(2, '0');
            const month = parts[1].padStart(2, '0');
            const year = new Date().getFullYear();
            formattedDate = `${year}-${month}-${day}`;
        } else if (parts.length === 3) {
            // Формат DD.MM.YYYY
            const day = parts[0].padStart(2, '0');
            const month = parts[1].padStart(2, '0');
            const year = parts[2].length === 2 ? `20${parts[2]}` : parts[2];
            formattedDate = `${year}-${month}-${day}`;
        }
    }
    
    // Функция для получения CSRF токена
    function getCsrfToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Отправляем данные на сервер
    fetch('/telegram/save-hours/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            hours: hoursData,
            objekt_id: objectId,
            date: formattedDate,
            position: position,
            total_hours: totalHours  // Передаем общее количество часов
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Закрываем модальное окно
            document.body.removeChild(modal);
        }
    })
    .catch(error => {
        console.error('Error saving hours:', error);
    });
}