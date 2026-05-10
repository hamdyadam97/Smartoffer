from django import template

register = template.Library()


@register.filter
def has_perm(user, perm_codename):
    """Check if user has a specific permission."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.has_perm(perm_codename)


@register.filter
def has_any_perm(user, perm_codenames):
    """Check if user has any of the given permissions (comma-separated)."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    for codename in perm_codenames.split(','):
        if user.has_perm(codename.strip()):
            return True
    return False
