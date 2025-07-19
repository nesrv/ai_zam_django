// Простой скрипт для отображения сотрудников в ячейках категории "Кадровое обеспечение"

document.addEventListener('DOMContentLoaded', function() {
    // Находим все строки с категорией "Кадровое обеспечение"
    const rows = document.querySelectorAll('tr');
    
    // Ищем строку с заголовком категории "КАДРОВОЕ ОБЕСПЕЧЕНИЕ"
    for (let i = 0; i < rows.length; i++) {
        const headerCell = rows[i].querySelector('td');
        if (headerCell && headerCell.textContent && headerCell.textContent.trim().toUpperCase().includes('КАДРОВОЕ ОБЕСПЕЧЕНИЕ')) {
            console.log('Найдена категория "Кадровое обеспечение"');
            
            // Находим все строки ресурсов этой категории
            let currentRow = rows[i].nextElementSibling;
            
            while (currentRow && 
                   !currentRow.classList.contains('category-header') && 
                   !currentRow.classList.contains('total-row')) {
                
                // Получаем ячейки с датами (начиная с 8-й ячейки)
                const cells = currentRow.querySelectorAll('td');
                if (cells.length < 7) {
                    currentRow = currentRow.nextElementSibling;
                    continue;
                }
                
                // Добавляем кнопку в каждую ячейку с датой
                for (let j = 7; j < cells.length; j++) {
                    const cell = cells[j];
                    
                    // Добавляем кнопку
                    const btn = document.createElement('button');
                    btn.textContent = '👥';
                    btn.style.marginLeft = '5px';
                    btn.style.background = 'none';
                    btn.style.border = 'none';
                    btn.style.cursor = 'pointer';
                    btn.style.color = '#3498db';
                    btn.title = 'Показать сотрудников';
                    
                    cell.appendChild(btn);
                    
                    // Добавляем обработчик клика
                    btn.addEventListener('click', function(event) {
                        event.stopPropagation();
                        
                        // Получаем ID объекта из URL
                        const objectId = window.location.pathname.split('/')[2];
                        
                        // Создаем модальное окно
                        showEmployeesModal(objectId);
                    });
                }
                
                currentRow = currentRow.nextElementSibling;
            }
            
            break;
        }
    }
});

// Функция для отображения модального окна с сотрудниками
function showEmployeesModal(objectId) {
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
    content.style.width = '500px';
    content.style.color = 'white';
    
    // Заголовок
    const header = document.createElement('h3');
    header.textContent = 'Сотрудники';
    header.style.marginTop = '0';
    content.appendChild(header);
    
    // Загрузка данных
    const loading = document.createElement('p');
    loading.textContent = 'Загрузка данных...';
    content.appendChild(loading);
    
    // Кнопка закрытия
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Закрыть';
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
    
    content.appendChild(closeBtn);
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Загружаем данные о сотрудниках
    fetch(`/objects/${objectId}/employees/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Получены данные:', data);
            
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
                thName.style.padding = '8px';
                thName.style.textAlign = 'left';
                thName.style.border = '1px solid #2c3e50';
                
                const thOrg = document.createElement('th');
                thOrg.textContent = 'Организация';
                thOrg.style.padding = '8px';
                thOrg.style.textAlign = 'center';
                thOrg.style.border = '1px solid #2c3e50';
                
                headerRow.appendChild(thName);
                headerRow.appendChild(thOrg);
                thead.appendChild(headerRow);
                table.appendChild(thead);
                
                // Тело таблицы
                const tbody = document.createElement('tbody');
                
                data.employees.forEach(employee => {
                    const row = document.createElement('tr');
                    row.style.backgroundColor = 'rgba(255,255,255,0.1)';
                    
                    const tdName = document.createElement('td');
                    tdName.textContent = employee.fio;
                    tdName.style.padding = '8px';
                    tdName.style.border = '1px solid #34495e';
                    
                    const tdOrg = document.createElement('td');
                    tdOrg.textContent = employee.organizaciya || '-';
                    tdOrg.style.padding = '8px';
                    tdOrg.style.border = '1px solid #34495e';
                    tdOrg.style.textAlign = 'center';
                    
                    row.appendChild(tdName);
                    row.appendChild(tdOrg);
                    tbody.appendChild(row);
                });
                
                table.appendChild(tbody);
                content.insertBefore(table, closeBtn);
            } else {
                const noData = document.createElement('p');
                noData.textContent = 'Сотрудники не найдены';
                content.insertBefore(noData, closeBtn);
            }
        })
        .catch(error => {
            console.error('Error loading employees:', error);
            
            // Удаляем сообщение о загрузке
            content.removeChild(loading);
            
            const errorMsg = document.createElement('p');
            errorMsg.textContent = `Ошибка загрузки данных: ${error.message}`;
            errorMsg.style.color = '#e74c3c';
            content.insertBefore(errorMsg, closeBtn);
        });
    
    // Закрытие по клику вне модального окна
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
    });
}