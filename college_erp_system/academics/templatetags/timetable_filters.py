from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a dictionary value by key
    Usage: {{ my_dict|lookup:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key, [])

@register.filter
def get_item(dictionary, key):
    """
    Alternative way to get dictionary item
    Usage: {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
