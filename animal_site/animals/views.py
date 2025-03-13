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

def add_animal(request):  # Убедитесь, что эта функция есть
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f"animal_submission_{ip}"
            submission_count = cache.get(cache_key, 0)
            if submission_count >= 4:
                messages.warning(request, "Вы отправляете слишком много анкет. Пожалуйста, подождите 30 минут.")
                return redirect('add_animal')
            animal = form.save(commit=False)
            animal.ip_address = ip
            animal.save()
            cache.set(cache_key, submission_count + 1, 1800)  # 30 минут
            messages.success(request, "Анкета успешно добавлена!")
            return redirect('home')
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

