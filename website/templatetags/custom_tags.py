from django import template

register = template.Library()


@register.simple_tag()
def get_medal_color_by_position(position):
    medals_data = {
        1: 'yellow-300',
        2: 'gray-300',
        3: 'yellow-600',
        4: 'blue-300',
        5: 'yellow-600',
        6: 'rose-300',
    }
    if position in medals_data:
        return medals_data[position]

    return 'white'


@register.filter
def get_range(value):
    return range(value)
