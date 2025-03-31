from django import forms
from .models import Product, Price, Supplier
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
        price_value = self.cleaned_data['price']
        
        # Проверка на пустое значение
        if not price_value:
            raise forms.ValidationError('Цена не может быть пустой.')

        # Преобразование строки в Decimal и проверка на корректность
        try:
            # Преобразуем цену, заменяя запятую на точку (если необходимо)
            price = Decimal(price_value.replace(',', '.'))
        except InvalidOperation:
            raise forms.ValidationError('Введите корректную цену (например, 10.50).')

        # Проверка на отрицательные значения
        if price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной.')

        # Проверка на слишком большие значения (например, максимальная цена 1000000)
        if price > 1000000:
            raise forms.ValidationError('Цена не может превышать 1 000 000.')

        return price

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_info']

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
