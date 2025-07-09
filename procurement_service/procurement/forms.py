from django import forms
from .models import Product, Price, Supplier, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Выберите Excel-файл")

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label  # Добавляет placeholder с названием поля

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['product', 'price']
    
    def clean_price(self):
        price_value = self.cleaned_data.get('price')

        # 1. Проверка на пустоту
        if price_value in [None, '', 0]:
            raise ValidationError('Цена не может быть пустой или равной нулю.')

        # 2. Приведение к строке (на случай если price пришёл не строкой)
        if not isinstance(price_value, str):
            price_value = str(price_value)

        # 3. Удаление пробелов, замена запятой на точку
        normalized = price_value.strip().replace(',', '.')

        # 4. Проверка на допустимый числовой формат с максимум двумя знаками после точки
        import re
        if not re.fullmatch(r'^\d+(\.\d{1,2})?$', normalized):
            raise ValidationError('Введите корректную цену — только цифры, до двух знаков после точки.')

        # 5. Конвертация в Decimal
        try:
            price = Decimal(normalized)
        except InvalidOperation:
            raise ValidationError('Введите корректное число.')

        # 6. Диапазон цены
        if price < 0:
            raise ValidationError('Цена не может быть отрицательной.')
        if price > 1_000_000:
            raise ValidationError('Цена не может превышать 1 000 000.')

        return price

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()

        self.fields['price'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например, 299.99',
            'inputmode': 'decimal',  # показывает числовую клавиатуру на мобильных
            'pattern': r'^\d+(\.\d{1,2})?$',  # HTML-проверка
            'title': 'Введите только число, до двух знаков после точки',
        })

        self.fields['product'].widget.attrs.update({'class': 'form-control'})

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'inn', 'contact_info', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unit', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
