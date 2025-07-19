(function($) {
    $(document).ready(function() {
        // Создаем словарь соответствия кодов и названий подразделений
        var podrazdeleniaMap = {};
        
        // Функция для загрузки данных о подразделениях
        function loadPodrazdeleniaData() {
            $.ajax({
                url: '/sotrudniki/api/podrazdeleniya/',
                method: 'GET',
                success: function(data) {
                    // Заполняем словарь соответствия кодов и названий
                    data.podrazdeleniya.forEach(function(item) {
                        if (item.kod && item.nazvanie) {
                            podrazdeleniaMap[item.kod] = item.nazvanie;
                        }
                    });
                }
            });
        }
        
        // Загружаем данные при загрузке страницы
        loadPodrazdeleniaData();
        
        // Обработчик изменения кода подразделения
        $(document).on('change', 'input[name$="-kod"]', function() {
            var kodInput = $(this);
            var kod = kodInput.val();
            
            // Находим соответствующее поле для названия
            var row = kodInput.closest('tr');
            var nazvanieInput = row.find('input[name$="-nazvanie"]');
            
            // Если код есть в словаре, заполняем название
            if (podrazdeleniaMap[kod]) {
                nazvanieInput.val(podrazdeleniaMap[kod]);
            }
        });
    });
})(django.jQuery);