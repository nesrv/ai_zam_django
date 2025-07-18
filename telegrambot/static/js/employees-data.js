// Функция для получения сотрудников по объекту
function getEmployeesByObject(objectId) {
    return fetch(`/telegram/get-employees/?object_id=${objectId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.employees;
            } else {
                console.error('Ошибка получения сотрудников:', data.error);
                return [];
            }
        })
        .catch(error => {
            console.error('Ошибка запроса:', error);
            return [];
        });
}

// Обновляем функцию открытия модального окна для получения сотрудников
function updateModalWithEmployees(objectId, messageText) {
    const modal = document.getElementById('hoursModal');
    if (!modal) return;
    
    // Добавляем текст сообщения
    const messageElement = document.createElement('div');
    messageElement.className = 'message-preview';
    messageElement.style.padding = '12px';
    messageElement.style.marginBottom = '15px';
    messageElement.style.backgroundColor = '#e3f2fd';
    messageElement.style.border = '1px solid #90caf9';
    messageElement.style.borderRadius = '5px';
    messageElement.style.fontSize = '1rem';
    messageElement.style.fontWeight = '500';
    messageElement.style.color = '#0d47a1';
    messageElement.textContent = messageText || 'Сообщение не выбрано';
    
    // Находим тело модального окна
    const modalBody = modal.querySelector('.modal-body');
    
    // Удаляем предыдущий превью сообщения, если он есть
    const oldPreview = modalBody.querySelector('.message-preview');
    if (oldPreview) {
        oldPreview.remove();
    }
    
    // Удаляем предыдущий список сотрудников, если он есть
    const oldEmployeesList = modalBody.querySelector('.employees-list');
    if (oldEmployeesList) {
        oldEmployeesList.remove();
    }
    
    // Добавляем новый превью сообщения в начало тела модального окна
    modalBody.insertBefore(messageElement, modalBody.firstChild);
    
    // Создаем элемент для списка сотрудников
    const employeesList = document.createElement('div');
    employeesList.className = 'employees-list';
    employeesList.style.padding = '12px';
    employeesList.style.marginBottom = '15px';
    employeesList.style.backgroundColor = '#f5f5f5';
    employeesList.style.border = '1px solid #ddd';
    employeesList.style.borderRadius = '5px';
    employeesList.style.fontSize = '0.9rem';
    employeesList.style.color = '#333';
    
    // Заголовок списка сотрудников
    const employeesTitle = document.createElement('h4');
    employeesTitle.style.marginTop = '0';
    employeesTitle.style.marginBottom = '10px';
    employeesTitle.style.color = '#333';
    employeesTitle.textContent = 'Сотрудники по объекту:';
    employeesList.appendChild(employeesTitle);
    
    // Добавляем индикатор загрузки
    const loadingIndicator = document.createElement('div');
    loadingIndicator.textContent = 'Загрузка данных...';
    loadingIndicator.style.fontStyle = 'italic';
    loadingIndicator.style.color = '#666';
    employeesList.appendChild(loadingIndicator);
    
    // Добавляем список сотрудников после текста сообщения
    modalBody.insertBefore(employeesList, modalBody.querySelector('table'));
    
    // Показываем модальное окно
    modal.style.display = 'block';
    
    // Получаем данные о сотрудниках
    getEmployeesByObject(objectId)
        .then(employees => {
            // Удаляем индикатор загрузки
            loadingIndicator.remove();
            
            if (employees && employees.length > 0) {
                // Создаем пре-форматированный блок с JSON
                const preElement = document.createElement('pre');
                preElement.style.backgroundColor = '#f8f9fa';
                preElement.style.padding = '10px';
                preElement.style.borderRadius = '4px';
                preElement.style.border = '1px solid #e9ecef';
                preElement.style.fontSize = '0.85rem';
                preElement.style.overflow = 'auto';
                preElement.style.maxHeight = '150px';
                preElement.style.color = '#212529';
                preElement.textContent = JSON.stringify(employees, null, 2);
                employeesList.appendChild(preElement);
            } else {
                // Если сотрудников нет, показываем сообщение
                const noEmployeesMessage = document.createElement('div');
                noEmployeesMessage.textContent = 'Сотрудники не найдены';
                noEmployeesMessage.style.fontStyle = 'italic';
                noEmployeesMessage.style.color = '#666';
                employeesList.appendChild(noEmployeesMessage);
            }
        });
}