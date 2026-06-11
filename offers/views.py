from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import BranchPermissionMixin, filter_by_branch
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
from .forms import StudentOfferForm, OfferRecipientForm, OfferRecipientAddForm, OfferNoteForm, QuickOfferForm
from .whatsapp import send_whatsapp_message


def _prepare_arabic(text):
    """Reshape and apply BiDi algorithm for Arabic text in ReportLab PDF.
    Also escapes XML special chars so ReportLab Paragraph doesn't break."""
    if not text:
        return ''
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        # Escape XML special chars for ReportLab Paragraph safety
        bidi_text = bidi_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return bidi_text
    except Exception:
        # Fallback: just escape XML chars and return as-is
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def export_studentoffer_pdf(request, slug):
    """Export offer as a professional one-page PDF with logo and modern design."""
    from io import BytesIO
    import base64
    import os

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT

    offer = get_object_or_404(StudentOffer, slug=slug)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="offer-{offer.slug}.pdf"'

    # Compact margins to fit everything on one page
    doc = SimpleDocTemplate(
        response, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.2*cm, bottomMargin=1.2*cm
    )
    elements = []
    styles = getSampleStyleSheet()

    # Register Arabic font
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    arial_path = r'C:\Windows\Fonts\arial.ttf'
    font_name = 'ArialArabic'
    if os.path.exists(arial_path):
        pdfmetrics.registerFont(TTFont(font_name, arial_path))
        registerFontFamily(font_name, normal=font_name, bold=font_name, italic=font_name, boldItalic=font_name)
    else:
        from django.contrib.staticfiles.finders import find
        font_path = find('fonts/Cairo-Regular.ttf') or os.path.join('static', 'fonts', 'Cairo-Regular.ttf')
        if font_path and os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            registerFontFamily(font_name, normal=font_name, bold=font_name, italic=font_name, boldItalic=font_name)
        else:
            font_name = 'Helvetica'

    # Accent color
    PRIMARY = colors.HexColor('#1e40af')
    SECONDARY = colors.HexColor('#64748B')
    LIGHT_BG = colors.HexColor('#f8fafc')
    BORDER = colors.HexColor('#e2e8f0')

    # Styles
    arabic_style = ParagraphStyle('Arabic', parent=styles['Normal'], fontName=font_name, fontSize=10, leading=14, alignment=TA_RIGHT)
    title_style = ParagraphStyle('ArabicTitle', parent=styles['Title'], fontName=font_name, fontSize=18, leading=24, alignment=TA_CENTER, textColor=PRIMARY)
    label_style = ParagraphStyle('ArabicLabel', parent=styles['Normal'], fontName=font_name, fontSize=9, leading=12, alignment=TA_RIGHT, textColor=SECONDARY)
    price_style = ParagraphStyle('ArabicPrice', parent=styles['Normal'], fontName=font_name, fontSize=14, leading=20, alignment=TA_CENTER, textColor=PRIMARY)
    sig_style = ParagraphStyle('ArabicSig', parent=styles['Normal'], fontName=font_name, fontSize=10, leading=14, alignment=TA_CENTER)
    small_style = ParagraphStyle('ArabicSmall', parent=styles['Normal'], fontName=font_name, fontSize=8, leading=11, alignment=TA_CENTER, textColor=SECONDARY)
    content_style = ParagraphStyle('ArabicContent', parent=styles['Normal'], fontName=font_name, fontSize=10, leading=15, alignment=TA_RIGHT)

    branch = offer.branch
    company = branch.company if branch else None

    # ========== HEADER WITH LOGO ==========
    header_parts = []
    logo_img = None

    # Try branch logo first, then company logo
    logo_path = None
    if branch and branch.logo:
        logo_path = branch.logo.path
    elif company and company.logo:
        logo_path = company.logo.path
    if logo_path:
        try:
            logo_img = Image(logo_path, width=2.2*cm, height=2.2*cm)
        except Exception:
            logo_img = None

    # Header text lines
    header_text_lines = []
    if company:
        header_text_lines.append(_prepare_arabic(company.name))
    if branch:
        header_text_lines.append(_prepare_arabic(branch.name))
        if branch.address:
            header_text_lines.append(_prepare_arabic(branch.address))
        contacts = []
        if branch.mobile:
            contacts.append(branch.mobile)
        if branch.phone1:
            contacts.append(branch.phone1)
        if contacts:
            header_text_lines.append(_prepare_arabic(' / '.join(contacts)))
        if branch.email:
            header_text_lines.append(_prepare_arabic(branch.email))

    header_text = '<br/>'.join(header_text_lines) if header_text_lines else ''

    if logo_img and header_text:
        header_table = Table(
            [[logo_img, Paragraph(header_text, small_style)]],
            colWidths=[doc.width*0.18, doc.width*0.82]
        )
    elif logo_img:
        header_table = Table([[logo_img]], colWidths=[doc.width])
    elif header_text:
        header_table = Table([[Paragraph(header_text, small_style)]], colWidths=[doc.width])
    else:
        header_table = None

    if header_table:
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*cm))

    # Decorative line
    elements.append(Table([['']], colWidths=[doc.width], rowHeights=[2], style=TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ])))
    elements.append(Spacer(1, 0.3*cm))

    # ========== TITLE ==========
    elements.append(Paragraph(_prepare_arabic('عرض سعر'), title_style))
    elements.append(Spacer(1, 0.3*cm))

    # ========== RECIPIENT INFO ==========
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
        contact = getattr(student, 'contact', None)
        if student:
            r_name = contact.get_full_name() if contact else student.get_full_name()
            r_phone = contact.mobile if contact else ''
            r_email = contact.email if contact else ''
        else:
            r_name = recipient.contact_name or 'مستلم سريع'
            r_phone = recipient.contact_phone
            r_email = recipient.contact_email

        recipient_data = [
            [Paragraph(_prepare_arabic(r_name), arabic_style), Paragraph(_prepare_arabic('المستلم'), label_style)],
            [Paragraph(_prepare_arabic(r_phone or '-'), arabic_style), Paragraph(_prepare_arabic('الجوال'), label_style)],
        ]
        if r_email:
            recipient_data.append([Paragraph(_prepare_arabic(r_email), arabic_style), Paragraph(_prepare_arabic('البريد'), label_style)])
        st = Table(recipient_data, colWidths=[doc.width*0.72, doc.width*0.28])
        st.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, -1), LIGHT_BG),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(st)
        elements.append(Spacer(1, 0.3*cm))

    # ========== OFFER DETAILS ==========
    detail_rows = [
        [Paragraph(_prepare_arabic(offer.title), arabic_style), Paragraph(_prepare_arabic('عنوان العرض'), label_style)],
        [Paragraph(_prepare_arabic(str(offer.branch)), arabic_style), Paragraph(_prepare_arabic('الفرع'), label_style)],
        [Paragraph(_prepare_arabic(str(offer.course) if offer.course else '-'), arabic_style), Paragraph(_prepare_arabic('الدورة'), label_style)],
        [Paragraph(_prepare_arabic(offer.created_at.strftime('%Y-%m-%d')), arabic_style), Paragraph(_prepare_arabic('تاريخ العرض'), label_style)],
        [Paragraph(_prepare_arabic(offer.get_status_display()), arabic_style), Paragraph(_prepare_arabic('الحالة'), label_style)],
    ]

    if offer.start_date:
        detail_rows.append([Paragraph(_prepare_arabic(offer.start_date.strftime('%Y-%m-%d')), arabic_style), Paragraph(_prepare_arabic('تاريخ البداية'), label_style)])
    if offer.end_date:
        detail_rows.append([Paragraph(_prepare_arabic(offer.end_date.strftime('%Y-%m-%d')), arabic_style), Paragraph(_prepare_arabic('تاريخ النهاية'), label_style)])

    dt = Table(detail_rows, colWidths=[doc.width*0.72, doc.width*0.28])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, -1), LIGHT_BG),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(dt)
    elements.append(Spacer(1, 0.3*cm))

    # ========== PRICE HIGHLIGHT ==========
    price_text = f'{offer.price} ريال'
    if offer.price_description:
        price_text += f'<br/><font size="9" color="#64748B">{offer.price_description}</font>'

    price_box = Table(
        [[Paragraph(_prepare_arabic(price_text), price_style)]],
        colWidths=[doc.width]
    )
    price_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(price_box)
    elements.append(Spacer(1, 0.3*cm))

    # ========== CONTENT BOX ==========
    elements.append(Paragraph(_prepare_arabic('وصف العرض'), label_style))
    content_box = Table(
        [[Paragraph(_prepare_arabic(offer.content or '-'), content_style)]],
        colWidths=[doc.width]
    )
    content_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#f59e0b')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(content_box)
    elements.append(Spacer(1, 0.4*cm))

    # ========== FOOTER / SIGNATURE ==========
    sig_elements = []

    # Branch signature image if available
    sig_path = branch.signature.path if branch and branch.signature else None
    sig_img = None
    if sig_path:
        try:
            sig_img = Image(sig_path, width=3*cm, height=1.5*cm)
        except Exception:
            sig_img = None

    if sig_img:
        sig_elements.append(sig_img)
        elements.append(sig_img)
        elements.append(Spacer(1, 0.1*cm))

    sig_row = [
        Paragraph(_prepare_arabic(f"التاريخ: {offer.created_at.strftime('%Y-%m-%d')}"), sig_style),
        Paragraph(_prepare_arabic('التوقيع: _________________'), sig_style),
    ]
    sig_table = Table([sig_row], colWidths=[doc.width*0.5, doc.width*0.5])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(sig_table)
    elements.append(Spacer(1, 0.2*cm))

    # Created by
    elements.append(Paragraph(_prepare_arabic(f"تم إعداد العرض بواسطة: {offer.created_by.get_full_name() or offer.created_by.email}"), small_style))

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

    # Determine recipient display name
    if student:
        recipient_name = student.get_full_name()
    else:
        recipient_name = recipient.contact_name or recipient.contact_phone or 'مستلم سريع'

    if channel == 'whatsapp':
        phone = contact.mobile if contact else recipient.contact_phone
        if not phone:
            messages.error(request, 'لا يوجد رقم محمول مسجل لهذا المستلم.')
            return redirect('studentoffer-detail', slug=slug)
        result = send_whatsapp_message(phone, body)
        if result.get('success'):
            messages.success(request, f'تم إرسال العرض عبر واتساب إلى {recipient_name}.')
            recipient.status = 'مرسل'
            recipient.save()
        else:
            messages.error(request, f'فشل إرسال واتساب: {result.get("error", "خطأ غير معروف")}')
    elif channel == 'email':
        email = contact.email if contact else recipient.contact_email
        if not email:
            messages.warning(request, 'لا يوجد بريد إلكتروني مسجل لهذا المستلم.')
        else:
            messages.info(request, f'تمت محاكاة إرسال الإيميل إلى {email} (قيد التطوير).')
            recipient.status = 'مرسل'
            recipient.save()
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
            name = str(recipient.student) if recipient.student else (recipient.contact_name or recipient.contact_phone or 'مستلم سريع')
            return JsonResponse({
                'success': True,
                'message': f'تم إضافة المستلم {name} بنجاح.',
                'id': recipient.id,
                'student_name': name,
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
            phone = contact.mobile if contact else recipient.contact_phone
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
            email = contact.email if contact else recipient.contact_email
            if email:
                # TODO: integrate real email backend
                recipient.status = 'مرسل'
                recipient.save()
                sent_count += 1
            else:
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
            f'تأكد من وجود أرقام واتساب أو بريد إلكتروني مسجل للمستلمين.'
        )

    return redirect('studentoffer-detail', slug=slug)


@require_POST
@login_required
def quick_offer_ajax(request):
    """AJAX endpoint to create a quick offer with a manual recipient in one step."""
    form = QuickOfferForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        offer = StudentOffer.objects.create(
            title=cd['title'],
            content=cd['content'],
            branch=cd['branch'],
            course=cd['course'],
            price=cd['price'],
            price_description=cd['price_description'],
            created_by=request.user,
            status='مسودة',
        )
        OfferRecipient.objects.create(
            offer=offer,
            student=None,
            contact_name=cd['contact_name'],
            contact_phone=cd['contact_phone'],
            contact_email=cd['contact_email'],
            channel=cd['channel'],
            status='مرسل',
        )
        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء العرض السريع وإضافة المستلم بنجاح.',
            'slug': offer.slug,
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# StudentOffer
# ============================================================

class StudentOfferListView(BranchPermissionMixin, ListView):
    model = StudentOffer
    template_name = 'offers/studentoffer_list.html'
    context_object_name = 'offers'
    paginate_by = 25
    required_perm = 'view_studentoffer'
    branch_field = 'branch'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_by_branch(queryset, self.request.user, self.branch_field)
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


class StudentOfferDetailView(BranchPermissionMixin, DetailView):
    model = StudentOffer
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'offers/studentoffer_detail.html'
    context_object_name = 'offer'
    required_perm = 'view_studentoffer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['courses'] = Course.objects.select_related('master').all()
        context['all_students'] = Student.objects.select_related('contact').all()
        context['all_offers'] = StudentOffer.objects.select_related('branch', 'course__master').all()
        return context


class StudentOfferCreateView(BranchPermissionMixin, SuccessMessageMixin, CreateView):
    model = StudentOffer
    form_class = StudentOfferForm
    template_name = 'offers/studentoffer_form.html'
    success_url = reverse_lazy('studentoffer-list')
    success_message = 'تم إنشاء العرض بنجاح.'
    required_perm = 'add_studentoffer'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class StudentOfferUpdateView(BranchPermissionMixin, SuccessMessageMixin, UpdateView):
    model = StudentOffer
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = StudentOfferForm
    template_name = 'offers/studentoffer_form.html'
    success_url = reverse_lazy('studentoffer-list')
    success_message = 'تم تحديث العرض بنجاح.'
    required_perm = 'change_studentoffer'


class StudentOfferDeleteView(BranchPermissionMixin, SuccessMessageMixin, DeleteView):
    model = StudentOffer
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'offers/studentoffer_confirm_delete.html'
    success_url = reverse_lazy('studentoffer-list')
    success_message = 'تم حذف العرض بنجاح.'
    required_perm = 'delete_studentoffer'


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

class OfferRecipientListView(BranchPermissionMixin, ListView):
    model = OfferRecipient
    template_name = 'offers/offerrecipient_list.html'
    context_object_name = 'recipients'
    paginate_by = 25
    required_perm = 'view_studentoffer'
    branch_field = 'offer__branch'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_by_branch(queryset, self.request.user, self.branch_field)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(offer__title__icontains=q) |
                Q(student__contact__first_name__icontains=q) |
                Q(student__contact__forth_name__icontains=q) |
                Q(contact_name__icontains=q) |
                Q(contact_phone__icontains=q)
            )
        return queryset


