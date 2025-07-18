// Функция для сравнения фамилий с учетом возможных ошибок
function isSimilarSurname(surname1, surname2) {
    // Приводим к нижнему регистру и удаляем лишние символы
    const clean1 = surname1.toLowerCase().replace(/[^\u0430-\u044f\u0451]/g, '');
    const clean2 = surname2.toLowerCase().replace(/[^\u0430-\u044f\u0451]/g, '');
    
    // Точное совпадение
    if (clean1 === clean2) return true;
    
    // Если одна фамилия содержит другую и длиннее не более чем на 3 символа
    if (clean1.includes(clean2) && clean1.length - clean2.length <= 3) return true;
    if (clean2.includes(clean1) && clean2.length - clean1.length <= 3) return true;
    
    // Расстояние Левенштейна для коротких фамилий
    if (clean1.length <= 5 && clean2.length <= 5) {
        // Для коротких фамилий допускаем только 1 ошибку
        return levenshteinDistance(clean1, clean2) <= 1;
    }
    
    // Для более длинных фамилий допускаем до 2 ошибок
    return levenshteinDistance(clean1, clean2) <= 2;
}

// Расстояние Левенштейна для определения схожести строк
function levenshteinDistance(a, b) {
    if (a.length === 0) return b.length;
    if (b.length === 0) return a.length;

    const matrix = [];

    for (let i = 0; i <= b.length; i++) {
        matrix[i] = [i];
    }

    for (let j = 0; j <= a.length; j++) {
        matrix[0][j] = j;
    }

    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            const cost = a[j - 1] === b[i - 1] ? 0 : 1;
            matrix[i][j] = Math.min(
                matrix[i - 1][j] + 1,      // удаление
                matrix[i][j - 1] + 1,      // вставка
                matrix[i - 1][j - 1] + cost // замена
            );
        }
    }

    return matrix[b.length][a.length];
}

// Функция для извлечения фамилий и часов из текста сообщения
function extractEmployeesAndHours(messageText) {
    const result = [];
    
    // Разбиваем текст на строки
    const lines = messageText.split('\n');
    
    // Ищем строки с упоминанием ФИО или фамилий
    for (const line of lines) {
        // Проверяем разные форматы записи ФИО
        
        // Формат: Фамилия И.О. - X часов
        let match = line.match(/([\u0410-\u042f][\u0430-\u044f\u0451]+)\s+[\u0410-\u042f]\.[\u0410-\u042f]\.(\s*[-:]\s*(\d+)\s*(?:ч|час|часов|часа))?/i);
        if (match) {
            result.push({
                surname: match[1],
                hours: match[3] ? parseInt(match[3]) : 8 // По умолчанию 8 часов
            });
            continue;
        }
        
        // Формат: Фамилия Имя Отчество - X часов
        match = line.match(/([\u0410-\u042f][\u0430-\u044f\u0451]+)(?:\s+[\u0410-\u042f][\u0430-\u044f\u0451]+){1,2}(\s*[-:]\s*(\d+)\s*(?:ч|час|часов|часа))?/i);
        if (match) {
            result.push({
                surname: match[1],
                hours: match[3] ? parseInt(match[3]) : 8
            });
            continue;
        }
        
        // Формат: ФИО: Фамилия Имя Отчество, часы: X
        match = line.match(/фио:?\s*([\u0410-\u042f][\u0430-\u044f\u0451]+(?:\s+[\u0410-\u042f][\u0430-\u044f\u0451]+){0,2}).*?час(?:ы|ов)?:?\s*(\d+)/i);
        if (match) {
            const fullName = match[1].trim();
            const surname = fullName.split(' ')[0]; // Берем первое слово как фамилию
            result.push({
                surname: surname,
                hours: parseInt(match[2])
            });
            continue;
        }
        
        // Просто фамилия с часами
        match = line.match(/([\u0410-\u042f][\u0430-\u044f\u0451]+)\s*[-:]\s*(\d+)\s*(?:ч|час|часов|часа)/i);
        if (match) {
            result.push({
                surname: match[1],
                hours: parseInt(match[2])
            });
        }
    }
    
    return result;
}

