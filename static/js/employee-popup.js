// employee-popup.js - Обработчик для ячеек категории "Кадровое обеспечение"

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeEmployeeIcons, 500); // Даем время на загрузку страницы
});

function initializeEmployeeIcons() {
    console.log('Инициализация иконок сотрудников...');
    
    // Находим все строки с категорией "Кадровое обеспечение"
    const rows = document.querySelectorAll('tr');
    let kadryRow = null;
    
    // Ищем строку с заголовком категории "КАДРОВОЕ ОБЕСПЕЧЕНИЕ"
    for (let i = 0; i < rows.length; i++) {
        const headerCell = rows[i].querySelector('td');
        if (headerCell && headerCell.textContent && headerCell.textContent.trim().toUpperCase().includes('КАДРОВОЕ ОБЕСПЕЧЕНИЕ')) {
            kadryRow = rows[i];
            console.log('Найдена строка с категорией "Кадровое обеспечение":', headerCell.textContent);
            break;
        }
    }
    
    // Если нашли строку с категорией "Кадровое обеспечение"
    if (kadryRow) {
        console.log('Найдена категория "Кадровое обеспечение"');
        // Находим все строки ресурсов этой категории до следующего заголовка категории или итоговой строки
        let currentRow = kadryRow.nextElementSibling;
        
        while (currentRow && 
               !currentRow.classList.contains('category-header') && 
               !currentRow.classList.contains('total-row')) {
            
            // Получаем ячейки с датами (начиная с 8-й ячейки)
            const cells = currentRow.querySelectorAll('td');
            if (cells.length < 7) {
                currentRow = currentRow.nextElementSibling;
                continue;
            }
            
            const resourceName = cells[0].textContent.trim(); // Наименование должности
            console.log('Найдена должность:', resourceName);
            
            // Добавляем обработчик для ячеек с датами
            for (let i = 7; i < cells.length; i++) {
                const cell = cells[i];
                
                // Проверяем, что ячейка еще не обработана
                if (cell.querySelector('.employee-icon')) {
                    continue;
                }
                
                // Добавляем иконку сотрудников
                const employeeIcon = document.createElement('span');
                employeeIcon.className = 'employee-icon';
                employeeIcon.innerHTML = '👥';
                employeeIcon.title = 'Показать сотрудников';
                
                // Добавляем иконку в ячейку
                cell.appendChild(employeeIcon);
                cell.classList.add('kadry-cell');
                
                // Добавляем обработчик клика на иконку
                employeeIcon.addEventListener('click', function(event) {
                    event.stopPropagation(); // Предотвращаем всплытие события
                    
                    // Получаем данные о ресурсе и дате
                    const dateCell = document.querySelectorAll('th')[i];
                    const dateText = dateCell ? dateCell.textContent.trim() : 'Неизвестная дата';
                    
                    // Получаем ID объекта из URL
                    const objectId = window.location.pathname.split('/')[2];
                    
                    // Открываем модальное окно с сотрудниками
                    showEmployeesModal(objectId, resourceName, dateText);
                });
            }
            
            currentRow = currentRow.nextElementSibling;
        }
    } else {
        console.log('Категория "Кадровое обеспечение" не найдена');
    }
}

