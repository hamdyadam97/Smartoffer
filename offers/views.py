from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from core.models import Branch
from courses.models import Course
from .models import StudentOffer, OfferRecipient, OfferNote
from .forms import StudentOfferForm, OfferRecipientForm, OfferNoteForm


def _prepare_arabic(text):
    """Reshape and reverse Arabic text for ReportLab LTR rendering."""
    if not text:
        return ''
    import arabic_reshaper
    reshaped = arabic_reshaper.reshape(str(text))
    return reshaped[::-1]


def export_studentoffer_pdf(request, slug):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    import os

    offer = get_object_or_404(StudentOffer, slug=slug)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="offer-{offer.slug}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Register Cairo font for Arabic support
    font_path = os.path.join('static', 'fonts', 'Cairo-Regular.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Cairo', font_path))

    arabic_style = ParagraphStyle('Arabic', parent=styles['Normal'], fontName='Cairo', fontSize=11, leading=16, alignment=2)
    title_style = ParagraphStyle('ArabicTitle', parent=styles['Title'], fontName='Cairo', fontSize=20, leading=28, alignment=1)
    label_style = ParagraphStyle('ArabicLabel', parent=styles['Normal'], fontName='Cairo', fontSize=10, leading=14, alignment=2, textColor=colors.HexColor('#64748B'))
    signature_style = ParagraphStyle('ArabicSig', parent=styles['Normal'], fontName='Cairo', fontSize=12, leading=18, alignment=1)

    # Title
    elements.append(Paragraph(_prepare_arabic('عرض طالب'), title_style))
    elements.append(Spacer(1, 0.8*cm))

    # Offer details table
    data = [
        [Paragraph(_prepare_arabic('عنوان العرض'), label_style), Paragraph(_prepare_arabic(offer.title), arabic_style)],
        [Paragraph(_prepare_arabic('الفرع'), label_style), Paragraph(_prepare_arabic(str(offer.branch)), arabic_style)],
        [Paragraph(_prepare_arabic('الدورة / الدبلوم'), label_style), Paragraph(_prepare_arabic(str(offer.course) if offer.course else '-'), arabic_style)],
        [Paragraph(_prepare_arabic('المستوى المستهدف'), label_style), Paragraph(_prepare_arabic(offer.get_target_level_display()), arabic_style)],
        [Paragraph(_prepare_arabic('الحالة'), label_style), Paragraph(_prepare_arabic(offer.get_status_display()), arabic_style)],
        [Paragraph(_prepare_arabic('تاريخ الإنشاء'), label_style), Paragraph(_prepare_arabic(offer.created_at.strftime('%Y-%m-%d')), arabic_style)],
    ]

    if offer.scheduled_at:
        data.append([Paragraph(_prepare_arabic('موعد الإرسال المجدول'), label_style), Paragraph(_prepare_arabic(offer.scheduled_at.strftime('%Y-%m-%d %H:%M')), arabic_style)])
    if offer.sent_at:
        data.append([Paragraph(_prepare_arabic('تاريخ الإرسال الفعلي'), label_style), Paragraph(_prepare_arabic(offer.sent_at.strftime('%Y-%m-%d %H:%M')), arabic_style)])

    table = Table(data, colWidths=[doc.width*0.35, doc.width*0.65])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#334155')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Cairo'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.8*cm))

    # Content
    elements.append(Paragraph(_prepare_arabic('تفاصيل العرض / المحتوى:'), label_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(_prepare_arabic(offer.content), arabic_style))
    elements.append(Spacer(1, 1.2*cm))

    # Signature section
    sig_data = [
        [Paragraph(_prepare_arabic('التوقيع'), label_style)],
        [Paragraph(_prepare_arabic('___________________________'), signature_style)],
        [Paragraph(_prepare_arabic(f"{offer.created_by.get_full_name() or offer.created_by.email}"), signature_style)],
        [Paragraph(_prepare_arabic(offer.created_at.strftime('%Y-%m-%d')), signature_style)],
    ]
    sig_table = Table(sig_data, colWidths=[doc.width])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Cairo'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    return response


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
