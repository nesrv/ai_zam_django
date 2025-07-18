// Простой скрипт для обеспечения прокрутки сообщений
(function() {
    // Функция для настройки прокрутки
    function setupScrolling() {
        // Находим все контейнеры сообщений
        const containers = document.querySelectorAll('.messages-container');
        
        // Применяем стили и обработчики к каждому контейнеру
        containers.forEach(container => {
            // Прокручиваем к последнему сообщению
            container.scrollTop = container.scrollHeight;
            
            // Удаляем существующие обработчики, если они есть
            if (container._wheelHandler) {
                container.removeEventListener('wheel', container._wheelHandler);
            }
            
            // Создаем новый обработчик
            container._wheelHandler = function(e) {
                // Останавливаем стандартное поведение
                e.preventDefault();
                e.stopPropagation();
                
                // Прокручиваем контейнер
                this.scrollTop += e.deltaY;
                
                return false;
            };
            
            // Добавляем обработчик события wheel
            container.addEventListener('wheel', container._wheelHandler, { passive: false, capture: true });
            
            // Добавляем MutationObserver для прокрутки при добавлении новых сообщений
            if (!container._observer) {
                container._observer = new MutationObserver(function() {
                    container.scrollTop = container.scrollHeight;
                });
                
                container._observer.observe(container, { childList: true, subtree: true });
            }
        });
    }
    
    // Запускаем настройку прокрутки при загрузке страницы
    document.addEventListener('DOMContentLoaded', setupScrolling);
    
    // Запускаем настройку прокрутки при изменении содержимого
    window.addEventListener('load', setupScrolling);
    
    // Добавляем функцию в глобальный объект для возможности вызова из других скриптов
    window.setupMessageScrolling = setupScrolling;
    
    // Запускаем настройку прокрутки каждые 2 секунды для надежности
    setInterval(setupScrolling, 2000);
})();