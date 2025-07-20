from django.shortcuts import render

def camera_list(request):
    # Список открытых видеопотоков
    cameras = [
        {
            'id': 1,
            'name': 'Камера 1',
            'url': 'https://rtsp.me/embed/7b49D38G/',
            'description': 'Онлайн трансляция'
        },
        {
            'id': 8,
            'name': 'Улица в реальном времени',
            'url': 'https://open.ivideon.com/embed/v3/?server=100-xdKWVLFVn1GVNmt5RHC3Q9&camera=0&width=&height=&lang=ru',
            'description': 'Онлайн трансляция с улицы'
        },
        {
            'id': 9,
            'name': 'Камера 9',
            'url': 'https://rtsp.me/embed/Qtsh3rNi/',
            'description': 'Онлайн трансляция'
        },
    ]
    
    return render(request, 'cams/camera_list.html', {'cameras': cameras})
    
    return render(request, 'cams/camera_list.html', {'cameras': moscow_cameras})
