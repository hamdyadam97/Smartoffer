from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from core.models import Branch
from .models import ReportSnapshot
from .forms import ReportSnapshotForm
from .utils import generate_report_data


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context


class ReportSnapshotDetailView(LoginRequiredMixin, DetailView):
    model = ReportSnapshot
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'reports/reportsnapshot_detail.html'
    context_object_name = 'report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context


class ReportSnapshotCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ReportSnapshot
    form_class = ReportSnapshotForm
    template_name = 'reports/reportsnapshot_form.html'
    success_url = reverse_lazy('reportsnapshot-list')
    success_message = 'تم إنشاء التقرير بنجاح.'

    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        response = super().form_valid(form)
        # Generate report data automatically
        self.object.data_json = generate_report_data(
            self.object.report_type,
            self.object.branch,
            self.object.start_date,
            self.object.end_date
        )
        self.object.save(update_fields=['data_json'])
        return response


class ReportSnapshotUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ReportSnapshot
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = ReportSnapshotForm
    template_name = 'reports/reportsnapshot_form.html'
    success_url = reverse_lazy('reportsnapshot-list')
    success_message = 'تم تحديث التقرير بنجاح.'


class ReportSnapshotDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ReportSnapshot
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'reports/reportsnapshot_confirm_delete.html'
    success_url = reverse_lazy('reportsnapshot-list')
    success_message = 'تم حذف التقرير بنجاح.'


@require_POST
def reportsnapshot_create_ajax(request):
    form = ReportSnapshotForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.generated_by = request.user
        report.save()
        # Generate report data automatically
        report.data_json = generate_report_data(
            report.report_type,
            report.branch,
            report.start_date,
            report.end_date
        )
        report.save(update_fields=['data_json'])
        return JsonResponse({'success': True, 'message': 'تم إنشاء التقرير بنجاح', 'id': report.id, 'slug': report.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def reportsnapshot_update_ajax(request, pk):
    report = get_object_or_404(ReportSnapshot, pk=pk)
    form = ReportSnapshotForm(request.POST, instance=report)
    if form.is_valid():
        report = form.save(commit=False)
        report.save()
        # Regenerate data
        report.data_json = generate_report_data(
            report.report_type,
            report.branch,
            report.start_date,
            report.end_date
        )
        report.save(update_fields=['data_json'])
        return JsonResponse({'success': True, 'message': 'تم تحديث التقرير بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
