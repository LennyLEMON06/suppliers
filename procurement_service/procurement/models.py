from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid
from datetime import timedelta
from django.utils.timezone import now


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"Наименование")
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name=u"Количество в месяц")  # (по умолчанию 0)
    unit = models.CharField(max_length=50, verbose_name=u"Единица измерения")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Город")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"Наименование")
    contact_info = models.TextField(verbose_name=u"Контактная информация")
    inn = models.CharField(max_length=12, null=True, blank=True, verbose_name="ИНН")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")
    is_hidden = models.BooleanField(default=False, verbose_name="Скрыт")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

class SupplierToken(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return now() > self.created_at + timedelta(hours=24)

    @classmethod
    def get_or_create_token(cls, supplier):
        token_obj, created = cls.objects.get_or_create(supplier=supplier)
        if not created and token_obj.is_expired():
            token_obj.token = uuid.uuid4()
            token_obj.created_at = now()
            token_obj.save()
        return token_obj.token

class Price(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now) #дата добавления
    date_updated = models.DateTimeField(auto_now=True) #дата обновления

    def __str__(self):
        return f"{self.product.name} - {self.supplier.name} - {self.price} - {self.date_added}"

    class Meta:
        unique_together = ('product', 'supplier', 'date_added') # убираем unique_together
        verbose_name = 'Предложения от поставщиков'
        verbose_name_plural = 'Предложения от поставщиков'

    def save(self, *args, **kwargs):
        self.date_updated = timezone.now()
        super().save(*args, **kwargs)

    