class OfferRecipientDetailView(BranchPermissionMixin, DetailView):
    model = OfferRecipient
    template_name = 'offers/offerrecipient_detail.html'
    context_object_name = 'recipient'
    required_perm = 'view_studentoffer'


class OfferRecipientCreateView(BranchPermissionMixin, SuccessMessageMixin, CreateView):
    model = OfferRecipient
    form_class = OfferRecipientForm
    template_name = 'offers/offerrecipient_form.html'
    success_url = reverse_lazy('offerrecipient-list')
    success_message = 'تم إنشاء المستلم بنجاح.'
    required_perm = 'add_studentoffer'


class OfferRecipientUpdateView(BranchPermissionMixin, SuccessMessageMixin, UpdateView):
    model = OfferRecipient
    form_class = OfferRecipientForm
    template_name = 'offers/offerrecipient_form.html'
    success_url = reverse_lazy('offerrecipient-list')
    success_message = 'تم تحديث المستلم بنجاح.'
    required_perm = 'change_studentoffer'


class OfferRecipientDeleteView(BranchPermissionMixin, SuccessMessageMixin, DeleteView):
    model = OfferRecipient
    template_name = 'offers/offerrecipient_confirm_delete.html'
    success_url = reverse_lazy('offerrecipient-list')
    success_message = 'تم حذف المستلم بنجاح.'
    required_perm = 'delete_studentoffer'


