from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import AppNotification
from .forms import AppNotificationForm

# الإشعارات شخصية: كل موظف بيشوف ويعدل ويمسح إشعاراته هو بس، وأي إشعار تاني بيرجع 404.


class OwnNotificationsMixin(LoginRequiredMixin):
    def get_queryset(self):
        return AppNotification.objects.filter(user=self.request.user)


class AppNotificationListView(OwnNotificationsMixin, ListView):
    model = AppNotification
    template_name = 'notifications/appnotification_list.html'
    context_object_name = 'notifications'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(body__icontains=q)
            )
        return queryset


class AppNotificationDetailView(OwnNotificationsMixin, DetailView):
    model = AppNotification
    template_name = 'notifications/appnotification_detail.html'
    context_object_name = 'notification'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_read:
            obj.is_read = True
            obj.save()
        return super().get(request, *args, **kwargs)


class AppNotificationCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AppNotification
    form_class = AppNotificationForm
    template_name = 'notifications/appnotification_form.html'
    success_url = reverse_lazy('appnotification-list')
    success_message = 'تم إنشاء الإشعار بنجاح.'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AppNotificationUpdateView(OwnNotificationsMixin, SuccessMessageMixin, UpdateView):
    model = AppNotification
    form_class = AppNotificationForm
    template_name = 'notifications/appnotification_form.html'
    success_url = reverse_lazy('appnotification-list')
    success_message = 'تم تحديث الإشعار بنجاح.'


class AppNotificationDeleteView(OwnNotificationsMixin, SuccessMessageMixin, DeleteView):
    model = AppNotification
    template_name = 'notifications/appnotification_confirm_delete.html'
    success_url = reverse_lazy('appnotification-list')
    success_message = 'تم حذف الإشعار بنجاح.'
