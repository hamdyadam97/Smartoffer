from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class BranchPermissionMixin(LoginRequiredMixin):
    """
    Mixin that:
    1. Requires login.
    2. Optionally checks a permission on a specific branch (via self.branch).
    3. Provides helper to filter querysets by accessible branches.
    """
    required_perm = None   # e.g. 'view_student'
    branch_field = None    # e.g. 'branch' or 'course__master__branch'

    def get_branch(self):
        """Override to return the branch to check permission against.
        Default: user's primary branch, or branch from GET param.
        """
        branch_id = self.request.GET.get('branch')
        if branch_id:
            from core.models import Branch
            return Branch.objects.filter(pk=branch_id).first()
        return self.request.user.branch

    def dispatch(self, request, *args, **kwargs):
        if self.required_perm and not request.user.is_superuser:
            branch = self.get_branch()
            if not request.user.has_perm(self.required_perm, branch=branch):
                raise PermissionDenied('غير مسموح لك دخول هنا')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        # If the model has a direct branch field, filter by it.
        if self.branch_field:
            accessible_ids = [b.pk for b in user.get_accessible_branches()]
            filters = {self.branch_field + '__in': accessible_ids}
            qs = qs.filter(**filters)
        return qs


def filter_by_branch(qs, user, branch_path='branch'):
    """Utility to filter any queryset by user's accessible branches."""
    if user.is_superuser:
        return qs
    accessible_ids = [b.pk for b in user.get_accessible_branches()]
    filters = {branch_path + '__in': accessible_ids}
    return qs.filter(**filters)
