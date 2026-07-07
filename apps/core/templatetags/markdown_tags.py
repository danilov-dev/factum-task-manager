import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    """Рендерит Markdown в HTML."""
    if not text:
        return ''
    return mark_safe(md.markdown(
        text,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'pymdownx.tilde',        # ← ~~зачёркивание~~
            'pymdownx.mark',         # ← ==подсветка==
            'pymdownx.tasklist',     # ← - [ ] чекбоксы
            'pymdownx.superfences',  # ← улучшенные блоки кода
        ],
        extension_configs={
            'pymdownx.tasklist': {
                'custom_checkbox': True,
            },
        },
    ))

@register.filter()
@stringfilter
def markdown_to_html(value):
    # Конвертируем Markdown в HTML, включая расширения таблиц и подсветку кода
    html_content = markdown.markdown(value, extensions=['extra', 'codehilite'])
    return mark_safe(html_content)