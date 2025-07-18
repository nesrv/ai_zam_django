// Простое решение для прокрутки сообщений
document.addEventListener('DOMContentLoaded', function() {
    // Находим все контейнеры сообщений
    const messageContainers = document.querySelectorAll('.messages-container');
    
    // Применяем стили и обработчики к каждому контейнеру
    messageContainers.forEach(container => {
        // Устанавливаем стили для прокрутки
        container.style.overflowY = 'scroll';
        container.style.height = '400px';
        container.style.maxHeight = '400px';
        
        // Прокручиваем к последнему сообщению
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
        
        // Добавляем обработчик события wheel
        container.addEventListener('wheel', function(e) {
            // Останавливаем распространение события
            e.stopPropagation();
            e.preventDefault();
            
            // Прокручиваем контейнер вручную
            container.scrollTop += e.deltaY;
        }, { passive: false, capture: true });
    });
});