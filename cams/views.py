from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Camera


def camera_list(request):
    cameras = Camera.objects.filter(is_active=True)
    return render(request, 'cams/camera_list.html', {'cameras': cameras})

