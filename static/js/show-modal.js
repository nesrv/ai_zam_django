// Функция для принудительного отображения модального окна
window.showHoursModal = function() {
    const modal = document.getElementById('hoursModal');
    if (modal) {
        console.log('Показываем модальное окно');
        modal.style.display = 'block';
    } else {
        console.error('Модальное окно не найдено');
    }
};

// Добавляем обработчик события для всех сообщений пользователя
document.addEventListener('DOMContentLoaded', function() {
    console.log('Добавляем обработчики для сообщений');
    
    // Находим все сообщения пользователя
    const userMessages = document.querySelectorAll('.user-message');
    console.log('Найдено сообщений пользователя:', userMessages.length);
    
    // Добавляем обработчик клика для каждого сообщения
    userMessages.forEach(function(message) {
        message.addEventListener('click', function() {
            console.log('Клик по сообщению');
            window.showHoursModal();
        });
    });
});