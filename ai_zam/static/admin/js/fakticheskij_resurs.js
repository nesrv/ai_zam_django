(function($) {
    $(document).ready(function() {
        var $objektSelect = $('#id_objekt');
        var $resursSelect = $('#id_resurs_po_objektu');
        
        // Сохраняем все опции при загрузке
        var allOptions = [];
        $resursSelect.find('option').each(function() {
            if ($(this).val()) {
                allOptions.push({
                    value: $(this).val(),
                    text: $(this).text(),
                    objektName: $(this).text().split(' - ')[0]
                });
            }
        });
        
        $objektSelect.change(function() {
            var selectedObjektName = $(this).find('option:selected').text();
            
            // Очищаем список ресурсов
            $resursSelect.empty();
            $resursSelect.append('<option value="">---------</option>');
            
            if (selectedObjektName && selectedObjektName !== 'Выберите объект') {
                // Фильтруем и добавляем опции для выбранного объекта
                allOptions.forEach(function(option) {
                    if (option.objektName === selectedObjektName) {
                        $resursSelect.append('<option value="' + option.value + '">' + option.text + '</option>');
                    }
                });
            }
        });
        
        // Инициализируем при загрузке, если объект уже выбран
        if ($objektSelect.val()) {
            $objektSelect.trigger('change');
        }
    });
})(django.jQuery);