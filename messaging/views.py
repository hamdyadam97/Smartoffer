from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import InternalMessage
from .forms import InternalMessageForm

# الرسائل شخصية: أي موظف مسجل دخول يقدر يبعت، وكل واحد بيشوف رسايله بس (مرسل أو مستلم)،
# والتعديل والحذف للمرسل بس. أي رسالة تانية بترجع 404.


class OwnMessagesMixin(LoginRequiredMixin):
    def get_queryset(self):
        user = self.request.user
        return InternalMessage.objects.filter(Q(sender=user) | Q(recipient=user))


class SentMessagesMixin(LoginRequiredMixin):
    def get_queryset(self):
        return InternalMessage.objects.filter(sender=self.request.user)


class InternalMessageListView(OwnMessagesMixin, ListView):
    model = InternalMessage
    template_name = 'messaging/internalmessage_list.html'
    context_object_name = 'messages_list'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('sender', 'recipient')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(subject__icontains=q) |
                Q(body__icontains=q) |
                Q(sender__first_name__icontains=q) |
                Q(recipient__first_name__icontains=q)
            )
        return queryset


class InternalMessageDetailView(OwnMessagesMixin, DetailView):
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


class InternalMessageUpdateView(SentMessagesMixin, SuccessMessageMixin, UpdateView):
    model = InternalMessage
    form_class = InternalMessageForm
    template_name = 'messaging/internalmessage_form.html'
    success_url = reverse_lazy('internalmessage-list')
    success_message = 'تم تحديث الرسالة بنجاح.'


class InternalMessageDeleteView(SentMessagesMixin, SuccessMessageMixin, DeleteView):
    model = InternalMessage
    template_name = 'messaging/internalmessage_confirm_delete.html'
    success_url = reverse_lazy('internalmessage-list')
    success_message = 'تم حذف الرسالة بنجاح.'
