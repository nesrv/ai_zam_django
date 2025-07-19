// Тестовый скрипт для проверки функциональности модального окна
document.addEventListener('DOMContentLoaded', function() {
    console.log('Тестовый скрипт загружен');
    
    // Функция для тестирования извлечения объекта из заголовка чата
    function testObjectExtraction() {
        const chatHeaders = document.querySelectorAll('.chat-header');
        if (chatHeaders.length === 0) {
            console.log('Заголовки чатов не найдены');
            return;
        }
        
        console.log('Найдено заголовков чатов:', chatHeaders.length);
        chatHeaders.forEach((header, index) => {
            const headerText = header.textContent.trim();
            const cleanedText = headerText.replace(/[+✔✓✗✘☑☒☐✅❌❎➕➖➗]/g, '').trim();
            console.log(`Заголовок ${index + 1}:`, headerText);
            console.log(`Очищенный заголовок ${index + 1}:`, cleanedText);
        });
    }
    
    // Функция для тестирования открытия модального окна
    function testModalOpening() {
        const modal = document.getElementById('hoursModal');
        if (!modal) {
            console.log('Модальное окно не найдено');
            return;
        }
        
        console.log('Модальное окно найдено');
        
        // Тестируем функцию openHoursModal
        if (typeof openHoursModal === 'function') {
            console.log('Функция openHoursModal доступна');
            
            // Тестовые данные
            const testMessage = 'Добавить часы в табель:\n- ФИО: Иванов И.И.\n- Дата: 15.05.2023\n- Количество часов: 8\n- Вид работ: Монтаж';
            const testDate = '15.05.2023';
            
            // Пробуем открыть модальное окно
            try {
                openHoursModal(testMessage, testDate);
                console.log('Модальное окно открыто успешно');
                
                // Проверяем заголовок
                const dateElement = modal.querySelector('#message-date');
                if (dateElement) {
                    console.log('Текст даты в заголовке:', dateElement.textContent);
                }
                
                // Закрываем окно через 3 секунды
                setTimeout(() => {
                    if (typeof closeHoursModal === 'function') {
                        closeHoursModal();
                        console.log('Модальное окно закрыто');
                    }
                }, 3000);
            } catch (e) {
                console.error('Ошибка при открытии модального окна:', e);
            }
        } else {
            console.log('Функция openHoursModal недоступна');
        }
    }
    
    // Запускаем тесты через 1 секунду после загрузки страницы
    setTimeout(() => {
        console.log('Запуск тестов...');
        testObjectExtraction();
        testModalOpening();
    }, 1000);
});