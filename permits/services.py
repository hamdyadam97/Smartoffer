"""منطق المشاهد: قواعد الإصدار، توليد الـ PDF، والإرسال."""
import base64
import logging
import os
from io import BytesIO
from types import SimpleNamespace

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Permit

logger = logging.getLogger(__name__)

FONTS_DIR = os.path.join(settings.BASE_DIR, 'static', 'fonts')
FONT_FILES = {
    'cairo': ('Cairo', 'Cairo-Regular.ttf', 'Cairo-Bold.ttf'),
    'amiri': ('Amiri', 'Amiri-Regular.ttf', 'Amiri-Bold.ttf'),
    'droidnaskh': ('Droidnaskh', 'DroidNaskh-Regular.ttf', 'DroidNaskh-Bold.ttf'),
}


# ---------------------------------------------------------------- قواعد الإصدار

def _student_permits(student):
    """مشاهد الطالب النشطة. نفس الشخص ممكن يبقى متسجل طالب في أكتر من فرع، فبنطابق برقم الهوية كمان."""
    qs = Permit.active().select_related('branch', 'issued_by')
    national_id = (student.contact.identity_number or '').strip()
    if national_id:
        return qs.filter(student__contact__identity_number=national_id)
    return qs.filter(student=student)


def find_blocking_permit(student, branch):
    """مشهد نشط في فرع تاني: بيمنع الإصدار لحد ما الفرع ده يلغيه."""
    return _student_permits(student).exclude(branch=branch).order_by('-created_at').first()


def find_existing_permit(student, branch):
    """مشهد نشط في نفس الفرع: مانطلعش واحد مكرر."""
    return _student_permits(student).filter(branch=branch).order_by('-created_at').first()


def contact_for(permit):
    """(الاسم، الرقم) اللي يتكلموا معاه عشان يلغي المشهد القديم."""
    for person in (permit.issued_by, permit.referral_employee):
        if person and (person.mobile or person.phone):
            return person.get_full_name() or person.email, person.mobile or person.phone
    branch = permit.branch
    return branch.name, branch.mobile or branch.phone1


def issue_error(student, branch):
    """رسالة المنع لو مينفعش يتطلع مشهد، أو None."""
    blocking = find_blocking_permit(student, branch)
    if blocking:
        name, phone = contact_for(blocking)
        return (f'الطالب عنده مشهد نشط من فرع «{blocking.branch.name}» (رقم {blocking.number}). '
                f'لازم تتواصل مع {name} على {phone or "رقم غير مسجل"} عشان يلغيه الأول.')
    existing = find_existing_permit(student, branch)
    if existing:
        return (f'الطالب عنده مشهد نشط في نفس الفرع (رقم {existing.number} بتاريخ {existing.issue_date:%Y-%m-%d}). '
                'مينفعش يتطلع مشهد مكرر.')
    return None


# ---------------------------------------------------------------- PDF

