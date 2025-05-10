# buea/backed/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safe dictionary lookup that returns None if key doesn't exist"""
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None