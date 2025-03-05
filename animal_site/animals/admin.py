from django.contrib import admin
from .models import Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'comment', 'number', 'ip_address', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('comment', 'ip_address')