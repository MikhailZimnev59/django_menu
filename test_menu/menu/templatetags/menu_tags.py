from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from ..models import MenuItem

import logging

# Создание логгера
logger = logging.getLogger("file_logger")
logger.setLevel(logging.DEBUG)

# Создание обработчика (запись в файл)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

# Настройка формата
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(file_handler)

register = template.Library()

@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_path = request.path
    try:
        # Загружаем все пункты меню за один запрос
        menu_items = MenuItem.objects.filter(menu_name=menu_name).select_related('parent')
        tree = build_tree(menu_items)
        active_item = find_active_item(tree, current_path)
        if active_item:
            new_expand_menu(tree, active_item)
        html = new_render_menu(tree)
        return mark_safe(html)
    except MenuItem.DoesNotExist:
        return ''

@register.simple_tag(takes_context=True)
def draw_menu_all(context):
    request = context['request']
    current_path = request.path
    try:
        # Загружаем все пункты меню за один запрос
        menu_items = MenuItem.objects.select_related('parent')
        tree = build_tree(menu_items)
        active_item = find_active_item(tree, current_path)
        if active_item:
            new_expand_menu(tree, active_item)
        html = new_render_menu(tree)
        return mark_safe(html)
    except MenuItem.DoesNotExist:
        return ''

def build_tree(items, parent=None):
    """Строит древовидную структуру из плоского списка."""
    tree =  [
        {
            'item': item,
            'children': build_tree(items, item),
            'parent': parent,
        }
        for item in items if item.parent == parent
    ]
    return tree

def find_active_item(tree, current_path):
    """Находит активный пункт меню."""
    for node in tree:
        item = node['item']
        url = item.get_url()
        named_url = item.get_named_url()
        if url == current_path or named_url == current_path:
            return item
        active_child = find_active_item(node['children'], current_path)
        if active_child:
            return active_child
    return None

def rec_new_expand_menu(tree, active_item):
    # Находит всех родителей
    for node in tree:
        if node['item'] == active_item:
            node['expanded'] = True
            return True
        else:
            if node['children']:
                if rec_new_expand_menu(node['children'], active_item):
                    node['expanded'] = True
                    return True

def new_expand_menu(tree, active_item):

    rec_new_expand_menu(tree, active_item)

    for node in tree:
        if node['item'] == active_item:
            node['expanded'] = True


def new_render_menu(tree):
    """Рекурсивно генерирует HTML для меню."""
    html = '<ul>'
    for node in tree:
        item = node['item']
        url = item.get_url()
        css_class = 'active' if getattr(node, 'expanded', False) else ''
        html += f'<li class="{css_class}"><a href="{url}">{item.name}</a>'

        if node.get('expanded') and node['children']:
            html += new_render_menu(node['children'])
        html += '</li>'
    html += '</ul>'

    return html