// Функция для открытия модального окна добавления часов в табель
function openHoursModal(messageText, messageDate) {
    const modal = document.getElementById('hoursModal');
    if (modal) {
        // Извлекаем дату из текста сообщения или используем переданную дату или текущую дату
        let dateText = messageDate || new Date().toLocaleDateString('ru-RU');
        
        // Проверяем, есть ли в тексте сообщения упоминание даты
        if (messageText) {
            // Проверяем наличие даты в формате "Дата: XX.XX.XXXX" или "Дата: XX.XX"
            const dateMatch = messageText.match(/\bдата:?\s*(\d{1,2}[.\/-]\d{1,2}(?:[.\/-]\d{2,4})?)/i);
            if (dateMatch && dateMatch[1]) {
                dateText = dateMatch[1];
            }
        }
        
        // Обновляем заголовок модального окна с датой
        const dateElement = modal.querySelector('#message-date');
        if (dateElement) {
            dateElement.textContent = dateText;
        }
        
        // Добавляем текст сообщения в модальное окно
        const messagePreview = document.createElement('div');
        messagePreview.className = 'message-preview';
        messagePreview.style.padding = '10px';
        messagePreview.style.marginBottom = '15px';
        messagePreview.style.backgroundColor = '#f0f8ff';
        messagePreview.style.borderLeft = '3px solid #007AFF';
        messagePreview.style.borderRadius = '5px';
        messagePreview.innerHTML = `<strong>Текст сообщения:</strong><br>${messageText || 'Сообщение не содержит текста'}`;
        
        // Находим тело модального окна
        const modalBody = modal.querySelector('.modal-body');
        
        // Удаляем предыдущий превью, если он есть
        const existingPreview = modalBody.querySelector('.message-preview');
        if (existingPreview) {
            existingPreview.remove();
        }
        
        // Добавляем превью в начало модального окна
        modalBody.insertBefore(messagePreview, modalBody.firstChild);
        
        // Извлекаем сотрудников из JSON в блоке employees-list
        let employeesData = [];
        const employeesList = document.querySelector('.employees-list pre');
        if (employeesList) {
            try {
                employeesData = JSON.parse(employeesList.textContent);
            } catch (e) {
                console.error('Ошибка парсинга JSON:', e);
            }
        }
        
        // Извлекаем фамилии и часы из текста сообщения
        const extractedEmployees = extractEmployeesAndHours(messageText);
        
        // Очищаем таблицу часов
        const hoursTable = modal.querySelector('.hours-table tbody');
        if (hoursTable) {
            hoursTable.innerHTML = '';
            
            // Заполняем таблицу совпадающими сотрудниками
            let matchFound = false;
            
            // Сначала проверяем совпадения из извлеченных данных
            for (const extracted of extractedEmployees) {
                for (const employee of employeesData) {
                    // Извлекаем фамилию из полного ФИО
                    const employeeSurname = employee.fio.split(' ')[0];
                    
                    // Проверяем схожесть фамилий
                    if (isSimilarSurname(extracted.surname, employeeSurname)) {
                        // Создаем строку в таблице
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><input type="text" value="${employee.specialnost}"></td>
                            <td><input type="text" value="${employee.fio}"></td>
                            <td><input type="number" value="${extracted.hours}" min="1" max="24"></td>
                            <td><input type="text" value="Строительство ЖК"></td>
                        `;
                        hoursTable.appendChild(row);
                        matchFound = true;
                    }
                }
            }
            
            // Если не нашли совпадений, добавляем хотя бы одну строку
            if (!matchFound) {
                // Если есть извлеченные данные, используем их
                if (extractedEmployees.length > 0) {
                    const extracted = extractedEmployees[0];
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="text" value="Прораб"></td>
                        <td><input type="text" value="${extracted.surname}"></td>
                        <td><input type="number" value="${extracted.hours}" min="1" max="24"></td>
                        <td><input type="text" value="Строительство ЖК"></td>
                    `;
                    hoursTable.appendChild(row);
                } else {
                    // Иначе добавляем пустую строку
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="text" value="Прораб"></td>
                        <td><input type="text" value="Иванов И.И."></td>
                        <td><input type="number" value="8" min="1" max="24"></td>
                        <td><input type="text" value="Строительство ЖК"></td>
                    `;
                    hoursTable.appendChild(row);
                }
            }
        }
        
        // Показываем модальное окно
        modal.style.display = 'block';
    }
}

// Функция для закрытия модального окна
function closeHoursModal() {
    const modal = document.getElementById('hoursModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Функция для сохранения часов в табель
function saveHours() {
    // Здесь можно добавить логику сохранения данных в базу
    alert('Часы успешно добавлены в табель');
    closeHoursModal();
}

// Добавляем обработчики событий после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем обработчики клика для сообщений пользователя
    document.querySelectorAll('.user-message').forEach(message => {
        message.addEventListener('click', function() {
            // Получаем текст сообщения
            const messageText = this.querySelector('.message-text').innerText;
            // Получаем дату из метаданных сообщения
            const messageMeta = this.querySelector('.message-meta');
            let messageDate = new Date().toLocaleDateString('ru-RU'); // По умолчанию текущая дата
            
            if (messageMeta) {
                const metaText = messageMeta.innerText;
                // Пробуем извлечь дату из метаданных (формат: "Имя • Дата")
                const datePart = metaText.split('•')[1];
                if (datePart) {
                    messageDate = datePart.trim();
                }
            }
            
            openHoursModal(messageText, messageDate);
        });
    });
    
    // Закрытие модального окна при клике вне его
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('hoursModal');
        if (event.target === modal) {
            closeHoursModal();
        }
    });
    
    // Добавляем обработчик для динамически созданных сообщений
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.classList.contains('user-message')) {
                        node.addEventListener('click', function() {
                            const messageText = node.querySelector('.message-text').innerText;
                            
                            // Получаем дату из метаданных сообщения
                            const messageMeta = node.querySelector('.message-meta');
                            let messageDate = new Date().toLocaleDateString('ru-RU'); // По умолчанию текущая дата
                            
                            if (messageMeta) {
                                const metaText = messageMeta.innerText;
                                // Пробуем извлечь дату из метаданных (формат: "Имя • Дата")
                                const datePart = metaText.split('•')[1];
                                if (datePart) {
                                    messageDate = datePart.trim();
                                }
                            }
                            
                            openHoursModal(messageText, messageDate);
                        });
                    }
                });
            }
        });
    });
    
    // Наблюдаем за всеми контейнерами сообщений
    document.querySelectorAll('.messages-container').forEach(container => {
        observer.observe(container, { childList: true, subtree: true });
    });
});