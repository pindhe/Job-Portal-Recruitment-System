from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def nav_link(url_name, icon, label, request, *args):
    """Render a sidebar nav link with active-state highlighting."""
    try:
        url = reverse(url_name, args=args)
    except NoReverseMatch:
        url = "#"
    active = request.path == url
    base = "flex items-center gap-3 px-3 py-2.5 rounded-lg transition"
    if active:
        cls = f"{base} gradient-primary text-white font-semibold shadow"
    else:
        cls = f"{base} hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300"
    return mark_safe(
        f'<a href="{url}" class="{cls}"><i data-lucide="{icon}" class="w-5 h-5"></i> {label}</a>'
    )