# ============================================================
# OfferNote
# ============================================================

class OfferNoteListView(BranchPermissionMixin, ListView):
    model = OfferNote
    template_name = 'offers/offernote_list.html'
    context_object_name = 'notes'
    paginate_by = 25
    required_perm = 'view_offernote'
    branch_field = 'offer__branch'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_by_branch(queryset, self.request.user, self.branch_field)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(note_text__icontains=q) |
                Q(offer__title__icontains=q)
            )
        return queryset


class OfferNoteDetailView(BranchPermissionMixin, DetailView):
    model = OfferNote
    template_name = 'offers/offernote_detail.html'
    context_object_name = 'note'
    required_perm = 'view_offernote'


class OfferNoteCreateView(BranchPermissionMixin, SuccessMessageMixin, CreateView):
    model = OfferNote
    form_class = OfferNoteForm
    template_name = 'offers/offernote_form.html'
    success_url = reverse_lazy('offernote-list')
    success_message = 'تم إضافة الملاحظة بنجاح.'
    required_perm = 'add_offernote'

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class OfferNoteUpdateView(BranchPermissionMixin, SuccessMessageMixin, UpdateView):
    model = OfferNote
    form_class = OfferNoteForm
    template_name = 'offers/offernote_form.html'
    success_url = reverse_lazy('offernote-list')
    success_message = 'تم تحديث الملاحظة بنجاح.'
    required_perm = 'change_offernote'


class OfferNoteDeleteView(BranchPermissionMixin, SuccessMessageMixin, DeleteView):
    model = OfferNote
    template_name = 'offers/offernote_confirm_delete.html'
    success_url = reverse_lazy('offernote-list')
    success_message = 'تم حذف الملاحظة بنجاح.'
    required_perm = 'delete_offernote'
