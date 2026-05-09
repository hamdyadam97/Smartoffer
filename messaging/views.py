from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import InternalMessage
from .forms import InternalMessageForm


class InternalMessageListView(LoginRequiredMixin, ListView):
    model = InternalMessage
    template_name = 'messaging/internalmessage_list.html'
    context_object_name = 'messages_list'
    paginate_by = 25

    def get_queryset(self):
        queryset = InternalMessage.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        )
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(subject__icontains=q) |
                Q(body__icontains=q) |
                Q(sender__first_name__icontains=q) |
                Q(recipient__first_name__icontains=q)
            )
        return queryset


class InternalMessageDetailView(LoginRequiredMixin, DetailView):
    model = InternalMessage
    template_name = 'messaging/internalmessage_detail.html'
    context_object_name = 'message_obj'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.recipient == request.user and not obj.is_read:
            obj.is_read = True
            obj.save()
        return super().get(request, *args, **kwargs)


class InternalMessageCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = InternalMessage
    form_class = InternalMessageForm
    template_name = 'messaging/internalmessage_form.html'
    success_url = reverse_lazy('internalmessage-list')
    success_message = 'تم إرسال الرسالة بنجاح.'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)


class InternalMessageUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = InternalMessage
    form_class = InternalMessageForm
    template_name = 'messaging/internalmessage_form.html'
    success_url = reverse_lazy('internalmessage-list')
    success_message = 'تم تحديث الرسالة بنجاح.'


class InternalMessageDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = InternalMessage
    template_name = 'messaging/internalmessage_confirm_delete.html'
    success_url = reverse_lazy('internalmessage-list')
    success_message = 'تم حذف الرسالة بنجاح.'
