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
        price = self.cleaned_data.get("price", "").strip()

        if not price:
            return None  # Позволяем пустое значение, если в модели price=null=True

        # Заменяем запятую на точку (если юзер вводит 1,99 вместо 1.99)
        price = price.replace(",", ".")

        try:
            return Decimal(price)
        except InvalidOperation:
            raise ValidationError("Введите корректную цену (например: 10.50)")

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
