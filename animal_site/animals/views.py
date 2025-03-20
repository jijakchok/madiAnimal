# animals/views.py
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Animal
from .forms import AnimalForm
from datetime import timedelta
from django.core.cache import cache
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def home(request):
    locations = Animal.objects.values_list('location', flat=True).distinct()
    numbers = Animal.objects.values_list('number', flat=True).distinct()

    location_filter = request.GET.get('location')
    number_filter = request.GET.get('number')

    animals = Animal.objects.all()

    if location_filter:
        animals = animals.filter(location=location_filter)
    if number_filter:
        animals = animals.filter(number=number_filter)

    paginator = Paginator(animals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'locations': locations,
        'numbers': numbers,
    }
    return render(request, 'animals/home.html', context)

def upload_to_imgbb(image_file):
    # Проверка размера изображения (максимум 32 МБ)
    if image_file.size > 32 * 1024 * 1024:  # 32 МБ
        raise Exception("Изображение слишком большое. Максимальный размер — 32 МБ.")

    # Проверка формата изображения
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    file_extension = image_file.name.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        raise Exception("Недопустимый формат изображения. Используйте JPEG, PNG или GIF.")

    try:
        logger.info("Начало загрузки изображения на ImgBB")
        url = "https://api.imgbb.com/1/upload"
        api_key = "386b55dd6972e7905abca308bbae6312"  # Замените на ваш API-ключ
        logger.info(f"API ключ: {api_key}")

        response = requests.post(
            url,
            data={
                "key": api_key,
            },
            files={
                "image": image_file,
            },
        )

        logger.info(f"Ответ от ImgBB: {response.status_code}, {response.text}")

        if response.status_code == 200:
            data = response.json()
            return data["data"]["id"], data["data"]["image"]["filename"]
        else:
            raise Exception(f"Ошибка при загрузке изображения на ImgBB: {response.text}")
    except Exception as e:
        logger.error(f"Ошибка в функции upload_to_imgbb: {e}")
        raise




logger = logging.getLogger(__name__)


def add_animal(request):
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            logger.info(f"Файл изображения: {request.FILES.get('image')}")

            try:
                image_code, image_filename = upload_to_imgbb(request.FILES['image'])
                animal.image_code = image_code
                animal.image_filename = image_filename
                logger.info(f"Изображение успешно загружено: {image_code}, {image_filename}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке изображения: {e}")
                messages.error(request, f"Ошибка при загрузке изображения: {e}")
                animal.image_code = None
                animal.image_filename = None

            # Извлечение IP-адреса пользователя
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            animal.ip_address = ip_address

            try:
                animal.save()
                messages.success(request, "Анкета успешно добавлена!")
                return redirect('home')
            except Exception as e:
                logger.error(f"Ошибка при сохранении анкеты: {e}")
                messages.error(request, "Ошибка при сохранении анкеты.")
        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Форма заполнена неправильно. Проверьте введенные данные.")
    else:
        form = AnimalForm()
    return render(request, 'animals/add_animal.html', {'form': form})

def about(request):
    return render(request, 'animals/about.html')

def search(request):
    query = request.GET.get('q')
    animals = Animal.objects.all()  # По умолчанию показываем все анкеты

    if query:
        try:
            # Преобразуем строку в объект datetime
            search_date = datetime.strptime(query, '%d.%m.%Y').date()
            # Ищем записи с указанной датой
            animals = animals.filter(date__date=search_date)
            if not animals.exists():
                messages.info(request, "Такой даты не существует.")
        except ValueError:
            # Если дата некорректна, выводим сообщение
            messages.error(request, "Некорректный формат даты. Используйте формат ДД.ММ.ГГГГ.")

    # Добавляем пагинацию
    paginator = Paginator(animals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Передаем данные в шаблон
    context = {
        'page_obj': page_obj,
        'total_animals': Animal.objects.count(),
    }
    return render(request, 'animals/home.html', context)

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

