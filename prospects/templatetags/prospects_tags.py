from django import template
from ..utils import get_user_root_branch_ids

register = template.Library()


@register.filter
def has_root_prospect_perm(user):
    """Return True if user can view prospects on any Root/Digital Roots branch."""
    if not user or not user.is_authenticated:
        return False
    return bool(get_user_root_branch_ids(user, 'view_prospect'))
