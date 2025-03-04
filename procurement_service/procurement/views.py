from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Supplier, Price, SupplierToken
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.conf import settings
from django.urls import reverse
from django.utils.dateparse import parse_date
import openpyxl
from django.http import HttpResponse, HttpResponseForbidden
import datetime
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill, Alignment, Border, Side
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.http import JsonResponse

# Функция для создания границ
def get_border():
    return Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

# Функция для создания и применения стилей
def apply_styles(sheet):
    best_price_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    border = get_border()

    # Применяем стили ко всем ячейкам
    for row in sheet.iter_rows():
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            if cell.value == 'Best Price':
                cell.fill = best_price_fill

# Экспорт в Excel
@login_required
def export_to_excel(request):
    products = Product.objects.all()
    suppliers = Supplier.objects.all()

    # Создание книги и активного листа
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Таблица продуктов"
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    sheet.page_setup.fitToPage = True
    sheet.page_setup.fitToWidth = 1
    sheet.page_setup.fitToHeight = 1

    headers = ["Наименование", "Средняя потребность", "Единица измерения"]
    for supplier in suppliers:
        headers.extend([f"{supplier.name} (Цена)", f"{supplier.name} (Производитель)"])
    sheet.append(headers)

    # Данные
    for product in products:
        row_data = [product.name, product.quantity, product.unit]
        price_cells = {}  # Словарь {supplier_name: (cell, price)}
        best_price = None

        for supplier in suppliers:
            price_entry = Price.objects.filter(product=product, supplier=supplier).first()
            price = price_entry.price if price_entry else None
            manufacturer = price_entry.manufacturer if price_entry else "-"

            row_data.append(price if price else "-")
            row_data.append(manufacturer)

            if price and (best_price is None or price < best_price):
                best_price = price
                price_cells[supplier.name] = price  # Сохраняем цену для поставщика

        sheet.append(row_data)

        # Выделяем ячейку с лучшей ценой
        row_index = sheet.max_row  # Номер текущей строки
        col_index = 4  # Первый столбец цены
        for supplier in suppliers:
            if price_cells.get(supplier.name) == best_price:
                sheet.cell(row=row_index, column=col_index).fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
            col_index += 2

    apply_styles(sheet)

    # Автоматическая подгонка ширины колонок
    for col_num, column_cells in enumerate(sheet.columns, start=1):
        max_length = 0
        column = get_column_letter(col_num)
        for cell in column_cells:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        sheet.column_dimensions[column].width = max_length + 2

    # Формируем имя файла с датой
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"products_{current_date}.xlsx"

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)

    return response

