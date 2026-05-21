from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods

from core.models import Branch
from courses.models import Course
from students.models import Student
from .models import StudentOffer, OfferRecipient, OfferNote
from .forms import StudentOfferForm, OfferRecipientForm, OfferRecipientAddForm, OfferNoteForm
from .whatsapp import send_whatsapp_message


def _prepare_arabic(text):
    """Prepare Arabic text for ReportLab PDF.
    Uses BiDi only (no reshaper) to avoid missing glyphs in some fonts.
    Also escapes XML special chars so ReportLab Paragraph doesn't break."""
    if not text:
        return ''
    try:
        from bidi.algorithm import get_display
        bidi_text = get_display(str(text))
        # Escape XML special chars for ReportLab Paragraph safety
        bidi_text = bidi_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return bidi_text
    except Exception:
        # Fallback: just escape XML chars and return as-is
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def export_studentoffer_pdf(request, slug):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    import os

    offer = get_object_or_404(StudentOffer, slug=slug)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="offer-{offer.slug}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Register Cairo font for Arabic support
    from django.contrib.staticfiles.finders import find
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    font_path = find('fonts/Cairo-Regular.ttf')
    if font_path and os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Cairo', font_path))
        registerFontFamily('Cairo', normal='Cairo', bold='Cairo', italic='Cairo', boldItalic='Cairo')
    else:
        # Fallback to direct path
        font_path = os.path.join('static', 'fonts', 'Cairo-Regular.ttf')
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Cairo', font_path))
            registerFontFamily('Cairo', normal='Cairo', bold='Cairo', italic='Cairo', boldItalic='Cairo')
        else:
            print('[PDF Warning] Cairo font not found. Arabic text may not render correctly.')

    arabic_style = ParagraphStyle('Arabic', parent=styles['Normal'], fontName='Cairo', fontSize=11, leading=16, alignment=TA_RIGHT)
    title_style = ParagraphStyle('ArabicTitle', parent=styles['Title'], fontName='Cairo', fontSize=20, leading=28, alignment=TA_CENTER)
    label_style = ParagraphStyle('ArabicLabel', parent=styles['Normal'], fontName='Cairo', fontSize=10, leading=14, alignment=TA_RIGHT, textColor=colors.HexColor('#64748B'))
    signature_style = ParagraphStyle('ArabicSig', parent=styles['Normal'], fontName='Cairo', fontSize=12, leading=18, alignment=TA_CENTER)
    header_style = ParagraphStyle('ArabicHeader', parent=styles['Normal'], fontName='Cairo', fontSize=14, leading=20, alignment=TA_CENTER)
    header_small_style = ParagraphStyle('ArabicHeaderSmall', parent=styles['Normal'], fontName='Cairo', fontSize=10, leading=14, alignment=TA_CENTER, textColor=colors.HexColor('#64748B'))

    # Branch Header
    branch = offer.branch
    if branch:
        elements.append(Paragraph(_prepare_arabic(branch.name), header_style))
        if branch.sub_name:
            elements.append(Paragraph(_prepare_arabic(branch.sub_name), header_small_style))
        if branch.address:
            elements.append(Paragraph(_prepare_arabic(branch.address), header_small_style))
        contact_parts = []
        if branch.phone1:
            contact_parts.append(branch.phone1)
        if branch.phone2:
            contact_parts.append(branch.phone2)
        if branch.mobile:
            contact_parts.append(branch.mobile)
        if contact_parts:
            elements.append(Paragraph(_prepare_arabic(' - '.join(contact_parts)), header_small_style))
        if branch.email:
            elements.append(Paragraph(_prepare_arabic(branch.email), header_small_style))
        elements.append(Spacer(1, 0.6*cm))

    # Title
    elements.append(Paragraph(_prepare_arabic('عرض طالب'), title_style))
    elements.append(Spacer(1, 0.8*cm))

    # Student recipient info (single student)
    recipient = None
    recipient_pk = request.GET.get('recipient')
    if recipient_pk:
        try:
            recipient = offer.recipients.select_related('student__contact').get(pk=recipient_pk)
        except OfferRecipient.DoesNotExist:
            pass
    if not recipient:
        recipient = offer.recipients.select_related('student__contact').first()

    if recipient:
        student = recipient.student
        contact = student.contact
        name = contact.get_full_name() if contact else student.get_full_name()
        phone = contact.mobile if contact else ''
        elements.append(Paragraph(_prepare_arabic('بيانات الطالب:'), label_style))
        elements.append(Spacer(1, 0.3*cm))
        student_rows = [
            [Paragraph(_prepare_arabic(phone), arabic_style), Paragraph(_prepare_arabic('رقم الهاتف'), label_style)],
            [Paragraph(_prepare_arabic(name), arabic_style), Paragraph(_prepare_arabic('الاسم'), label_style)],
        ]
        student_table = Table(student_rows, colWidths=[doc.width*0.65, doc.width*0.35])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#334155')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Cairo'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 0.8*cm))

    # Offer details table - REVERSED columns for RTL feel in LTR document
    data = [
        [Paragraph(_prepare_arabic(offer.title), arabic_style), Paragraph(_prepare_arabic('عنوان العرض'), label_style)],
        [Paragraph(_prepare_arabic(str(offer.branch)), arabic_style), Paragraph(_prepare_arabic('الفرع'), label_style)],
        [Paragraph(_prepare_arabic(str(offer.course) if offer.course else '-'), arabic_style), Paragraph(_prepare_arabic('الدورة / الدبلوم'), label_style)],
        [Paragraph(_prepare_arabic(f'{offer.price} ريال'), arabic_style), Paragraph(_prepare_arabic('السعر'), label_style)],
        [Paragraph(_prepare_arabic(offer.price_description or '-'), arabic_style), Paragraph(_prepare_arabic('وصف السعر'), label_style)],
        [Paragraph(_prepare_arabic(offer.get_status_display()), arabic_style), Paragraph(_prepare_arabic('الحالة'), label_style)],
        [Paragraph(_prepare_arabic(offer.created_at.strftime('%Y-%m-%d')), arabic_style), Paragraph(_prepare_arabic('تاريخ الإنشاء'), label_style)],
    ]

    if offer.start_date:
        data.append([Paragraph(_prepare_arabic(offer.start_date.strftime('%Y-%m-%d')), arabic_style), Paragraph(_prepare_arabic('تاريخ بداية العرض'), label_style)])
    if offer.end_date:
        data.append([Paragraph(_prepare_arabic(offer.end_date.strftime('%Y-%m-%d')), arabic_style), Paragraph(_prepare_arabic('تاريخ نهاية العرض'), label_style)])
    if offer.scheduled_at:
        data.append([Paragraph(_prepare_arabic(offer.scheduled_at.strftime('%Y-%m-%d %H:%M')), arabic_style), Paragraph(_prepare_arabic('موعد الإرسال المجدول'), label_style)])
    if offer.sent_at:
        data.append([Paragraph(_prepare_arabic(offer.sent_at.strftime('%Y-%m-%d %H:%M')), arabic_style), Paragraph(_prepare_arabic('تاريخ الإرسال الفعلي'), label_style)])

    # Reversed: value column (0) wider on the LEFT, label column (1) narrower on the RIGHT
    table = Table(data, colWidths=[doc.width*0.65, doc.width*0.35])
    table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#334155')),
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
# Send Offer to Single Recipient
# ============================================================