// Функция для отображения модального окна с сотрудниками
function showEmployeesModal(objectId, position, dateText) {
    console.log(`Показываем модальное окно для объекта ${objectId}, должность: ${position}, дата: ${dateText}`);
    
    // Создаем модальное окно, если его еще нет
    let modal = document.getElementById('employeesModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'employeesModal';
        modal.style.display = 'none';
        modal.style.position = 'fixed';
        modal.style.zIndex = '1000';
        modal.style.left = '0';
        modal.style.top = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
        
        const modalContent = document.createElement('div');
        modalContent.style.backgroundColor = '#2c3e50';
        modalContent.style.margin = '10% auto';
        modalContent.style.padding = '20px';
        modalContent.style.borderRadius = '8px';
        modalContent.style.width = '600px';
        modalContent.style.color = 'white';
        modalContent.style.position = 'relative';
        
        // Добавляем кнопку закрытия в правом верхнем углу
        const closeX = document.createElement('span');
        closeX.innerHTML = '&times;';
        closeX.style.position = 'absolute';
        closeX.style.top = '10px';
        closeX.style.right = '15px';
        closeX.style.fontSize = '24px';
        closeX.style.fontWeight = 'bold';
        closeX.style.cursor = 'pointer';
        closeX.style.color = '#aaa';
        closeX.onclick = function() {
            modal.style.display = 'none';
        };
        closeX.onmouseover = function() {
            closeX.style.color = '#fff';
        };
        closeX.onmouseout = function() {
            closeX.style.color = '#aaa';
        };
        modalContent.appendChild(closeX);
        
        const modalHeader = document.createElement('div');
        modalHeader.id = 'employeesModalHeader';
        modalHeader.style.marginBottom = '20px';
        modalHeader.style.borderBottom = '1px solid #34495e';
        modalHeader.style.paddingBottom = '10px';
        
        const modalBody = document.createElement('div');
        modalBody.id = 'employeesModalBody';
        modalBody.style.maxHeight = '400px';
        modalBody.style.overflowY = 'auto';
        
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Закрыть';
        closeButton.style.background = '#e74c3c';
        closeButton.style.color = 'white';
        closeButton.style.padding = '8px 16px';
        closeButton.style.border = 'none';
        closeButton.style.borderRadius = '4px';
        closeButton.style.cursor = 'pointer';
        closeButton.style.float = 'right';
        closeButton.style.marginTop = '20px';
        closeButton.onclick = function() {
            modal.style.display = 'none';
        };
        
        modalContent.appendChild(modalHeader);
        modalContent.appendChild(modalBody);
        modalContent.appendChild(closeButton);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // Закрытие модального окна при клике вне его
        modal.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    }
    
    // Обновляем заголовок модального окна
    const modalHeader = document.getElementById('employeesModalHeader');
    modalHeader.innerHTML = `
        <h3 style="margin-top: 0; color: #3498db;">Сотрудники: ${position}</h3>
        <p style="margin-bottom: 5px; color: #bdc3c7;">Дата: ${dateText}</p>
    `;
    
    // Загружаем список сотрудников
    const modalBody = document.getElementById('employeesModalBody');
    modalBody.innerHTML = `
        <div style="text-align: center; padding: 20px;">
            <div style="display: inline-block; width: 30px; height: 30px; border: 3px solid #3498db; border-radius: 50%; border-top-color: transparent; animation: spin 1s linear infinite;"></div>
            <p style="margin-top: 10px;">Загрузка данных...</p>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    
    // Запрашиваем данные о сотрудниках с сервера
    console.log(`Запрос сотрудников: /objects/${objectId}/employees/?position=${encodeURIComponent(position)}`)
    fetch(`/objects/${objectId}/employees/?position=${encodeURIComponent(position)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(response => {
            console.log('API ответ:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Получены данные:', data);
            if (data.success && data.employees && data.employees.length > 0) {
                // Создаем таблицу сотрудников
                let tableHtml = `
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr style="background-color: #34495e;">
                                <th style="padding: 8px; text-align: left; border: 1px solid #2c3e50;">ФИО</th>
                                <th style="padding: 8px; text-align: center; border: 1px solid #2c3e50;">Организация</th>
                                <th style="padding: 8px; text-align: center; border: 1px solid #2c3e50;">Подразделение</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                data.employees.forEach(employee => {
                    tableHtml += `
                        <tr style="background-color: rgba(255,255,255,0.1);">
                            <td style="padding: 8px; border: 1px solid #34495e;">${employee.fio}</td>
                            <td style="padding: 8px; border: 1px solid #34495e; text-align: center;">${employee.organizaciya || '-'}</td>
                            <td style="padding: 8px; border: 1px solid #34495e; text-align: center;">${employee.podrazdelenie || '-'}</td>
                        </tr>
                    `;
                });
                
                tableHtml += `
                        </tbody>
                    </table>
                    <div style="margin-top: 10px; text-align: right; color: #bdc3c7;">
                        Всего сотрудников: ${data.employees.length}
                    </div>
                `;
                
                modalBody.innerHTML = tableHtml;
            } else {
                modalBody.innerHTML = `
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 48px; color: #95a5a6; margin-bottom: 10px;">👤</div>
                        <p>Сотрудники не найдены</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading employees:', error);
            modalBody.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <div style="font-size: 48px; color: #e74c3c; margin-bottom: 10px;">⚠️</div>
                    <p>Ошибка загрузки данных</p>
                    <p style="color: #95a5a6; font-size: 12px;">${error.message}</p>
                </div>
            `;
        });
    
    // Отображаем модальное окно
    modal.style.display = 'block';
}

// Добавляем стили для ячеек кадрового обеспечения
const style = document.createElement('style');
style.textContent = `
    .kadry-cell {
        position: relative;
    }
    
    .employee-icon {
        display: inline-block;
        margin-left: 5px;
        cursor: pointer;
        color: #3498db;
        font-size: 14px;
        background-color: rgba(52, 152, 219, 0.1);
        border-radius: 50%;
        padding: 2px;
        width: 18px;
        height: 18px;
        text-align: center;
        line-height: 18px;
        float: right;
    }
    
    .employee-icon:hover {
        color: #2980b9;
        transform: scale(1.2);
        background-color: rgba(52, 152, 219, 0.2);
    }
`;
document.head.appendChild(style);