@login_required
def upload_excel(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                # Чтение Excel-файла
                df = pd.read_excel(file)

                # Получаем список всех названий товаров из файла
                uploaded_product_names = df['Наименование товара'].tolist()

                # Удаляем продукты, которых нет в файле
                Product.objects.exclude(name__in=uploaded_product_names).delete()

                # Обновляем или создаем продукты
                for index, row in df.iterrows():
                    Product.objects.update_or_create(
                        name=row['Наименование товара'],  # Фильтр по названию
                        defaults={  # Обновляемые данные
                            'quantity': row['Средняя потребность на месяц'],
                            'unit': row['Единица измерения']
                        }
                    )

                return redirect('product_supplier_table')  # Перенаправление на таблицу
            except Exception as e:
                return render(request, 'upload_excel.html', {
                    'form': form,
                    'error': f"Ошибка при обработке файла: {str(e)}"
                })
    else:
        form = UploadFileForm()
    return render(request, 'upload_excel.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('product_supplier_table')  # Перенаправление на главную страницу
        else:
            return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')  # Перенаправление на главную страницу

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически входить после регистрации
            return redirect('home')  # Перенаправление на главную страницу
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def product_list(request):
    products = Product.objects.all()  # Получаем все продукты из базы данных
    return render(request, 'product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        # Если форма была отправлена, обрабатываем данные
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем продукт в базу данных
            return redirect('product_list')  # Перенаправляем на страницу со списком продуктов
    else:
        # Если это GET-запрос, показываем пустую форму
        form = ProductForm()
    
    # Рендерим шаблон с формой
    return render(request, 'add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Получаем продукт по ID
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)  # Заполняем форму данными продукта
        if form.is_valid():
            form.save()  # Сохраняем изменения
            return redirect('product_list')  # Перенаправляем на список продуктов
    else:
        form = ProductForm(instance=product)  # Показываем форму с текущими данными продукта
    return render(request, 'edit_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Получаем продукт по ID
    if request.method == 'POST':
        product.delete()  # Удаляем продукт
        return redirect('product_list')  # Перенаправляем на список продуктов
    return render(request, 'confirm_delete_product.html', {'product': product})

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()  # Получаем всех поставщиков из базы данных
    return render(request, 'supplier_list.html', {'suppliers': suppliers})

@login_required
def add_supplier(request):
    if request.method == 'POST':
        # Если форма была отправлена, обрабатываем данные
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем поставщика в базу данных
            return redirect('supplier_list')  # Перенаправляем на страницу со списком поставщиков
    else:
        # Если это GET-запрос, показываем пустую форму
        form = SupplierForm()
    
    # Рендерим шаблон с формой
    return render(request, 'add_supplier.html', {'form': form})

@login_required
def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)  # Получаем поставщика по ID
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)  # Заполняем форму данными поставщика
        if form.is_valid():
            form.save()  # Сохраняем изменения
            return redirect('supplier_list')  # Перенаправляем на список поставщиков
    else:
        form = SupplierForm(instance=supplier)  # Показываем форму с текущими данными поставщика
    return render(request, 'edit_supplier.html', {'form': form})

@login_required
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)  # Получаем поставщика по ID
    if request.method == 'POST':
        supplier.delete()  # Удаляем поставщика
        return redirect('supplier_list')  # Перенаправляем на список поставщиков
    return render(request, 'confirm_delete_supplier.html', {'supplier': supplier})

@login_required
def get_supplier_token(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    token = SupplierToken.get_or_create_token(supplier)
    url = request.build_absolute_uri(f"/supplier_form/{supplier_id}/{token}/")
    return JsonResponse({"url": url})


@login_required
def supplier_form(request, supplier_id, token):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    token_obj = get_object_or_404(SupplierToken, supplier=supplier, token=token)
    products = Product.objects.all()

    if token_obj.is_expired():
        return HttpResponseForbidden("Срок действия ссылки истек.")

    if request.method == 'POST':
        for product in products:
            price_str = request.POST.get(f'price_{product.id}', "").strip()
            manufacturer = request.POST.get(f'manufacturer_{product.id}', "").strip()

            if not price_str and not manufacturer:
                continue

            try:
                price = Decimal(price_str.replace(",", "."))
            except (InvalidOperation, ValueError):
                messages.error(request, f"Некорректная цена для {product.name}")
                continue

            existing_price = Price.objects.filter(product=product, supplier=supplier).order_by('-date_added').first()

            if not existing_price or existing_price.price != price or existing_price.manufacturer != manufacturer:
                Price.objects.create(product=product, supplier=supplier, price=price, manufacturer=manufacturer)

        messages.success(request, "Данные успешно сохранены!")
        return redirect('success')

    return render(request, 'supplier_form.html', {"products": products, "supplier": supplier})

def success(request):
    return render(request, 'success.html')

@login_required
def price_list(request):
    # Получаем параметры из GET-запроса
    date_str = request.GET.get('date')  # Дата
    supplier_id = request.GET.get('supplier')  # Поставщик
    
    # Сначала фильтруем по дате
    if date_str:
        selected_date = parse_date(date_str)  # Преобразуем строку в дату
        prices = Price.objects.filter(date_added__date=selected_date)  # Фильтруем по дате
    else:
        prices = Price.objects.all()  # Если даты нет, показываем все

    # Фильтруем по поставщику, если указан
    if supplier_id:
        prices = prices.filter(supplier_id=supplier_id)

    # Получаем список поставщиков для выпадающего списка
    suppliers = Supplier.objects.all()

    return render(request, 'price_list.html', {
        'prices': prices,
        'selected_date': date_str,
        'suppliers': suppliers,
        'selected_supplier_id': supplier_id,
    })

@login_required
def export_prices_to_excel(request):
    date_str = request.GET.get('date')
    supplier_id = request.GET.get('supplier')

    # Фильтрация данных
    prices = Price.objects.all()
    if date_str:
        selected_date = parse_date(date_str)
        prices = prices.filter(date_added__date=selected_date)
    if supplier_id:
        prices = prices.filter(supplier_id=supplier_id)

    # Создание книги и активного листа
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Цены"

    # Устанавливаем альбомную ориентацию и подгоняем ширину
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE
    sheet.page_setup.fitToPage = True
    sheet.page_setup.fitToWidth = 1
    sheet.page_setup.fitToHeight = 0

    # Границы для ячеек
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Заголовки
    headers = ["Продукт", "Поставщик", "Цена", "Производитель", "Дата добавления"]
    sheet.append(headers)

    # Заполняем таблицу данными
    for price in prices:
        row = [
            price.product.name,
            price.supplier.name,
            price.price,
            price.manufacturer,
            price.date_added.strftime("%Y-%m-%d")
        ]
        sheet.append(row)

    # Применяем границы и выравнивание
    for row in sheet.iter_rows():
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Автоматическая подгонка ширины колонок
    for col_num, column_cells in enumerate(sheet.columns, start=1):
        max_length = 0
        column_letter = get_column_letter(col_num)
        for cell in column_cells:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        sheet.column_dimensions[column_letter].width = max_length + 2

    # Формируем имя файла с датой
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"prices_{current_date}.xlsx"

    # Создание HTTP-ответа
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)

    return response

@login_required
def product_supplier_table(request):
    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    supplier_prices = Price.objects.all()

    # Получаем дату из GET-запроса
    date_str = request.GET.get('date')
    if date_str:
        selected_date = parse_date(date_str)  # Преобразуем строку в дату
        supplier_prices = supplier_prices.filter(date_added__date=selected_date)  # Фильтруем по дате

    # Создаем структуру данных для таблицы
    table_data = []
    for product in products:
        product_data = {
            'name': product.name,
            'quantity': product.quantity,
            'unit': product.unit,
            'supplier_prices': {},  # Словарь для хранения цен и производителей
            'best_price': None,
            'best_price_supplier': None,  # Поставщик с лучшей ценой
        }

        # Собираем цены и производителей всех поставщиков для текущего продукта
        for supplier in suppliers:
            price = supplier_prices.filter(product=product, supplier=supplier).first()
            product_data['supplier_prices'][supplier.name] = {
                'price': price.price if price else None,
                'manufacturer': price.manufacturer if price else None
            }

        # Находим лучшую цену и поставщика
        prices = {supplier: data['price'] for supplier, data in product_data['supplier_prices'].items() if data['price'] is not None}
        if prices:
            best_supplier = min(prices, key=prices.get)
            product_data['best_price'] = prices[best_supplier]
            product_data['best_price_supplier'] = best_supplier

        table_data.append(product_data)

    return render(request, 'product_supplier_table.html', {
        'table_data': table_data,
        'suppliers': suppliers,
        'selected_date': date_str  # Передаем выбранную дату в шаблон
    })