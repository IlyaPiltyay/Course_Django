from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Путь к административному интерфейсу
    path('mailings/', include('mailings.urls')),  # Подключаем приложение mailings
    path('users/', include('users.urls')),  # Подключаем приложение users для аутентификации
]