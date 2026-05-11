from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from core.models import Branch
from courses.models import Course
from .models import StudentOffer, OfferRecipient, OfferNote
from .forms import StudentOfferForm, OfferRecipientForm, OfferNoteForm


# ============================================================
# StudentOffer
# ============================================================

class StudentOfferListView(LoginRequiredMixin, ListView):
    model = StudentOffer
    template_name = 'offers/studentoffer_list.html'
    context_object_name = 'offers'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(branch__name__icontains=q) |
                Q(course__master__name__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['courses'] = Course.objects.select_related('master').all()
        return context


class StudentOfferDetailView(LoginRequiredMixin, DetailView):
    model = StudentOffer
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'offers/studentoffer_detail.html'
    context_object_name = 'offer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['courses'] = Course.objects.select_related('master').all()
        return context


class StudentOfferCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentOffer
    form_class = StudentOfferForm
    template_name = 'offers/studentoffer_form.html'
    success_url = reverse_lazy('studentoffer-list')
    success_message = 'تم إنشاء العرض بنجاح.'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class StudentOfferUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentOffer
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = StudentOfferForm
    template_name = 'offers/studentoffer_form.html'
    success_url = reverse_lazy('studentoffer-list')
    success_message = 'تم تحديث العرض بنجاح.'


class StudentOfferDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = StudentOffer
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'offers/studentoffer_confirm_delete.html'
    success_url = reverse_lazy('studentoffer-list')
    success_message = 'تم حذف العرض بنجاح.'


@require_POST
def studentoffer_create_ajax(request):
    form = StudentOfferForm(request.POST)
    if form.is_valid():
        offer = form.save(commit=False)
        offer.created_by = request.user
        offer.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء العرض بنجاح', 'id': offer.id, 'slug': offer.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def studentoffer_update_ajax(request, pk):
    offer = get_object_or_404(StudentOffer, pk=pk)
    form = StudentOfferForm(request.POST, instance=offer)
    if form.is_valid():
        offer = form.save(commit=False)
        offer.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث العرض بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# OfferRecipient
# ============================================================

class OfferRecipientListView(LoginRequiredMixin, ListView):
    model = OfferRecipient
    template_name = 'offers/offerrecipient_list.html'
    context_object_name = 'recipients'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(offer__title__icontains=q) |
                Q(student__contact__first_name__icontains=q) |
                Q(student__contact__forth_name__icontains=q)
            )
        return queryset


class OfferRecipientDetailView(LoginRequiredMixin, DetailView):
    model = OfferRecipient
    template_name = 'offers/offerrecipient_detail.html'
    context_object_name = 'recipient'


class OfferRecipientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OfferRecipient
    form_class = OfferRecipientForm
    template_name = 'offers/offerrecipient_form.html'
    success_url = reverse_lazy('offerrecipient-list')
    success_message = 'تم إنشاء المستلم بنجاح.'


class OfferRecipientUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OfferRecipient
    form_class = OfferRecipientForm
    template_name = 'offers/offerrecipient_form.html'
    success_url = reverse_lazy('offerrecipient-list')
    success_message = 'تم تحديث المستلم بنجاح.'


class OfferRecipientDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = OfferRecipient
    template_name = 'offers/offerrecipient_confirm_delete.html'
    success_url = reverse_lazy('offerrecipient-list')
    success_message = 'تم حذف المستلم بنجاح.'


# ============================================================
# OfferNote
# ============================================================

class OfferNoteListView(LoginRequiredMixin, ListView):
    model = OfferNote
    template_name = 'offers/offernote_list.html'
    context_object_name = 'notes'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(note_text__icontains=q) |
                Q(offer__title__icontains=q)
            )
        return queryset


class OfferNoteDetailView(LoginRequiredMixin, DetailView):
    model = OfferNote
    template_name = 'offers/offernote_detail.html'
    context_object_name = 'note'


class OfferNoteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OfferNote
    form_class = OfferNoteForm
    template_name = 'offers/offernote_form.html'
    success_url = reverse_lazy('offernote-list')
    success_message = 'تم إضافة الملاحظة بنجاح.'

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class OfferNoteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OfferNote
    form_class = OfferNoteForm
    template_name = 'offers/offernote_form.html'
    success_url = reverse_lazy('offernote-list')
    success_message = 'تم تحديث الملاحظة بنجاح.'


class OfferNoteDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = OfferNote
    template_name = 'offers/offernote_confirm_delete.html'
    success_url = reverse_lazy('offernote-list')
    success_message = 'تم حذف الملاحظة بنجاح.'
