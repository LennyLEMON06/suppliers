from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Фильтр для умножения значений"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value  # Возвращает оригинальное значение, если ошибка

@register.filter
def get(dictionary, key):
    return dictionary.get(key)


@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})