def _b64(field_file):
    try:
        if field_file and os.path.exists(field_file.path):
            with open(field_file.path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
    except (ValueError, NotImplementedError):
        pass
    return ''


def _font_face_css(choice):
    family, regular, bold = FONT_FILES.get(choice, FONT_FILES['cairo'])
    faces = []
    for weight, filename in (('normal', regular), ('bold', bold)):
        path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = base64.b64encode(f.read()).decode()
            faces.append(f"@font-face {{ font-family: '{family}'; src: url('data:font/ttf;base64,{data}'); font-weight: {weight}; }}")
    return '\n'.join(faces), f"'{family}', 'Arial', sans-serif"


def _months(period):
    """قوالب البرنامج القديم بتكتب «{{ program.duration_months }} شهر»: لو المدة «24 شهر» نرجّع 24 بس."""
    import re
    match = re.fullmatch(r'\s*(\d+)\s*(شهر|شهور|أشهر|اشهر)?\s*', period or '')
    return match.group(1) if match else (period or '')


def _file_or_none(field_file):
    return field_file if field_file else None


def build_context(permit):
    """نفس أسماء المتغيرات اللي في قوالب برنامج المشاهد القديم (client / institute / program)
    عشان القوالب المنقولة منه تشتغل زي ما هي."""
    contact = permit.student.contact
    branch = permit.branch
    template = branch_template(branch)
    course = permit.course
    client = SimpleNamespace(
        full_name=contact.get_full_name(), national_id=contact.identity_number, phone=contact.mobile,
        mobile=contact.mobile, nationality=contact.nationality, birth_date=contact.birth_date,
    )
    institute = SimpleNamespace(
        name=(template.institute_name if template else '') or branch.name, sub_name=branch.sub_name, code=branch.code, license_number=branch.licence_code,
        phone=branch.mobile or branch.phone1, email=branch.email, address=branch.address,
        logo=_file_or_none(branch.logo), signature_image=_file_or_none(branch.signature),
        stamp_image=_file_or_none(template.stamp_image) if template else None,
        registration_officer=template.registration_officer if template else '',
        city=template.city if template else '', region=template.region if template else '',
    )
    program = SimpleNamespace(
        name=permit.program_name or (course.get_display_name() if course else ''),
        program_type=course.program_type if course else '',
        duration_months=_months(course.period) if course else '', duration=course.period if course else '',
        hours=course.hours if course else None,
        start_date=course.start_date if course else None, end_date=course.end_date if course else None,
    )
    return {
        'permission': permit, 'permit': permit, 'client': client, 'student': permit.student,
        'institute': institute, 'branch': branch, 'program': program, 'issued_by': permit.issued_by,
        'today': timezone.localdate(), 'registration_officer': institute.registration_officer,
        'logo_b64': _b64(branch.logo), 'sig_b64': _b64(branch.signature),
        'stamp_b64': _b64(template.stamp_image) if template else '',
        'bg_b64': _b64(template.background_image) if template else '',
    }


def branch_template(branch):
    from .models import PermitTemplate
    return PermitTemplate.objects.filter(branch=branch).first()


def render_html(permit):
    context = build_context(permit)
    template = branch_template(permit.branch)
    if template is None or not (template.header_content or template.body_content or template.footer_content):
        font_css, font_stack = _font_face_css('cairo')
        return render_to_string('permits/default_pdf.html', {**context, 'font_css': font_css, 'font_stack': font_stack})

    font_css, font_stack = _font_face_css(template.font_family)
    background_css = background_html = ''
    source = template.header_content + template.body_content + template.footer_content + template.custom_css
    # لو القالب بيحط الخلفية بنفسه ({{ bg_b64 }}) مانحطهاش تاني
    bg = '' if 'bg_b64' in source else _b64(template.background_image)
    if bg:
        background_css = (".bg-watermark { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: -1;"
                          f" background-image: url('data:image/png;base64,{bg}'); background-size: 100% 100%; }}")
        background_html = '<div class="bg-watermark"></div>'
    html = f"""<html><head><meta charset="UTF-8"><style>
        @page {{ size: {template.page_size} {template.orientation}; margin: 0; }}
        {font_css}
        body {{ font-family: {font_stack}; direction: rtl; margin: 0; }}
        .page-container {{ padding: 1.5cm; box-sizing: border-box; }}
        {template.custom_css}
        {background_css}
    </style></head><body>{background_html}<div class="page-container">
        <header>{template.header_content}</header>
        <main>{template.body_content}</main>
        <footer>{template.footer_content}</footer>
    </div></body></html>"""
    return Template(html).render(Context(context))


def build_pdf(permit, strict=False):
    """بيرجّع bytes الـ PDF. لو قالب الفرع فيه غلط بيرجع للقالب الافتراضي،
    إلا لو strict (معاينة القالب): ساعتها الغلط بيطلع عشان يتصلح."""
    from weasyprint import HTML  # تقيلة ومحتاجة مكتبات نظام، فبنستوردها وقت الحاجة بس
    try:
        html = render_html(permit)
        return HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()
    except Exception:
        if strict:
            raise
        logger.exception('Permit template failed for branch %s, using default', permit.branch_id)
        font_css, font_stack = _font_face_css('cairo')
        html = render_to_string('permits/default_pdf.html',
                                {**build_context(permit), 'font_css': font_css, 'font_stack': font_stack})
        return HTML(string=html, base_url=str(settings.BASE_DIR)).write_pdf()


def pdf_filename(permit):
    return f'{permit.number}.pdf'


# ---------------------------------------------------------------- الإرسال

def whatsapp_caption(permit, title='✅ مشهد'):
    return (f'{title}\nالطالب: {permit.student.contact.get_full_name()}\n'
            f'البرنامج: {permit.program_name or "-"}\nرقم المشهد: {permit.number}\nالفرع: {permit.branch.name}')


def send_whatsapp(permit, phone, title='✅ مشهد'):
    from offers.whatsapp import send_whatsapp_pdf
    return send_whatsapp_pdf(phone, filename=pdf_filename(permit), pdf_bytes=build_pdf(permit),
                             caption=whatsapp_caption(permit, title))


def send_email(permit, email, site_url=''):
    name = permit.student.contact.get_full_name()
    html = render_to_string('permits/email.html', {'permit': permit, 'name': name, 'site_url': site_url})
    msg = EmailMultiAlternatives(
        subject=f'مشهد تسجيل: {name}',
        body=f'مرحباً {name}، مرفق مشهد التسجيل رقم {permit.number} - {permit.program_name}.',
        from_email=settings.DEFAULT_FROM_EMAIL, to=[email],
    )
    msg.attach_alternative(html, 'text/html')
    msg.attach(pdf_filename(permit), build_pdf(permit), 'application/pdf')
    msg.send()
