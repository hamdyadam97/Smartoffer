from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import ReportSnapshot
from .forms import ReportSnapshotForm


class ReportSnapshotListView(LoginRequiredMixin, ListView):
    model = ReportSnapshot
    template_name = 'reports/reportsnapshot_list.html'
    context_object_name = 'reports'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(report_type__icontains=q) |
                Q(period__icontains=q) |
                Q(branch__name__icontains=q)
            )
        return queryset


class ReportSnapshotDetailView(LoginRequiredMixin, DetailView):
    model = ReportSnapshot
    template_name = 'reports/reportsnapshot_detail.html'
    context_object_name = 'report'


class ReportSnapshotCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ReportSnapshot
    form_class = ReportSnapshotForm
    template_name = 'reports/reportsnapshot_form.html'
    success_url = reverse_lazy('reportsnapshot-list')
    success_message = 'تم إنشاء التقرير بنجاح.'

    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        return super().form_valid(form)


class ReportSnapshotUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ReportSnapshot
    form_class = ReportSnapshotForm
    template_name = 'reports/reportsnapshot_form.html'
    success_url = reverse_lazy('reportsnapshot-list')
    success_message = 'تم تحديث التقرير بنجاح.'


class ReportSnapshotDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ReportSnapshot
    template_name = 'reports/reportsnapshot_confirm_delete.html'
    success_url = reverse_lazy('reportsnapshot-list')
    success_message = 'تم حذف التقرير بنجاح.'
