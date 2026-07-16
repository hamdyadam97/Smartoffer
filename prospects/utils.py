from core.models import Branch


ROOT_COMPANY_NAME_MATCH = 'جذور'


def is_root_branch(branch):
    """Return True if the branch belongs to Root/Digital Roots company."""
    if not branch:
        return False
    company_name = getattr(branch.company, 'name', '') or ''
    return ROOT_COMPANY_NAME_MATCH in company_name


def get_root_branch_queryset():
    """Return all branches belonging to Root/Digital Roots company."""
    return Branch.objects.filter(company__name__icontains=ROOT_COMPANY_NAME_MATCH)


def get_user_root_branch_ids(user, perm='view_prospect'):
    """Return branch IDs the user can access for prospects (Root company only)."""
    if user.is_executive():
        return list(get_root_branch_queryset().values_list('pk', flat=True))
    branches = user.get_branches_for_perm(perm)
    return [b.pk for b in branches if is_root_branch(b)]
