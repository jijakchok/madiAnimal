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



def home(request):
    sort = request.GET.get('sort')
    show_all = request.GET.get('show') == 'all'

    if show_all:
        animals = Animal.objects.all()
    else:
        animals = Animal.objects.all()  # По умолчанию показываем все анкеты

    if sort == 'oldest':
        animals = animals.order_by('date')
    else:
        animals = animals.order_by('-date')

    total_animals = Animal.objects.count()

    paginator = Paginator(animals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'sort': sort,
        'total_animals': total_animals,
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

    url = "https://api.imgbb.com/1/upload"
    api_key = "386b55dd6972e7905abca308bbae6312"  # Замените на ваш API-ключ

    # Отправляем изображение на ImgBB
    response = requests.post(
        url,
        data={
            "key": api_key,
        },
        files={
            "image": image_file,
        },
    )

    if response.status_code == 200:
        data = response.json()
        return data["data"]["url"]  # Возвращаем URL изображения
    else:
        raise Exception("Ошибка при загрузке изображения на ImgBB")

def add_animal(request):
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            try:
                image_url = upload_to_imgbb(request.FILES['image'])
                animal.image_url = image_url
            except Exception as e:
                messages.error(request, f"Ошибка при загрузке изображения: {e}")
                animal.image_url = None  # Сохраните анкету без изображения
            animal.save()
            messages.success(request, "Анкета успешно добавлена!")
            return redirect('home')
        else:
            messages.error(request, "Форма заполнена неправильно.")
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

