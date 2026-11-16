from django.db import migrations


def merge_masters_into_courses(apps, schema_editor):
    """التخصص والدورة بقوا حاجة واحدة («التخصصات»). مفيش بيانات بتتمسح:

    - كل دورة بتاخد نوع واسم ومدة وساعات التخصص بتاعها.
    - كل تخصص ما عليهوش دورات بيتحول لتخصص جديد متاح لكل الفروع.
    - العروض اللي كانت على تخصص بس بتتربط بالتخصص الجديد المقابل ليه.
    - الأكواد بتتعاد بالترتيب عشان تبقى فريدة.
    """
    Master = apps.get_model('courses', 'Master')
    Course = apps.get_model('courses', 'Course')
    StudentOffer = apps.get_model('offers', 'StudentOffer')

    for course in Course.objects.select_related('master'):
        master = course.master
        own_name = (course.name or '').strip()
        course.program_type = master.program_type
        course.name = master.name if not own_name or own_name == master.name else f'{master.name} - {own_name}'
        course.period = master.period
        if course.hours is None:
            course.hours = master.hours
        course.save(update_fields=['program_type', 'name', 'period', 'hours'])

    for master in Master.objects.filter(courses__isnull=True):
        course = Course.objects.create(
            master=master, program_type=master.program_type, name=master.name,
            period=master.period, hours=master.hours, branch=None, last_person=master.last_person,
        )
        Course.objects.filter(pk=course.pk).update(created_at=master.created_at)

    for offer in StudentOffer.objects.filter(course__isnull=True, master__isnull=False):
        courses = Course.objects.filter(master=offer.master)
        offer.course = (
            courses.filter(branch=offer.branch).first()
            or courses.filter(branch__isnull=True).first()
            or courses.first()
        )
        offer.save(update_fields=['course'])

    for code, course in enumerate(Course.objects.order_by('created_at', 'pk'), start=1):
        Course.objects.filter(pk=course.pk).update(code=code)


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_merge_master_into_course'),
        ('offers', '0012_remove_offerrecipient_prospect'),
    ]

    operations = [
        migrations.RunPython(merge_masters_into_courses, migrations.RunPython.noop),
    ]
