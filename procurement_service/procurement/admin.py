from django.contrib import admin
from .models import Product, Supplier, Price, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit', 'last_updated')  # Отображаемые поля
    list_filter = ('unit',)  # Фильтр по единице измерения
    search_fields = ('name',)  # Поиск по названию
    ordering = ('name',)  # Сортировка по названию

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'contact_info', 'category')  # добавили category
    list_filter = ('category',)  # фильтрация по категории
    search_fields = ('name',)

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'price', 'manufacturer', 'date_added')  # Основные поля
    list_filter = ('supplier', 'date_added')  # Фильтры по поставщику и дате
    search_fields = ('product__name', 'supplier__name')  # Поиск по продукту и поставщику
    ordering = ('-date_added',)  # Последние добавленные записи в начале
    date_hierarchy = 'date_added'  # Добавляем навигацию по дате
