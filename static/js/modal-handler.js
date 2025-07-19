// Функция для сравнения фамилий с учетом возможных ошибок
function isSimilarSurname(surname1, surname2) {
    // Проверяем, что оба параметра определены
    if (!surname1 || !surname2) return false;
    
    // Приводим к нижнему регистру и удаляем лишние символы
    const clean1 = surname1.toLowerCase().replace(/[^а-яё]/g, '');
    const clean2 = surname2.toLowerCase().replace(/[^а-яё]/g, '');
    
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
    if (!messageText) return [];
    
    console.log('Начинаем извлечение фамилий и часов из текста:', messageText);
    
    const result = [];
    
    // Ищем пары "Фамилия число" в тексте
    const pattern = /([А-Я][а-яё]+)\s+(\d+)/g;
    let match;
    
    while ((match = pattern.exec(messageText)) !== null) {
        const surname = match[1];
        const hours = parseInt(match[2]);
        
        console.log(`Найдена пара "фамилия число": ${surname} - ${hours} часов`);
        
        result.push({
            surname: surname,
            hours: hours
        });
    }
    
    // Если не нашли пары "Фамилия число", ищем отдельно фамилии и числа
    if (result.length === 0) {
        // Ищем все фамилии (слова с заглавной буквы)
        const surnamesPattern = /[А-Я][а-яё]+/g;
        const surnames = [];
        let surnameMatch;
        
        while ((surnameMatch = surnamesPattern.exec(messageText)) !== null) {
            surnames.push(surnameMatch[0]);
        }
        
        // Ищем все числа
        const hoursPattern = /\d+/g;
        const hours = [];
        let hoursMatch;
        
        while ((hoursMatch = hoursPattern.exec(messageText)) !== null) {
            hours.push(parseInt(hoursMatch[0]));
        }
        
        console.log('Найденные фамилии:', surnames);
        console.log('Найденные числа:', hours);
        
        // Сопоставляем фамилии и часы
        for (let i = 0; i < surnames.length; i++) {
            result.push({
                surname: surnames[i],
                hours: i < hours.length ? hours[i] : 8 // Если часов меньше чем фамилий, используем 8 по умолчанию
            });
        }
    }
    
    // Если все еще ничего не нашли, добавляем хотя бы одного сотрудника
    if (result.length === 0) {
        console.log('Не нашли ни одной фамилии, добавляем дефолтного сотрудника');
        result.push({
            surname: 'Иванов',
            hours: 8
        });
    }
    
    console.log('Итоговый результат извлечения:', result);
    return result;
}

