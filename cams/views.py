from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Camera


def camera_list(request):
    if request.user.is_authenticated:
        from object.models import UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        organizations = user_profile.organizations.all()
        cameras = Camera.objects.filter(is_active=True, objekt__organizacii__in=organizations).distinct()
    else:
        cameras = Camera.objects.filter(is_active=True, objekt__demo=True)
    return render(request, 'cams/camera_list.html', {'cameras': cameras})

