from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def manage_menu(active_key=None):
    """Return content-management menu items grouped for the sidebar.

    Marks the active item and auto-opens the group that contains it.
    """
    from apps.dashboard.manage import manage_menu_items

    items = manage_menu_items()
    groups = []
    for item in items:
        item = {**item, "active": item["key"] == active_key}
        group = next((g for g in groups if g["name"] == item["group"]), None)
        if group is None:
            group = {"name": item["group"], "items": [], "open": False}
            groups.append(group)
        group["items"].append(item)
        if item["active"]:
            group["open"] = True
    return groups


@register.simple_tag
def nav_link(url_name, icon, label, request, i18n_key=""):
    """Render a sidebar nav link with active-state highlighting."""
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        url = "#"
    active = request.path == url
    base = "flex items-center gap-3 px-3 py-2.5 rounded-lg transition"
    if active:
        cls = f"{base} gradient-primary text-white font-semibold shadow"
    else:
        cls = f"{base} hover:bg-neutral-800 text-neutral-300 hover:text-white"
    attr = f' data-i18n="{i18n_key}"' if i18n_key else ""
    return mark_safe(
        f'<a href="{url}" class="{cls}"><i data-lucide="{icon}" class="w-5 h-5"></i> '
        f'<span{attr}>{label}</span></a>'
    )