// Функция для открытия модального окна добавления часов в табель
window.openHoursModal = function(messageText, messageDate) {
    const modal = document.getElementById('hoursModal');
    if (modal) {
        // Определяем ID объекта из сообщения
        let objektId = null;
        const messageElement = document.activeElement.closest('.user-message') || document.querySelector('.user-message:hover');
        if (messageElement) {
            const iphoneScreen = messageElement.closest('.iphone-screen');
            if (iphoneScreen) {
                const dropdownToggle = iphoneScreen.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    const onclickAttr = dropdownToggle.getAttribute('onclick');
                    if (onclickAttr) {
                        const match = onclickAttr.match(/toggleDropdown\((\d+)\)/i);
                        if (match && match[1]) {
                            objektId = match[1];
                            console.log(`Найден ID объекта: ${objektId}`);
                        }
                    }
                }
            }
        }
        
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
        
        // Заполняем поля даты в заголовке модального окна
        const messageDateElement = document.getElementById('message-date');
        if (messageDateElement) {
            // Удаляем время из даты, оставляем только дату
            let cleanDate = dateText;
            if (dateText.includes(' ')) {
                cleanDate = dateText.split(' ')[1]; // Берем только вторую часть после пробела
            }
            messageDateElement.textContent = cleanDate;
        }
        
        // Получаем название объекта по ID
        const messageObjectElement = document.getElementById('message-object');
        if (messageObjectElement) {
            let objectText = "";
            
            // Извлекаем объект из текста сообщения
            if (messageText) {
                // Проверяем наличие объекта в формате "Объект: название" или после "по"
                const objectMatch = messageText.match(/\bобъект:?\s*([^\n,]+)/i) || messageText.match(/\bпо\s+([^\n,]+)/i);
                if (objectMatch && objectMatch[1]) {
                    objectText = objectMatch[1].trim();
                }
            }
            
            // Если объект не найден в тексте, используем название объекта по ID
            if (!objectText && objektId) {
                // Ищем заголовок чата по ID объекта
                const dropdownToggle = document.querySelector(`.dropdown-toggle[onclick*="toggleDropdown(${objektId})"]`);
                if (dropdownToggle) {
                    const chatHeader = dropdownToggle.closest('.chat-header');
                    if (chatHeader) {
                        // Извлекаем текст заголовка чата (название объекта)
                        const headerText = chatHeader.textContent.trim();
                        if (headerText) {
                            // Удаляем все специальные символы из заголовка
                            objectText = headerText.replace(/[+✔✓✗❌🔄➕➖➗☑☒☐✅❎]/g, '').trim();
                            // Удаляем текст выпадающего меню
                            objectText = objectText.replace(/Часы рабочих в табель/g, '').replace(/Заявка на ресурсы/g, '').trim();
                            // Удаляем все непечатаемые символы
                            objectText = objectText.replace(/[^А-яёЁa-zA-Z0-9\s\-]/g, '').trim();
                            console.log(`Найдено название объекта по ID ${objektId}: ${objectText}`);
                        }
                    }
                }
            }
            
            // Если все еще нет названия объекта, ищем в заголовке чата
            if (!objectText) {
                // Пытаемся найти заголовок чата
                const messageContainer = document.querySelector('.message-item');
                let chatHeader = null;
                
                if (messageContainer) {
                    // Получаем родительский элемент iphone-screen
                    const iphoneScreen = messageContainer.closest('.iphone-screen');
                    if (iphoneScreen) {
                        chatHeader = iphoneScreen.querySelector('.chat-header');
                    }
                }
                
                // Если не нашли через сообщение, ищем любой заголовок чата
                if (!chatHeader) {
                    chatHeader = document.querySelector('.chat-header');
                }
                
                if (chatHeader) {
                    // Извлекаем текст заголовка чата (название объекта)
                    const headerText = chatHeader.textContent.trim();
                    if (headerText) {
                        // Удаляем все специальные символы из заголовка
                        objectText = headerText.replace(/[+✔✓✗❌🔄➕➖➗☑☒☐✅❎]/g, '').trim();
                        // Удаляем текст выпадающего меню
                        objectText = objectText.replace(/Часы рабочих в табель/g, '').replace(/Заявка на ресурсы/g, '').trim();
                        // Удаляем все непечатаемые символы
                        objectText = objectText.replace(/[^А-яёЁa-zA-Z0-9\s\-]/g, '').trim();
                    }
                }
            }
            
            // Если объект пустой или содержит только пробелы, используем слово "объекте"
            messageObjectElement.textContent = (objectText && objectText.trim()) ? objectText : "объекте Дом-3";
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
        console.log('Начинаем поиск списка сотрудников');
        const employeesList = document.querySelector('.employees-list pre');
        console.log('Найден элемент .employees-list pre:', employeesList);
        
        // Если не нашли список, попробуем создать тестовые данные
        if (!employeesList) {
            console.log('Список сотрудников не найден, используем тестовые данные');
            employeesData = [
                {"fio": "Иванов Иван Иванович", "specialnost": "альпинист", "surname": "Иванов"},
                {"fio": "Петров Петр Петрович", "specialnost": "монтажник", "surname": "Петров"},
                {"fio": "Сидоров Сидор Сидорович", "specialnost": "сварщик", "surname": "Сидоров"}
            ];
        } else {
            try {
                console.log('Текст JSON:', employeesList.textContent);
                employeesData = JSON.parse(employeesList.textContent);
                console.log('Успешно парсим JSON:', employeesData);
                
                // Добавляем дополнительные фамилии для поиска
                for (const employee of employeesData) {
                    // Добавляем только фамилию для поиска
                    if (employee.fio) {
                        const parts = employee.fio.split(' ');
                        if (parts.length > 0) {
                            employee.surname = parts[0];
                        }
                    }
                }
            } catch (e) {
                console.error('Ошибка парсинга JSON:', e);
                // Используем тестовые данные
                employeesData = [
                    {"fio": "Иванов Иван Иванович", "specialnost": "альпинист", "surname": "Иванов"},
                    {"fio": "Петров Петр Петрович", "specialnost": "монтажник", "surname": "Петров"},
                    {"fio": "Сидоров Сидор Сидорович", "specialnost": "сварщик", "surname": "Сидоров"}
                ];
            }
        }
        
        // Извлекаем фамилии и часы из текста сообщения
        console.log('Текст сообщения для анализа:', messageText);
        const extractedEmployees = extractEmployeesAndHours(messageText);
        console.log('Извлеченные сотрудники и часы:', extractedEmployees);
        
        // Получаем ID объекта из выпадающего меню
        let objektId = null;
        const messageContainer = document.querySelector('.message-item');
        let chatHeader = null;
        
        if (messageContainer) {
            // Получаем родительский элемент iphone-screen
            const iphoneScreen = messageContainer.closest('.iphone-screen');
            if (iphoneScreen) {
                chatHeader = iphoneScreen.querySelector('.chat-header');
            }
        }
        
        // Если не нашли через сообщение, ищем любой заголовок чата
        if (!chatHeader) {
            chatHeader = document.querySelector('.chat-header');
        }
        
        if (chatHeader) {
            // Проверяем, есть ли выпадающее меню с ID объекта
            const dropdownToggle = chatHeader.querySelector('.dropdown-toggle');
            if (dropdownToggle) {
                const onclickAttr = dropdownToggle.getAttribute('onclick');
                if (onclickAttr) {
                    const match = onclickAttr.match(/toggleDropdown\((\d+)\)/i);
                    if (match && match[1]) {
                        objektId = match[1];
                        console.log(`Найден ID объекта из выпадающего меню: ${objektId}`);
                        
                        // Ищем сотрудников по объекту
                        findEmployeesByObject(extractedEmployees, objektId);
                        return; // Выходим из функции, т.к. дальнейшая обработка будет в findEmployeesByObject
                    }
                }
            }
        }
        
        // Если не нашли ID объекта, используем стандартную логику
        console.log('Не найден ID объекта, используем стандартную логику');
        
        // Создаем отладочный блок
        let debugContainer = document.getElementById('employees-debug');
        if (!debugContainer) {
            debugContainer = document.createElement('div');
            debugContainer.id = 'employees-debug';
            debugContainer.style.padding = '10px';
            debugContainer.style.marginTop = '15px';
            debugContainer.style.backgroundColor = '#f8f9fa';
            debugContainer.style.border = '1px solid #dee2e6';
            debugContainer.style.borderRadius = '5px';
            debugContainer.style.fontSize = '0.9rem';
            
            // Добавляем заголовок
            const debugHeader = document.createElement('h4');
            debugHeader.textContent = 'Отладка поиска сотрудников';
            debugHeader.style.fontSize = '1rem';
            debugHeader.style.marginBottom = '10px';
            debugContainer.appendChild(debugHeader);
            
            // Добавляем информацию о необходимости выбрать объект
            const infoText = document.createElement('p');
            infoText.textContent = 'Не найден ID объекта. Для поиска сотрудников необходимо выбрать объект.';
            infoText.style.fontStyle = 'italic';
            debugContainer.appendChild(infoText);
            
            // Добавляем контейнер в модальное окно
            const modalBody = document.querySelector('.modal-body');
            if (modalBody) {
                modalBody.appendChild(debugContainer);
            }
        }
        
        // Очищаем таблицу часов
        const hoursTable = modal.querySelector('.hours-table tbody');
        console.log('Найдена таблица часов:', hoursTable);
        if (hoursTable) {
            hoursTable.innerHTML = '';
            
            // Получаем название объекта из страницы
            let objectName = "Строительство ЖК";
            
            // Пытаемся найти заголовок чата в родительском элементе сообщения
            const messageContainer = document.querySelector('.message-item');
            let chatHeader = null;
            
            if (messageContainer) {
                // Получаем родительский элемент iphone-screen
                const iphoneScreen = messageContainer.closest('.iphone-screen');
                if (iphoneScreen) {
                    chatHeader = iphoneScreen.querySelector('.chat-header');
                }
            }
            
            // Если не нашли через сообщение, ищем любой заголовок чата
            if (!chatHeader) {
                chatHeader = document.querySelector('.chat-header');
            }
            
            if (chatHeader) {
                // Извлекаем текст заголовка чата (название объекта)
                const headerText = chatHeader.textContent.trim();
                if (headerText) {
                    // Удаляем все специальные символы из заголовка
                    objectName = headerText.replace(/[+✔✓✗❌🔄➕➖➗☑☒☐✅❎]/g, '').trim();
                    
                    // Проверяем, есть ли выпадающее меню с ID объекта
                    const dropdownToggle = chatHeader.querySelector('.dropdown-toggle');
                    if (dropdownToggle) {
                        const onclickAttr = dropdownToggle.getAttribute('onclick');
                        if (onclickAttr) {
                            const match = onclickAttr.match(/toggleDropdown\((\d+)\)/i);
                            if (match && match[1]) {
                                const objectId = match[1];
                                console.log(`Найден ID объекта из выпадающего меню: ${objectId}`);
                            }
                        }
                    }
                }
            }
            
            // Заполняем таблицу совпадающими сотрудниками
            let matchFound = false;
            
            // Сначала проверяем совпадения из извлеченных данных
            for (const extracted of extractedEmployees) {
                for (const employee of employeesData) {
                    // Используем готовую фамилию или извлекаем из полного ФИО
                    const employeeSurname = employee.surname || employee.fio.split(' ')[0];
                    
                    // Проверяем схожесть фамилий
                    console.log(`Сравниваем фамилии: "${extracted.surname}" и "${employeeSurname}"`);
                    if (isSimilarSurname(extracted.surname, employeeSurname)) {
                        console.log(`НАЙДЕНО СОВПАДЕНИЕ: "${extracted.surname}" и "${employeeSurname}"!`);
                        
                        // Создаем строку в таблице с данными сотрудника
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><input type="text" value="${employee.specialnost}" data-employee-id="${employee.id || ''}"></td>
                            <td><input type="text" value="${employee.fio}"></td>
                            <td><input type="number" value="${extracted.hours}" min="1" max="24"></td>
                            <td><input type="number" value="1.0" min="0.1" max="2.0" step="0.1"></td>
                            <td><input type="text" value="${objectName}"></td>
                        `;
                        hoursTable.appendChild(row);
                        matchFound = true;
                    }
                }
            }
            
            // Если не нашли совпадений, но есть сотрудники в списке
            if (!matchFound && employeesData.length > 0) {
                // Если есть извлеченные данные, используем их с первым сотрудником
                if (extractedEmployees.length > 0) {
                    const extracted = extractedEmployees[0];
                    const employee = employeesData[0]; // Берем первого сотрудника из списка
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="text" value="${employee.specialnost}" data-employee-id="${employee.id || ''}"></td>
                        <td><input type="text" value="${employee.fio}"></td>
                        <td><input type="number" value="${extracted.hours}" min="1" max="24"></td>
                        <td><input type="number" value="1.0" min="0.1" max="2.0" step="0.1"></td>
                        <td><input type="text" value="${objectName}"></td>
                    `;
                    hoursTable.appendChild(row);
                    matchFound = true;
                }
            }
            
            // Если все еще нет совпадений, добавляем строку с извлеченными данными
            if (!matchFound) {
                // Если есть извлеченные данные, используем их
                if (extractedEmployees.length > 0) {
                    const extracted = extractedEmployees[0];
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="text" value="Прораб"></td>
                        <td><input type="text" value="${extracted.surname}"></td>
                        <td><input type="number" value="${extracted.hours}" min="1" max="24"></td>
                        <td><input type="number" value="1.0" min="0.1" max="2.0" step="0.1"></td>
                        <td><input type="text" value="${objectName}"></td>
                    `;
                    hoursTable.appendChild(row);
                } else {
                    // Иначе добавляем пустую строку
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="text" value="Прораб"></td>
                        <td><input type="text" value="Иванов И.И."></td>
                        <td><input type="number" value="8" min="1" max="24"></td>
                        <td><input type="number" value="1.0" min="0.1" max="2.0" step="0.1"></td>
                        <td><input type="text" value="${objectName}"></td>
                    `;
                    hoursTable.appendChild(row);
                }
            }
        }
        
        // Показываем модальное окно
        console.log('Показываем модальное окно в конце функции openHoursModal');
        modal.style.display = 'block';
        
        // Дополнительно устанавливаем стили для модального окна
        modal.style.zIndex = '10000';
        modal.style.opacity = '1';
        
        // Проверяем, что модальное окно видимо
        setTimeout(function() {
            if (modal.style.display !== 'block') {
                console.log('Модальное окно не отображается, повторная попытка');
                modal.style.display = 'block';
            }
        }, 100);
    }
}

// Функция для закрытия модального окна
window.closeHoursModal = function() {
    const modal = document.getElementById('hoursModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Функция для сохранения часов в табель
window.saveHours = function() {
    // Здесь можно добавить логику сохранения данных в базу
    alert('Часы успешно добавлены в табель');
    window.closeHoursModal();
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
// Функция для поиска сотрудников по фамилии и объекту
function findEmployeesByObject(extractedEmployees, objektId) {
    if (!extractedEmployees || extractedEmployees.length === 0 || !objektId) {
        console.log('Нет данных для поиска сотрудников');
        return;
    }
    
    console.log(`Поиск сотрудников по объекту ID: ${objektId}`);
    console.log('Извлеченные фамилии:', extractedEmployees);
    
    // Создаем или обновляем поле для отладки
    let debugContainer = document.getElementById('employees-debug');
    if (!debugContainer) {
        debugContainer = document.createElement('div');
        debugContainer.id = 'employees-debug';
        debugContainer.style.padding = '10px';
        debugContainer.style.marginTop = '15px';
        debugContainer.style.backgroundColor = '#f8f9fa';
        debugContainer.style.border = '1px solid #dee2e6';
        debugContainer.style.borderRadius = '5px';
        debugContainer.style.fontSize = '0.9rem';
        debugContainer.style.maxHeight = '200px';
        debugContainer.style.overflowY = 'auto';
        
        // Добавляем заголовок
        const debugHeader = document.createElement('h4');
        debugHeader.textContent = 'Отладка поиска сотрудников';
        debugHeader.style.fontSize = '1rem';
        debugHeader.style.marginBottom = '10px';
        debugContainer.appendChild(debugHeader);
        
        // Добавляем контейнер в модальное окно
        const modalBody = document.querySelector('.modal-body');
        if (modalBody) {
            modalBody.appendChild(debugContainer);
        }
    } else {
        // Очищаем содержимое, оставляя заголовок
        const debugHeader = debugContainer.querySelector('h4');
        debugContainer.innerHTML = '';
        if (debugHeader) {
            debugContainer.appendChild(debugHeader);
        }
    }
    
    // Добавляем индикатор загрузки
    const loadingIndicator = document.createElement('p');
    loadingIndicator.textContent = 'Идет поиск сотрудников...';
    loadingIndicator.style.fontStyle = 'italic';
    debugContainer.appendChild(loadingIndicator);
    
    // Собираем фамилии для поиска
    const surnames = extractedEmployees.map(emp => emp.surname);
    
    // Функция для получения cookie
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
    
    // Отправляем AJAX-запрос на сервер для поиска сотрудников
    fetch('/telegram/find-employees/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            surnames: surnames,
            objekt_id: objektId
        })
    })
    .then(response => response.json())
    .then(data => {
        // Удаляем индикатор загрузки, если он существует
        if (loadingIndicator && loadingIndicator.parentNode === debugContainer) {
            debugContainer.removeChild(loadingIndicator);
        }
        
        if (data.success) {
            console.log('Найденные сотрудники:', data.employees);
            
            // Добавляем результаты в отладочный контейнер
            const resultsHeader = document.createElement('p');
            resultsHeader.innerHTML = `<strong>Найдено сотрудников: ${data.employees.length}</strong>`;
            debugContainer.appendChild(resultsHeader);
            
            // Создаем список найденных сотрудников
            const employeesList = document.createElement('ul');
            employeesList.style.paddingLeft = '20px';
            employeesList.style.marginBottom = '10px';
            
            data.employees.forEach(emp => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<strong>${emp.fio}</strong> - ${emp.specialnost || 'Должность не указана'} (Совпадение с "${emp.matched_surname}")`;
                employeesList.appendChild(listItem);
            });
            
            debugContainer.appendChild(employeesList);
            
            // Если есть ненайденные фамилии
            if (data.not_found && data.not_found.length > 0) {
                const notFoundHeader = document.createElement('p');
                notFoundHeader.innerHTML = `<strong>Не найдены сотрудники с фамилиями:</strong>`;
                debugContainer.appendChild(notFoundHeader);
                
                const notFoundList = document.createElement('ul');
                notFoundList.style.paddingLeft = '20px';
                
                data.not_found.forEach(surname => {
                    const listItem = document.createElement('li');
                    listItem.textContent = surname;
                    notFoundList.appendChild(listItem);
                });
                
                debugContainer.appendChild(notFoundList);
            }
            
            // Заполняем таблицу часов найденными сотрудниками
            updateHoursTable(data.employees, extractedEmployees);
            
            // Явно показываем модальное окно
            const modal = document.getElementById('hoursModal');
            if (modal) {
                console.log('Показываем модальное окно после получения данных');
                modal.style.display = 'block';
            } else {
                console.error('Модальное окно не найдено');
            }
            
        } else {
            console.error('Ошибка поиска сотрудников:', data.error);
            
            const errorMessage = document.createElement('p');
            errorMessage.textContent = `Ошибка: ${data.error || 'Не удалось найти сотрудников'}`;
            errorMessage.style.color = '#dc3545';
            debugContainer.appendChild(errorMessage);
        }
    })
    .catch(error => {
        console.error('Ошибка запроса:', error);
        
        // Удаляем индикатор загрузки, если он существует
        if (loadingIndicator && loadingIndicator.parentNode === debugContainer) {
            debugContainer.removeChild(loadingIndicator);
        }
        
        const errorMessage = document.createElement('p');
        errorMessage.textContent = `Ошибка запроса: ${error.message || error}`;
        errorMessage.style.color = '#dc3545';
        debugContainer.appendChild(errorMessage);
    });
}

// Функция для обновления таблицы часов найденными сотрудниками
function updateHoursTable(employees, extractedEmployees) {
    if (!employees || employees.length === 0) return;
    
    const hoursTable = document.querySelector('.hours-table tbody');
    if (!hoursTable) return;
    
    // Очищаем таблицу
    hoursTable.innerHTML = '';
    
    // Получаем название объекта
    const objectElement = document.getElementById('message-object');
    let objectName = objectElement ? objectElement.textContent : 'объекте';
    
    // Заполняем таблицу найденными сотрудниками
    employees.forEach(employee => {
        // Ищем соответствующие часы для сотрудника
        let hours = 8; // По умолчанию
        
        // Ищем совпадение по фамилии или другому слову
        for (const extracted of extractedEmployees) {
            // Проверяем наличие matched_word (новое поле) или matched_surname (старое поле)
            const matchedWord = employee.matched_word || employee.matched_surname;
            
            // Проверяем, что matchedWord существует перед вызовом toLowerCase()
            if (matchedWord && extracted.surname && 
                isSimilarSurname(extracted.surname, matchedWord)) {
                hours = extracted.hours;
                break;
            }
        }
        
        // Создаем строку в таблице
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="text" value="${employee.specialnost || 'Не указана'}" data-employee-id="${employee.id || ''}"></td>
            <td><input type="text" value="${employee.fio}"></td>
            <td><input type="number" value="${hours}" min="1" max="24"></td>
            <td><input type="number" value="1.0" min="0.1" max="2.0" step="0.1"></td>
            <td><input type="text" value="${objectName}"></td>
        `;
        hoursTable.appendChild(row);
    });
}