@login_required
def send_offer_to_recipient(request, slug, recipient_pk):
    """Send an offer to a single recipient via their preferred channel."""
    offer = get_object_or_404(StudentOffer, slug=slug)
    recipient = get_object_or_404(OfferRecipient, pk=recipient_pk, offer=offer)

    channel = recipient.channel
    student = recipient.student
    contact = getattr(student, 'contact', None)
    body = f"{offer.title}\n\n{offer.content}"

    if channel == 'whatsapp':
        phone = contact.mobile if contact else ''
        if not phone:
            messages.error(request, 'لا يوجد رقم محمول مسجل لهذا الطالب.')
            return redirect('studentoffer-detail', slug=slug)
        result = send_whatsapp_message(phone, body)
        if result.get('success'):
            messages.success(request, f'تم إرسال العرض عبر واتساب إلى {student.get_full_name()}.')
            recipient.status = 'مرسل'
            recipient.save()
        else:
            messages.error(request, f'فشل إرسال واتساب: {result.get("error", "خطأ غير معروف")}')
    elif channel == 'email':
        messages.warning(request, 'قناة البريد الإلكتروني غير مفعلة حالياً (لا يوجد إيميل مسجل للطالب).')
    elif channel == 'app':
        messages.warning(request, 'قناة إشعار التطبيق غير مفعلة حالياً.')
    else:
        messages.error(request, 'قناة إرسال غير معروفة.')

    return redirect('studentoffer-detail', slug=slug)


