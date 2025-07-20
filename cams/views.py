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
            'name': 'Москва HD',
            'url': 'https://vkvideo.ru/video_ext.php?oid=-106879986&id=456252667&hd=2&autoplay=1',
            'description': 'Вид на город в высоком качестве'
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
