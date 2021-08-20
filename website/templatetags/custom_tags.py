import os
import random

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag()
def get_medal_color_by_position(position):
    medals_data = {
        1: 'yellow-300',
        2: 'gray-300',
        3: 'yellow-600',
        4: 'blue-500',
        5: 'green-400',
        6: 'rose-300',
    }
    if position in medals_data:
        return medals_data[position]

    return 'white'


@register.simple_tag(takes_context=True)
def get_points_list(context, player_in_game_name):
    return context['players_points'][player_in_game_name.lower()]['point_list']


@register.simple_tag(takes_context=False)
def get_random_wallpaper():
    return random.choice(
        os.listdir(os.path.join(settings.BASE_DIR, 'website/static/assets/backgrounds/'))
    )


@register.simple_tag(takes_context=True)
def get_total_points(context, player_in_game_name):
    return context['players_points'][player_in_game_name.lower()]['total_points']


@register.simple_tag(takes_context=True)
def get_position_chart_data(context, player_id):
    return context['chart']['data'][player_id]


@register.filter
def get_range(value):
    return range(value)
