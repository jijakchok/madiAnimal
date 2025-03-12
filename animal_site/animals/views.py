# animals/views.py

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
    sort = request.GET.get('sort', 'newest')  # По умолчанию сортируем от новых к старым
    animals = Animal.objects.filter(date__gte=timezone.now() - timedelta(days=30))

    if sort == 'oldest':
        animals = animals.order_by('date')  # От старых к новым
    else:
        animals = animals.order_by('-date')  # От новых к старым

    # Подсчет общего количества объявлений
    total_animals = Animal.objects.count()

    # Пагинация
    paginator = Paginator(animals, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Передаем данные в шаблон
    context = {
        'page_obj': page_obj,
        'sort': sort,
        'total_animals': total_animals,  # Добавляем счетчик
    }
    return render(request, 'animals/home.html', context)

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
    animals = Animal.objects.none()  # По умолчанию пустой queryset

    if query:
        try:
            # Преобразуем строку в объект datetime
            search_date = datetime.strptime(query, '%d.%m.%Y').date()
            # Ищем записи с указанной датой
            animals = Animal.objects.filter(date__date=search_date)
            if not animals.exists():
                messages.info(request, "Такой даты не существует.")
        except ValueError:
            # Если дата некорректна, выводим сообщение
            messages.error(request, "Некорректный формат даты. Используйте формат ДД.ММ.ГГГГ.")

    return render(request, 'animals/home.html', {'animals': animals})

