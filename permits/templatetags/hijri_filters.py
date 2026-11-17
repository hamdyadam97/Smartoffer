"""فلاتر التاريخ الهجري: نفس اسم المكتبة اللي في قوالب برنامج المشاهد القديم ({% load hijri_filters %})."""
from datetime import date, datetime

from django import template

register = template.Library()


def _to_hijri(value):
    from hijridate import Gregorian
    if isinstance(value, datetime):
        value = value.date()
    if not isinstance(value, date):
        return None
    try:
        return Gregorian(value.year, value.month, value.day).to_hijri()
    except (ValueError, OverflowError):
        return None


@register.filter
def hijri(value, fmt='Y/m/d'):
    """{{ program.start_date|hijri }} -> 1448/06/07 (وممكن تحدد الشكل: |hijri:"d/m/Y")."""
    h = _to_hijri(value)
    if h is None:
        return ''
    return (fmt.replace('Y', str(h.year)).replace('m', f'{h.month:02d}').replace('d', f'{h.day:02d}'))


@register.filter
def hijri_year(value):
    h = _to_hijri(value)
    return h.year if h else ''
