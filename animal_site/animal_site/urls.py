# animal_site/urls.py

from django.contrib import admin
from django.urls import path
from animals import views  # Убедитесь, что views импортированы правильно
from django.conf.urls import handler404
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('add/', views.add_animal, name='add_animal'),  # Проверьте этот путь
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Обработчик для ошибки 404
handler404 = 'animals.views.custom_404'