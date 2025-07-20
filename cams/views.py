from django.shortcuts import render

def camera_list(request):
    # Список открытых видеопотоков с видами Москвы
    moscow_cameras = [
        {
            'id': 1,
            'name': 'Красная площадь',
            'url': 'https://www.youtube.com/embed/NjhQnXITow4?autoplay=1&mute=1',
            'description': 'Вид на главную площадь страны'
        },
        {
            'id': 2,
            'name': 'Москва-Сити',
            'url': 'https://www.youtube.com/embed/BMQQQynlrn4?autoplay=1&mute=1',
            'description': 'Панорама небоскребов делового центра'
        },
        {
            'id': 3,
            'name': 'Воробьевы горы',
            'url': 'https://www.youtube.com/embed/5YYIlLCK9Hk?autoplay=1&mute=1',
            'description': 'Смотровая площадка с видом на город'
        },
        {
            'id': 4,
            'name': 'Парк Зарядье',
            'url': 'https://www.youtube.com/embed/Wp43Tbij4ss?autoplay=1&mute=1',
            'description': 'Современный парк в центре столицы'
        },
        {
            'id': 5,
            'name': 'Кутузовский проспект',
            'url': 'https://www.youtube.com/embed/8A9WOSCwJ8s?autoplay=1&mute=1',
            'description': 'Одна из главных магистралей города'
        },
        {
            'id': 6,
            'name': 'Садовое кольцо',
            'url': 'https://www.youtube.com/embed/ch1_4LtwNxA?autoplay=1&mute=1',
            'description': 'Круговая магистраль в центре Москвы'
        },
    ]
    
    return render(request, 'cams/camera_list.html', {'cameras': moscow_cameras})