@login_required
def add_recipient_to_offer(request, slug):
    """Add a recipient directly to a specific offer (HTML form fallback)."""
    offer = get_object_or_404(StudentOffer, slug=slug)
    if request.method == 'POST':
        form = OfferRecipientAddForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.offer = offer
            try:
                recipient.save()
                messages.success(request, f'تم إضافة المستلم {recipient.student} بنجاح.')
                return redirect('studentoffer-detail', slug=slug)
            except Exception as e:
                messages.error(request, f'خطأ أثناء الحفظ: {str(e)}')
    else:
        form = OfferRecipientAddForm()
    return render(request, 'offers/add_recipient_form.html', {'form': form, 'offer': offer})


@require_POST
@login_required
def studentoffer_add_recipient_ajax(request, slug):
    """AJAX endpoint to add a recipient to an offer from a modal."""
    offer = get_object_or_404(StudentOffer, slug=slug)
    form = OfferRecipientAddForm(request.POST)
    if form.is_valid():
        recipient = form.save(commit=False)
        recipient.offer = offer
        try:
            recipient.save()
            return JsonResponse({
                'success': True,
                'message': f'تم إضافة المستلم {recipient.student} بنجاح.',
                'id': recipient.id,
                'student_name': str(recipient.student),
                'channel': recipient.get_channel_display(),
                'status': recipient.get_status_display(),
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def send_offer_to_all(request, slug):
    """Send the offer to all recipients via their preferred channels."""
    offer = get_object_or_404(StudentOffer, slug=slug)
    recipients = offer.recipients.select_related('student__contact').all()
    if not recipients:
        messages.warning(request, 'لا يوجد مستلمون لهذا العرض. أضف مستلمين أولاً.')
        return redirect('studentoffer-detail', slug=slug)

    sent_count = 0
    failed_count = 0
    body = f"{offer.title}\n\n{offer.content}"

    for recipient in recipients:
        channel = recipient.channel
        student = recipient.student
        contact = getattr(student, 'contact', None)

        if channel == 'whatsapp':
            phone = contact.mobile if contact else ''
            if phone:
                result = send_whatsapp_message(phone, body)
                if result.get('success'):
                    recipient.status = 'مرسل'
                    recipient.save()
                    sent_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        elif channel == 'email':
            failed_count += 1
        elif channel == 'app':
            failed_count += 1
        else:
            failed_count += 1

    if sent_count:
        messages.success(request, f'تم الإرسال بنجاح إلى {sent_count} مستلم.')
        offer.status = 'مرسلة'
        offer.sent_at = timezone.now()
        offer.save()
    if failed_count:
        messages.warning(
            request,
            f'فشل الإرسال إلى {failed_count} مستلم. '
            f'تأكد من وجود أرقام واتساب مسجلة أو تفعيل قنوات الإيميل/التطبيق.'
        )

    return redirect('studentoffer-detail', slug=slug)


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
        context['all_students'] = Student.objects.select_related('contact').all()
        context['all_offers'] = StudentOffer.objects.select_related('branch', 'course__master').all()
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
