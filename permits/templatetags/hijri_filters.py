"""فلاتر التاريخ الهجري: نفس المكتبة اللي في قوالب برنامج المشاهد القديم ({% load hijri_filters %})
وبنفس شكل التاريخ بالظبط."""
from django import template

register = template.Library()

HIJRI_MONTHS = ['محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
                'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة']


def _to_hijri(value):
    from hijridate import Gregorian
    if not value:
        return None
    try:
        return Gregorian(value.year, value.month, value.day).to_hijri()
    except Exception:
        return None


@register.filter
def hijri(value):
    """{{ some_date|hijri }} -> '1448/01/05هـ'"""
    h = _to_hijri(value)
    return f'{h.year}/{h.month:02d}/{h.day:02d}هـ' if h else ''


@register.filter
def hijri_words(value):
    """{{ some_date|hijri_words }} -> '5 محرم 1448هـ'"""
    h = _to_hijri(value)
    return f'{h.day} {HIJRI_MONTHS[h.month - 1]} {h.year}هـ' if h else ''
