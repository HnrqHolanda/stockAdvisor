from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include


def redirect_to_login(request):
    return redirect('/auth/login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login),
    path("auth/", include("users.urls")),
    path("menu/", include("menu.urls")),
]
